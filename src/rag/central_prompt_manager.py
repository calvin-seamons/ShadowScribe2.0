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
        Build the final response prompt using assembled context data.
        Creates a professional prompt that makes the AI act as an authoritative knowledge source.
        """
        import json
        
        context_sections = []
        
        # Process character data
        if "character" in raw_results and raw_results["character"]:
            char_result = raw_results["character"]
            
            if hasattr(char_result, 'character_data') and char_result.character_data:
                try:
                    def custom_serializer(obj):
                        """Custom serializer for complex objects"""
                        if hasattr(obj, '__dict__'):
                            return obj.__dict__
                        elif hasattr(obj, '_asdict'):
                            return obj._asdict()
                        else:
                            return str(obj)
                    
                    char_data_json = json.dumps(char_result.character_data, indent=2, default=custom_serializer)
                    context_sections.append(f"CHARACTER INFORMATION:\n{char_data_json}")
                    
                except Exception as e:
                    context_sections.append(f"CHARACTER INFORMATION:\n{str(char_result.character_data)}")
        
        # Process rulebook data
        if "rulebook" in raw_results and raw_results["rulebook"]:
            rulebook_result = raw_results["rulebook"]
            
            if isinstance(rulebook_result, tuple) and len(rulebook_result) >= 2:
                search_results, performance = rulebook_result
                if search_results:
                    rulebook_content = []
                    for i, result in enumerate(search_results, 1):
                        if hasattr(result, 'section'):
                            rulebook_content.append(f"RULE SECTION: {result.section.title}")
                            rulebook_content.append(f"{result.section.content}")
                    
                    if rulebook_content:
                        context_sections.append("RULES REFERENCE:\n" + "\n\n".join(rulebook_content))
        
        # Process session notes data
        if "session_notes" in raw_results and raw_results["session_notes"]:
            session_result = raw_results["session_notes"]
            
            if hasattr(session_result, 'contexts') and session_result.contexts:
                session_content = []
                for i, context in enumerate(session_result.contexts, 1):
                    session_content.append(f"SESSION CONTEXT {i}: {str(context)}")
                
                if session_content:
                    context_sections.append("CAMPAIGN HISTORY:\n" + "\n\n".join(session_content))
        
        # Assemble the full context
        full_context = "\n\n".join(context_sections) if context_sections else "No relevant data found."
        
        # Build the final authoritative prompt
        final_prompt = f"""You are an expert D&D assistant with comprehensive knowledge of characters, rules, and campaign history. Answer the user's question directly and authoritatively using the provided information.

AVAILABLE INFORMATION:
{full_context}

USER QUESTION: {user_query}

RESPONSE GUIDELINES:
- Answer the question directly and confidently
- Present information as established facts, not as "based on data" or "according to records"
- Be comprehensive but focused on what the user asked
- If multiple data sources are relevant, synthesize them naturally
- Use a knowledgeable, helpful tone as if you personally know this information
- Do not mention data sources, JSON structures, or technical implementation details
- If you don't have the specific information requested, say so clearly

Provide your response:"""
        
        return final_prompt
