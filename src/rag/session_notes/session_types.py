from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

# Enums for categorization
class EntityType(Enum):
    """Types of entities that can be referenced in session notes"""
    PC = "player_character"
    NPC = "non_player_character"
    LOCATION = "location"
    ITEM = "item"
    ARTIFACT = "artifact"
    SPELL = "spell"
    ABILITY = "ability"
    ORGANIZATION = "organization"
    DEITY = "deity"
    CREATURE = "creature"
    EVENT = "event"
    QUEST = "quest"
    PUZZLE = "puzzle"

class UserIntention(Enum):
    """Categories of user queries about session notes"""
    CHARACTER_STATUS = "character_status"
    EVENT_SEQUENCE = "event_sequence"
    NPC_INFO = "npc_info"
    LOCATION_DETAILS = "location_details"
    ITEM_TRACKING = "item_tracking"
    COMBAT_RECAP = "combat_recap"
    SPELL_ABILITY_USAGE = "spell_ability_usage"
    CHARACTER_DECISIONS = "character_decisions"
    PARTY_DYNAMICS = "party_dynamics"
    QUEST_TRACKING = "quest_tracking"
    PUZZLE_SOLUTIONS = "puzzle_solutions"
    LOOT_REWARDS = "loot_rewards"
    DEATH_REVIVAL = "death_revival"
    DIVINE_RELIGIOUS = "divine_religious"
    MEMORY_VISION = "memory_vision"
    RULES_MECHANICS = "rules_mechanics"
    HUMOR_MOMENTS = "humor_moments"
    UNRESOLVED_MYSTERIES = "unresolved_mysteries"
    FUTURE_IMPLICATIONS = "future_implications"
    CROSS_SESSION = "cross_session"

# Data structures for entities
@dataclass
class Entity:
    """Base entity that can be referenced in session notes"""
    name: str
    entity_type: EntityType
    aliases: List[str] = field(default_factory=list)
    first_appearance: Optional[int] = None  # Session number
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CharacterStatus:
    """Current status of a character at a point in time"""
    session_number: int
    hp_current: Optional[int] = None
    hp_max: Optional[int] = None
    conditions: List[str] = field(default_factory=list)
    location: Optional[str] = None
    is_alive: bool = True
    soul_status: Optional[str] = None  # For special cases like Duskryn
    physical_description: Optional[str] = None
    equipment_changes: List[str] = field(default_factory=list)

@dataclass
class CombatEncounter:
    """Details of a combat encounter"""
    enemies: List[Entity]
    location: Optional[str] = None
    outcome: Optional[str] = None
    damage_dealt: Dict[str, int] = field(default_factory=dict)  # character -> damage
    damage_taken: Dict[str, int] = field(default_factory=dict)
    spells_used: List[str] = field(default_factory=list)
    killing_blow: Optional[str] = None
    tactics: Optional[str] = None

@dataclass
class SpellAbilityUse:
    """Record of spell or ability usage"""
    name: str
    caster: str
    targets: List[str] = field(default_factory=list)
    effect: Optional[str] = None
    success: Optional[bool] = None
    save_dc: Optional[int] = None
    damage: Optional[int] = None
    duration: Optional[str] = None

@dataclass
class CharacterDecision:
    """Important decision made by a character"""
    character: str
    decision: str
    context: str
    consequences: Optional[str] = None
    party_reaction: Optional[str] = None
    motivation: Optional[str] = None

@dataclass
class Memory:
    """Character memory or vision"""
    character: str
    memory_type: str  # "memory", "vision", "dream", etc.
    content: str
    emotional_context: Optional[str] = None
    significance: Optional[str] = None
    reveals: List[str] = field(default_factory=list)  # What it reveals about character/plot

@dataclass
class QuestObjective:
    """Quest or objective tracking"""
    name: str
    description: str
    status: str  # "active", "completed", "failed", "abandoned"
    giver: Optional[str] = None
    requirements: List[str] = field(default_factory=list)
    rewards: List[str] = field(default_factory=list)
    deadline: Optional[str] = None

@dataclass
class SessionEvent:
    """A significant event that occurred during a session"""
    session_number: int
    description: str
    event_type: str  # "ritual", "combat", "social", "exploration", etc.
    participants: List[Entity] = field(default_factory=list)
    location: Optional[str] = None
    timestamp: Optional[str] = None  # In-game time
    outcomes: List[str] = field(default_factory=list)
    related_events: List[int] = field(default_factory=list)  # Session numbers

