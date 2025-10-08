"""
Build Session Notes Storage

Parses markdown session notes and builds the storage system with embeddings.
"""

import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.session_notes.session_notes_parser import SessionNotesParser, parse_session_notes_directory
from src.rag.session_notes.session_notes_storage import SessionNotesStorage
from src.rag.session_notes.session_notes_query_router import SessionNotesQueryRouter
from src.rag.session_notes.session_types import UserIntention, EntityType, Entity


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
    
    # Initialize storage manager
    print("\nInitializing storage system...")
    storage_manager = SessionNotesStorage()
    
    # Create or get main campaign
    campaign_name = "main_campaign"
    campaign = storage_manager.get_campaign(campaign_name)
    if not campaign:
        print(f"Creating new campaign: {campaign_name}")
        campaign = storage_manager.create_campaign(campaign_name)
    else:
        print(f"Using existing campaign: {campaign_name}")
    
    print("✓ Campaign storage ready")
    
    # Store all sessions in the campaign
    print("\nStoring sessions and generating embeddings...")
    for session_note in session_notes:
        print(f"  Processing Session {session_note.session_number}...")
        campaign.add_session(session_note)
    
    # Save campaign to disk
    print("\nSaving campaign to disk...")
    if storage_manager.save_campaign(campaign_name):
        print("✓ Campaign saved successfully")
    else:
        print("✗ Failed to save campaign")
    
    print("✓ All sessions stored successfully")
    
    # Initialize query engine
    print("\nInitializing query engine...")
    query_engine = SessionNotesQueryRouter(campaign)
    print("✓ Query engine initialized")
    
    # Test basic functionality
    print("\n" + "=" * 40)
    print("Testing Basic Queries")
    print("=" * 40)
    
    # Test NPC interaction query
    print("\nTest 1: NPC Interactions")
    results = query_engine.query(
        user_query="Tell me about Ghul'vor interactions",
        intention=UserIntention.NPC_INFO,
        entities=[Entity(name="Ghul'vor", entity_type=EntityType.NPC)],
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
        intention=UserIntention.CHARACTER_STATUS,
        entities=[Entity(name="Duskryn", entity_type=EntityType.PC)],
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
        intention=UserIntention.EVENT_SEQUENCE,
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