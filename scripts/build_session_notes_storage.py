"""
Build Session Notes Storage

Parses markdown session notes and builds the storage system with embeddings.
"""

import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.session_notes import (
    SessionNotesParser, SessionNotesStorage, SessionNotesQueryRouter,
    parse_session_notes_directory, SessionNotesQueryIntent,
    QueryEntity, EntityType
)


def main():
    """Build session notes storage from markdown files"""
    print("Building Session Notes Storage")
    print("=" * 40)
    
    # Parse session notes
    notes_directory = "knowledge_base/source/session_notes"
    print(f"Parsing session notes from {notes_directory}...")
    
    try:
        session_notes = parse_session_notes_directory(notes_directory)
        print(f"✓ Parsed {len(session_notes)} session notes")
        
        for note in session_notes:
            print(f"  - Session {note.session_number}: {note.title} ({note.date})")
    
    except Exception as e:
        print(f"✗ Error parsing session notes: {e}")
        return
    
    # Initialize storage
    print("\nInitializing storage system...")
    storage = SessionNotesStorage()
    print("✓ Storage system initialized")
    
    # Store all sessions
    print("\nStoring sessions and generating embeddings...")
    for session_note in session_notes:
        print(f"  Processing Session {session_note.session_number}...")
        storage.store_session(session_note)
    
    print("✓ All sessions stored successfully")
    
    # Initialize query engine
    print("\nInitializing query engine...")
    query_engine = SessionNotesQueryRouter(storage)
    print("✓ Query engine initialized")
    
    # Test basic functionality
    print("\n" + "=" * 40)
    print("Testing Basic Queries")
    print("=" * 40)
    
    # Test NPC interaction query
    print("\nTest 1: NPC Interactions")
    results = query_engine.query(
        user_query="Tell me about Ghul'vor interactions",
        intention=SessionNotesQueryIntent.FIND_NPC_INTERACTIONS,
        entities=[QueryEntity(name="Ghul'vor", entity_type=EntityType.NPC)],
        k=3
    )
    
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  - Session {result.session_number}: {result.session_title}")
        if hasattr(result, 'npc_name'):
            print(f"    NPC: {result.npc_name}, Type: {result.interaction_type}")
    
    # Test character arc query
    print("\nTest 2: Character Development")
    results = query_engine.query(
        user_query="How has Duskryn changed over time?",
        intention=SessionNotesQueryIntent.CHARACTER_ARC_TRACKING,
        entities=[QueryEntity(name="Duskryn", entity_type=EntityType.CHARACTER)],
        k=3
    )
    
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  - Session {result.session_number}: {result.session_title}")
        if hasattr(result, 'character_name'):
            print(f"    Character: {result.character_name}")
    
    # Test recent events
    print("\nTest 3: Recent Events")
    results = query_engine.query(
        user_query="What happened recently?",
        intention=SessionNotesQueryIntent.RECENT_EVENTS,
        entities=[],
        k=2
    )
    
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  - Session {result.session_number}: {result.session_title}")
        print(f"    Summary: {result.session_summary[:100]}...")
    
    print(f"\n✓ Session notes storage system ready!")
    print(f"Available query intentions: {[intent.value for intent in query_engine.get_available_intents()]}")


if __name__ == "__main__":
    main()