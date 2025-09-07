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

TASK: Determine if this query needs CHARACTER DATA (stats, inventory, spells, abilities) and generate inputs. If not, ensure that "is_needed" is false.

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

TASK: Determine if this query needs RULEBOOK INFO (rules, mechanics, spells) and generate inputs. If not, ensure that "is_needed" is false.

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

TASK: Determine if this query needs SESSION HISTORY (past events, NPCs, decisions) and generate inputs. If not, ensure that "is_needed" is false.

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
        """
        # Get assembled context from Context Assembler
        assembled_context = self.context_assembler.assemble_context(raw_results, user_query)
        
        # Build final response prompt using assembled context
        prompt_parts = []
        
        # Add character data if available
        if assembled_context.character_data:
            prompt_parts.append(f"CHARACTER DATA:\n{assembled_context.character_data}")
        
        # Add rules content if available
        if assembled_context.rules_content:
            prompt_parts.append(f"RULES:\n{assembled_context.rules_content}")
        
        # Add session context if available
        if assembled_context.session_context:
            prompt_parts.append(f"SESSION HISTORY:\n{assembled_context.session_context}")
        
        # Add supporting content if available
        if assembled_context.supporting_content:
            prompt_parts.append(f"ADDITIONAL CONTEXT:\n{assembled_context.supporting_content}")
        
        # Join all context sections
        context_sections = "\n\n".join(prompt_parts)
        
        # Add synthesis notes if available
        synthesis_section = ""
        if assembled_context.synthesis_notes:
            synthesis_notes = "\n".join([f"- {note}" for note in assembled_context.synthesis_notes])
            synthesis_section = f"\n\nRELATIONSHIPS BETWEEN INFORMATION:\n{synthesis_notes}"
        
        # Build final prompt
        final_prompt = f"""Given this information, provide a comprehensive answer to the user's query:

{context_sections}{synthesis_section}

Original Query: {user_query}

Provide a complete, accurate answer that references specific sources when relevant. Be thorough but concise, and maintain character voice if applicable."""
        
        return final_prompt
