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
        
        # Conversation history tracking
        self.conversation_history: List[Dict[str, str]] = []
    
    @classmethod
    def create_from_config(cls, prompt_manager, character=None, 
                          rulebook_storage=None, campaign_session_notes=None):
        """Create CentralEngine instance using default configuration."""
        llm_clients = LLMClientFactory.create_default_clients()
        return cls(llm_clients, prompt_manager, character, rulebook_storage, campaign_session_notes)
    
    def add_conversation_turn(self, role: str, content: str):
        """Add a turn to the conversation history.
        
        Args:
            role: Either "user" or "assistant"
            content: The message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def clear_conversation_history(self):
        """Clear all conversation history."""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
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
            print(f"🔧 DEBUG: Entity results detail: {entity_results}")
            
            # Step 3.5: Fallback search for entities not found in selected tools
            empty_entities = [name for name, results in entity_results.items() if not results]
            if empty_entities:
                print(f"🔧 DEBUG: Step 3.5 - Fallback search for entities not found: {empty_entities}")
                all_tools = ['character_data', 'session_notes', 'rulebook']
                unselected_tools = [t for t in all_tools if t not in selected_tools]
                
                if unselected_tools:
                    fallback_results = self.entity_search_engine.resolve_entities(
                        entities=[e for e in entity_extractor_output.entities if e.get('name') in empty_entities],
                        selected_tools=unselected_tools,
                        character=self.character,
                        session_notes_storage=self.campaign_session_notes,
                        rulebook_storage=self.rulebook_storage
                    )
                    
                    # Merge fallback results
                    for entity_name, results in fallback_results.items():
                        if results:
                            entity_results[entity_name] = results
                            print(f"🔧 DEBUG: Found '{entity_name}' in fallback tools: {[r.found_in_sections for r in results]}")
        else:
            print("🔧 DEBUG: No entities to resolve")
        
        # Step 4: Distribute entities to RAG tools based on where they were found
        print(f"🔧 DEBUG: Step 4 - Distributing entities to RAG tools...")
        entity_distribution = self._distribute_entities_to_rag_queries(
            entity_results, 
            tool_selector_output.tools_needed
        )
        print(f"🔧 DEBUG: Entity distribution: {entity_distribution}")
        print(f"🔧 DEBUG: Tools needed: {tool_selector_output.tools_needed}")
        
        # Step 4.5: Add fallback tools if entities were found there but tool wasn't selected
        tools_with_entities = set(entity_distribution.keys())
        selected_tool_names = {t["tool"] for t in tool_selector_output.tools_needed}
        new_tools_needed = tools_with_entities - selected_tool_names
        
        if new_tools_needed:
            print(f"🔧 DEBUG: Step 4.5 - Adding fallback tools with entities: {new_tools_needed}")
            for tool in new_tools_needed:
                # Add tool with a generic intention based on tool type
                intention_map = {
                    "character_data": "inventory_info",
                    "session_notes": "general_history", 
                    "rulebook": "general_info"
                }
                tool_selector_output.tools_needed.append({
                    "tool": tool,
                    "intention": intention_map.get(tool, "general_info"),
                    "confidence": 0.75
                })
            print(f"🔧 DEBUG: Updated tools needed: {tool_selector_output.tools_needed}")
        
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
    
    async def process_query_stream(self, user_query: str, character_name: str, metadata_callback=None):
        """
        Main processing pipeline with streaming final response.
        Performs all routing and RAG queries, then streams the final response.
        
        Args:
            user_query: User's question
            character_name: Name of the character
            metadata_callback: Optional async callback function for emitting metadata events.
                              Called with (event_type: str, data: dict)
        
        Yields:
            str: Chunks of the final response as they are generated
        """
        print(f"🔧 DEBUG: Processing query (streaming): '{user_query}'")
        
        # Track timing for performance metrics
        start_time = time.time()
        timing = {}
        
        # Add user query to conversation history
        self.add_conversation_turn("user", user_query)
        
        # Step 1: Make 2 parallel LLM calls
        print("🔧 DEBUG: Step 1 - Making parallel LLM calls (tool selector + entity extractor)")
        step1_start = time.time()
        tool_selector_output, entity_extractor_output = await asyncio.gather(
            self._call_tool_selector(user_query, character_name),
            self._call_entity_extractor(user_query)
        )
        timing['routing_and_entities'] = (time.time() - step1_start) * 1000  # Convert to ms
        
        print(f"🔧 DEBUG: Tool selector returned {len(tool_selector_output.tools_needed)} tools")
        print(f"🔧 DEBUG: Entity extractor returned {len(entity_extractor_output.entities)} entities")
        
        # Emit routing metadata
        if metadata_callback:
            await metadata_callback('routing_metadata', {
                'tools_needed': tool_selector_output.tools_needed
            })
        
        # Step 2: Derive selected tools from tool selector output
        selected_tools = [t["tool"] for t in tool_selector_output.tools_needed]
        print(f"🔧 DEBUG: Step 2 - Selected tools: {selected_tools}")
        
        # Step 3: Resolve entities ONLY in selected tools
        print(f"🔧 DEBUG: Step 3 - Resolving entities in selected tools...")
        step3_start = time.time()
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
            print(f"🔧 DEBUG: Entity results detail: {entity_results}")
            
            # Step 3.5: Fallback search for entities not found in selected tools
            empty_entities = [name for name, results in entity_results.items() if not results]
            if empty_entities:
                print(f"🔧 DEBUG: Step 3.5 - Fallback search for entities not found: {empty_entities}")
                all_tools = ['character_data', 'session_notes', 'rulebook']
                unselected_tools = [t for t in all_tools if t not in selected_tools]
                
                if unselected_tools:
                    fallback_results = self.entity_search_engine.resolve_entities(
                        entities=[e for e in entity_extractor_output.entities if e.get('name') in empty_entities],
                        selected_tools=unselected_tools,
                        character=self.character,
                        session_notes_storage=self.campaign_session_notes,
                        rulebook_storage=self.rulebook_storage
                    )
                    
                    # Merge fallback results
                    for entity_name, results in fallback_results.items():
                        if results:
                            entity_results[entity_name] = results
                            print(f"🔧 DEBUG: Found '{entity_name}' in fallback tools: {[r.found_in_sections for r in results]}")
        else:
            print("🔧 DEBUG: No entities to resolve")
        
        # Step 4: Distribute entities to RAG tools based on where they were found
        print(f"🔧 DEBUG: Step 4 - Distributing entities to RAG tools...")
        entity_distribution = self._distribute_entities_to_rag_queries(
            entity_results, 
            tool_selector_output.tools_needed
        )
        print(f"🔧 DEBUG: Entity distribution: {entity_distribution}")
        print(f"🔧 DEBUG: Tools needed: {tool_selector_output.tools_needed}")
        
        # Step 4.5: Add fallback tools if entities were found there but tool wasn't selected
        tools_with_entities = set(entity_distribution.keys())
        selected_tool_names = {t["tool"] for t in tool_selector_output.tools_needed}
        new_tools_needed = tools_with_entities - selected_tool_names
        
        if new_tools_needed:
            print(f"🔧 DEBUG: Step 4.5 - Adding fallback tools with entities: {new_tools_needed}")
            for tool in new_tools_needed:
                # Add tool with a generic intention based on tool type
                intention_map = {
                    "character_data": "inventory_info",
                    "session_notes": "general_history", 
                    "rulebook": "general_info"
                }
                tool_selector_output.tools_needed.append({
                    "tool": tool,
                    "intention": intention_map.get(tool, "general_info"),
                    "confidence": 0.75
                })
            print(f"🔧 DEBUG: Updated tools needed: {tool_selector_output.tools_needed}")
        
        timing['entity_resolution'] = (time.time() - step3_start) * 1000
        
        # Emit entities metadata
        if metadata_callback:
            await metadata_callback('entities_metadata', {
                'entities': [
                    {
                        'name': name,
                        'found_in_sections': [r.found_in_sections for r in results],
                        'match_confidence': [r.match_confidence for r in results],
                        'match_strategy': [r.match_strategy for r in results]
                    }
                    for name, results in entity_results.items()
                ]
            })
        
        # Step 5: Execute RAG queries for selected tools
        print(f"🔧 DEBUG: Step 5 - Executing RAG queries...")
        step5_start = time.time()
        raw_results = await self._execute_rag_queries(
            tool_selector_output.tools_needed,
            entity_distribution,
            entity_results,
            user_query
        )
        timing['rag_queries'] = (time.time() - step5_start) * 1000
        
        # Emit context sources metadata
        if metadata_callback:
            context_sources = self._extract_context_sources(raw_results)
            await metadata_callback('context_sources', context_sources)
        
        # Step 6: Stream final response
        print(f"🔧 DEBUG: Step 6 - Streaming final response...")
        step6_start = time.time()
        
        # Capture the full response as we stream it
        full_response = ""
        async for chunk in self.generate_final_response_stream(raw_results, user_query):
            full_response += chunk
            yield chunk
        
        timing['response_generation'] = (time.time() - step6_start) * 1000
        timing['total'] = (time.time() - start_time) * 1000
        
        # Emit performance metrics
        if metadata_callback:
            await metadata_callback('performance_metrics', {'timing': timing})
        
        # Add assistant response to conversation history
        self.add_conversation_turn("assistant", full_response)
    
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
    
    async def generate_final_response_stream(self, raw_results: Dict[str, Any], user_query: str):
        """
        Get final response prompt from Prompt Manager and stream the LLM response.
        Yields response chunks as they arrive.
        
        Yields:
            str: Chunks of the response as they are generated
        """
        # Get final response prompt from Prompt Manager/Context Assembler
        final_prompt = self.prompt_manager.get_final_response_prompt(raw_results, user_query)
        
        try:
            # Use configured final response provider
            provider = self.config.final_response_llm_provider
            final_client = self.llm_clients.get(provider)
            
            if not final_client:
                # Fallback to available clients
                final_client = (self.llm_clients.get("openai") or 
                               self.llm_clients.get("anthropic"))
                if not final_client:
                    yield "Error: No suitable LLM client available for final response generation"
                    return
            
            # Select appropriate model based on provider
            if provider == "openai":
                model = self.config.openai_final_model
            elif provider == "anthropic":
                model = self.config.anthropic_final_model
            else:
                model = None  # Use client default
            
            # Get LLM parameters from config
            llm_params = self.config.get_final_llm_params(model)
            
            # Stream the response with conversation history
            async for chunk in final_client.generate_response_stream(
                final_prompt,
                model=model,
                conversation_history=self.conversation_history[:-1],  # Exclude current user query (already in prompt)
                **llm_params
            ):
                yield chunk
                
        except Exception as e:
            yield f"\n[Error generating final response: {str(e)}]"
    
    
    # ===== HELPER METHODS =====
    
    async def _call_tool_selector(self, user_query: str, character_name: str) -> ToolSelectorOutput:
        """
        Make LLM call for Tool & Intention Selector.
        Determines which RAG tools are needed and what intention to use for each.
        """
        try:
            history = self.conversation_history[:-1] if len(self.conversation_history) > 0 else []
            
            prompt = self.prompt_manager.get_tool_and_intention_selector_prompt(
                user_query, 
                character_name,
                character=self.character,
                conversation_history=history
            )
            
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider) or self.llm_clients.get("openai") or self.llm_clients.get("anthropic")
            
            if not client:
                raise RuntimeError("No suitable LLM client available for tool selector")
            
            model = self.config.openai_router_model if provider == "openai" else self.config.anthropic_router_model if provider == "anthropic" else None
            llm_params = self.config.get_router_llm_params(model)
            
            response = await client.generate_json_response(prompt, model=model, **llm_params)
            
            # Debug: Print raw response
            print(f"🔍 RAW TOOL SELECTOR RESPONSE:")
            print(f"   Type: {type(response)}")
            if hasattr(response, 'content'):
                print(f"   Content: {response.content}")
            elif isinstance(response, dict):
                print(f"   Dict: {response}")
            else:
                print(f"   Value: {response}")
            
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
            history = self.conversation_history[:-1] if len(self.conversation_history) > 0 else []
            
            prompt = self.prompt_manager.get_entity_extraction_prompt(user_query, conversation_history=history)
            
            provider = self.config.router_llm_provider
            client = self.llm_clients.get(provider) or self.llm_clients.get("openai") or self.llm_clients.get("anthropic")
            
            if not client:
                raise RuntimeError("No suitable LLM client available for entity extractor")
            
            model = self.config.openai_router_model if provider == "openai" else self.config.anthropic_router_model if provider == "anthropic" else None
            llm_params = self.config.get_router_llm_params(model)
            
            response = await client.generate_json_response(prompt, model=model, **llm_params)
            
            # Debug: Print raw response
            print(f"🔍 RAW ENTITY EXTRACTOR RESPONSE:")
            print(f"   Type: {type(response)}")
            if hasattr(response, 'content'):
                print(f"   Content: {response.content}")
            elif isinstance(response, dict):
                print(f"   Dict: {response}")
            else:
                print(f"   Value: {response}")
            
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
                # EntitySearchResult has found_in_sections (list), not section (single)
                for section in result.found_in_sections:
                    tool = self._section_to_tool(section)
                    
                    if tool in selected_tools:
                        if tool not in tool_entities:
                            tool_entities[tool] = []
                        
                        if entity_name not in tool_entities[tool]:
                            tool_entities[tool].append(entity_name)
        
        return tool_entities
    
    def _extract_context_sources(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured context sources from RAG results for metadata display.
        
        Returns:
            dict with character_fields, rulebook_sections, session_notes keys
        """
        context_sources = {
            'character_fields': [],
            'rulebook_sections': [],
            'session_notes': []
        }
        
        # Extract character data fields
        if 'character_data' in raw_results:
            char_result = raw_results['character_data']
            if hasattr(char_result, 'metadata') and 'required_fields' in char_result.metadata:
                context_sources['character_fields'] = char_result.metadata['required_fields']
        
        # Extract rulebook sections
        if 'rulebook' in raw_results:
            rulebook_results = raw_results['rulebook']
            if isinstance(rulebook_results, list):
                for result in rulebook_results:
                    if hasattr(result, 'section'):
                        context_sources['rulebook_sections'].append({
                            'title': result.section.title,
                            'id': result.section.id,
                            'score': getattr(result, 'score', 0)
                        })
        
        # Extract session notes
        if 'session_notes' in raw_results:
            session_result = raw_results['session_notes']
            if hasattr(session_result, 'contexts'):
                for ctx in session_result.contexts:
                    context_sources['session_notes'].append({
                        'session_number': ctx.session_number,
                        'relevance_score': getattr(ctx, 'relevance_score', 0)
                    })
        
        return context_sources
    
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
                    # EntitySearchResult has found_in_sections (list)
                    for section in result.found_in_sections:
                        # Only include sections that belong to this tool
                        if self._section_to_tool(section) == tool:
                            sections.add(section)
        
        return list(sections)

