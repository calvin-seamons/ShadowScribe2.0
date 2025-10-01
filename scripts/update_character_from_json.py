#!/usr/bin/env python3
"""
Update Character from JSON

Updates the main character pickle file used by the RAG system from a D&D Beyond JSON export.
This script uses CharacterBuilder to parse the JSON and save it to the correct location.

Usage:
    python -m scripts.update_character_from_json <path_to_dndbeyond_json>
    
    # With custom character name
    python -m scripts.update_character_from_json <path_to_dndbeyond_json> --name "Custom Name"
    
Example:
    python -m scripts.update_character_from_json knowledge_base/legacy_json/Duskryn_Nightwarden/character.json
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.character_creation.character_builder import CharacterBuilder
from src.utils.character_manager import CharacterManager


def update_character_from_json(json_path: str, character_name: str = None):
    """
    Update the main character from a D&D Beyond JSON file.
    
    Args:
        json_path: Path to D&D Beyond JSON export file
        character_name: Optional custom character name (overrides name in JSON)
    """
    print("=" * 80)
    print("🔄 CHARACTER UPDATE SCRIPT")
    print("=" * 80)
    print(f"📄 Source JSON: {json_path}")
    
    # Build character from JSON
    print("\n🏗️  Building character from JSON...")
    try:
        character = CharacterBuilder.from_json_file(json_path)
    except FileNotFoundError:
        print(f"❌ Error: JSON file not found: {json_path}")
        return False
    except Exception as e:
        print(f"❌ Error building character: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Override character name if provided
    if character_name:
        print(f"\n📝 Overriding character name to: {character_name}")
        character.character_base.name = character_name
    
    # Save character
    print(f"\n💾 Saving character to knowledge base...")
    manager = CharacterManager(save_directory="knowledge_base/saved_characters")
    
    try:
        saved_path = manager.save_character(character)
        print(f"✅ Character saved successfully!")
        print(f"📍 Location: {saved_path}")
        
        # Show what was saved
        print(f"\n📊 Character Summary:")
        print(f"   • Name: {character.character_base.name}")
        print(f"   • Race: {character.character_base.race}")
        print(f"   • Class: {character.character_base.character_class}")
        print(f"   • Level: {character.character_base.total_level}")
        print(f"   • Background: {character.character_base.background}")
        
        if character.spell_list:
            total_spells = sum(
                len(spells)
                for class_spells in character.spell_list.spells.values()
                for spells in class_spells.values()
            )
            print(f"   • Spells: {total_spells}")
        
        if character.inventory:
            total_items = (
                sum(len(items) for items in character.inventory.equipped_items.values()) +
                len(character.inventory.backpack)
            )
            print(f"   • Inventory Items: {total_items}")
        
        print(f"\n🎯 This character is now ready for use in the RAG system!")
        print(f"   The demo will automatically load: {character.character_base.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving character: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Update character pickle file from D&D Beyond JSON export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update from JSON file (uses name from JSON)
  python -m scripts.update_character_from_json data/character.json
  
  # Update with custom name
  python -m scripts.update_character_from_json data/character.json --name "Duskryn Nightwarden"
  
  # Update from legacy JSON
  python -m scripts.update_character_from_json knowledge_base/legacy_json/Duskryn_Nightwarden/character.json
        """
    )
    
    parser.add_argument(
        'json_path',
        help='Path to D&D Beyond JSON export file'
    )
    
    parser.add_argument(
        '--name',
        help='Override character name (optional)',
        default=None
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate file exists
    json_file = Path(args.json_path)
    if not json_file.exists():
        print(f"❌ Error: File not found: {args.json_path}")
        sys.exit(1)
    
    # Update character
    success = update_character_from_json(args.json_path, args.name)
    
    if success:
        print("\n" + "=" * 80)
        print("✅ UPDATE COMPLETE!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ UPDATE FAILED!")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
