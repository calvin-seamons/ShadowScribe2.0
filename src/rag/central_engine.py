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
    
    def process_query(self, user_query: str, character_name: str) -> str:
        """
        Main processing pipeline:
        1. Get router decision prompts from Prompt Manager
        2. Make 3 parallel LLM calls for router decisions  
        3. Execute needed query routers in parallel
        4. Get final response prompt from Prompt Manager/Context Assembler
        5. Make final LLM call and return response
        """
        # Step 1: Make parallel router decisions
        router_outputs = asyncio.run(
            self.make_parallel_router_decisions(user_query, character_name)
        )
        
        # Step 2: Execute needed routers in parallel
        raw_results = asyncio.run(
            self.execute_needed_routers(router_outputs, user_query)
        )
        
        # Step 3: Generate final response
        final_response = self.generate_final_response(raw_results, user_query)
        
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
        tasks = []
        result_keys = []
        
        # Character router execution
        if router_outputs.character_output and router_outputs.character_output.is_needed:
            tasks.append(self._execute_character_router(router_outputs.character_output))
            result_keys.append("character")
        
        # Rulebook router execution
        if router_outputs.rulebook_output and router_outputs.rulebook_output.is_needed and self.rulebook_router:
            tasks.append(self._execute_rulebook_router(router_outputs.rulebook_output, user_query))
            result_keys.append("rulebook")
        
        # Session notes router execution
        if router_outputs.session_notes_output and router_outputs.session_notes_output.is_needed and self.session_notes_router:
            tasks.append(self._execute_session_notes_router(router_outputs.session_notes_output, user_query))
            result_keys.append("session_notes")
        
        # Execute all needed routers in parallel
        if tasks:
            results = await asyncio.gather(*tasks)
            return dict(zip(result_keys, results))
        else:
            return {}
    
    def generate_final_response(self, raw_results: Dict[str, Any], user_query: str) -> str:
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
                # Fallback to available clients
                final_client = self.llm_clients.get("openai_gpt4") or self.llm_clients.get("openai") or self.llm_clients.get("anthropic")
                if not final_client:
                    return "Error: No suitable LLM client available for final response generation"
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_final_model
            elif provider == "anthropic":
                model = self.config.anthropic_final_model
            else:
                model = None  # Use client default
            
            response = asyncio.run(final_client.generate_response(
                final_prompt,
                model=model,
                temperature=0.7,
                max_tokens=1500
            ))
            
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
                # Fallback to available clients
                client = self.llm_clients.get("openai") or self.llm_clients.get("anthropic")
                if not client:
                    return CharacterLLMRouterOutput(is_needed=False)
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_router_model
            elif provider == "anthropic":
                model = self.config.anthropic_router_model
            else:
                model = None  # Use client default
            
            response = await client.generate_json_response(
                prompt,
                model=model,
                temperature=0.3,
                max_tokens=500
            )
            
            if "error" in response:
                return CharacterLLMRouterOutput(is_needed=False)
            
            return CharacterLLMRouterOutput(
                is_needed=response.get("is_needed", False),
                user_intention=response.get("user_intention"),
                entities=response.get("entities", [])
            )
        except Exception as e:
            # Fallback to not needed on error
            return CharacterLLMRouterOutput(is_needed=False)
    
    async def _make_rulebook_router_llm_call(self, prompt: str) -> RulebookLLMRouterOutput:
        """Make LLM call for rulebook router decision."""
        try:
            # Use configured router provider
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider)
            
            if not client:
                # Fallback to available clients
                client = self.llm_clients.get("anthropic") or self.llm_clients.get("openai")
                if not client:
                    return RulebookLLMRouterOutput(is_needed=False)
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_router_model
            elif provider == "anthropic":
                model = self.config.anthropic_router_model
            else:
                model = None  # Use client default
            
            response = await client.generate_json_response(
                prompt,
                model=model,
                max_tokens=500
            )
            
            if "error" in response:
                return RulebookLLMRouterOutput(is_needed=False)
            
            return RulebookLLMRouterOutput(
                is_needed=response.get("is_needed", False),
                user_intention=response.get("user_intention"),
                entities=response.get("entities", []),
                context_hints=response.get("context_hints", []),
                k=5  # Fixed internally
            )
        except Exception as e:
            # Fallback to not needed on error
            return RulebookLLMRouterOutput(is_needed=False)
    
    async def _make_session_notes_router_llm_call(self, prompt: str, character_name: str) -> SessionNotesLLMRouterOutput:
        """Make LLM call for session notes router decision."""
        try:
            # Use configured router provider
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider)
            
            if not client:
                # Fallback to available clients
                client = self.llm_clients.get("openai") or self.llm_clients.get("anthropic")
                if not client:
                    return SessionNotesLLMRouterOutput(is_needed=False, character_name=character_name)
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_router_model
            elif provider == "anthropic":
                model = self.config.anthropic_router_model
            else:
                model = None  # Use client default
            
            response = await client.generate_json_response(
                prompt,
                model=model,
                temperature=0.3,
                max_tokens=500
            )
            
            if "error" in response:
                return SessionNotesLLMRouterOutput(is_needed=False, character_name=character_name)
            
            return SessionNotesLLMRouterOutput(
                is_needed=response.get("is_needed", False),
                character_name=character_name,  # Set from engine class
                user_intention=response.get("user_intention"),
                entities=response.get("entities", []),
                context_hints=response.get("context_hints", []),
                top_k=5  # Fixed internally
            )
        except Exception as e:
            # Fallback to not needed on error
            return SessionNotesLLMRouterOutput(is_needed=False, character_name=character_name)
    
    # ===== PRIVATE ROUTER EXECUTION METHODS =====
    
    async def _execute_character_router(self, output: CharacterLLMRouterOutput) -> CharacterQueryResult:
        """Execute character query router with LLM-generated inputs."""
        if not output.user_intention:
            return CharacterQueryResult(character_data={})
        
        try:
            # Pass parameters directly from LLM router output (character is pre-loaded)
            result = self.character_router.query_character(
                user_intention=output.user_intention,
                entities=output.entities
            )
            return result
        except Exception as e:
            return CharacterQueryResult(character_data={}, warnings=[f"Character router error: {str(e)}"])
    
    async def _execute_rulebook_router(self, output: RulebookLLMRouterOutput, user_query: str) -> tuple[List[SearchResult], Optional[QueryPerformanceMetrics]]:
        """Execute rulebook query router with LLM-generated inputs."""
        if not output.user_intention or not self.rulebook_router:
            return [], None
        
        try:
            # Convert string intention to enum
            intention_enum = RulebookQueryIntent(output.user_intention.lower())
            
            # Pass all parameters directly from LLM router output
            results, performance = self.rulebook_router.query(
                intention=intention_enum,
                user_query=user_query,  # Get from engine class
                entities=[entity["name"] for entity in output.entities],
                context_hints=output.context_hints,
                k=output.k
            )
            return results, performance
        except Exception as e:
            return [], None
    
    async def _execute_session_notes_router(self, output: SessionNotesLLMRouterOutput, user_query: str) -> QueryEngineResult:
        """Execute session notes query router with LLM-generated inputs."""
        if not output.user_intention or not self.session_notes_router:
            return QueryEngineResult(contexts=[], total_sessions_searched=0, entities_resolved=[])
        
        try:
            # Pass all parameters directly from LLM router output
            result = self.session_notes_router.query(
                character_name=output.character_name,
                original_query=user_query,  # Get from engine class
                intention=output.user_intention,
                entities=output.entities,
                context_hints=output.context_hints,
                top_k=output.top_k
            )
            return result
        except Exception as e:
            return QueryEngineResult(contexts=[], total_sessions_searched=0, entities_resolved=[])
