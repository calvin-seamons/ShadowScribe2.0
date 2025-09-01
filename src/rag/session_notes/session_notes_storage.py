"""
Session Notes Storage System

Hybrid storage using SQLite for structured data and vector embeddings for semantic search.
"""

import sqlite3
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import openai
import numpy as np
from datetime import datetime

from .session_notes_types import (
    SessionNote, SessionSearchResult, NPCInteraction, CharacterDecision,
    Quote, SessionNotesQueryIntent
)
from ..config import get_config

config = get_config()


class SessionNotesStorage:
    """Hybrid storage system for session notes"""
    
    def __init__(self, storage_path: str = "knowledge_base/processed_session_notes"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.storage_path / "session_notes.db"
        self.embeddings_path = self.storage_path / "embeddings.pkl"
        
        self._init_database()
        self._load_embeddings()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Core session metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY,
                    session_number INTEGER UNIQUE,
                    date TEXT,
                    title TEXT,
                    summary TEXT,
                    cliffhanger TEXT
                )
            ''')
            
            # Key events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS key_events (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER,
                    event_description TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # NPCs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS npcs (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    first_appearance_session INTEGER,
                    description TEXT
                )
            ''')
            
            # NPC interactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS npc_interactions (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER,
                    npc_id INTEGER,
                    npc_name TEXT,
                    interaction_type TEXT,
                    description TEXT,
                    character_involved TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    FOREIGN KEY (npc_id) REFERENCES npcs (id)
                )
            ''')
            
            # Character decisions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_decisions (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER,
                    character_name TEXT,
                    decision_description TEXT,
                    context TEXT,
                    consequences TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Spells used
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spell_usage (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER,
                    spell_name TEXT,
                    caster TEXT,
                    target TEXT,
                    outcome TEXT,
                    context TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Quotes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER,
                    quote_text TEXT,
                    speaker TEXT,
                    context TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Locations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    first_visit_session INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS location_visits (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER,
                    location_id INTEGER,
                    location_name TEXT,
                    description TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    FOREIGN KEY (location_id) REFERENCES locations (id)
                )
            ''')
            
            conn.commit()
    
    def _load_embeddings(self):
        """Load embeddings from disk if they exist"""
        if self.embeddings_path.exists():
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
        else:
            self.embeddings = {
                'session_summaries': {},
                'key_events': {},
                'character_moments': {},
                'quotes': {}
            }
    
    def _save_embeddings(self):
        """Save embeddings to disk"""
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
    
    def store_session(self, session: SessionNote):
        """Store a complete session note"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store main session data
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_number, date, title, summary, cliffhanger)
                VALUES (?, ?, ?, ?, ?)
            ''', (session.session_number, session.date, session.title, 
                  session.summary, session.cliffhanger))
            
            session_id = cursor.lastrowid
            
            # Store key events
            cursor.execute('DELETE FROM key_events WHERE session_id = ?', (session_id,))
            for event in session.key_events:
                cursor.execute('''
                    INSERT INTO key_events (session_id, event_description)
                    VALUES (?, ?)
                ''', (session_id, event))
            
            # Store NPCs and interactions
            cursor.execute('DELETE FROM npc_interactions WHERE session_id = ?', (session_id,))
            for npc_name, npc_interaction in session.npcs.items():
                # Ensure NPC exists
                cursor.execute('''
                    INSERT OR IGNORE INTO npcs (name, first_appearance_session, description)
                    VALUES (?, ?, ?)
                ''', (npc_name, session.session_number, npc_interaction.description))
                
                # Get NPC ID
                cursor.execute('SELECT id FROM npcs WHERE name = ?', (npc_name,))
                npc_id = cursor.fetchone()[0]
                
                # Store interaction
                cursor.execute('''
                    INSERT INTO npc_interactions 
                    (session_id, npc_id, npc_name, interaction_type, description, character_involved)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, npc_id, npc_name, npc_interaction.interaction_type,
                      npc_interaction.description, npc_interaction.character_involved))
            
            # Store character decisions
            cursor.execute('DELETE FROM character_decisions WHERE session_id = ?', (session_id,))
            for character, decisions in session.character_decisions.items():
                for decision in decisions:
                    cursor.execute('''
                        INSERT INTO character_decisions 
                        (session_id, character_name, decision_description, context, consequences)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (session_id, decision.character_name, decision.decision_description,
                          decision.context, decision.consequences))
            
            # Store spell usage
            cursor.execute('DELETE FROM spell_usage WHERE session_id = ?', (session_id,))
            for spell in session.spells_used:
                cursor.execute('''
                    INSERT INTO spell_usage 
                    (session_id, spell_name, caster, target, outcome, context)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, spell.spell_name, spell.caster, spell.target,
                      spell.outcome, spell.context))
            
            # Store quotes
            cursor.execute('DELETE FROM quotes WHERE session_id = ?', (session_id,))
            for quote in session.quotes:
                cursor.execute('''
                    INSERT INTO quotes (session_id, quote_text, speaker, context)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, quote.text, quote.speaker, quote.context))
            
            # Store locations
            cursor.execute('DELETE FROM location_visits WHERE session_id = ?', (session_id,))
            for location in session.locations:
                # Ensure location exists
                cursor.execute('''
                    INSERT OR IGNORE INTO locations (name, first_visit_session)
                    VALUES (?, ?)
                ''', (location.location_name, session.session_number))
                
                # Get location ID
                cursor.execute('SELECT id FROM locations WHERE name = ?', (location.location_name,))
                location_id = cursor.fetchone()[0]
                
                # Store visit
                cursor.execute('''
                    INSERT INTO location_visits 
                    (session_id, location_id, location_name, description)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, location_id, location.location_name, location.description))
            
            conn.commit()
        
        # Generate and store embeddings
        self._generate_session_embeddings(session)
    
    def _generate_session_embeddings(self, session: SessionNote):
        """Generate embeddings for session content"""
        try:
            client = openai.OpenAI(api_key=config.openai_api_key)
            
            # Summary embedding
            if session.summary:
                response = client.embeddings.create(
                    input=session.summary,
                    model="text-embedding-3-small"
                )
                self.embeddings['session_summaries'][session.session_number] = response.data[0].embedding
            
            # Key events embeddings
            for i, event in enumerate(session.key_events):
                key = f"{session.session_number}_{i}"
                response = client.embeddings.create(
                    input=event,
                    model="text-embedding-3-small"
                )
                self.embeddings['key_events'][key] = response.data[0].embedding
            
            # Character moments (combine decisions and growth)
            character_texts = []
            for character, decisions in session.character_decisions.items():
                for decision in decisions:
                    text = f"{character}: {decision.decision_description}"
                    character_texts.append((f"{session.session_number}_{character}_{len(character_texts)}", text))
            
            for key, text in character_texts:
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                self.embeddings['character_moments'][key] = response.data[0].embedding
            
            # Quote embeddings
            for i, quote in enumerate(session.quotes):
                key = f"{session.session_number}_{i}"
                quote_text = f'"{quote.text}" - {quote.speaker}'
                response = client.embeddings.create(
                    input=quote_text,
                    model="text-embedding-3-small"
                )
                self.embeddings['quotes'][key] = response.data[0].embedding
            
            self._save_embeddings()
            
        except Exception as e:
            print(f"Error generating embeddings for session {session.session_number}: {e}")
    
    def get_npc_interactions(self, npc_name: str) -> List[Dict]:
        """Get all interactions with a specific NPC"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.session_number, s.title, s.date, ni.interaction_type, 
                       ni.description, ni.character_involved
                FROM npc_interactions ni
                JOIN sessions s ON ni.session_id = s.id
                WHERE ni.npc_name = ?
                ORDER BY s.session_number
            ''', (npc_name,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def get_character_decisions(self, character_name: str) -> List[Dict]:
        """Get all decisions by a specific character"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.session_number, s.title, s.date, cd.decision_description,
                       cd.context, cd.consequences
                FROM character_decisions cd
                JOIN sessions s ON cd.session_id = s.id
                WHERE cd.character_name = ?
                ORDER BY s.session_number
            ''', (character_name,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def get_spell_usage_history(self, spell_name: str, caster: str = None) -> List[Dict]:
        """Get usage history for a specific spell"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if caster:
                cursor.execute('''
                    SELECT s.session_number, s.title, s.date, su.caster, su.target,
                           su.outcome, su.context
                    FROM spell_usage su
                    JOIN sessions s ON su.session_id = s.id
                    WHERE su.spell_name = ? AND su.caster = ?
                    ORDER BY s.session_number
                ''', (spell_name, caster))
            else:
                cursor.execute('''
                    SELECT s.session_number, s.title, s.date, su.caster, su.target,
                           su.outcome, su.context
                    FROM spell_usage su
                    JOIN sessions s ON su.session_id = s.id
                    WHERE su.spell_name = ?
                    ORDER BY s.session_number
                ''', (spell_name,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def search_sessions_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get sessions within a date range"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_number, title, date, summary
                FROM sessions
                WHERE date BETWEEN ? AND ?
                ORDER BY session_number
            ''', (start_date, end_date))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def get_session_metadata(self, session_number: int) -> Optional[Dict]:
        """Get session metadata by session number"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_number, title, date, summary
                FROM sessions
                WHERE session_number = ?
            ''', (session_number,))
            
            row = cursor.fetchone()
            if row:
                return dict(zip([col[0] for col in cursor.description], row))
            return None
    
    def semantic_search(self, query: str, collection: str, k: int = 5) -> List[Tuple[str, float]]:
        """Perform semantic search using embeddings"""
        try:
            client = openai.OpenAI(api_key=config.openai_api_key)
            
            # Get query embedding
            response = client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            query_embedding = np.array(response.data[0].embedding)
            
            # Calculate similarities
            similarities = []
            for key, embedding in self.embeddings[collection].items():
                similarity = np.dot(query_embedding, np.array(embedding))
                similarities.append((key, similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:k]
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def get_session_metadata(self, session_number: int) -> Optional[Dict]:
        """Get session metadata by session number"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_number, title, date, summary
                FROM sessions
                WHERE session_number = ?
            ''', (session_number,))
            
            row = cursor.fetchone()
            if row:
                return dict(zip([col[0] for col in cursor.description], row))
            return None