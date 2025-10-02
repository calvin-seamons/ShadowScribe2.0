"""
Central Engine & Query Processing Pipeline

Main orchestrator that makes LLM calls and coordinates the entire query processing pipeline.
Uses 2 parallel LLM calls (tool selector + entity extractor) to determine query routing.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

# Import LLM client abstraction
from .llm.llm_client import LLMClient, LLMClientFactory
from .config import get_config
from .llm.json_repair import JSONRepair

# Import query router types
from .rag.character.character_query_router import CharacterQueryRouter, CharacterQueryResult
from .rag.character.character_query_types import UserIntention as CharacterIntention
from .rag.rulebook.rulebook_query_router import RulebookQueryRouter
from .rag.rulebook.rulebook_types import RulebookQueryIntent, SearchResult, QueryPerformanceMetrics
from .rag.session_notes.session_notes_query_router import SessionNotesQueryRouter
from .rag.session_notes.campaign_session_notes_storage import CampaignSessionNotesStorage
from .rag.session_notes.session_types import QueryEngineResult

# Import EntitySearchEngine for new architecture
from .utils.entity_search_engine import EntitySearchEngine


# ===== ROUTER OUTPUT DATACLASSES =====

@dataclass
class ToolSelectorOutput:
    """Output from Tool & Intention Selector LLM call."""
    tools_needed: List[Dict[str, Any]] = field(default_factory=list)
    # Each tool dict: {"tool": "character_data", "intention": "combat_info", "confidence": 0.95}


@dataclass
class EntityExtractorOutput:
    """Output from Entity Extractor LLM call."""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    # Each entity dict: {"name": "Eldaryth of Regret", "confidence": 1.0}


# ===== CENTRAL ENGINE =====

class CentralEngine:
    """Main orchestrator - makes all LLM calls and coordinates the pipeline."""
    
    def __init__(self, llm_clients: Dict[str, LLMClient], prompt_manager, 
                 character=None, rulebook_storage=None, campaign_session_notes=None,
                 entity_search_engine=None):
        """Initialize with LLM clients and prompt manager."""
        self.llm_clients = llm_clients
        self.prompt_manager = prompt_manager
        self.config = get_config()
        
        # Store data sources for entity resolution
        self.character = character
        self.rulebook_storage = rulebook_storage
        self.campaign_session_notes = campaign_session_notes
        
        # Initialize EntitySearchEngine
        self.entity_search_engine = entity_search_engine or EntitySearchEngine()
        
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
        1. Make 2 parallel LLM calls: tool selector + entity extractor
        2. Resolve entities using EntitySearchEngine with selected tools
        3. Distribute entities to appropriate RAG tools
        4. Execute needed query routers in parallel
        5. Generate final response
        """
        print(f"🔧 DEBUG: Processing query: '{user_query}'")
        
        # Step 1: Make 2 parallel LLM calls
        print("🔧 DEBUG: Step 1 - Making parallel LLM calls (tool selector + entity extractor)")
        tool_selector_output, entity_extractor_output = await asyncio.gather(
            self._call_tool_selector(user_query, character_name),
            self._call_entity_extractor(user_query)
        )
        
        print(f"🔧 DEBUG: Tool selector returned {len(tool_selector_output.tools_needed)} tools")
        print(f"🔧 DEBUG: Entity extractor returned {len(entity_extractor_output.entities)} entities")
        
        # Step 2: Derive selected tools from tool selector output
        selected_tools = [t["tool"] for t in tool_selector_output.tools_needed]
        print(f"🔧 DEBUG: Step 2 - Selected tools: {selected_tools}")
        
        # Step 3: Resolve entities ONLY in selected tools
        print(f"🔧 DEBUG: Step 3 - Resolving entities in selected tools...")
        entity_results = {}
        if entity_extractor_output.entities:
            entity_results = self.entity_search_engine.resolve_entities(
                entities=entity_extractor_output.entities,
                selected_tools=selected_tools,
                character=self.character,
                session_notes_storage=self.campaign_session_notes,
                rulebook_storage=self.rulebook_storage
            )
            print(f"🔧 DEBUG: Entity resolution found {len(entity_results)} entities")
        else:
            print("🔧 DEBUG: No entities to resolve")
        
        # Step 4: Distribute entities to RAG tools based on where they were found
        print(f"🔧 DEBUG: Step 4 - Distributing entities to RAG tools...")
        entity_distribution = self._distribute_entities_to_rag_queries(
            entity_results, 
            tool_selector_output.tools_needed
        )
        print(f"🔧 DEBUG: Entity distribution: {entity_distribution}")
        
        # Step 5: Execute RAG queries for selected tools
        print(f"🔧 DEBUG: Step 5 - Executing RAG queries...")
        raw_results = await self._execute_rag_queries(
            tool_selector_output.tools_needed,
            entity_distribution,
            entity_results,
            user_query
        )
        
        # Step 6: Generate final response
        print(f"🔧 DEBUG: Step 6 - Generating final response...")
        final_response = await self.generate_final_response(raw_results, user_query)
        
        return final_response
    
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
    
    
    # ===== HELPER METHODS =====
    
    async def _call_tool_selector(self, user_query: str, character_name: str) -> ToolSelectorOutput:
        """
        Make LLM call for Tool & Intention Selector.
        Determines which RAG tools are needed and what intention to use for each.
        """
        try:
            prompt = self.prompt_manager.get_tool_and_intention_selector_prompt(user_query, character_name)
            
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider) or self.llm_clients.get("openai") or self.llm_clients.get("anthropic")
            
            if not client:
                raise RuntimeError("No suitable LLM client available for tool selector")
            
            model = self.config.openai_router_model if provider == "openai" else self.config.anthropic_router_model if provider == "anthropic" else None
            llm_params = self.config.get_router_llm_params(model)
            
            response = await client.generate_json_response(prompt, model=model, **llm_params)
            
            repair_result = JSONRepair.repair_tool_selector_response(response)
            
            if repair_result.was_repaired:
                print(f"🔧 JSON REPAIR: Tool selector response was repaired")
                for detail in repair_result.repair_details:
                    print(f"   • {detail}")
            
            return ToolSelectorOutput(tools_needed=repair_result.data.get("tools_needed", []))
            
        except Exception as e:
            raise RuntimeError(f"Tool selector LLM call failed: {str(e)}") from e
    
    async def _call_entity_extractor(self, user_query: str) -> EntityExtractorOutput:
        """
        Make LLM call for Entity Extractor.
        Extracts entity names from the user query without guessing search contexts.
        """
        try:
            prompt = self.prompt_manager.get_entity_extraction_prompt(user_query)
            
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider) or self.llm_clients.get("openai") or self.llm_clients.get("anthropic")
            
            if not client:
                raise RuntimeError("No suitable LLM client available for entity extractor")
            
            model = self.config.openai_router_model if provider == "openai" else self.config.anthropic_router_model if provider == "anthropic" else None
            llm_params = self.config.get_router_llm_params(model)
            
            response = await client.generate_json_response(prompt, model=model, **llm_params)
            
            repair_result = JSONRepair.repair_entity_extractor_response(response)
            
            if repair_result.was_repaired:
                print(f"🔧 JSON REPAIR: Entity extractor response was repaired")
                for detail in repair_result.repair_details:
                    print(f"   • {detail}")
            
            return EntityExtractorOutput(entities=repair_result.data.get("entities", []))
            
        except Exception as e:
            raise RuntimeError(f"Entity extractor LLM call failed: {str(e)}") from e
    
    def _section_to_tool(self, section_name: str) -> str:
        """
        Map a section name to its parent tool.
        
        Examples:
            "inventory" -> "character_data"
            "session_notes.npc" -> "session_notes"
            "rulebook.combat.grappling" -> "rulebook"
        """
        if section_name.startswith("rulebook.") or section_name == "rulebook":
            return "rulebook"
        elif section_name.startswith("session_notes.") or section_name == "session_notes":
            return "session_notes"
        else:
            return "character_data"
    
    def _distribute_entities_to_rag_queries(
        self,
        entity_results: Dict[str, List[Any]],
        tools_needed: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Map entities to tools based on where they were found.
        Multi-location entities are passed to all relevant tools for richer context.
        """
        tool_entities = {}
        selected_tools = {t["tool"] for t in tools_needed}
        
        for entity_name, results in entity_results.items():
            for result in results:
                tool = self._section_to_tool(result.section)
                
                if tool in selected_tools:
                    if tool not in tool_entities:
                        tool_entities[tool] = []
                    
                    if entity_name not in tool_entities[tool]:
                        tool_entities[tool].append(entity_name)
        
        return tool_entities
    
    async def _execute_rag_queries(
        self,
        tools_needed: List[Dict[str, Any]],
        entity_distribution: Dict[str, List[str]],
        entity_results: Dict[str, List[Any]],
        user_query: str
    ) -> Dict[str, Any]:
        """
        Execute RAG queries for selected tools with distributed entities.
        Includes auto-include sections derived from entity resolution results.
        """
        results = {}
        
        for tool_info in tools_needed:
            tool = tool_info["tool"]
            intention = tool_info["intention"]
            entities = entity_distribution.get(tool, [])
            
            # Extract auto-include sections from entity resolution
            auto_include_sections = self._extract_auto_include_sections(
                entities, entity_results, tool
            )
            
            print(f"🔧 DEBUG: Executing {tool} with intention='{intention}', entities={entities}")
            if auto_include_sections:
                print(f"🔧 DEBUG: Auto-include sections: {auto_include_sections}")
            
            if tool == "character_data" and self.character_router:
                results["character"] = self.character_router.query_character(
                    user_intentions=[intention],
                    entities=[{"name": e, "confidence": 1.0} for e in entities],
                    auto_include_sections=auto_include_sections
                )
                
            elif tool == "session_notes" and self.session_notes_router:
                results["session_notes"] = self.session_notes_router.query(
                    character_name=self.character.character_base.name if self.character else "",
                    original_query=user_query,
                    intention=intention,
                    entities=[{"name": e} for e in entities],
                    context_hints=[],
                    top_k=5
                )
                
            elif tool == "rulebook" and self.rulebook_router:
                try:
                    intention_enum = RulebookQueryIntent(intention.lower())
                    results["rulebook"], _ = self.rulebook_router.query(
                        intention=intention_enum,
                        user_query=user_query,
                        entities=entities,
                        context_hints=[],
                        k=5
                    )
                except ValueError:
                    print(f"🔧 WARNING: Invalid rulebook intention '{intention}', skipping")
        
        return results
    
    def _extract_auto_include_sections(
        self,
        entity_names: List[str],
        entity_results: Dict[str, List[Any]],
        tool: str
    ) -> List[str]:
        """
        Extract section names from entity resolution results for auto-inclusion.
        
        Args:
            entity_names: List of entity names for this tool
            entity_results: Full entity resolution results
            tool: Tool name to filter by
            
        Returns:
            List of unique section names to auto-include in the query
            
        Example:
            If "Eldaryth of Regret" found in ["inventory", "backstory"],
            returns ["inventory", "backstory"] for character_data tool.
        """
        sections = set()
        
        for entity_name in entity_names:
            if entity_name in entity_results:
                for result in entity_results[entity_name]:
                    # Only include sections that belong to this tool
                    if self._section_to_tool(result.section) == tool:
                        sections.add(result.section)
        
        return list(sections)

