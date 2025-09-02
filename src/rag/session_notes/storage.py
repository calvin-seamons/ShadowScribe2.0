"""
Session Notes Storage System

Handles storage and retrieval of SessionNotes objects using pickle files.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime

from .session_types import SessionNotes, Entity, EntityType


class SessionNotesStorage:
    """Storage system for session notes using pickle files"""
    
    def __init__(self, storage_dir: str = "knowledge_base/processed_session_notes"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage files
        self.sessions_file = self.storage_dir / "sessions.pkl"
        self.entities_file = self.storage_dir / "entities.pkl"
        self.metadata_file = self.storage_dir / "metadata.pkl"
        
        # In-memory caches
        self._sessions: Dict[int, SessionNotes] = {}
        self._entities: Dict[str, Entity] = {}
        self._metadata: Dict[str, any] = {}
        
        # Load existing data
        self._load_from_disk()
    
    def store_session(self, session_notes: SessionNotes) -> None:
        """Store a session notes object"""
        # Store in memory
        self._sessions[session_notes.session_number] = session_notes
        
        # Update entity registry
        self._update_entities(session_notes)
        
        # Update metadata
        self._update_metadata(session_notes)
        
        # Save to disk
        self._save_to_disk()
        
        print(f"✓ Stored Session {session_notes.session_number}: {session_notes.title}")
    
    def get_session(self, session_number: int) -> Optional[SessionNotes]:
        """Get a specific session by number"""
        return self._sessions.get(session_number)
    
    def get_all_sessions(self) -> List[SessionNotes]:
        """Get all stored sessions, sorted by session number"""
        return sorted(self._sessions.values(), key=lambda s: s.session_number)
    
    def get_sessions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[SessionNotes]:
        """Get sessions within a date range"""
        return [
            session for session in self._sessions.values()
            if start_date <= session.date <= end_date
        ]
    
    def get_sessions_with_entity(self, entity_name: str) -> List[SessionNotes]:
        """Get all sessions that mention a specific entity"""
        sessions_with_entity = []
        
        for session in self._sessions.values():
            if self._session_contains_entity(session, entity_name):
                sessions_with_entity.append(session)
        
        return sorted(sessions_with_entity, key=lambda s: s.session_number)
    
    def get_entity(self, entity_name: str) -> Optional[Entity]:
        """Get entity information"""
        return self._entities.get(entity_name.lower())
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type"""
        return [
            entity for entity in self._entities.values()
            if entity.entity_type == entity_type
        ]
    
    def get_all_entities(self) -> List[Entity]:
        """Get all registered entities"""
        return list(self._entities.values())
    
    def search_sessions_by_keyword(self, keyword: str) -> List[SessionNotes]:
        """Simple keyword search across session content"""
        keyword_lower = keyword.lower()
        matching_sessions = []
        
        for session in self._sessions.values():
            if self._session_contains_keyword(session, keyword_lower):
                matching_sessions.append(session)
        
        return sorted(matching_sessions, key=lambda s: s.session_number)
    
    def get_latest_sessions(self, count: int = 5) -> List[SessionNotes]:
        """Get the most recent sessions"""
        all_sessions = sorted(self._sessions.values(), key=lambda s: s.session_number, reverse=True)
        return all_sessions[:count]
    
    def get_session_count(self) -> int:
        """Get total number of stored sessions"""
        return len(self._sessions)
    
    def get_storage_info(self) -> Dict[str, any]:
        """Get information about the storage system"""
        return {
            "session_count": len(self._sessions),
            "entity_count": len(self._entities),
            "storage_dir": str(self.storage_dir),
            "last_updated": self._metadata.get("last_updated"),
            "session_range": {
                "min": min(self._sessions.keys()) if self._sessions else None,
                "max": max(self._sessions.keys()) if self._sessions else None
            },
            "entity_types": {
                entity_type.value: len([e for e in self._entities.values() if e.entity_type == entity_type])
                for entity_type in EntityType
            }
        }
    
    def delete_session(self, session_number: int) -> bool:
        """Delete a session from storage"""
        if session_number in self._sessions:
            del self._sessions[session_number]
            self._save_to_disk()
            print(f"✓ Deleted Session {session_number}")
            return True
        return False
    
    def clear_all_data(self) -> None:
        """Clear all stored data (destructive operation)"""
        self._sessions.clear()
        self._entities.clear()
        self._metadata.clear()
        
        # Remove pickle files
        for file_path in [self.sessions_file, self.entities_file, self.metadata_file]:
            if file_path.exists():
                file_path.unlink()
        
        print("✓ Cleared all session notes data")
    
    def _update_entities(self, session_notes: SessionNotes) -> None:
        """Update entity registry with entities from a session"""
        all_entities = (
            session_notes.player_characters +
            session_notes.npcs +
            session_notes.locations +
            session_notes.items
        )
        
        for entity in all_entities:
            key = entity.name.lower()
            if key not in self._entities:
                self._entities[key] = entity
            else:
                # Update existing entity with new information
                existing = self._entities[key]
                if entity.description and not existing.description:
                    existing.description = entity.description
                if entity.aliases:
                    existing.aliases.extend([a for a in entity.aliases if a not in existing.aliases])
    
    def _update_metadata(self, session_notes: SessionNotes) -> None:
        """Update storage metadata"""
        self._metadata["last_updated"] = datetime.now()
        self._metadata["last_session_added"] = session_notes.session_number
        
        if "first_session" not in self._metadata:
            self._metadata["first_session"] = session_notes.session_number
    
    def _session_contains_entity(self, session: SessionNotes, entity_name: str) -> bool:
        """Check if a session contains references to an entity"""
        entity_name_lower = entity_name.lower()
        
        # Check in entity lists
        all_entities = (
            session.player_characters + session.npcs + 
            session.locations + session.items
        )
        
        for entity in all_entities:
            if entity.name.lower() == entity_name_lower:
                return True
            if any(alias.lower() == entity_name_lower for alias in entity.aliases):
                return True
        
        # Check in text content
        text_fields = [
            session.summary, session.cliffhanger or "",
            session.next_session_hook or ""
        ]
        
        for field in text_fields:
            if entity_name_lower in field.lower():
                return True
        
        # Check in raw sections
        for section_text in session.raw_sections.values():
            if entity_name_lower in section_text.lower():
                return True
        
        return False
    
    def _session_contains_keyword(self, session: SessionNotes, keyword: str) -> bool:
        """Check if a session contains a keyword"""
        # Check in main text fields
        text_fields = [
            session.title, session.summary,
            session.cliffhanger or "", session.next_session_hook or ""
        ]
        
        for field in text_fields:
            if keyword in field.lower():
                return True
        
        # Check in raw sections
        for section_text in session.raw_sections.values():
            if keyword in section_text.lower():
                return True
        
        # Check in structured data
        for quote in session.quotes:
            if keyword in quote.get("quote", "").lower() or keyword in quote.get("speaker", "").lower():
                return True
        
        for moment in session.funny_moments:
            if keyword in moment.lower():
                return True
        
        return False
    
    def _load_from_disk(self) -> None:
        """Load data from pickle files"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'rb') as f:
                    self._sessions = pickle.load(f)
                    print(f"✓ Loaded {len(self._sessions)} sessions from disk")
        except Exception as e:
            print(f"⚠ Warning: Could not load sessions file: {e}")
            self._sessions = {}
        
        try:
            if self.entities_file.exists():
                with open(self.entities_file, 'rb') as f:
                    self._entities = pickle.load(f)
                    print(f"✓ Loaded {len(self._entities)} entities from disk")
        except Exception as e:
            print(f"⚠ Warning: Could not load entities file: {e}")
            self._entities = {}
        
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'rb') as f:
                    self._metadata = pickle.load(f)
        except Exception as e:
            print(f"⚠ Warning: Could not load metadata file: {e}")
            self._metadata = {}
    
    def _save_to_disk(self) -> None:
        """Save data to pickle files"""
        try:
            with open(self.sessions_file, 'wb') as f:
                pickle.dump(self._sessions, f)
        except Exception as e:
            print(f"✗ Error saving sessions: {e}")
        
        try:
            with open(self.entities_file, 'wb') as f:
                pickle.dump(self._entities, f)
        except Exception as e:
            print(f"✗ Error saving entities: {e}")
        
        try:
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self._metadata, f)
        except Exception as e:
            print(f"✗ Error saving metadata: {e}")
    
    def __str__(self) -> str:
        """String representation of storage system"""
        info = self.get_storage_info()
        return f"SessionNotesStorage({info['session_count']} sessions, {info['entity_count']} entities)"
    
    def __repr__(self) -> str:
        return self.__str__()