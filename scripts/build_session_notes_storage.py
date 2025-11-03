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
from src.rag.session_notes.session_types import (
    UserIntention, EntityType, Entity, SessionMetadata, ProcessedSession, SessionEntity
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
        
        # Convert SessionNotes to ProcessedSession
        session_id = f"session_{session_note.session_number}"
        
        # Create metadata
        metadata = SessionMetadata(
            session_id=session_id,
            session_date=session_note.date,
            title=session_note.title,
            session_number=session_note.session_number
        )
        
        # Create processed session
        processed = ProcessedSession(
            metadata=metadata,
            content=session_note.summary,  # Use summary as content for now
            summary=session_note.summary,
            raw_notes=session_note
        )
        
        # Add to campaign storage
        campaign.sessions[session_id] = processed
        
        # Extract and store entities
        all_entities = (
            session_note.player_characters +
            session_note.npcs +
            session_note.locations +
            session_note.items
        )
        
        for entity in all_entities:
            entity_key = entity.name
            if entity_key not in campaign.entities:
                # Create new SessionEntity
                session_entity = SessionEntity(
                    name=entity.name,
                    entity_type=entity.entity_type.value,
                    description="",
                    first_mentioned=session_note.session_number,
                    sessions_appeared=[session_note.session_number],
                    aliases=entity.aliases if hasattr(entity, 'aliases') else []
                )
                campaign.entities[entity_key] = session_entity
            else:
                # Update existing entity
                if session_note.session_number not in campaign.entities[entity_key].sessions_appeared:
                    campaign.entities[entity_key].sessions_appeared.append(session_note.session_number)
    
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
        character_name="Duskryn",
        original_query="Tell me about Ghul'vor interactions",
        intention="npc_info",
        entities=[{"name": "Ghul'vor", "type": "npc"}],
        context_hints=[],
        top_k=3
    )
    
    print(f"Found {len(results.contexts)} results:")
    for context in results.contexts:
        print(f"  - Session {context.session_number}: {context.session_summary[:100]}...")
    
    # Test character arc query
    print("\nTest 2: Character Development")
    results = query_engine.query(
        character_name="Duskryn",
        original_query="How has Duskryn changed over time?",
        intention="character_status",
        entities=[{"name": "Duskryn", "type": "player_character"}],
        context_hints=[],
        top_k=3
    )
    
    print(f"Found {len(results.contexts)} results:")
    for context in results.contexts:
        print(f"  - Session {context.session_number}: {context.session_summary[:100]}...")
    
    # Test recent events
    print("\nTest 3: Recent Events")
    results = query_engine.query(
        character_name="Duskryn",
        original_query="What happened recently?",
        intention="event_sequence",
        entities=[],
        context_hints=[],
        top_k=2
    )
    
    print(f"Found {len(results.contexts)} results:")
    for context in results.contexts:
        print(f"  - Session {context.session_number}: {context.session_summary[:100]}...")
    
    print(f"\n✓ Session notes storage system ready!")
    print(f"Campaign: {campaign_name}")
    print(f"Sessions: {len(campaign.sessions)}")
    print(f"Entities: {len(campaign.entities)}")


if __name__ == "__main__":
    main()