"""
D&D 5e Session Notes Storage System

Core types and storage for D&D 5e session notes organization.
"""

from .session_notes_types import (
    SessionNotesQueryIntent, SessionNote, SessionSearchResult,
    CharacterArcResult, NPCInteractionResult, Quote, NPCInteraction,
    CharacterDecision, LocationVisit, Encounter, SpellUsage, ItemTransaction,
    RelationshipChange, CharacterGrowthMoment, SessionNotesQueryRequest,
    SessionNotesQueryResponse, QueryEntity, EntityType
)
from .session_notes_parser import SessionNotesParser, parse_session_notes_directory
from .session_notes_storage import SessionNotesStorage
from .session_notes_query_engine import SessionNotesQueryEngine

__all__ = [
    # Core types
    'SessionNotesQueryIntent',
    'SessionNote', 
    'SessionSearchResult',
    'CharacterArcResult',
    'NPCInteractionResult',
    'Quote',
    'NPCInteraction',
    'CharacterDecision',
    'LocationVisit',
    'Encounter',
    'SpellUsage',
    'ItemTransaction',
    'RelationshipChange', 
    'CharacterGrowthMoment',
    'SessionNotesQueryRequest', 
    'SessionNotesQueryResponse',
    'QueryEntity',
    'EntityType',
    
    # Main classes
    'SessionNotesParser',
    'SessionNotesStorage',
    'SessionNotesQueryEngine',
    
    # Utility functions
    'parse_session_notes_directory'
]