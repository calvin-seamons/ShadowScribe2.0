from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import re


class CharacterStatus(Enum):
    """Status conditions for characters"""
    ALIVE = "alive"
    DEAD = "dead"
    UNCONSCIOUS = "unconscious"
    TRAPPED_SOUL = "trapped_soul"
    MISSING = "missing"
    TRANSFORMED = "transformed"


class RelationshipType(Enum):
    """Types of character relationships"""
    ALLY = "ally"
    ENEMY = "enemy"
    NEUTRAL = "neutral"
    ROMANTIC = "romantic"
    MENTOR = "mentor"
    RIVAL = "rival"
    UNKNOWN = "unknown"


@dataclass
class NPC:
    """Non-player character information"""
    name: str
    role: str
    description: str
    first_appearance: int  # Session number
    last_appearance: Optional[int] = None
    status: CharacterStatus = CharacterStatus.ALIVE
    affiliations: List[str] = field(default_factory=list)
    notable_actions: List[str] = field(default_factory=list)


@dataclass
class Location:
    """Location information"""
    name: str
    description: str
    region: Optional[str] = None
    first_visited: Optional[int] = None
    last_visited: Optional[int] = None
    notable_events: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # Connected locations


@dataclass
class CharacterState:
    """Tracks a character's state at a point in time"""
    name: str
    hp_current: Optional[int] = None
    hp_max: Optional[int] = None
    status: CharacterStatus = CharacterStatus.ALIVE
    conditions: List[str] = field(default_factory=list)
    inventory_changes: List[str] = field(default_factory=list)
    abilities_used: List[str] = field(default_factory=list)
    emotional_state: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Relationship:
    """Tracks relationships between characters"""
    character1: str
    character2: str
    relationship_type: RelationshipType
    description: str
    session_established: int
    session_changed: Optional[int] = None
    trust_level: int = 5  # 1-10 scale


@dataclass
class PlotThread:
    """Tracks ongoing plot threads"""
    title: str
    description: str
    introduced_session: int
    resolved_session: Optional[int] = None
    related_npcs: List[str] = field(default_factory=list)
    related_locations: List[str] = field(default_factory=list)
    status: str = "active"  # active, resolved, abandoned, paused

@dataclass
class Session:
    """Complete session information"""
    number: int
    title: str
    date: datetime
    summary: str
    
    # Core content
    key_events: List[str] = field(default_factory=list)
    npcs_encountered: List[str] = field(default_factory=list)
    locations_visited: List[str] = field(default_factory=list)
    combat_encounters: List[Dict[str, Any]] = field(default_factory=list)
    
    # Character tracking
    character_states: Dict[str, CharacterState] = field(default_factory=dict)
    party_dynamics: List[str] = field(default_factory=list)
    
    # Game elements
    items_gained: List[Dict[str, str]] = field(default_factory=list)
    spells_used: List[Dict[str, str]] = field(default_factory=list)
    
    # Story elements
    lore_revealed: List[str] = field(default_factory=list)
    quotes: List[Dict[str, str]] = field(default_factory=list)
    cliffhangers: List[str] = field(default_factory=list)
    
    # Metadata
    dm_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary for storage"""
        return {
            'number': self.number,
            'title': self.title,
            'date': self.date.isoformat(),
            'summary': self.summary,
            'key_events': self.key_events,
            'npcs_encountered': self.npcs_encountered,
            'locations_visited': self.locations_visited,
            'combat_encounters': self.combat_encounters,
            'character_states': {
                name: {
                    'name': state.name,
                    'hp_current': state.hp_current,
                    'hp_max': state.hp_max,
                    'status': state.status.value,
                    'conditions': state.conditions,
                    'inventory_changes': state.inventory_changes,
                    'abilities_used': state.abilities_used,
                    'emotional_state': state.emotional_state,
                    'location': state.location
                } for name, state in self.character_states.items()
            },
            'party_dynamics': self.party_dynamics,
            'items_gained': self.items_gained,
            'spells_used': self.spells_used,
            'lore_revealed': self.lore_revealed,
            'quotes': self.quotes,
            'cliffhangers': self.cliffhangers,
            'dm_notes': self.dm_notes
        }