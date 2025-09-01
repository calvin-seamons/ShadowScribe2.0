"""
Session Notes Query Engine

Main query engine that combines SQL and vector search for session notes retrieval.
"""

import time
from typing import List, Dict, Optional, Tuple, Any
from abc import ABC, abstractmethod

from .session_notes_types import (
    SessionNotesQueryIntent, SessionSearchResult, CharacterArcResult,
    NPCInteractionResult, Quote, NPCInteraction, CharacterDecision,
    QueryEntity, EntityType
)
from .session_notes_storage import SessionNotesStorage


class SearchStrategy(ABC):
    """Abstract base class for search strategies"""
    
    @abstractmethod
    def execute_search(
        self, 
        query: str, 
        entities: List[QueryEntity], 
        storage: SessionNotesStorage, 
        k: int
    ) -> List[SessionSearchResult]:
        pass


class NPCInteractionStrategy(SearchStrategy):
    """Strategy for finding NPC interactions"""
    
    def execute_search(
        self, 
        query: str, 
        entities: List[QueryEntity], 
        storage: SessionNotesStorage, 
        k: int
    ) -> List[NPCInteractionResult]:
        npc_entity = self._get_entity_by_type(entities, EntityType.NPC)
        if not npc_entity:
            return []
        
        npc_name = npc_entity.name
        
        # 1. Direct database lookup for all NPC interactions
        direct_interactions = storage.get_npc_interactions(npc_name)
        
        # 2. Semantic search for additional mentions
        semantic_matches = storage.semantic_search(
            f"{npc_name} {query}", 
            "session_summaries", 
            k=k*2
        )
        
        # 3. Combine and format results
        results = []
        seen_sessions = set()
        
        # Process direct interactions first
        for interaction in direct_interactions[:k]:
            session_num = interaction['session_number']
            if session_num not in seen_sessions:
                seen_sessions.add(session_num)
                
                result = NPCInteractionResult(
                    session_number=session_num,
                    session_title=interaction['title'],
                    session_date=interaction['date'],
                    relevance_score=1.0,  # Direct matches get highest score
                    npc_name=npc_name,
                    interaction_type=interaction['interaction_type'],
                    relationship_status="unknown",
                    session_summary="",
                    matched_npcs=[NPCInteraction(
                        npc_name=npc_name,
                        interaction_type=interaction['interaction_type'],
                        description=interaction['description'],
                        character_involved=interaction['character_involved']
                    )]
                )
                results.append(result)
        
        # Add semantic matches if we need more results
        for match_key, similarity in semantic_matches:
            if len(results) >= k:
                break
                
            # Extract session number from embedding key (format: session_number or session_number_index)
            try:
                session_num = int(match_key.split('_')[0]) if '_' in str(match_key) else int(match_key)
            except (ValueError, AttributeError):
                continue
                
            if session_num and session_num not in seen_sessions:
                seen_sessions.add(session_num)
                
                # Get proper session metadata
                session_meta = storage.get_session_metadata(session_num)
                title = session_meta['title'] if session_meta else f"Session {session_num}"
                date = session_meta['date'] if session_meta else "unknown"
                
                result = NPCInteractionResult(
                    session_number=session_num,
                    session_title=title,
                    session_date=date,
                    relevance_score=similarity,
                    npc_name=npc_name,
                    interaction_type="mentioned",
                    relationship_status="unknown",
                    session_summary=""
                )
                results.append(result)
        
        return results[:k]
    
    def _get_entity_by_type(self, entities: List[QueryEntity], entity_type: EntityType) -> Optional[QueryEntity]:
        """Get the first entity of a specific type"""
        for entity in entities:
            if entity.entity_type == entity_type:
                return entity
        return None


