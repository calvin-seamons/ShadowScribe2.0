"""
Demo Session Notes Query Engine

Interactive demo to test session notes querying functionality.
"""

import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.session_notes import (
    SessionNotesStorage, SessionNotesQueryEngine, SessionNotesQueryIntent,
    QueryEntity, EntityType
)


def main():
    """Interactive demo of session notes query engine"""
    print("Session Notes Query Engine Demo")
    print("=" * 40)
    
    # Initialize storage and engine
    try:
        storage = SessionNotesStorage()
        engine = SessionNotesQueryEngine(storage)
        print("✓ Query engine initialized")
    except Exception as e:
        print("✗ Failed to initialize query engine!")
        print("Please run: python -m scripts.build_session_notes_storage")
        print(f"Error: {e}")
        return
    
    # Show available intents
    print(f"\nAvailable query intentions:")
    for intent in engine.get_available_intents():
        print(f"  - {intent.value}")
    
    # Demo queries
    demo_queries = [
        {
            "description": "NPC Interaction Query",
            "query": "What happened with Ghul'vor?",
            "intention": SessionNotesQueryIntent.FIND_NPC_INTERACTIONS,
            "entities": [QueryEntity(name="Ghul'vor", entity_type=EntityType.NPC)]
        },
        {
            "description": "Character Development Query", 
            "query": "How has Duskryn's faith evolved?",
            "intention": SessionNotesQueryIntent.CHARACTER_ARC_TRACKING,
            "entities": [
                QueryEntity(name="Duskryn", entity_type=EntityType.CHARACTER),
                QueryEntity(name="faith", entity_type=EntityType.THEME)
            ]
        },
        {
            "description": "Spell Usage Query",
            "query": "When did Duskryn cast Calm Emotions?",
            "intention": SessionNotesQueryIntent.SPELL_USAGE_HISTORY,
            "entities": [
                QueryEntity(name="Calm Emotions", entity_type=EntityType.SPELL),
                QueryEntity(name="Duskryn", entity_type=EntityType.CHARACTER)
            ]
        },
        {
            "description": "Recent Events Query",
            "query": "What happened in the most recent sessions?",
            "intention": SessionNotesQueryIntent.RECENT_EVENTS,
            "entities": []
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n" + "=" * 40)
        print(f"Demo Query {i}: {demo['description']}")
        print(f"Query: '{demo['query']}'")
        print(f"Intention: {demo['intention'].value}")
        print(f"Entities: {[f'{e.name} ({e.entity_type.value})' for e in demo['entities']]}")
        print("-" * 40)
        
        try:
            results = engine.query(
                user_query=demo['query'],
                intention=demo['intention'],
                entities=demo['entities'],
                k=3
            )
            
            if results:
                print(f"Found {len(results)} results:")
                for j, result in enumerate(results, 1):
                    print(f"\n{j}. Session {result.session_number}: {result.session_title}")
                    print(f"   Date: {result.session_date}")
                    print(f"   Relevance: {result.relevance_score:.2f}")
                    
                    if result.session_summary:
                        print(f"   Summary: {result.session_summary[:150]}...")
                    
                    if hasattr(result, 'npc_name') and result.npc_name:
                        print(f"   NPC: {result.npc_name}")
                    
                    if hasattr(result, 'character_name') and result.character_name:
                        print(f"   Character: {result.character_name}")
                    
                    if result.matched_events:
                        print(f"   Key Events: {'; '.join(result.matched_events[:2])}")
            else:
                print("No results found.")
                
        except Exception as e:
            print(f"Error executing query: {e}")
    
    print(f"\n" + "=" * 40)
    print("Demo completed! The session notes query engine is ready for use.")


if __name__ == "__main__":
    main()