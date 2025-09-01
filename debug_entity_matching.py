#!/usr/bin/env python3
"""
Debug entity matching issue
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.character.character_manager import CharacterManager
from src.rag.character.entity_matcher import EntityMatcher

def debug_entity_matching():
    # Load character
    manager = CharacterManager('knowledge_base/saved_characters')
    char = manager.load_character('Duskryn Nightwarden')
    
    # Get weapons directly
    if char.inventory and char.inventory.equipped_items:
        weapons = char.inventory.equipped_items.get('weapons', [])
        print(f"Found {len(weapons)} weapons:")
        for weapon in weapons:
            print(f"  - Name: '{weapon.name}', Type: '{weapon.type}'")
    
    # Test entity matcher directly
    matcher = EntityMatcher()
    entities = [{'name': 'longsword', 'type': 'weapon'}]
    
    print(f"\nTesting entity matching with: {entities}")
    
    # Test with actual weapon objects
    if weapons:
        filtered_weapons, matches = matcher.filter_items_by_entities(weapons, entities)
        print(f"Direct test: {len(matches)} matches found")
        for match in matches:
            print(f"  - {match.get('reason', 'No reason')}")

if __name__ == "__main__":
    debug_entity_matching()