# Main session storage structure
@dataclass
class SessionNotes:
    """Complete session notes with all relevant information"""
    session_number: int
    date: datetime
    title: str
    summary: str
    
    # Entities present/mentioned
    player_characters: List[Entity] = field(default_factory=list)
    npcs: List[Entity] = field(default_factory=list)
    locations: List[Entity] = field(default_factory=list)
    items: List[Entity] = field(default_factory=list)
    
    # Events and encounters
    key_events: List[SessionEvent] = field(default_factory=list)
    combat_encounters: List[CombatEncounter] = field(default_factory=list)
    
    # Character information
    character_statuses: Dict[str, CharacterStatus] = field(default_factory=dict)
    character_decisions: List[CharacterDecision] = field(default_factory=list)
    memories_visions: List[Memory] = field(default_factory=list)
    
    # Spells and abilities
    spells_abilities_used: List[SpellAbilityUse] = field(default_factory=list)
    
    # Quest tracking
    quest_updates: List[QuestObjective] = field(default_factory=list)
    
    # Puzzle and mystery information
    puzzles_encountered: Dict[str, str] = field(default_factory=dict)  # puzzle -> solution/status
    mysteries_revealed: List[str] = field(default_factory=list)
    unresolved_questions: List[str] = field(default_factory=list)
    
    # Loot and rewards
    loot_obtained: Dict[str, List[str]] = field(default_factory=dict)  # character -> items
    
    # Death and revival
    deaths: List[Dict[str, Any]] = field(default_factory=list)
    revivals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Divine/religious elements
    divine_interventions: List[str] = field(default_factory=list)
    religious_elements: List[str] = field(default_factory=list)
    
    # Party dynamics
    party_conflicts: List[str] = field(default_factory=list)
    party_bonds: List[str] = field(default_factory=list)
    
    # Memorable moments
    quotes: List[Dict[str, str]] = field(default_factory=list)  # {"speaker": "", "quote": ""}
    funny_moments: List[str] = field(default_factory=list)
    
    # Mechanics and rules
    rules_clarifications: List[str] = field(default_factory=list)
    dice_rolls: List[Dict[str, Any]] = field(default_factory=list)
    
    # Session metadata
    cliffhanger: Optional[str] = None
    next_session_hook: Optional[str] = None
    dm_notes: List[str] = field(default_factory=list)
    
    # Raw text sections for complex narrative
    raw_sections: Dict[str, str] = field(default_factory=dict)  # section_name -> text

# Query input structure
@dataclass
class QueryInput:
    """Input structure for content retrieval"""
    intention: UserIntention
    entities: List[Entity]
    session_range: Optional[tuple[int, int]] = None  # (start, end) session numbers
    keywords: List[str] = field(default_factory=list)
    context: Optional[str] = None  # Additional context from user query

# Content retrieval result
@dataclass
class RetrievedContent:
    """Structure for content retrieved based on query"""
    primary_content: str
    supporting_details: List[str] = field(default_factory=list)
    related_sessions: List[int] = field(default_factory=list)
    entities_mentioned: List[Entity] = field(default_factory=list)
    confidence_score: float = 1.0
    source_sections: List[str] = field(default_factory=list)  # Which parts of notes this came from

# Query engine structures
@dataclass
class SessionNotesContext:
    """Context from a specific session relevant to a query"""
    session_number: int
    session_summary: str
    relevant_sections: Dict[str, Any] = field(default_factory=dict)
    entities_found: List[Entity] = field(default_factory=list)
    relevance_score: float = 0.0

@dataclass
class QueryEngineResult:
    """Result from the query engine"""
    contexts: List[SessionNotesContext] = field(default_factory=list)
    total_sessions_searched: int = 0
    entities_resolved: List[Entity] = field(default_factory=list)
    query_summary: str = ""
    performance_metrics: Optional['SessionNotesQueryPerformanceMetrics'] = None


