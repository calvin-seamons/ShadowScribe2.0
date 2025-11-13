"""Chat service for processing queries through CentralEngine."""
import sys
from pathlib import Path
from typing import AsyncGenerator, Callable, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.central_engine import CentralEngine
from src.llm.central_prompt_manager import CentralPromptManager
from src.rag.context_assembler import ContextAssembler
from src.utils.character_manager import CharacterManager
from src.rag.rulebook.rulebook_storage import RulebookStorage
from src.rag.session_notes.session_notes_storage import SessionNotesStorage
from src.config import get_config
from api.database.connection import AsyncSessionLocal


class ChatService:
    """Service for handling chat queries."""
    
    def __init__(self):
        """Initialize chat service with CentralEngine."""
        self._engines = {}
        self._rulebook_storage = None
        self._session_notes_storage = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize rulebook and session notes storage."""
        try:
            # Load rulebook storage
            self._rulebook_storage = RulebookStorage()
            rulebook_path = Path(project_root) / "knowledge_base" / "processed_rulebook" / "rulebook_storage.pkl"
            if rulebook_path.exists():
                self._rulebook_storage.load_from_disk(str(rulebook_path))
            
            # Load session notes storage
            session_storage = SessionNotesStorage()
            self._session_notes_storage = session_storage.get_campaign("main_campaign")
        except Exception as e:
            print(f"Warning: Could not load storage: {e}")
    
    async def _get_or_create_engine(self, character_name: str) -> CentralEngine:
        """Get or create CentralEngine for character."""
        if character_name in self._engines:
            return self._engines[character_name]
        
        # Create database session and character manager
        async with AsyncSessionLocal() as db_session:
            character_manager = CharacterManager(db_session=db_session)
            
            # Load character from database (with pickle fallback)
            character = await character_manager.load_character_async(character_name)
            if not character:
                raise ValueError(f"Character '{character_name}' not found")
            
            # Create engine
            context_assembler = ContextAssembler()
            prompt_manager = CentralPromptManager(context_assembler)
            
            engine = CentralEngine.create_from_config(
                prompt_manager,
                character=character,
                rulebook_storage=self._rulebook_storage,
                campaign_session_notes=self._session_notes_storage
            )
            
            self._engines[character_name] = engine
            return engine
    
    def clear_conversation_history(self, character_name: str):
        """Clear conversation history for a character."""
        if character_name in self._engines:
            self._engines[character_name].clear_conversation_history()
    
    async def process_query_stream(
        self, 
        user_query: str, 
        character_name: str,
        metadata_callback: Optional[Callable] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process query and stream response chunks.
        
        Args:
            user_query: User's question
            character_name: Name of character
            metadata_callback: Optional async callback for metadata events
        """
        engine = await self._get_or_create_engine(character_name)
        
        async for chunk in engine.process_query_stream(user_query, character_name, metadata_callback):
            yield chunk