class CharacterArcStrategy(SearchStrategy):
    """Strategy for tracking character development"""
    
    def execute_search(
        self, 
        query: str, 
        entities: List[QueryEntity], 
        storage: SessionNotesStorage, 
        k: int
    ) -> List[CharacterArcResult]:
        character_entity = self._get_entity_by_type(entities, EntityType.CHARACTER)
        if not character_entity:
            return []
        
        character_name = character_entity.name
        
        # 1. Get character decisions across all sessions
        decisions = storage.get_character_decisions(character_name)
        
        # 2. Semantic search for character growth moments
        semantic_matches = storage.semantic_search(
            f"{character_name} {query} growth development change",
            "character_moments",
            k=k*2
        )
        
        # 3. Build timeline of character development
        results = []
        seen_sessions = set()
        
        # Process decisions
        for decision in decisions:
            session_num = decision['session_number']
            if session_num not in seen_sessions:
                seen_sessions.add(session_num)
                
                char_decision = CharacterDecision(
                    character_name=character_name,
                    decision_description=decision['decision_description'],
                    context=decision['context'] or "",
                    consequences=decision['consequences']
                )
                
                result = CharacterArcResult(
                    session_number=session_num,
                    session_title=decision['title'],
                    session_date=decision['date'],
                    relevance_score=1.0,
                    character_name=character_name,
                    session_summary="",
                    matched_decisions=[char_decision],
                    decisions_and_consequences=[(
                        decision['decision_description'], 
                        decision['consequences'] or "Unknown"
                    )]
                )
                results.append(result)
        
        # Add semantic matches
        for match_key, similarity in semantic_matches:
            if len(results) >= k:
                break
                
            # Parse session number from match key
            session_num = self._extract_session_from_key(str(match_key))
            if session_num and session_num not in seen_sessions:
                seen_sessions.add(session_num)
                
                result = CharacterArcResult(
                    session_number=session_num,
                    session_title=f"Session {session_num}",
                    session_date="unknown",
                    relevance_score=similarity,
                    character_name=character_name,
                    session_summary=""
                )
                results.append(result)
        
        # Sort by session number (chronological order)
        results.sort(key=lambda x: x.session_number)
        return results[:k]
    
    def _get_entity_by_type(self, entities: List[QueryEntity], entity_type: EntityType) -> Optional[QueryEntity]:
        """Get the first entity of a specific type"""
        for entity in entities:
            if entity.entity_type == entity_type:
                return entity
        return None
    
    def _extract_session_from_key(self, key: str) -> Optional[int]:
        """Extract session number from embedding key"""
        try:
            return int(key.split('_')[0])
        except (ValueError, IndexError):
            return None


class RecentEventsStrategy(SearchStrategy):
    """Strategy for finding recent events"""
    
    def execute_search(
        self, 
        query: str, 
        entities: List[QueryEntity], 
        storage: SessionNotesStorage, 
        k: int
    ) -> List[SessionSearchResult]:
        # Get recent sessions (last 5 by default)
        recent_sessions = storage.search_sessions_by_date_range("2020-01-01", "2030-12-31")
        recent_sessions = sorted(recent_sessions, key=lambda x: x['session_number'], reverse=True)[:k]
        
        results = []
        for session in recent_sessions:
            # Semantic search within recent sessions
            semantic_matches = storage.semantic_search(query, "key_events", k=3)
            
            result = SessionSearchResult(
                session_number=session['session_number'],
                session_title=session['title'],
                session_date=session['date'],
                relevance_score=1.0 - (len(results) * 0.1),  # Decrease score for older sessions
                session_summary=session['summary']
            )
            results.append(result)
        
        return results


class SessionSummariesStrategy(SearchStrategy):
    """Strategy for finding session summaries"""
    
    def execute_search(
        self, 
        query: str, 
        entities: List[QueryEntity], 
        storage: SessionNotesStorage, 
        k: int
    ) -> List[SessionSearchResult]:
        # Semantic search across all session summaries
        semantic_matches = storage.semantic_search(query, "session_summaries", k=k)
        
        results = []
        for match_key, similarity in semantic_matches:
            # Extract session number from embedding key
            try:
                session_num = int(str(match_key).split('_')[0]) if '_' in str(match_key) else int(match_key)
            except (ValueError, AttributeError):
                continue
                
            if session_num:
                result = SessionSearchResult(
                    session_number=session_num,
                    session_title=f"Session {session_num}",
                    session_date="unknown",
                    relevance_score=similarity,
                    session_summary=""
                )
                results.append(result)
        
        return results


