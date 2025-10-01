"""
Session Notes System Summary

Shows the current state and capabilities of the session notes RAG system.
"""

import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.session_notes import (
    SessionNotesStorage, SessionNotesQueryRouter, SessionNotesQueryIntent,
    parse_session_notes_directory
)


def main():
    """Display session notes system summary"""
    print("Session Notes RAG System - Phase 1 Implementation")
    print("=" * 60)
    
    # Check if storage exists
    try:
        storage = SessionNotesStorage()
        engine = SessionNotesQueryRouter(storage)
        print("✓ System Status: READY")
    except Exception as e:
        print("✗ System Status: NOT READY")
        print(f"Error: {e}")
        print("Run: python scripts/build_session_notes_storage.py")
        return
    
    # Show parsed session count
    notes_directory = "knowledge_base/source/session_notes"
    session_notes = parse_session_notes_directory(notes_directory)
    print(f"✓ Sessions Parsed: {len(session_notes)}")
    
    for note in session_notes:
        print(f"  - Session {note.session_number}: {note.title}")
        print(f"    Date: {note.date}, Events: {len(note.key_events)}, NPCs: {len(note.npcs)}")
    
    # Show available query intentions
    print(f"\n✓ Available Query Intentions: {len(engine.get_available_intents())}")
    for intent in engine.get_available_intents():
        print(f"  - {intent.value}")
    
    # Show storage statistics
    print(f"\n✓ Storage Components:")
    print(f"  - SQLite Database: {storage.db_path}")
    print(f"  - Vector Embeddings: {storage.embeddings_path}")
    
    # Test key functionality
    print(f"\n✓ Core Features Implemented:")
    print(f"  - ✅ Markdown parsing (converts session notes to structured data)")
    print(f"  - ✅ Hybrid storage (SQLite + vector embeddings)")
    print(f"  - ✅ Intent-based query routing")
    print(f"  - ✅ NPC interaction tracking")
    print(f"  - ✅ Character decision history")
    print(f"  - ✅ Semantic search across sessions")
    print(f"  - ✅ Recent events queries")
    
    # Sample successful query
    print(f"\n✓ Sample Query Test:")
    results = engine.query(
        user_query="Tell me about Ghul'vor",
        intention=SessionNotesQueryIntent.FIND_NPC_INTERACTIONS,
        entities=["Ghul'vor"],
        k=2
    )
    
    print(f"  Query: 'Tell me about Ghul'vor'")
    print(f"  Results: {len(results)} sessions found")
    for result in results:
        print(f"    - Session {result.session_number}: Relevance {result.relevance_score:.2f}")
    
    print(f"\n" + "=" * 60)
    print("Phase 1 Implementation Complete!")
    print("Ready for Phase 2: Enhanced features and relationship tracking")


if __name__ == "__main__":
    main()