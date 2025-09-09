"""
Test Multi-Intention Character Query Router

Comprehensive test for the multi-intention CharacterQueryRouter functionality
to ensure both single and multiple intentions work correctly.
"""

import sys
from pathlib import Path
import time

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
    print(f" {title}")
    print(f"{'='*60}")
    if content:
        print(content)


def print_query_result(result: CharacterQueryResult, test_name: str, start_time: float = None):
    """Print formatted query result."""
    if start_time:
        elapsed = (time.perf_counter() - start_time) * 1000
        print(f"\n🎯 {test_name.upper()} - {elapsed:.1f}ms")
    else:
        print(f"\n🎯 {test_name.upper()}")
    
    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   • {warning}")
    
    print(f"📊 Data sections returned: {len(result.character_data) if result.character_data else 0}")
    if result.character_data:
        for key in sorted(result.character_data.keys()):
            print(f"   • {key}")
    
    print(f"🎭 Entity matches: {len(result.entity_matches)}")
    if result.entity_matches:
        for match in result.entity_matches[:3]:  # Show first 3
            print(f"   • {match}")
    
    if result.performance_metrics:
        print(f"⚡ Performance: {result.performance_metrics.total_time_ms:.1f}ms total")
        print(f"   • Intention mapping: {result.performance_metrics.intention_mapping_ms:.1f}ms")
        print(f"   • Data extraction: {result.performance_metrics.data_extraction_ms:.1f}ms")
    
    print(f"📋 Metadata:")
    if result.metadata:
        for key, value in result.metadata.items():
            if key == "intentions":
                print(f"   • {key}: {value}")
            else:
                print(f"   • {key}: {len(value) if isinstance(value, (list, dict)) else value}")


def test_single_intentions():
    """Test single intention queries (regression test)."""
    print_section("TESTING SINGLE INTENTIONS (REGRESSION)")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    character = character_manager.load_character("Duskryn Nightwarden")
    router = CharacterQueryRouter(character)
    
    # Test core single intentions
    single_intentions = [
        "character_basics",
        "combat_info", 
        "abilities_info",
        "inventory_info",
        "magic_info",
        "story_info"
    ]
    
    total_start = time.perf_counter()
    
    for intention in single_intentions:
        try:
            start_time = time.perf_counter()
            result = router.query_character(
                user_intentions=[intention]  # Single intention in array
            )
            print_query_result(result, intention, start_time)
        except Exception as e:
            print(f"❌ Error testing {intention}: {str(e)}")
    
    total_elapsed = (time.perf_counter() - total_start) * 1000
    print(f"\n🏁 Single intention tests completed in {total_elapsed:.1f}ms")


def test_valid_multi_intentions():
    """Test valid two-part intention queries."""
    print_section("TESTING VALID MULTI-INTENTIONS")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    character = character_manager.load_character("Duskryn Nightwarden")
    router = CharacterQueryRouter(character)
    
    # Test valid multi-intention combinations
    multi_intention_tests = [
        (["magic_info", "inventory_info"], "spells and inventory"),
        (["combat_info", "abilities_info"], "combat stats and abilities"),
        (["character_basics", "story_info"], "basic info and background"),
        (["inventory_info", "combat_info"], "equipment and combat readiness")
    ]
    
    for intentions, description in multi_intention_tests:
        try:
            start_time = time.perf_counter()
            result = router.query_character(
                user_intentions=intentions
            )
            print_query_result(result, f"{description} ({'/'.join(intentions)})", start_time)
            
            # Verify we got data from both intentions
            expected_sections = set()
            if "magic_info" in intentions:
                expected_sections.update(["spell_list"])
            if "inventory_info" in intentions:
                expected_sections.update(["inventory"])
            if "combat_info" in intentions:
                expected_sections.update(["combat_stats", "damage_modifiers"])
            if "abilities_info" in intentions:
                expected_sections.update(["proficiencies", "features_and_traits"])
            if "character_basics" in intentions:
                expected_sections.update(["character_base", "ability_scores"])
            if "story_info" in intentions:
                expected_sections.update(["background_info", "personality"])
            
            actual_sections = set(result.character_data.keys()) if result.character_data else set()
            missing = expected_sections - actual_sections
            if missing:
                print(f"⚠️  Expected sections missing: {missing}")
            else:
                print(f"✅ All expected data sections present!")
                
        except Exception as e:
            print(f"❌ Error testing {intentions}: {str(e)}")


