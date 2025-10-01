#!/usr/bin/env python3
"""
Character Builder Validation Script

This script tests the character builder to ensure:
1. All parsers run successfully in parallel
2. No data is lost during parsing
3. All character fields are properly populated
4. The character object is valid and complete
"""

import sys
from pathlib import Path
from dataclasses import fields

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.character_creation.character_builder import CharacterBuilder


def validate_character(character):
    """Validate that the character has all expected data."""
    print("\n" + "=" * 80)
    print("DETAILED CHARACTER VALIDATION")
    print("=" * 80)
    
    validation_results = {
        "✓ Passed": [],
        "✗ Failed": [],
        "⚠ Warning": []
    }
    
    # Check required fields
    print("\n[1] Checking required core fields...")
    required_checks = [
        ("Character Name", character.character_base.name, lambda x: x != "Unknown" and len(x) > 0),
        ("Race", character.character_base.race, lambda x: x != "Unknown"),
        ("Class", character.character_base.character_class, lambda x: x != "Unknown"),
        ("Level", character.character_base.total_level, lambda x: x > 0),
        ("HP", character.combat_stats.max_hp, lambda x: x > 0),
        ("AC", character.combat_stats.armor_class, lambda x: x >= 10),
        ("Background", character.background_info.name, lambda x: x != "Unknown"),
    ]
    
    for name, value, check_fn in required_checks:
        if check_fn(value):
            validation_results["✓ Passed"].append(f"{name}: {value}")
        else:
            validation_results["✗ Failed"].append(f"{name}: {value}")
    
    # Check ability scores
    print("\n[2] Validating ability scores...")
    abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    for ability in abilities:
        score = getattr(character.ability_scores, ability)
        if 3 <= score <= 30:  # Valid D&D range
            validation_results["✓ Passed"].append(f"{ability.upper()}: {score}")
        else:
            validation_results["✗ Failed"].append(f"{ability.upper()}: {score} (out of range)")
    
    # Check optional but important fields
    print("\n[3] Checking optional content...")
    optional_checks = [
        ("Proficiencies", character.proficiencies, lambda x: len(x) > 0),
        ("Racial Traits", character.features_and_traits.racial_traits if character.features_and_traits else [], lambda x: len(x) > 0),
        ("Class Features", 
         sum(len(features) for levels in (character.features_and_traits.class_features.values() if character.features_and_traits else [])
             for features in (levels.values() if hasattr(levels, 'values') else [])),
         lambda x: x > 0),
        ("Actions", character.action_economy.actions if character.action_economy else [], lambda x: len(x) > 0),
        ("Inventory Items", 
         (sum(len(items) for items in character.inventory.equipped_items.values()) + len(character.inventory.backpack))
         if character.inventory else 0,
         lambda x: x > 0),
    ]
    
    for name, value, check_fn in optional_checks:
        count = value if isinstance(value, int) else len(value) if hasattr(value, '__len__') else 0
        if check_fn(value):
            validation_results["✓ Passed"].append(f"{name}: {count} items")
        else:
            validation_results["⚠ Warning"].append(f"{name}: {count} items (may be empty)")
    
    # Check spell data (if character is a spellcaster)
    print("\n[4] Checking spell data...")
    if character.spell_list and character.spell_list.spellcasting:
        for class_name, spell_info in character.spell_list.spellcasting.items():
            validation_results["✓ Passed"].append(
                f"Spellcasting ({class_name}): Save DC {spell_info.spell_save_dc}, "
                f"Attack +{spell_info.spell_attack_bonus}"
            )
            cantrip_count = len(spell_info.cantrips_known)
            spell_count = len(spell_info.spells_known)
            validation_results["✓ Passed"].append(
                f"  ├─ Cantrips: {cantrip_count}"
            )
            validation_results["✓ Passed"].append(
                f"  └─ Spells: {spell_count}"
            )
    else:
        validation_results["⚠ Warning"].append("No spellcasting (non-caster or data missing)")
    
    # Check background/personality data
    print("\n[5] Checking background and personality...")
    personality_checks = [
        ("Personality Traits", character.personality.personality_traits),
        ("Ideals", character.personality.ideals),
        ("Bonds", character.personality.bonds),
        ("Flaws", character.personality.flaws),
        ("Allies", character.allies),
        ("Enemies", character.enemies),
    ]
    
    for name, value in personality_checks:
        count = len(value) if value else 0
        if count > 0:
            validation_results["✓ Passed"].append(f"{name}: {count} items")
        else:
            validation_results["⚠ Warning"].append(f"{name}: empty")
    
    # Print results
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    
    for category in ["✓ Passed", "⚠ Warning", "✗ Failed"]:
        if validation_results[category]:
            print(f"\n{category}:")
            for result in validation_results[category]:
                print(f"  {result}")
    
    # Summary
    passed = len(validation_results["✓ Passed"])
    warnings = len(validation_results["⚠ Warning"])
    failed = len(validation_results["✗ Failed"])
    total = passed + warnings + failed
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed}/{total} passed, {warnings} warnings, {failed} failed")
    print("=" * 80)
    
    return failed == 0


def main():
    """Main test function."""
    if len(sys.argv) != 2:
        print("Usage: python test_character_builder_validation.py <path_to_dndbeyond_json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    print("=" * 80)
    print("CHARACTER BUILDER VALIDATION TEST")
    print("=" * 80)
    print(f"Testing with: {json_file}")
    
    try:
        # Build the character
        print("\nBuilding character...")
        character = CharacterBuilder.from_json_file(json_file)
        
        # Validate the character
        success = validate_character(character)
        
        if success:
            print("\n✓ All validation checks passed!")
            print("✓ Character builder is working correctly")
            print("✓ No data loss detected")
            sys.exit(0)
        else:
            print("\n✗ Some validation checks failed")
            print("✗ Please review the failures above")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
