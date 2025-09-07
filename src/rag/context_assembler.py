"""
Context Assembler

Takes raw results from multiple query routers and assembles them into coherent,
structured context for LLM consumption. No LLM calls - just data organization.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class AssembledContext:
    """Final assembled context ready for LLM response generation."""
    character_data: Optional[str] = None      # Formatted character info
    rules_content: Optional[str] = None       # Relevant rules/mechanics  
    session_context: Optional[str] = None     # Historical context from sessions
    supporting_content: Optional[str] = None  # Additional context
    synthesis_notes: List[str] = None         # Notes about how content relates
    
    def __post_init__(self):
        if self.synthesis_notes is None:
            self.synthesis_notes = []


class ContextAssembler:
    """Assembles context from multiple query router results."""
    
    def __init__(self):
        """Initialize the context assembler."""
        pass
    
    def assemble_context(self, raw_results: Dict[str, Any], user_query: str) -> AssembledContext:
        """
        Main assembly method. Takes raw router results and creates coherent context.
        
        Args:
            raw_results: Dictionary with keys like 'character', 'rulebook', 'session_notes'
            user_query: Original user query for context
            
        Returns:
            AssembledContext object with formatted context sections
        """
        assembled = AssembledContext()
        
        # Format character data if available
        if "character" in raw_results and raw_results["character"]:
            assembled.character_data = self._format_character_content(raw_results["character"])
        
        # Format rulebook content if available
        if "rulebook" in raw_results and raw_results["rulebook"]:
            assembled.rules_content = self._format_rulebook_content(raw_results["rulebook"])
        
        # Format session notes content if available
        if "session_notes" in raw_results and raw_results["session_notes"]:
            assembled.session_context = self._format_session_content(raw_results["session_notes"])
        
        # Generate synthesis notes about relationships
        assembled.synthesis_notes = self._generate_synthesis_notes(raw_results, user_query)
        
        return assembled
    
    def _format_character_content(self, character_results: Dict[str, Any]) -> str:
        """
        Format character query results into readable context.
        """
        if not character_results:
            return ""
        
        formatted_parts = []
        
        # Add character basic info if available
        if "character_info" in character_results:
            formatted_parts.append(f"Character Information:\n{character_results['character_info']}")
        
        # Add character data sections
        if "character_data" in character_results:
            formatted_parts.append(f"Character Data:\n{character_results['character_data']}")
        
        # Add any additional character context
        if "additional_context" in character_results:
            formatted_parts.append(f"Additional Context:\n{character_results['additional_context']}")
        
        # If we have raw character results without specific keys, format them directly
        if not formatted_parts and character_results:
            formatted_parts.append(f"Character Results:\n{str(character_results)}")
        
        return "\n\n".join(formatted_parts) if formatted_parts else ""
    
    def _format_rulebook_content(self, rulebook_results: Dict[str, Any]) -> str:
        """
        Format rulebook results into coherent rules explanations.
        """
        if not rulebook_results:
            return ""
        
        formatted_parts = []
        
        # Add rules content if available
        if "rules_content" in rulebook_results:
            formatted_parts.append(f"Rules Content:\n{rulebook_results['rules_content']}")
        
        # Add spell details if available
        if "spell_details" in rulebook_results:
            formatted_parts.append(f"Spell Details:\n{rulebook_results['spell_details']}")
        
        # Add equipment info if available
        if "equipment_info" in rulebook_results:
            formatted_parts.append(f"Equipment Information:\n{rulebook_results['equipment_info']}")
        
        # Add additional rulebook context
        if "additional_context" in rulebook_results:
            formatted_parts.append(f"Additional Rules Context:\n{rulebook_results['additional_context']}")
        
        # If we have raw rulebook results without specific keys, format them directly
        if not formatted_parts and rulebook_results:
            formatted_parts.append(f"Rulebook Results:\n{str(rulebook_results)}")
        
        return "\n\n".join(formatted_parts) if formatted_parts else ""
    
    def _format_session_content(self, session_results: Dict[str, Any]) -> str:
        """
        Format session notes results into narrative context.
        """
        if not session_results:
            return ""
        
        formatted_parts = []
        
        # Add session events if available
        if "session_events" in session_results:
            formatted_parts.append(f"Session Events:\n{session_results['session_events']}")
        
        # Add character interactions if available
        if "character_interactions" in session_results:
            formatted_parts.append(f"Character Interactions:\n{session_results['character_interactions']}")
        
        # Add quest progression if available
        if "quest_progression" in session_results:
            formatted_parts.append(f"Quest Progression:\n{session_results['quest_progression']}")
        
        # Add additional session context
        if "additional_context" in session_results:
            formatted_parts.append(f"Additional Session Context:\n{session_results['additional_context']}")
        
        # If we have raw session results without specific keys, format them directly
        if not formatted_parts and session_results:
            formatted_parts.append(f"Session Results:\n{str(session_results)}")
        
        return "\n\n".join(formatted_parts) if formatted_parts else ""
    
    def _generate_synthesis_notes(self, raw_results: Dict[str, Any], user_query: str) -> List[str]:
        """
        Generate notes about relationships between different content domains.
        """
        notes = []
        
        # Check what data types we have
        has_character = "character" in raw_results and raw_results["character"]
        has_rulebook = "rulebook" in raw_results and raw_results["rulebook"]
        has_session = "session_notes" in raw_results and raw_results["session_notes"]
        
        # Generate synthesis notes based on what's available
        if has_character and has_rulebook:
            notes.append("Character abilities and relevant rules are both available for comprehensive analysis")
        
        if has_character and has_session:
            notes.append("Character data can be contextualized with session history")
        
        if has_rulebook and has_session:
            notes.append("Rules mechanics can be related to past session events")
        
        if has_character and has_rulebook and has_session:
            notes.append("Full context available: character data, rules, and session history for complete analysis")
        
        # Add query-specific context note
        if any([has_character, has_rulebook, has_session]):
            notes.append(f"Context assembled for query: '{user_query}'")
        
        return notes
