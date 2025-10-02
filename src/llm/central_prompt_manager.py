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
    
    def get_entity_extraction_prompt(self, user_query: str) -> str:
        """
        Build prompt for Entity Extraction LLM call (NEW ARCHITECTURE).
        
        This is the second of 2 parallel LLM calls that replace the old 3 sequential router calls.
        Extracts entity names from the user query without worrying about search contexts
        (those are derived from tool selection).
        
        Args:
            user_query: The user's question
            
        Returns:
            Prompt string for the entity extractor LLM
        """
        return f'''You are an expert D&D entity extractor. Extract ALL specific named entities from this query.

Query: "{user_query}"

TASK: Extract entity names with confidence scores. DO NOT determine where to search - that's handled separately.

ENTITY TYPES TO EXTRACT:
- Character names (PC or NPC names)
- Item names (weapons, armor, magical items)
- Spell names (specific spells like "Eldritch Blast")
- Feature/ability names (class features, racial traits)
- Location names (cities, dungeons, regions)
- Rule terms (game mechanics like "grappling", "opportunity attack")
- Organization names (guilds, factions)

EXTRACTION GUIDELINES:
1. Extract the EXACT name as mentioned in the query
2. Include partial names if clearly referenced (e.g., "Eldaryth" when full name is "Eldaryth of Regret")
3. Confidence scoring:
   - 1.0: Explicit mention with exact name
   - 0.95: Clear reference with minor variations
   - 0.9: Implied reference or partial name
   - 0.8: Ambiguous reference
4. DO NOT extract:
   - Generic terms ("my spell", "my weapon" without specific name)
   - Question words ("what", "how", "tell me")
   - Character stats without specific names ("AC", "HP" by themselves)

EXAMPLES:

Query: "What combat abilities do I have tied to Eldaryth of Regret?"
Response: {{
  "entities": [
    {{"name": "Eldaryth of Regret", "confidence": 1.0}}
  ]
}}

Query: "Tell me about my Hexblade's Curse ability"
Response: {{
  "entities": [
    {{"name": "Hexblade's Curse", "confidence": 1.0}}
  ]
}}

Query: "How many spell slots do I have?"
Response: {{
  "entities": []
}}
Explanation: No specific entity mentioned, just general magic info request.

Query: "Remind me who Elara is and what persuasion abilities I have"
Response: {{
  "entities": [
    {{"name": "Elara", "confidence": 1.0}}
  ]
}}
Explanation: "Elara" is an NPC name. "persuasion abilities" is generic, not an entity.

Query: "How does grappling work and what's my athletics bonus?"
Response: {{
  "entities": [
    {{"name": "grappling", "confidence": 1.0}},
    {{"name": "athletics", "confidence": 1.0}}
  ]
}}
Explanation: Both are specific game mechanics/skills to look up.

Query: "What spells can I cast with my staff?"
Response: {{
  "entities": []
}}
Explanation: Generic "staff" without specific name. If they said "Staff of Power" → extract it.

Query: "Tell me about Shadowfell and the Raven Queen"
Response: {{
  "entities": [
    {{"name": "Shadowfell", "confidence": 1.0}},
    {{"name": "Raven Queen", "confidence": 1.0}}
  ]
}}
Explanation: Both are specific named entities (location and deity).

Query: "What's my AC?"
Response: {{
  "entities": []
}}
Explanation: Pure stat check, no entities.

Query: "Can I use my Eldritch Blast on the orc?"
Response: {{
  "entities": [
    {{"name": "Eldritch Blast", "confidence": 1.0}}
  ]
}}
Explanation: Specific spell name. "orc" is generic monster type, not a named NPC.

Return ONLY valid JSON:
{{
  "entities": [
    {{"name": "entity_name", "confidence": 0.0-1.0}}
  ]
}}

IMPORTANT: Return valid JSON only. Empty array [] if no entities found. No explanations.'''
    
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
