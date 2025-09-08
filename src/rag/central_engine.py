"""
Central Engine & Query Processing Pipeline

Main orchestrator that makes LLM calls and coordinates the entire query processing pipeline.
Implements the design from DESIGN_CENTRAL_PROMPT_SYSTEM.md with three parallel LLM calls.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

# Import LLM client abstraction
from .llm_client import LLMClient, LLMClientFactory
from .config import get_config

# Import query router types
from .character.character_query_router import CharacterQueryRouter, CharacterQueryResult
from .character.character_query_types import UserIntention as CharacterIntention
from .rulebook.rulebook_query_router import RulebookQueryRouter
from .rulebook.rulebook_types import RulebookQueryIntent, SearchResult, QueryPerformanceMetrics
from .session_notes.session_notes_query_router import SessionNotesQueryRouter
from .session_notes.campaign_session_notes_storage import CampaignSessionNotesStorage
from .session_notes.session_types import QueryEngineResult


# ===== ROUTER OUTPUT DATACLASSES =====

@dataclass
class CharacterLLMRouterOutput:
    """Output from Character Router LLM call."""
    is_needed: bool
    user_intention: Optional[str] = None
    entities: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RulebookLLMRouterOutput:
    """Output from Rulebook Router LLM call."""
    is_needed: bool
    user_intention: Optional[str] = None
    entities: List[Dict[str, str]] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)
    k: int = 5


@dataclass
class SessionNotesLLMRouterOutput:
    """Output from Session Notes Router LLM call."""
    is_needed: bool
    character_name: str = ""
    user_intention: Optional[str] = None
    entities: List[Dict[str, str]] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)
    top_k: int = 5


@dataclass
class RouterOutputs:
    """Combined outputs from all three router LLM calls."""
    character_output: Optional[CharacterLLMRouterOutput] = None
    rulebook_output: Optional[RulebookLLMRouterOutput] = None
    session_notes_output: Optional[SessionNotesLLMRouterOutput] = None


# ===== CENTRAL ENGINE =====

class CentralEngine:
    """Main orchestrator - makes all LLM calls and coordinates the pipeline."""
    
    def __init__(self, llm_clients: Dict[str, LLMClient], prompt_manager, 
                 character=None, rulebook_storage=None, campaign_session_notes=None):
        """Initialize with LLM clients and prompt manager."""
        self.llm_clients = llm_clients
        self.prompt_manager = prompt_manager
        self.config = get_config()
        
        # Initialize query routers with required storage instances
        self.character_router = CharacterQueryRouter(character) if character else None
        self.rulebook_router = RulebookQueryRouter(rulebook_storage) if rulebook_storage else None
        self.session_notes_router = SessionNotesQueryRouter(campaign_session_notes) if campaign_session_notes else None
    
    @classmethod
    def create_from_config(cls, prompt_manager, character=None, 
                          rulebook_storage=None, campaign_session_notes=None):
        """Create CentralEngine instance using default configuration."""
        llm_clients = LLMClientFactory.create_default_clients()
        return cls(llm_clients, prompt_manager, character, rulebook_storage, campaign_session_notes)
    
    async def process_query(self, user_query: str, character_name: str) -> str:
        """
        Main processing pipeline:
        1. Get router decision prompts from Prompt Manager
        2. Make 3 parallel LLM calls for router decisions  
        3. Execute needed query routers in parallel
        4. Get final response prompt from Prompt Manager/Context Assembler
        5. Make final LLM call and return response
        """
        # Step 1: Make parallel router decisions
        router_outputs = await self.make_parallel_router_decisions(user_query, character_name)
        
        # Step 2: Execute needed routers in parallel
        raw_results = await self.execute_needed_routers(router_outputs, user_query)
        
        # Step 3: Generate final response
        final_response = await self.generate_final_response(raw_results, user_query)
        
        return final_response
    
    async def make_parallel_router_decisions(self, user_query: str, character_name: str) -> RouterOutputs:
        """
        Make 3 parallel LLM calls to determine router needs and generate inputs.
        Gets prompts from Prompt Manager, makes LLM calls, returns decisions.
        """
        # Get prompts from Prompt Manager
        character_prompt = self.prompt_manager.get_character_router_prompt(user_query, character_name)
        rulebook_prompt = self.prompt_manager.get_rulebook_router_prompt(user_query)
        session_notes_prompt = self.prompt_manager.get_session_notes_router_prompt(user_query, character_name)
        
        # Make parallel LLM calls
        tasks = [
            self._make_character_router_llm_call(character_prompt, character_name),
            self._make_rulebook_router_llm_call(rulebook_prompt),
            self._make_session_notes_router_llm_call(session_notes_prompt, character_name)
        ]
        
        character_output, rulebook_output, session_notes_output = await asyncio.gather(*tasks)
        
        return RouterOutputs(
            character_output=character_output,
            rulebook_output=rulebook_output,
            session_notes_output=session_notes_output
        )
    
    async def execute_needed_routers(self, router_outputs: RouterOutputs, user_query: str = "") -> Dict[str, Any]:
        """
        Execute only the needed query routers in parallel based on LLM decisions.
        Returns raw router results for context assembly.
        """
        print("🔧 DEBUG: Starting router execution...")
        tasks = []
        result_keys = []
        
        # Character router execution
        if router_outputs.character_output and router_outputs.character_output.is_needed:
            print(f"🔧 DEBUG: Scheduling Character router execution")
            print(f"   • Character router available: {self.character_router is not None}")
            print(f"   • User intention: {router_outputs.character_output.user_intention}")
            tasks.append(self._execute_character_router(router_outputs.character_output))
            result_keys.append("character")
        else:
            print("🔧 DEBUG: Character router NOT scheduled")
            print(f"   • Output exists: {router_outputs.character_output is not None}")
            print(f"   • Is needed: {router_outputs.character_output.is_needed if router_outputs.character_output else 'N/A'}")
        
        # Rulebook router execution
        if router_outputs.rulebook_output and router_outputs.rulebook_output.is_needed and self.rulebook_router:
            print(f"🔧 DEBUG: Scheduling Rulebook router execution")
            print(f"   • Rulebook router available: {self.rulebook_router is not None}")
            print(f"   • User intention: {router_outputs.rulebook_output.user_intention}")
            tasks.append(self._execute_rulebook_router(router_outputs.rulebook_output, user_query))
            result_keys.append("rulebook")
        else:
            print("🔧 DEBUG: Rulebook router NOT scheduled")
            print(f"   • Output exists: {router_outputs.rulebook_output is not None}")
            print(f"   • Is needed: {router_outputs.rulebook_output.is_needed if router_outputs.rulebook_output else 'N/A'}")
            print(f"   • Router available: {self.rulebook_router is not None}")
        
        # Session notes router execution
        if router_outputs.session_notes_output and router_outputs.session_notes_output.is_needed and self.session_notes_router:
            print(f"🔧 DEBUG: Scheduling Session Notes router execution")
            print(f"   • Session Notes router available: {self.session_notes_router is not None}")
            print(f"   • User intention: {router_outputs.session_notes_output.user_intention}")
            tasks.append(self._execute_session_notes_router(router_outputs.session_notes_output, user_query))
            result_keys.append("session_notes")
        else:
            print("🔧 DEBUG: Session Notes router NOT scheduled")
            print(f"   • Output exists: {router_outputs.session_notes_output is not None}")
            print(f"   • Is needed: {router_outputs.session_notes_output.is_needed if router_outputs.session_notes_output else 'N/A'}")
            print(f"   • Router available: {self.session_notes_router is not None}")
        
        print(f"🔧 DEBUG: Total tasks scheduled: {len(tasks)} - {result_keys}")
        
        # Execute all needed routers in parallel
        if tasks:
            print("🔧 DEBUG: Executing scheduled router tasks...")
            try:
                results = await asyncio.gather(*tasks)
                print(f"🔧 DEBUG: Router execution completed, got {len(results)} results")
                return dict(zip(result_keys, results))
            except Exception as e:
                print(f"🔧 DEBUG: Router execution failed: {str(e)}")
                raise e
        else:
            print("🔧 DEBUG: No tasks to execute, returning empty results")
            return {}
    
    async def generate_final_response(self, raw_results: Dict[str, Any], user_query: str) -> str:
        """
        Get final response prompt from Prompt Manager and make final LLM call.
        Returns completed response to user.
        """
        # Get final response prompt from Prompt Manager/Context Assembler
        final_prompt = self.prompt_manager.get_final_response_prompt(raw_results, user_query)
        
        # Make final LLM call for response generation using configured provider and model
        try:
            # Use configured final response provider
            provider = self.config.final_response_llm_provider
            final_client = self.llm_clients.get(provider)
            
            if not final_client:
                # Fallback to available clients using new naming convention
                final_client = (self.llm_clients.get("openai") or 
                               self.llm_clients.get("anthropic"))
                if not final_client:
                    return "Error: No suitable LLM client available for final response generation"
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_final_model
            elif provider == "anthropic":
                model = self.config.anthropic_final_model
            else:
                model = None  # Use client default
            
            # Get LLM parameters from config
            llm_params = self.config.get_final_llm_params(model)
            
            response = await final_client.generate_response(
                final_prompt,
                model=model,
                **llm_params
            )
            
            if response.success:
                return response.content
            else:
                return f"Error generating final response: {response.error}"
        except Exception as e:
            return f"Error generating final response: {str(e)}"
    
    # ===== PRIVATE LLM CALL METHODS =====
    
    async def _make_character_router_llm_call(self, prompt: str, character_name: str) -> CharacterLLMRouterOutput:
        """Make LLM call for character router decision."""
        try:
            # Use configured router provider
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider)
            
            if not client:
                # Fallback to router clients using new naming convention
                client = (self.llm_clients.get("openai_router") or 
                         self.llm_clients.get("anthropic_router") or
                         self.llm_clients.get("openai") or 
                         self.llm_clients.get("anthropic"))
                if not client:
                    raise RuntimeError("No suitable LLM client available for character router")
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_router_model
            elif provider == "anthropic":
                model = self.config.anthropic_router_model
            else:
                model = None  # Use client default
            
            # Get LLM parameters from config
            llm_params = self.config.get_router_llm_params(model)
            
            response = await client.generate_json_response(
                prompt,
                model=model,
                **llm_params
            )
            
            # Strict validation of response format
            if "error" in response:
                raise RuntimeError(f"Character router LLM call failed: {response['error']}")
            
            # Validate required fields
            if "is_needed" not in response:
                raise ValueError("Character router response missing required field 'is_needed'")
                
            is_needed = response["is_needed"]
            
            # Validate intention requirement
            if is_needed and (response.get("user_intention") is None or response.get("user_intention") == ""):
                raise ValueError("Character router response has 'is_needed': true but missing valid 'user_intention'")
            
            # Validate entities format
            entities = response.get("entities", [])
            if not isinstance(entities, list):
                raise ValueError("Character router response 'entities' must be a list")
            
            for entity in entities:
                if not isinstance(entity, dict):
                    raise ValueError("Character router response entities must be dictionaries")
                if "name" not in entity:
                    raise ValueError("Character router response entity missing required field 'name'")
                if "type" not in entity:
                    raise ValueError("Character router response entity missing required field 'type'")
            
            return CharacterLLMRouterOutput(
                is_needed=is_needed,
                user_intention=response.get("user_intention"),
                entities=entities
            )
        except Exception as e:
            # Re-raise all exceptions instead of providing fallbacks
            raise RuntimeError(f"Character router LLM call failed: {str(e)}") from e
    
    async def _make_rulebook_router_llm_call(self, prompt: str) -> RulebookLLMRouterOutput:
        """Make LLM call for rulebook router decision."""
        try:
            # Use configured router provider
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider)
            
            if not client:
                # Fallback to router clients using new naming convention
                client = (self.llm_clients.get("openai_router") or 
                         self.llm_clients.get("anthropic_router") or
                         self.llm_clients.get("openai") or 
                         self.llm_clients.get("anthropic"))
                if not client:
                    raise RuntimeError("No suitable LLM client available for rulebook router")
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_router_model
            elif provider == "anthropic":
                model = self.config.anthropic_router_model
            else:
                model = None  # Use client default
            
            # Get LLM parameters from config
            llm_params = self.config.get_router_llm_params(model)
            
            response = await client.generate_json_response(
                prompt,
                model=model,
                **llm_params
            )
            
            # Strict validation of response format
            if "error" in response:
                raise RuntimeError(f"Rulebook router LLM call failed: {response['error']}")
            
            # Validate required fields
            if "is_needed" not in response:
                raise ValueError("Rulebook router response missing required field 'is_needed'")
                
            is_needed = response["is_needed"]
            
            # Validate intention requirement (note: uses 'intention' not 'user_intention' for rulebook)
            if is_needed and (response.get("intention") is None or response.get("intention") == ""):
                raise ValueError("Rulebook router response has 'is_needed': true but missing valid 'intention'")
            
            # Validate entities format
            entities = response.get("entities", [])
            if not isinstance(entities, list):
                raise ValueError("Rulebook router response 'entities' must be a list")
            
            # Validate context_hints format
            context_hints = response.get("context_hints", [])
            if not isinstance(context_hints, list):
                raise ValueError("Rulebook router response 'context_hints' must be a list")
            
            return RulebookLLMRouterOutput(
                is_needed=is_needed,
                user_intention=response.get("intention"),
                entities=entities,
                context_hints=context_hints,
                k=5  # Fixed internally
            )
        except Exception as e:
            # Re-raise validation errors and LLM errors
            raise RuntimeError(f"Rulebook router failed: {str(e)}") from e
    
    async def _make_session_notes_router_llm_call(self, prompt: str, character_name: str) -> SessionNotesLLMRouterOutput:
        """Make LLM call for session notes router decision."""
        try:
            # Use configured router provider
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider)
            
            if not client:
                # Fallback to router clients using new naming convention
                client = (self.llm_clients.get("openai_router") or 
                         self.llm_clients.get("anthropic_router") or
                         self.llm_clients.get("openai") or 
                         self.llm_clients.get("anthropic"))
                if not client:
                    raise RuntimeError("No suitable LLM client available for session notes router")
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_router_model
            elif provider == "anthropic":
                model = self.config.anthropic_router_model
            else:
                model = None  # Use client default
            
            # Get LLM parameters from config
            llm_params = self.config.get_router_llm_params(model)
            
            response = await client.generate_json_response(
                prompt,
                model=model,
                **llm_params
            )
            
            # Strict validation of response format
            if "error" in response:
                raise RuntimeError(f"Session notes router LLM call failed: {response['error']}")
            
            # Validate required fields
            if "is_needed" not in response:
                raise ValueError("Session notes router response missing required field 'is_needed'")
                
            is_needed = response["is_needed"]
            
            # Validate intention requirement
            if is_needed and (response.get("intention") is None or response.get("intention") == ""):
                raise ValueError("Session notes router response has 'is_needed': true but missing valid 'intention'")
            
            # Validate entities format
            entities = response.get("entities", [])
            if not isinstance(entities, list):
                raise ValueError("Session notes router response 'entities' must be a list")
            
            # Validate context_hints format
            context_hints = response.get("context_hints", [])
            if not isinstance(context_hints, list):
                raise ValueError("Session notes router response 'context_hints' must be a list")
            
            return SessionNotesLLMRouterOutput(
                is_needed=is_needed,
                character_name=character_name,  # Set from engine class
                user_intention=response.get("intention"),
                entities=entities,
                context_hints=context_hints,
                top_k=5  # Fixed internally
            )
        except Exception as e:
            # Re-raise validation errors and LLM errors
            raise RuntimeError(f"Session notes router failed: {str(e)}") from e
    
    # ===== PRIVATE ROUTER EXECUTION METHODS =====
    
    async def _execute_character_router(self, output: CharacterLLMRouterOutput) -> CharacterQueryResult:
        """Execute character query router with LLM-generated inputs."""
        print(f"🔧 DEBUG: Executing Character router...")
        print(f"   • User intention: {output.user_intention}")
        print(f"   • Entities count: {len(output.entities) if output.entities else 0}")
        
        if not output.user_intention:
            print("🔧 DEBUG: No user intention, returning empty result")
            return CharacterQueryResult(character_data={})
        
        if not self.character_router:
            print("🔧 DEBUG: Character router not available!")
            return CharacterQueryResult(character_data={}, warnings=["Character router not available"])
        
        try:
            print(f"🔧 DEBUG: Calling character_router.query_character() with intention '{output.user_intention}'")
            # Pass parameters directly from LLM router output (character is pre-loaded)
            result = self.character_router.query_character(
                user_intention=output.user_intention,
                entities=output.entities
            )
            print(f"🔧 DEBUG: Character router returned result with {len(result.character_data) if result.character_data else 0} data items")
            return result
        except Exception as e:
            print(f"🔧 DEBUG: Character router execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return CharacterQueryResult(character_data={}, warnings=[f"Character router error: {str(e)}"])
    
    async def _execute_rulebook_router(self, output: RulebookLLMRouterOutput, user_query: str) -> tuple[List[SearchResult], Optional[QueryPerformanceMetrics]]:
        """Execute rulebook query router with LLM-generated inputs."""
        print(f"🔧 DEBUG: Executing Rulebook router...")
        print(f"   • User intention: {output.user_intention}")
        print(f"   • Entities count: {len(output.entities) if output.entities else 0}")
        print(f"   • Context hints: {len(output.context_hints) if output.context_hints else 0}")
        
        if not output.user_intention or not self.rulebook_router:
            print("🔧 DEBUG: No intention or router unavailable, returning empty results")
            return [], None
        
        try:
            print(f"🔧 DEBUG: Converting intention '{output.user_intention}' to enum")
            # Convert string intention to enum
            intention_enum = RulebookQueryIntent(output.user_intention.lower())
            print(f"🔧 DEBUG: Converted to enum: {intention_enum}")
            
            # Pass all parameters directly from LLM router output
            print(f"🔧 DEBUG: Calling rulebook_router.query() with {output.k} results")
            results, performance = self.rulebook_router.query(
                intention=intention_enum,
                user_query=user_query,  # Get from engine class
                entities=[entity["name"] for entity in output.entities],
                context_hints=output.context_hints,
                k=output.k
            )
            print(f"🔧 DEBUG: Rulebook router returned {len(results) if results else 0} results")
            return results, performance
        except Exception as e:
            print(f"🔧 DEBUG: Rulebook router execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], None
    
    async def _execute_session_notes_router(self, output: SessionNotesLLMRouterOutput, user_query: str) -> QueryEngineResult:
        """Execute session notes query router with LLM-generated inputs."""
        print(f"🔧 DEBUG: Executing Session Notes router...")
        print(f"   • User intention: {output.user_intention}")
        print(f"   • Character name: {output.character_name}")
        print(f"   • Entities count: {len(output.entities) if output.entities else 0}")
        print(f"   • Context hints: {len(output.context_hints) if output.context_hints else 0}")
        
        if not output.user_intention or not self.session_notes_router:
            print("🔧 DEBUG: No intention or router unavailable, returning empty result")
            return QueryEngineResult(contexts=[], total_sessions_searched=0, entities_resolved=[])
        
        try:
            print(f"🔧 DEBUG: Calling session_notes_router.query() with top_k={output.top_k}")
            # Pass all parameters directly from LLM router output
            result = self.session_notes_router.query(
                character_name=output.character_name,
                original_query=user_query,  # Get from engine class
                intention=output.user_intention,
                entities=output.entities,
                context_hints=output.context_hints,
                top_k=output.top_k
            )
            print(f"🔧 DEBUG: Session Notes router returned {len(result.contexts) if result.contexts else 0} contexts")
            return result
        except Exception as e:
            print(f"🔧 DEBUG: Session Notes router execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return QueryEngineResult(contexts=[], total_sessions_searched=0, entities_resolved=[])