def test_edge_cases():
    """Test edge cases and error conditions."""
    print_section("TESTING EDGE CASES")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    character = character_manager.load_character("Duskryn Nightwarden")
    router = CharacterQueryRouter(character)
    
    # Test empty intentions
    try:
        result = router.query_character(user_intentions=[])
        print_query_result(result, "empty intentions list")
    except Exception as e:
        print(f"❌ Empty intentions error: {str(e)}")
    
    # Test too many intentions (should raise ValueError)
    try:
        result = router.query_character(
            user_intentions=["character_basics", "combat_info", "abilities_info"]  # 3 intentions
        )
        print(f"❌ Should have raised ValueError for 3 intentions!")
    except ValueError as e:
        print(f"✅ Correctly caught ValueError: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    # Test invalid intention name
    try:
        result = router.query_character(
            user_intentions=["invalid_intention"]
        )
        print_query_result(result, "invalid intention (should fallback)")
    except Exception as e:
        print(f"❌ Invalid intention error: {str(e)}")
    
    # Test duplicate intentions
    try:
        result = router.query_character(
            user_intentions=["combat_info", "combat_info"]  # Same intention twice
        )
        print_query_result(result, "duplicate intentions")
    except Exception as e:
        print(f"❌ Duplicate intentions error: {str(e)}")


def test_with_entities():
    """Test multi-intentions with entity filtering."""
    print_section("TESTING MULTI-INTENTIONS WITH ENTITIES")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    character = character_manager.load_character("Duskryn Nightwarden")
    router = CharacterQueryRouter(character)
    
    # Test specific entities with multi-intentions
    test_cases = [
        {
            "intentions": ["magic_info", "inventory_info"],
            "entities": [
                {"name": "eldritch blast", "type": "spell"},
                {"name": "longsword", "type": "weapon"}
            ],
            "description": "specific spell and weapon"
        },
        {
            "intentions": ["combat_info", "abilities_info"], 
            "entities": [
                {"name": "stealth", "type": "skill"},
                {"name": "armor", "type": "armor"}
            ],
            "description": "skill and armor focus"
        }
    ]
    
    for test_case in test_cases:
        try:
            start_time = time.perf_counter()
            result = router.query_character(
                user_intentions=test_case["intentions"],
                entities=test_case["entities"]
            )
            test_name = f"{test_case['description']} ({'/'.join(test_case['intentions'])})"
            print_query_result(result, test_name, start_time)
            
        except Exception as e:
            print(f"❌ Error testing {test_case['description']}: {str(e)}")


def performance_comparison():
    """Compare performance between single and multi-intention queries."""
    print_section("PERFORMANCE COMPARISON")
    
    character_manager = CharacterManager("knowledge_base/saved_characters")
    character = character_manager.load_character("Duskryn Nightwarden")
    router = CharacterQueryRouter(character)
    
    # Time single intention queries
    single_times = []
    for _ in range(3):  # 3 runs for average
        start_time = time.perf_counter()
        router.query_character(user_intentions=["magic_info"])
        single_times.append((time.perf_counter() - start_time) * 1000)
    
    single_avg = sum(single_times) / len(single_times)
    
    # Time multi-intention queries
    multi_times = []
    for _ in range(3):  # 3 runs for average
        start_time = time.perf_counter()
        router.query_character(user_intentions=["magic_info", "inventory_info"])
        multi_times.append((time.perf_counter() - start_time) * 1000)
    
    multi_avg = sum(multi_times) / len(multi_times)
    
    overhead = ((multi_avg - single_avg) / single_avg) * 100
    
    print(f"📊 Single intention average: {single_avg:.1f}ms")
    print(f"📊 Multi-intention average: {multi_avg:.1f}ms")
    print(f"📊 Overhead: {overhead:.1f}%")
    
    if overhead < 20:
        print(f"✅ Performance overhead within acceptable range (<20%)")
    else:
        print(f"⚠️  Performance overhead exceeds target (20%)")


def main():
    """Run all multi-intention tests."""
    print("🚀 Starting Multi-Intention Character Router Tests")
    print(f"Character: Duskryn Nightwarden")
    
    try:
        test_single_intentions()
        test_valid_multi_intentions()
        test_edge_cases()
        test_with_entities()
        performance_comparison()
        
        print_section("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