class SpellUsageStrategy(SearchStrategy):
    """Strategy for tracking spell usage history"""
    
    def execute_search(
        self, 
        query: str, 
        entities: List[QueryEntity], 
        storage: SessionNotesStorage, 
        k: int
    ) -> List[SessionSearchResult]:
        # Extract spell and character from entities
        spell_entity = self._get_entity_by_type(entities, EntityType.SPELL)
        character_entity = self._get_entity_by_type(entities, EntityType.CHARACTER)
        
        if not spell_entity:
            return []
        
        spell_name = spell_entity.name
        caster = character_entity.name if character_entity else None
        
        # Get spell usage history
        spell_history = storage.get_spell_usage_history(spell_name, caster)
        
        results = []
        for usage in spell_history[:k]:
            result = SessionSearchResult(
                session_number=usage['session_number'],
                session_title=usage['title'],
                session_date=usage['date'],
                relevance_score=1.0,
                session_summary=f"Spell '{spell_name}' used by {usage['caster']}. Outcome: {usage['outcome']}"
            )
            results.append(result)
        
        return results
    
    def _get_entity_by_type(self, entities: List[QueryEntity], entity_type: EntityType) -> Optional[QueryEntity]:
        """Get the first entity of a specific type"""
        for entity in entities:
            if entity.entity_type == entity_type:
                return entity
        return None


class SessionNotesQueryEngine:
    """Main query engine for session notes"""
    
    def __init__(self, storage: SessionNotesStorage):
        self.storage = storage
        
        # Map intentions to strategies
        self.strategy_map = {
            SessionNotesQueryIntent.FIND_NPC_INTERACTIONS: NPCInteractionStrategy(),
            SessionNotesQueryIntent.CHARACTER_ARC_TRACKING: CharacterArcStrategy(),
            SessionNotesQueryIntent.RECENT_EVENTS: RecentEventsStrategy(),
            SessionNotesQueryIntent.SESSION_SUMMARIES: SessionSummariesStrategy(),
            SessionNotesQueryIntent.SPELL_USAGE_HISTORY: SpellUsageStrategy(),
            SessionNotesQueryIntent.RELATIONSHIP_EVOLUTION: CharacterArcStrategy(),  # Reuse for now
            SessionNotesQueryIntent.DECISION_CONSEQUENCES: CharacterArcStrategy(),  # Reuse for now
        }
    
    def query(
        self,
        user_query: str,
        intention: SessionNotesQueryIntent,
        entities: List[QueryEntity],
        k: int = 5
    ) -> List[SessionSearchResult]:
        """
        Query session notes with processed intent and entities.
        
        Args:
            user_query: Original user query for semantic search
            intention: Pre-classified query intention
            entities: List of QueryEntity objects with names and types
            k: Number of results to return
            
        Returns:
            List of SessionSearchResult objects with relevant session content
        """
        start_time = time.time()
        
        # Get appropriate strategy
        strategy = self.strategy_map.get(intention)
        if not strategy:
            # Fallback to session summaries search
            strategy = self.strategy_map[SessionNotesQueryIntent.SESSION_SUMMARIES]
        
        # Execute search
        try:
            results = strategy.execute_search(user_query, entities, self.storage, k)
            
            # Add query time to results
            query_time = (time.time() - start_time) * 1000
            for result in results:
                if hasattr(result, 'query_time_ms'):
                    result.query_time_ms = query_time
            
            return results
            
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def get_available_intents(self) -> List[SessionNotesQueryIntent]:
        """Get list of supported query intentions"""
        return list(self.strategy_map.keys())