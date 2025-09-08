"""
Central Prompt Manager

Builds all prompts and coordinates between components. No LLM calls - just prompt generation 
and component coordination.
"""

from typing import Dict, Any, Optional
from src.rag.character.character_query_types import CharacterPromptHelper
from src.rag.rulebook.rulebook_types import RulebookPromptHelper
from src.rag.session_notes.session_types import SessionNotesPromptHelper


class CentralPromptManager:
    """Builds prompts and coordinates components - no LLM calls."""
    
    def __init__(self, context_assembler):
        """Initialize with context assembler."""
        self.context_assembler = context_assembler
    
    def get_character_router_prompt(self, user_query: str, character_name: str) -> str:
        """
        Build specialized prompt for Character Router LLM call.
        Uses CharacterPromptHelper to get current intent definitions and entity types.
        """
        intent_definitions = CharacterPromptHelper.get_intent_definitions()
        entity_type_definitions = CharacterPromptHelper.get_entity_type_definitions()
        
        # Format intentions for prompt
        intention_lines = [f"- {intent}: {definition}" for intent, definition in intent_definitions.items()]
        intentions_text = "\n".join(intention_lines)
        
        # Format entity types for prompt
        entity_lines = [f"- {entity_type}: {definition}" for entity_type, definition in entity_type_definitions.items()]
        entities_text = "\n".join(entity_lines)
        
        return f'''You are an expert D&D character assistant. Analyze this query for CHARACTER DATA needs.

Query: "{user_query}"
Character: "{character_name}"

TASK: Determine if this query needs CHARACTER DATA (stats, inventory, spells, abilities) and generate inputs.

IMPORTANT RULES:
- If "is_needed" is true, you MUST provide a valid "user_intention" from the list below
- If "is_needed" is false, set "user_intention" to null
- Never return "is_needed": true with "user_intention": null

CHARACTER INTENTIONS (choose the most relevant):
{intentions_text}

ENTITY TYPES:
{entities_text}

Return JSON:
{{
  "is_needed": boolean,
  "confidence": float,
  "user_intention": "intention_name" or null,
  "entities": [{{"name": "string", "type": "type", "confidence": float}}]
}}'''
    
    def get_rulebook_router_prompt(self, user_query: str) -> str:
        """
        Build specialized prompt for Rulebook Router LLM call.
        Uses RulebookPromptHelper to get current intent definitions and entity types.
        """
        intent_definitions = RulebookPromptHelper.get_intent_definitions()
        entity_type_definitions = RulebookPromptHelper.get_entity_type_definitions()
        
        # Format intentions for prompt  
        intention_lines = [f"- {intent}: {definition}" for intent, definition in intent_definitions.items()]
        intentions_text = "\n".join(intention_lines)
        
        # Format entity types for prompt
        entity_lines = [f"- {entity_type}: {definition}" for entity_type, definition in entity_type_definitions.items()]
        entities_text = "\n".join(entity_lines)
        
        return f'''You are an expert D&D rules assistant. Analyze this query for RULEBOOK INFO needs.

Query: "{user_query}"

TASK: Determine if this query needs RULEBOOK INFO (rules, mechanics, spells) and generate inputs.

IMPORTANT RULES:
- If "is_needed" is true, you MUST provide a valid "intention" from the list below
- If "is_needed" is false, set "intention" to null
- Never return "is_needed": true with "intention": null

RULEBOOK INTENTIONS (choose the most relevant):
{intentions_text}

ENTITY TYPES:
{entities_text}

Return JSON:
{{
  "is_needed": boolean,
  "confidence": float,
  "intention": "intention_name" or null,
  "entities": [{{"name": "string", "type": "type"}}],
  "context_hints": ["hint1", "hint2", "hint3"]
}}'''
    
    def get_session_notes_router_prompt(self, user_query: str, character_name: str) -> str:
        """
        Build specialized prompt for Session Notes Router LLM call.
        Uses SessionNotesPromptHelper to get current intent definitions and entity types.
        """
        intent_definitions = SessionNotesPromptHelper.get_intent_definitions()
        entity_type_definitions = SessionNotesPromptHelper.get_entity_type_definitions()
        
        # Format intentions for prompt
        intention_lines = [f"- {intent}: {definition}" for intent, definition in intent_definitions.items()]
        intentions_text = "\n".join(intention_lines)
        
        # Format entity types for prompt
        entity_lines = [f"- {entity_type}: {definition}" for entity_type, definition in entity_type_definitions.items()]
        entities_text = "\n".join(entity_lines)
        
        return f'''You are an expert D&D session assistant. Analyze this query for SESSION HISTORY needs.

Query: "{user_query}"
Character: "{character_name}"

TASK: Determine if this query needs SESSION HISTORY (past events, NPCs, decisions) and generate inputs.

IMPORTANT RULES:
- If "is_needed" is true, you MUST provide a valid "intention" from the list below
- If "is_needed" is false, set "intention" to null
- Never return "is_needed": true with "intention": null

SESSION INTENTIONS (choose the most relevant):
{intentions_text}

ENTITY TYPES:
{entities_text}

Return JSON:
{{
  "is_needed": boolean,
  "confidence": float,
  "intention": "intention_name" or null,
  "entities": [{{"name": "string", "type": "type"}}],
  "context_hints": ["hint1", "hint2", "hint3"]
}}'''
    
    def get_final_response_prompt(self, raw_results: Dict[str, Any], user_query: str) -> str:
        """
        Coordinate with Context Assembler to build final response prompt.
        Context Assembler assembles context, this method builds the final LLM prompt.
        
        DEBUG MODE: Bypassing context assembler to show raw data directly.
        """
        # DEBUG: Skip context assembler and show raw data
        import json
        
        print("🔍 DEBUG: Building final response prompt...")
        print(f"🔍 Raw results keys: {list(raw_results.keys())}")
        
        prompt_parts = []
        
        # Add raw character data with debugging
        if "character" in raw_results and raw_results["character"]:
            char_result = raw_results["character"]
            prompt_parts.append("=== CHARACTER DATA (RAW DEBUG) ===")
            
            print(f"🔍 Character result type: {type(char_result)}")
            print(f"🔍 Character result attributes: {dir(char_result)}")
            
            if hasattr(char_result, 'character_data'):
                print(f"🔍 Character data type: {type(char_result.character_data)}")
                print(f"🔍 Character data keys: {list(char_result.character_data.keys()) if isinstance(char_result.character_data, dict) else 'Not a dict'}")
                
                # Show inventory data specifically
                if isinstance(char_result.character_data, dict) and 'inventory' in char_result.character_data:
                    inventory_data = char_result.character_data['inventory']
                    print(f"🔍 INVENTORY DATA TYPE: {type(inventory_data)}")
                    print(f"🔍 INVENTORY KEYS: {list(inventory_data.keys()) if isinstance(inventory_data, dict) else 'Not a dict'}")
                    
                    if isinstance(inventory_data, dict):
                        for key, value in inventory_data.items():
                            print(f"🔍 INVENTORY[{key}]: {type(value)} - FULL DATA: {value}")  # NO TRUNCATION!
                            
                            # Specifically check equipped_items
                            if key == 'equipped_items' and isinstance(value, dict):
                                print(f"🔍 EQUIPPED_ITEMS SLOTS: {list(value.keys())}")
                                for slot, items in value.items():
                                    print(f"🔍 SLOT[{slot}]: {len(items) if isinstance(items, list) else 'Not a list'} items")
                                    if isinstance(items, list):
                                        for i, item in enumerate(items):  # Show ALL items
                                            print(f"🔍   Item {i+1}: {item}")
                
                prompt_parts.append(f"Character Data Type: {type(char_result.character_data)}")
                prompt_parts.append(f"Character Data Keys: {list(char_result.character_data.keys()) if isinstance(char_result.character_data, dict) else 'Not a dict'}")
                
                # Pretty print the character data - use custom serializer to include everything
                try:
                    def custom_serializer(obj):
                        """Custom serializer that includes everything"""
                        if hasattr(obj, '__dict__'):
                            return obj.__dict__
                        elif hasattr(obj, '_asdict'):  # For namedtuples
                            return obj._asdict()
                        else:
                            return str(obj)
                    
                    char_data_json = json.dumps(char_result.character_data, indent=2, default=custom_serializer)
                    prompt_parts.append(f"Character Data JSON:\n{char_data_json}")
                    
                    print(f"🔍 JSON LENGTH: {len(char_data_json)} characters")
                    
                except Exception as e:
                    prompt_parts.append(f"Character Data (str): {str(char_result.character_data)}")
                    prompt_parts.append(f"JSON serialization error: {e}")
                    print(f"🔍 JSON ERROR: {e}")
                
                # Add metadata if available
                if hasattr(char_result, 'metadata') and char_result.metadata:
                    prompt_parts.append(f"Metadata: {json.dumps(char_result.metadata, indent=2, default=str)}")
                
                # Add warnings if any
                if hasattr(char_result, 'warnings') and char_result.warnings:
                    prompt_parts.append(f"Warnings: {char_result.warnings}")
                    
            else:
                prompt_parts.append(f"Character Result: {str(char_result)}")
                print(f"🔍 No character_data attribute found")
        
        # Add raw rulebook data with debugging - FULL DATA NO TRUNCATION
        if "rulebook" in raw_results and raw_results["rulebook"]:
            rulebook_result = raw_results["rulebook"]
            prompt_parts.append("=== RULEBOOK DATA (RAW DEBUG) ===")
            prompt_parts.append(f"Rulebook Result Type: {type(rulebook_result)}")
            
            if isinstance(rulebook_result, tuple) and len(rulebook_result) >= 2:
                search_results, performance = rulebook_result
                prompt_parts.append(f"Search Results Count: {len(search_results) if search_results else 0}")
                if search_results:
                    for i, result in enumerate(search_results, 1):  # ALL RESULTS
                        if hasattr(result, 'section'):
                            prompt_parts.append(f"Result {i}: {result.section.title}")
                            # COMPLETE CONTENT - NO TRUNCATION
                            prompt_parts.append(f"Content: {result.section.content}")
            else:
                prompt_parts.append(f"Rulebook Result: {str(rulebook_result)}")
        
        # Add raw session data with debugging - FULL DATA NO TRUNCATION  
        if "session_notes" in raw_results and raw_results["session_notes"]:
            session_result = raw_results["session_notes"]
            prompt_parts.append("=== SESSION NOTES DATA (RAW DEBUG) ===")
            prompt_parts.append(f"Session Result Type: {type(session_result)}")
            
            if hasattr(session_result, 'contexts'):
                prompt_parts.append(f"Contexts Count: {len(session_result.contexts)}")
                if session_result.contexts:
                    for i, context in enumerate(session_result.contexts, 1):  # ALL CONTEXTS
                        # COMPLETE CONTEXT - NO TRUNCATION
                        prompt_parts.append(f"Context {i}: {str(context)}")
            else:
                prompt_parts.append(f"Session Result: {str(session_result)}")
        
        # Join all debug sections
        debug_content = "\n\n".join(prompt_parts)
        
        # Build final prompt with debug data
        final_prompt = f"""DEBUG MODE: Raw data analysis for query optimization.

{debug_content}

Original Query: {user_query}

ANALYSIS TASK: Based on the RAW DATA above, provide a comprehensive answer to the user's query. 
Pay special attention to the character data structure and ensure you're accessing the correct fields.
Look specifically for inventory data, equipped items, weapons, and any relevant character information.

If you see character inventory data, make sure to examine the equipped_items section for weapons.
Focus on finding the most powerful weapon based on damage values and magical properties."""
        
        print(f"🔍 FINAL PROMPT LENGTH: {len(final_prompt)} characters")
        # NEVER TRUNCATE THE PREVIEW - SHOW EVERYTHING
        print(f"🔍 FULL PROMPT:\n{final_prompt}")
        
        return final_prompt
