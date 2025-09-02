#!/usr/bin/env python3
"""
Demo script for the Session Notes Query Engine

This script demonstrates various query capabilities of the session notes system.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.session_notes import (
    SessionNotesStorage, SessionNotesQueryEngine,
    QueryEngineInput, UserIntention
)


def main():
    """Demo the query engine capabilities"""
    print("🔍 Session Notes Query Engine Demo")
    print("=" * 50)
    
    # Initialize storage
    storage = SessionNotesStorage()
    query_engine = SessionNotesQueryEngine(storage)
    
    # Check if we have any data
    storage_info = storage.get_storage_info()
    print(f"📚 Storage Info: {storage_info['session_count']} sessions, {storage_info['entity_count']} entities")
    
    if storage_info['session_count'] == 0:
        print("⚠️  No session data found. Please run build_session_notes_storage.py first.")
        return
    
    # Demo queries
    demo_queries = [
        {
            "name": "Character Status Query",
            "query": QueryEngineInput(
                user_query="What's Duskryn's current status?",
                intention="character_status",
                entities=[{"name": "Duskryn", "type": "player_character"}],
                context_hints=["status", "health"],
                top_k=3
            )
        },
        {
            "name": "Spell Usage Query",
            "query": QueryEngineInput(
                user_query="What spells did Dusk cast in combat recently?",
                intention="spell_ability_usage", 
                entities=[{"name": "Dusk", "type": "player_character"}],
                context_hints=["combat", "recently"],
                top_k=5
            )
        },
        {
            "name": "Combat Recap Query",
            "query": QueryEngineInput(
                user_query="Tell me about recent combat encounters",
                intention="combat_recap",
                entities=[],
                context_hints=["combat", "fight", "recently"],
                top_k=3
            )
        },
        {
            "name": "Quest Tracking Query",
            "query": QueryEngineInput(
                user_query="What are our active quests?",
                intention="quest_tracking",
                entities=[],
                context_hints=["quest", "objective", "active"],
                top_k=5
            )
        },
        {
            "name": "Party Dynamics Query",
            "query": QueryEngineInput(
                user_query="How is the party getting along?",
                intention="party_dynamics",
                entities=[],
                context_hints=["party", "relationship", "conflict"],
                top_k=3
            )
        }
    ]
    
    # Execute demo queries
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{i}. {demo['name']}")
        print(f"   Query: {demo['query'].user_query}")
        print(f"   Intention: {demo['query'].intention}")
        print("-" * 50)
        
        try:
            result = query_engine.query(demo['query'])
            
            print(f"📊 Results: {len(result.contexts)} contexts from {result.total_sessions_searched} sessions searched")
            print(f"🎯 Query Summary: {result.query_summary}")
            print(f"👥 Entities Resolved: {[e.name for e in result.entities_resolved]}")
            
            if result.contexts:
                print("\n📋 Top Results:")
                for j, context in enumerate(result.contexts[:2], 1):  # Show top 2
                    print(f"   {j}. Session {context.session_number} (Score: {context.relevance_score:.2f})")
                    print(f"      Summary: {context.session_summary[:100]}...")
                    print(f"      Entities Found: {[e.name for e in context.entities_found]}")
                    print(f"      Relevant Sections: {list(context.relevant_sections.keys())}")
                    
                    # Show some content details
                    if context.relevant_sections:
                        for section_name, section_data in list(context.relevant_sections.items())[:1]:
                            print(f"      {section_name}: {str(section_data)[:150]}...")
                    print()
            else:
                print("   No relevant contexts found.")
                
        except Exception as e:
            print(f"❌ Error executing query: {e}")
        
        print()
    
    print("\n👋 Demo completed!")


if __name__ == "__main__":
    main()