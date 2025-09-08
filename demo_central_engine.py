"""
Interactive Central Engine Demo

Simple script that lets you ask questions to the CentralEngine and see:
- Router decisions (which routers are needed)
- Performance metrics
- Full response from the model
- All using config.py settings
"""
import asyncio
import sys
from pathlib import Path
import json
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag.central_engine import CentralEngine
from src.rag.central_prompt_manager import CentralPromptManager
from src.rag.context_assembler import ContextAssembler
from src.rag.config import get_config
from src.utils.character_manager import CharacterManager
from src.rag.rulebook.rulebook_storage import RulebookStorage
from src.rag.session_notes.session_notes_storage import SessionNotesStorage


class InteractiveCentralEngineDemo:
    """Interactive demo that shows routing decisions and performance"""
    
    def __init__(self):
        """Initialize the demo with CentralEngine"""
        print("🚀 Initializing ShadowScribe2.0 Central Engine...")
        
        # Load config
        self.config = get_config()
        print(f"   Config loaded - Router: {self.config.router_llm_provider}, Final: {self.config.final_response_llm_provider}")
        
        # Load storage components
        print("📦 Loading storage components...")
        
        # Load Duskryn character
        character_manager = CharacterManager()
        character_name = "Duskryn Nightwarden"
        try:
            character = character_manager.load_character(character_name)
            print(f"   ✅ Character loaded: {character.character_base.name}")
            self.character_name = character.character_base.name
        except Exception as e:
            print(f"   ⚠️  Failed to load character: {e}")
            character = None
            self.character_name = "Demo Character"
        
        # Load rulebook storage
        try:
            rulebook_storage = RulebookStorage()
            if rulebook_storage.load_from_disk("rulebook_storage.pkl"):
                print(f"   ✅ Rulebook storage loaded")
            else:
                print(f"   ⚠️  Rulebook storage file not found")
                rulebook_storage = None
        except Exception as e:
            print(f"   ⚠️  Failed to load rulebook storage: {e}")
            rulebook_storage = None
        
        # Load session notes storage
        try:
            session_notes_storage = SessionNotesStorage()
            main_campaign = session_notes_storage.get_campaign("main_campaign")
            if main_campaign:
                print(f"   ✅ Session notes storage loaded for main_campaign")
            else:
                print(f"   ⚠️  Main campaign not found in session notes")
                main_campaign = None
        except Exception as e:
            print(f"   ⚠️  Failed to load session notes: {e}")
            main_campaign = None
        
        # Create components
        self.context_assembler = ContextAssembler()
        self.prompt_manager = CentralPromptManager(self.context_assembler)
        
        # Create central engine using config with storage components
        self.engine = CentralEngine.create_from_config(
            self.prompt_manager,
            character=character,
            rulebook_storage=rulebook_storage,
            campaign_session_notes=main_campaign
        )
        
        print(f"   LLM Clients available: {list(self.engine.llm_clients.keys())}")
        print("✅ Central Engine ready!\n")
    
    async def process_query_with_visibility(self, user_query: str, character_name: str = None):
        """Process a query with full visibility into routing and performance"""
        
        # Use loaded character name if none provided
        if character_name is None:
            character_name = self.character_name
        
        print("=" * 80)
        print(f"🎯 PROCESSING QUERY: '{user_query}'")
        print(f"📋 Character: {character_name}")
        print("=" * 80)
        
        # Step 1: Show router decisions
        print("\n🧠 STEP 1: Router Decision Phase")
        print("-" * 40)
        
        router_outputs = await self.engine.make_parallel_router_decisions(user_query, character_name)
        
        # Display character router decision
        if router_outputs.character_output:
            print(f"📊 Character Router:")
            print(f"   • Needed: {router_outputs.character_output.is_needed}")
            print(f"   • Intention: {router_outputs.character_output.user_intention}")
            print(f"   • Entities: {len(router_outputs.character_output.entities)} found")
            if router_outputs.character_output.entities:
                for entity in router_outputs.character_output.entities[:3]:  # Show first 3
                    print(f"     - {entity.get('name', 'Unknown')} ({entity.get('type', 'unknown')})")
        
        # Display rulebook router decision
        if router_outputs.rulebook_output:
            print(f"📚 Rulebook Router:")
            print(f"   • Needed: {router_outputs.rulebook_output.is_needed}")
            print(f"   • Intention: {router_outputs.rulebook_output.user_intention}")
            print(f"   • Entities: {len(router_outputs.rulebook_output.entities)} found")
            print(f"   • Context Hints: {len(router_outputs.rulebook_output.context_hints)} provided")
        
        # Display session notes router decision
        if router_outputs.session_notes_output:
            print(f"📝 Session Notes Router:")
            print(f"   • Needed: {router_outputs.session_notes_output.is_needed}")
            print(f"   • Intention: {router_outputs.session_notes_output.user_intention}")
            print(f"   • Entities: {len(router_outputs.session_notes_output.entities)} found")
        
        # Step 2: Execute routers and show performance
        print(f"\n⚡ STEP 2: Router Execution Phase")
        print("-" * 40)
        
        import time
        start_time = time.time()
        
        raw_results = await self.engine.execute_needed_routers(router_outputs, user_query)
        
        execution_time = time.time() - start_time
        
        print(f"🏃 Execution completed in {execution_time:.2f}s")
        print(f"📊 Results obtained from {len(raw_results)} router(s)")
        
        for router_name, result in raw_results.items():
            print(f"   • {router_name.title()} Router: {'✅ Success' if result else '❌ No data'}")
        
        # Step 3: Generate final response
        print(f"\n🎨 STEP 3: Final Response Generation")
        print("-" * 40)
        
        start_time = time.time()
        
        final_response = await self.engine.generate_final_response(raw_results, user_query)
        
        generation_time = time.time() - start_time
        
        print(f"💬 Response generated in {generation_time:.2f}s")
        print(f"📏 Response length: {len(final_response)} characters")
        
        # Step 4: Show configuration used
        print(f"\n⚙️  CONFIGURATION USED")
        print("-" * 40)
        print(f"Router Model: {self.config.openai_router_model if self.config.router_llm_provider == 'openai' else self.config.anthropic_router_model}")
        print(f"Router Temp: {self.config.router_temperature}")
        print(f"Router Max Tokens: {self.config.router_max_tokens}")
        print(f"Final Model: {self.config.openai_final_model if self.config.final_response_llm_provider == 'openai' else self.config.anthropic_final_model}")
        print(f"Final Temp: {self.config.final_temperature}")
        print(f"Final Max Tokens: {self.config.final_max_tokens}")
        
        # Step 5: Show final response
        print(f"\n🎯 FINAL RESPONSE")
        print("=" * 80)
        print(final_response)
        print("=" * 80)
        
        return final_response
    
    def run_interactive_demo(self):
        """Run the interactive demo loop"""
        print("🎮 Interactive ShadowScribe2.0 Demo")
        print("Type your questions below. Type 'quit' to exit.\n")
        
        while True:
            try:
                # Get user input
                user_query = input("❓ Your question: ").strip()
                
                if user_query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thanks for using ShadowScribe2.0!")
                    break
                
                if not user_query:
                    print("Please enter a question.\n")
                    continue
                
                # Process the query
                asyncio.run(self.process_query_with_visibility(user_query))
                
                print("\n" + "="*80 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using ShadowScribe2.0!")
                break
            except Exception as e:
                print(f"❌ Error processing query: {str(e)}")
                print("Please try again.\n")


def main():
    """Main entry point"""
    try:
        demo = InteractiveCentralEngineDemo()
        demo.run_interactive_demo()
    except Exception as e:
        print(f"❌ Failed to initialize demo: {str(e)}")
        print("Make sure you have activated the virtual environment and set up your API keys.")


if __name__ == "__main__":
    main()
