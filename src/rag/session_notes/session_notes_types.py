"""
Session Notes Types and Data Structures

Core data types for D&D 5e session notes storage and retrieval.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any, Union
import re


class EntityType(Enum):
    """Types of entities that can be extracted from queries"""
    CHARACTER = "character"
    NPC = "npc"
    LOCATION = "location"
    SPELL = "spell"
    ITEM = "item"
    ORGANIZATION = "organization"
    EVENT = "event"
    THEME = "theme"


@dataclass
class QueryEntity:
    """An entity extracted from a query with its type"""
    name: str
    entity_type: EntityType
    aliases: List[str] = field(default_factory=list)


class SessionNotesQueryIntent(Enum):
    """Core session notes query intentions for Phase 1"""
    # Entity Tracking
    FIND_NPC_INTERACTIONS = "find_npc_interactions"
    TRACK_ITEM_HISTORY = "track_item_history" 
    LOCATION_VISITS = "location_visits"
    SPELL_USAGE_HISTORY = "spell_usage_history"
    
    # Character Development
    CHARACTER_ARC_TRACKING = "character_arc_tracking"
    RELATIONSHIP_EVOLUTION = "relationship_evolution"
    DECISION_CONSEQUENCES = "decision_consequences"
    
    # Session Context
    RECENT_EVENTS = "recent_events"
    SESSION_SUMMARIES = "session_summaries"


@dataclass
class Quote:
    """A memorable quote from a session"""
    text: str
    speaker: str
    context: Optional[str] = None


@dataclass
class NPCInteraction:
    """Details about an NPC interaction"""
    npc_name: str
    interaction_type: str  # "combat", "dialogue", "first_meeting", etc.
    description: str
    character_involved: Optional[str] = None


@dataclass
class LocationVisit:
    """Details about visiting a location"""
    location_name: str
    description: str
    events_occurred: List[str] = field(default_factory=list)


@dataclass
class Encounter:
    """Combat or challenge encounter"""
    encounter_type: str  # "combat", "puzzle", "social", etc.
    description: str
    enemies: List[str] = field(default_factory=list)
    outcome: Optional[str] = None


@dataclass
class SpellUsage:
    """Record of spell usage"""
    spell_name: str
    caster: str
    target: Optional[str] = None
    outcome: Optional[str] = None
    context: Optional[str] = None


@dataclass
class ItemTransaction:
    """Item gained or lost"""
    item_name: str
    transaction_type: str  # "gained", "lost", "used", "found"
    character: Optional[str] = None
    context: Optional[str] = None


@dataclass
class CharacterDecision:
    """A significant character decision"""
    character_name: str
    decision_description: str
    context: str
    consequences: Optional[str] = None


@dataclass
class RelationshipChange:
    """Change in relationship between characters/NPCs"""
    character_a: str
    character_b: str
    change_description: str
    relationship_type: str  # "ally", "enemy", "neutral", "romantic", etc.
    previous_status: Optional[str] = None


@dataclass
class CharacterGrowthMoment:
    """A moment of character development or growth"""
    character_name: str
    growth_description: str
    growth_type: str  # "emotional", "skill", "belief", "relationship", etc.


@dataclass
class SessionNote:
    """Complete session note structure"""
    session_number: int
    date: str  # YYYY-MM-DD format
    title: str
    summary: str
    
    # Core narrative sections
    key_events: List[str] = field(default_factory=list)
    npcs: Dict[str, NPCInteraction] = field(default_factory=dict)
    locations: List[LocationVisit] = field(default_factory=list)
    
    # Combat & mechanics
    encounters: List[Encounter] = field(default_factory=list)
    spells_used: List[SpellUsage] = field(default_factory=list)
    items_gained_lost: List[ItemTransaction] = field(default_factory=list)
    
    # Character development
    character_decisions: Dict[str, List[CharacterDecision]] = field(default_factory=dict)
    relationship_changes: List[RelationshipChange] = field(default_factory=list)
    character_growth: List[CharacterGrowthMoment] = field(default_factory=list)
    
    # Session metadata
    cliffhanger: Optional[str] = None
    fun_moments: List[str] = field(default_factory=list)
    quotes: List[Quote] = field(default_factory=list)
    
    # Computed fields
    summary_embedding: Optional[List[float]] = None
    event_embeddings: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class SessionSearchResult:
    """Base search result for session queries"""
    session_number: int
    session_title: str
    session_date: str
    relevance_score: float
    
    # Matched content sections
    matched_events: List[str] = field(default_factory=list)
    matched_npcs: List[NPCInteraction] = field(default_factory=list)
    matched_decisions: List[CharacterDecision] = field(default_factory=list)
    matched_quotes: List[Quote] = field(default_factory=list)
    
    # Context information
    session_summary: str = ""
    related_sessions: List[int] = field(default_factory=list)
    
    # Semantic matches
    highlighted_passages: List[str] = field(default_factory=list)
    
    def get_full_context(self) -> str:
        """Return formatted context for this session result"""
        context_parts = [
            f"Session {self.session_number}: {self.session_title} ({self.session_date})",
            f"Summary: {self.session_summary}"
        ]
        
        if self.matched_events:
            context_parts.append(f"Key Events: {'; '.join(self.matched_events)}")
        
        if self.matched_npcs:
            npc_descriptions = [f"{npc.npc_name}: {npc.description}" for npc in self.matched_npcs]
            context_parts.append(f"NPCs: {'; '.join(npc_descriptions)}")
        
        if self.matched_quotes:
            quote_texts = [f'"{quote.text}" - {quote.speaker}' for quote in self.matched_quotes]
            context_parts.append(f"Quotes: {'; '.join(quote_texts)}")
        
        return "\n\n".join(context_parts)


@dataclass
class CharacterArcResult(SessionSearchResult):
    """Specialized result for character development queries"""
    character_name: str = ""
    character_growth_moments: List[CharacterGrowthMoment] = field(default_factory=list)
    relationship_changes: List[RelationshipChange] = field(default_factory=list)
    decisions_and_consequences: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class NPCInteractionResult(SessionSearchResult):
    """Specialized result for NPC interaction queries"""
    npc_name: str = ""
    interaction_type: str = ""
    relationship_status: str = ""
    previous_interactions: List['SessionSearchResult'] = field(default_factory=list)


@dataclass
class SessionNotesQueryRequest:
    """Request object for session notes queries"""
    user_query: str
    intention: SessionNotesQueryIntent
    entities: List[QueryEntity]
    k: int = 5
    date_range: Optional[Tuple[str, str]] = None
    character_filter: Optional[str] = None


@dataclass
class SessionNotesQueryResponse:
    """Response object for session notes queries"""
    results: List[SessionSearchResult]
    total_results_found: int
    query_time_ms: float
    intention_used: SessionNotesQueryIntent
    entities_matched: List[str]