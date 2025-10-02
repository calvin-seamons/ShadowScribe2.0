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
    
    def get_tool_and_intention_selector_prompt(self, user_query: str, character_name: str) -> str:
        """
        Build prompt for Tool & Intention Selector LLM call (NEW ARCHITECTURE).
        
        This is the first of 2 parallel LLM calls that replace the old 3 sequential router calls.
        Returns which RAG tools are needed and what intention to use for each.
        
        Args:
            user_query: The user's question about their character
            character_name: Name of the character being queried
            
        Returns:
            Prompt string for the tool selector LLM
        """
        # Get intention definitions from each helper
        character_intents = CharacterPromptHelper.get_intent_definitions()
        session_intents = SessionNotesPromptHelper.get_intent_definitions()
        rulebook_intents = RulebookPromptHelper.get_intent_definitions()
        
        # Format intentions for prompt
        character_intentions_text = "\n".join([f"- {intent}: {definition}" for intent, definition in character_intents.items()])
        session_intentions_text = "\n".join([f"- {intent}: {definition}" for intent, definition in session_intents.items()])
        rulebook_intentions_text = "\n".join([f"- {intent}: {definition}" for intent, definition in rulebook_intents.items()])
        
        return f'''You are an expert D&D assistant analyzing what information sources are needed to answer a query.

Query: "{user_query}"
Character: "{character_name}"

TASK: Determine which RAG tools are needed and what intention to use for each tool.

AVAILABLE TOOLS:
1. character_data - Character stats, inventory, spells, abilities, features
2. session_notes - Campaign history, past events, NPCs, decisions
3. rulebook - D&D rules, mechanics, spell descriptions, combat rules

TOOL SELECTION GUIDELINES:
- Select ONLY the tools actually needed to answer the query
- Most queries need 1-2 tools, rarely 3
- Examples:
  * "What's my AC?" → character_data only
  * "Tell me about Elara" → session_notes only (if NPC)
  * "How does grappling work?" → rulebook only
  * "What persuasion abilities do I have?" → character_data only
  * "Remind me about Elara and my persuasion abilities" → session_notes + character_data

CHARACTER_DATA INTENTIONS (choose ONE per tool):
{character_intentions_text}

SESSION_NOTES INTENTIONS (choose ONE per tool):
{session_intentions_text}

RULEBOOK INTENTIONS (choose ONE per tool):
{rulebook_intentions_text}

EXAMPLES:

Query: "What combat abilities do I have tied to Eldaryth of Regret?"
Response: {{
  "tools_needed": [
    {{"tool": "character_data", "intention": "combat_info", "confidence": 0.95}}
  ]
}}

Query: "Remind me who Elara is and what persuasion abilities I have"
Response: {{
  "tools_needed": [
    {{"tool": "session_notes", "intention": "npc_history", "confidence": 0.95}},
    {{"tool": "character_data", "intention": "abilities_info", "confidence": 0.95}}
  ]
}}

Query: "How does grappling work and what's my athletics bonus?"
Response: {{
  "tools_needed": [
    {{"tool": "rulebook", "intention": "rule_mechanics", "confidence": 0.95}},
    {{"tool": "character_data", "intention": "abilities_info", "confidence": 0.90}}
  ]
}}

Query: "What spells can I cast?"
Response: {{
  "tools_needed": [
    {{"tool": "character_data", "intention": "magic_info", "confidence": 1.0}}
  ]
}}

Query: "Tell me about my weapon"
Response: {{
  "tools_needed": [
    {{"tool": "character_data", "intention": "inventory_info", "confidence": 0.95}}
  ]
}}

Return ONLY valid JSON:
{{
  "tools_needed": [
    {{
      "tool": "tool_name",
      "intention": "intention_name",
      "confidence": 0.0-1.0
    }}
  ]
}}

IMPORTANT: Return valid JSON only. No explanations.'''
    
    def get_character_router_prompt(self, user_query: str, character_name: str) -> str:
        """
        Build specialized prompt for Character Router LLM call.
        Uses CharacterPromptHelper to get current intent definitions and search contexts.
        """
        intent_definitions = CharacterPromptHelper.get_intent_definitions()
        search_contexts = CharacterPromptHelper.get_all_search_contexts()
        
        # Format intentions for prompt
        intention_lines = [f"- {intent}: {definition}" for intent, definition in intent_definitions.items()]
        intentions_text = "\n".join(intention_lines)
        
        # Format search contexts for prompt
        search_contexts_text = "\n".join([
            "- character_data: Search all character sections (inventory, spells, features, abilities, etc.)",
            "- session_notes: Search campaign history and past events",
            "- rulebook: Search D&D rules and mechanics",
            "- all: Search everywhere (use when uncertain)"
        ])
        
        return f'''You are an expert D&D character assistant. Analyze this query for CHARACTER DATA needs.

Query: "{user_query}"
Character: "{character_name}"

TASK: Determine if this query needs CHARACTER DATA (stats, inventory, spells, abilities) and generate inputs.

CRITICAL MULTI-INTENTION RULES:
- ONLY return multiple intentions for clear two-part questions that need different data types
- Single concepts should use ONE intention only
- Maximum 2 intentions allowed - NEVER return more than 2
- Examples of valid multi-intention: "show my spells and inventory", "what are my combat stats and abilities"
- Examples of single intention: "what spells do I have", "show my combat info", "tell me about my character"

IMPORTANT RULES:
- If "is_needed" is true, you MUST provide valid intention(s) from the list below
- If "is_needed" is false, set "user_intentions" to empty array []
- Never return "is_needed": true with empty "user_intentions"

CHARACTER INTENTIONS (choose the most relevant):
{intentions_text}

ENTITY EXTRACTION:
When you identify specific items, spells, features, or other named entities in the query:
- Extract the entity name exactly as mentioned
- Specify WHERE to search using search_contexts (usually ["character_data"] for character queries)
- Include confidence score (0.0-1.0) based on how clearly the entity is referenced

SEARCH CONTEXTS (where to look for entities):
{search_contexts_text}

Return JSON:
{{
  "is_needed": boolean,
  "confidence": float,
  "user_intentions": ["intention_name"] or ["intention_1", "intention_2"] or [],
  "entities": [
    {{
      "name": "entity name from query",
      "search_contexts": ["character_data"],
      "confidence": 0.95
    }}
  ]
}}

ENTITY EXAMPLES:
- Query: "What actions are tied to Eldaryth of Regret?"
  Entity: {{"name": "Eldaryth of Regret", "search_contexts": ["character_data"], "confidence": 1.0}}

- Query: "Tell me about my Hexblade's Curse ability"
  Entity: {{"name": "Hexblade's Curse", "search_contexts": ["character_data"], "confidence": 1.0}}

- Query: "How many spell slots do I have?"
  Entities: [] (no specific entity, just general magic info)'''
    
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
