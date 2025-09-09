"""
Test Character Query Router

Comprehensive test for the CharacterQueryRouter using multiple intentions and entities
to query information about Duskryn Nightwarden.

NOTE: Updated for multi-intention support - all user_intention parameters now use
user_intentions arrays for consistency with new multi-intention functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.character.character_query_router import CharacterQueryRouter, CharacterQueryResult
from src.rag.character.character_query_types import UserIntention
from src.utils.character_manager import CharacterManager
import json


def print_section(title: str, content: str = ""):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    if content:
        print(content)


def print_query_result(result: CharacterQueryResult, intention: str):
    """Print formatted query result."""
    print(f"\n--- Query: {intention} ---")
    
    if result.warnings:
        print(f"⚠️  Warnings: {', '.join(result.warnings)}")
    
    if result.character_data:
        print(f"✅ Data sections returned: {list(result.character_data.keys())}")
        
        # Show entity match details if present
        if result.entity_matches:
            print(f"🎯 Entity matches found: {len(result.entity_matches)}")
            for match in result.entity_matches:
                entity_name = match['entity'].get('name', 'unknown')
                item_name = match['item'].get('name', 'unknown')
                similarity = match.get('similarity', 0)
                match_type = match.get('match_type', 'unknown')
                print(f"   • {entity_name} → {item_name} ({match_type}, {similarity:.2f})")
        
        # Show some sample data for key sections
        for section, data in result.character_data.items():
            if section == "character_base" and isinstance(data, dict):
                print(f"   📋 Character: {data.get('name', 'Unknown')} - {data.get('race', 'Unknown')} {data.get('character_class', 'Unknown')} (Level {data.get('total_level', '?')})")
            
            elif section == "ability_scores" and isinstance(data, dict):
                print(f"   💪 Abilities: STR {data.get('strength', '?')}, DEX {data.get('dexterity', '?')}, CON {data.get('constitution', '?')}")
            
            elif section == "combat_stats" and isinstance(data, dict):
                print(f"   ⚔️  Combat: {data.get('max_hp', '?')} HP, {data.get('armor_class', '?')} AC, {data.get('speed', '?')} ft speed")
            
            elif section == "inventory" and isinstance(data, dict):
                equipped_count = sum(len(items) for items in data.get('equipped_items', {}).values()) if data.get('equipped_items') else 0
                backpack_count = len(data.get('backpack', [])) if data.get('backpack') else 0
                total_weight = data.get('total_weight', 0)
                print(f"   🎒 Inventory: {equipped_count} equipped, {backpack_count} in backpack, {total_weight} lbs total")
            
            elif section == "spell_list" and isinstance(data, dict):
                spell_count = 0
                spellcasting_info = ""
                if data.get('spells'):
                    for class_spells in data['spells'].values():
                        for level_spells in class_spells.values():
                            spell_count += len(level_spells)
                if data.get('spellcasting'):
                    for class_name, casting_info in data['spellcasting'].items():
                        spell_dc = casting_info.get('spell_save_dc', '?')
                        spell_attack = casting_info.get('spell_attack_bonus', '?')
                        spellcasting_info = f"DC {spell_dc}, +{spell_attack} attack"
                print(f"   🔮 Spells: {spell_count} total spells, {spellcasting_info}")
            
            elif section == "features_and_traits" and isinstance(data, dict):
                feature_count = 0
                if data.get('class_features'):
                    for class_features in data['class_features'].values():
                        feature_count += len(class_features.get('features', []))
                feature_count += len(data.get('racial_traits', []))
                feature_count += len(data.get('feats', []))
                print(f"   ⭐ Features: {feature_count} total features and traits")
    else:
        print("❌ No data returned")
    
    print(f"   📊 Metadata: {result.metadata}")


def test_single_intentions():
    """Test individual user intentions."""
    print_section("TESTING SINGLE INTENTIONS")
    
    # Use the correct path for knowledge_base/saved_characters
    character_manager = CharacterManager("knowledge_base/saved_characters")
    character = character_manager.load_character("Duskryn Nightwarden")
    router = CharacterQueryRouter(character)
    character_name = "Duskryn Nightwarden"
    
    # Test core intentions based on the UserIntention enum
    test_intentions = [
        "character_basics",
        "ability_scores", 
        "combat_info",
        "inventory",
        "weapons",
        "spell_list",
        "spellcasting",
        "class_features",
        "racial_traits",
        "background_info",
        "personality",
        "backstory"
    ]
    
    for intention in test_intentions:
        try:
            result = router.query_character(
                user_intentions=[intention]
            )
            print_query_result(result, intention)
        except Exception as e:
            print(f"❌ Error testing {intention}: {str(e)}")


def test_entity_filtering():
    """Test entity filtering with specific items/spells."""
    print_section("TESTING ENTITY FILTERING")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    router = CharacterQueryRouter(character_manager)
    character_name = "Duskryn Nightwarden"
    
    # Test specific weapon queries
    weapon_entities = [
        {"name": "longsword", "type": "weapon"},
        {"name": "crossbow", "type": "weapon"}
    ]
    
    result = router.query_character(
        user_intentions=["weapons"],
        entities=weapon_entities
    )
    print_query_result(result, "weapons with specific entities")
    
    # Test specific spell queries
    spell_entities = [
        {"name": "eldritch blast", "type": "spell"},
        {"name": "hex", "type": "spell"},
        {"name": "armor of agathys", "type": "spell"}
    ]
    
    result = router.query_character(
        character_name=character_name,
        user_intention="spell_details",
        entities=spell_entities
    )
    print_query_result(result, "spell_details with specific entities")
    
    # Test magical items
    magic_item_entities = [
        {"name": "rod", "type": "item"},
        {"name": "cloak", "type": "item"}
    ]
    
    result = router.query_character(
        character_name=character_name,
        user_intention="magical_items",
        entities=magic_item_entities
    )
    print_query_result(result, "magical_items with specific entities")


def test_comprehensive_queries():
    """Test more comprehensive character queries."""
    print_section("TESTING COMPREHENSIVE QUERIES")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    router = CharacterQueryRouter(character_manager)
    character_name = "Duskryn Nightwarden"
    
    # Test full character sheet
    result = router.query_character(
        character_name=character_name,
        user_intention="full_character_sheet"
    )
    print_query_result(result, "full_character_sheet")
    
    # Test character summary
    result = router.query_character(
        character_name=character_name,
        user_intention="character_summary"
    )
    print_query_result(result, "character_summary")
    
    # Test action economy
    result = router.query_character(
        character_name=character_name,
        user_intention="action_economy"
    )
    print_query_result(result, "action_economy")


def test_advanced_features():
    """Test advanced character features."""
    print_section("TESTING ADVANCED FEATURES")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    router = CharacterQueryRouter(character_manager)
    character_name = "Duskryn Nightwarden"
    
    # Test movement and senses
    result = router.query_character(
        character_name=character_name,
        user_intention="movement_senses"
    )
    print_query_result(result, "movement_senses")
    
    # Test proficiencies
    result = router.query_character(
        character_name=character_name,
        user_intention="proficiencies"
    )
    print_query_result(result, "proficiencies")
    
    # Test passive abilities
    result = router.query_character(
        character_name=character_name,
        user_intention="passive_abilities"
    )
    print_query_result(result, "passive_abilities")
    
    # Test relationships
    result = router.query_character(
        character_name=character_name,
        user_intention="relationships"
    )
    print_query_result(result, "relationships")


def test_error_handling():
    """Test error handling and edge cases."""
    print_section("TESTING ERROR HANDLING")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    router = CharacterQueryRouter(character_manager)
    
    # Test unknown intention
    result = router.query_character(
        character_name="Duskryn Nightwarden",
        user_intention="unknown_intention"
    )
    print_query_result(result, "unknown_intention")
    
    # Test nonexistent character
    result = router.query_character(
        character_name="Nonexistent Character",
        user_intention="character_basics"
    )
    print_query_result(result, "nonexistent_character")


def run_comprehensive_test():
    """Run all tests."""
    print_section("CHARACTER QUERY ROUTER COMPREHENSIVE TEST", 
                  "Testing multiple intentions and entities for Duskryn Nightwarden")
    
    try:
        test_single_intentions()
        test_entity_filtering()
        test_comprehensive_queries()
        test_advanced_features()
        test_error_handling()
        
        print_section("TEST COMPLETE", "All tests finished successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


def detailed_data_inspection():
    """Inspect specific data structures returned."""
    print_section("DETAILED DATA INSPECTION")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    router = CharacterQueryRouter(character_manager)
    character_name = "Duskryn Nightwarden"
    
    # Get inventory details
    result = router.query_character(character_name, "inventory")
    if result.character_data.get('inventory'):
        inventory = result.character_data['inventory']
        print("\n🔍 INVENTORY DETAILS:")
        print(f"   Total Weight: {inventory.get('total_weight', 0)} {inventory.get('weight_unit', 'lbs')}")
        
        if inventory.get('equipped_items'):
            print("   Equipped Items:")
            for slot, items in inventory['equipped_items'].items():
                print(f"     {slot}: {len(items)} items")
                for item in items[:2]:  # Show first 2 items
                    print(f"       - {item.get('name', 'Unknown')} ({item.get('type', 'Unknown')})")
        
        if inventory.get('backpack'):
            print(f"   Backpack: {len(inventory['backpack'])} items")
            for item in inventory['backpack'][:3]:  # Show first 3 items
                print(f"     - {item.get('name', 'Unknown')} ({item.get('type', 'Unknown')})")
    
    # Get spell details
    result = router.query_character(character_name, "spell_list")
    if result.character_data.get('spell_list'):
        spell_data = result.character_data['spell_list']
        print("\n🔍 SPELL LIST DETAILS:")
        
        if spell_data.get('spellcasting'):
            print("   Spellcasting Classes:")
            for class_name, casting_info in spell_data['spellcasting'].items():
                print(f"     {class_name}:")
                print(f"       Spell Save DC: {casting_info.get('spell_save_dc', '?')}")
                print(f"       Spell Attack Bonus: +{casting_info.get('spell_attack_bonus', '?')}")
                print(f"       Spellcasting Ability: {casting_info.get('ability', '?')}")
        
        if spell_data.get('spells'):
            print("   Spells by Level:")
            for class_name, class_spells in spell_data['spells'].items():
                print(f"     {class_name}:")
                for level, spells in class_spells.items():
                    print(f"       {level}: {len(spells)} spells")
                    for spell in spells[:2]:  # Show first 2 spells per level
                        print(f"         - {spell.get('name', 'Unknown')} ({spell.get('school', 'Unknown')})")


def test_edge_cases():
    """Test edge cases for entity matching."""
    print_section("TESTING EDGE CASES")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    router = CharacterQueryRouter(character_manager)
    character_name = "Duskryn Nightwarden"
    
    # Test partial spell names
    result = router.query_character(
        character_name,
        "spell_details",
        entities=[{"name": "eldritch", "type": "spell"}]  # Partial name
    )
    print_query_result(result, "partial spell name 'eldritch'")
    
    # Test case variations
    result = router.query_character(
        character_name,
        "weapons", 
        entities=[{"name": "LONGSWORD", "type": "WEAPON"}]  # All caps
    )
    print_query_result(result, "case variation 'LONGSWORD'")
    
    # Test common misspellings
    result = router.query_character(
        character_name,
        "spell_details",
        entities=[{"name": "eldrich blast", "type": "spell"}]  # Misspelling
    )
    print_query_result(result, "misspelling 'eldrich blast'")
    
    # Test fuzzy matching with Rod
    result = router.query_character(
        character_name,
        "magical_items",
        entities=[{"name": "pact keeper", "type": "rod"}]  # Partial item name
    )
    print_query_result(result, "fuzzy match 'pact keeper'")
    
    # Test type-only matching
    result = router.query_character(
        character_name,
        "weapons",
        entities=[{"type": "weapon"}]  # Type only, no name
    )
    print_query_result(result, "type-only match 'weapon'")
    
    # Test very specific item name
    result = router.query_character(
        character_name,
        "weapons",
        entities=[{"name": "Eldaryth of Regret", "type": "weapon"}]  # Exact name
    )
    print_query_result(result, "exact match 'Eldaryth of Regret'")


if __name__ == "__main__":
    run_comprehensive_test()
    test_edge_cases()
    detailed_data_inspection()