@dataclass
class SessionNotesQueryPerformanceMetrics:
    """Detailed timing performance information for session notes query operations"""
    total_time_ms: float = 0.0
    entity_resolution_ms: float = 0.0
    session_filtering_ms: float = 0.0
    context_building_ms: float = 0.0
    scoring_sorting_ms: float = 0.0
    result_limiting_ms: float = 0.0
    
    # Entity processing metrics
    entities_input: int = 0
    entities_resolved: int = 0
    fuzzy_matches_performed: int = 0
    
    # Search scope metrics
    total_sessions_available: int = 0
    sessions_searched: int = 0
    contexts_built: int = 0
    results_returned: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for analysis"""
        return {
            'total_time_ms': self.total_time_ms,
            'timing_breakdown': {
                'entity_resolution_ms': self.entity_resolution_ms,
                'session_filtering_ms': self.session_filtering_ms,
                'context_building_ms': self.context_building_ms,
                'scoring_sorting_ms': self.scoring_sorting_ms,
                'result_limiting_ms': self.result_limiting_ms
            },
            'entity_processing': {
                'entities_input': self.entities_input,
                'entities_resolved': self.entities_resolved,
                'fuzzy_matches_performed': self.fuzzy_matches_performed
            },
            'search_scope': {
                'total_sessions_available': self.total_sessions_available,
                'sessions_searched': self.sessions_searched,
                'contexts_built': self.contexts_built,
                'results_returned': self.results_returned
            }
        }


# ===== PROMPT GENERATION HELPERS =====

class SessionNotesPromptHelper:
    """Provides prompt-ready information for session notes intents and entity types."""
    
    @staticmethod
    def get_intent_definitions() -> Dict[str, str]:
        """Returns all session notes intentions with their definitions for prompts."""
        return {
            "character_status": "Current character status and conditions",
            "event_sequence": "What happened when - chronological events",
            "npc_info": "NPC interactions, relationships, and information",
            "location_details": "Information about places visited and explored",
            "item_tracking": "Items found, lost, used, or traded",
            "combat_recap": "Details of past combat encounters",
            "spell_ability_usage": "Spells and abilities used during sessions",
            "character_decisions": "Important character choices and their outcomes",
            "party_dynamics": "Group interactions and relationships",
            "quest_tracking": "Quest progress, objectives, and completion status",
            "puzzle_solutions": "Puzzles encountered and how they were solved",
            "loot_rewards": "Treasure, rewards, and items obtained",
            "death_revival": "Character deaths, revivals, and soul-related events",
            "divine_religious": "Interactions with deities and religious events",
            "memory_vision": "Memories recovered, visions seen, dreams experienced",
            "rules_mechanics": "Rule interpretations and mechanical decisions made",
            "humor_moments": "Funny moments and memorable jokes",
            "unresolved_mysteries": "Ongoing mysteries and unanswered questions",
            "future_implications": "Events that might affect future sessions",
            "cross_session": "Connections and patterns across multiple sessions"
        }
    
    @staticmethod
    def get_entity_type_definitions() -> Dict[str, str]:
        """Returns all session notes entity types with examples for prompts."""
        return {
            "player_character": "Player characters (e.g., 'Duskryn', 'party members')",
            "non_player_character": "NPCs (e.g., 'tavern keeper', 'quest giver', 'villain')",
            "location": "Places (e.g., 'tavern', 'dungeon', 'city', 'forest')",
            "item": "Items and objects (e.g., 'magic sword', 'treasure chest', 'key')",
            "artifact": "Powerful magical items (e.g., 'staff of power', 'ancient relic')",
            "spell": "Spells cast (e.g., 'fireball', 'healing word', 'teleport')",
            "ability": "Special abilities used (e.g., 'rage', 'sneak attack', 'turn undead')",
            "organization": "Groups and factions (e.g., 'thieves guild', 'royal court')",
            "deity": "Gods and divine beings (e.g., 'Tyr', 'Shar', 'patron deity')",
            "creature": "Monsters and creatures (e.g., 'dragon', 'goblin', 'undead')",
            "event": "Significant occurrences (e.g., 'battle', 'discovery', 'betrayal')",
            "quest": "Missions and objectives (e.g., 'rescue mission', 'fetch quest')",
            "puzzle": "Puzzles and challenges (e.g., 'riddle', 'trap', 'maze')"
        }
    
    @staticmethod
    def get_all_intents() -> List[str]:
        """Returns list of all session notes intention names."""
        return [intent.value for intent in UserIntention]
    
    @staticmethod
    def get_all_entity_types() -> List[str]:
        """Returns list of all session notes entity type names."""
        return [entity.value for entity in EntityType]