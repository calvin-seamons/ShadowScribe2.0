#!/usr/bin/env python3
"""
Export Character to JSON

This script parses a D&D Beyond JSON export using CharacterBuilder and saves
the resulting Character object as a JSON file in the knowledge base source folder.

Usage:
    python -m scripts.export_character_to_json
    python -m scripts.export_character_to_json --input path/to/dndbeyond.json
    python -m scripts.export_character_to_json --output custom_name.json
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import asdict, is_dataclass
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.character_creation.character_builder import CharacterBuilder
from src.rag.character.character_types import Character


def dataclass_to_dict(obj: Any) -> Any:
    """
    Recursively convert dataclass objects to dictionaries for JSON serialization.
    
    Handles nested dataclasses, lists, dicts, and datetime objects.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable dictionary representation
    """
    if is_dataclass(obj):
        # Convert dataclass to dict, then recursively process nested objects
        return {
            key: dataclass_to_dict(value)
            for key, value in asdict(obj).items()
        }
    elif isinstance(obj, dict):
        return {key: dataclass_to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # For other types, try to convert to string
        return str(obj)


def character_to_json(character: Character, indent: int = 2) -> str:
    """
    Convert a Character object to JSON string.
    
    Args:
        character: Character object to serialize
        indent: Number of spaces for JSON indentation (default 2)
        
    Returns:
        JSON string representation of the character
    """
    character_dict = dataclass_to_dict(character)
    return json.dumps(character_dict, indent=indent, ensure_ascii=False)


def main():
    """Main function for script execution."""
    parser = argparse.ArgumentParser(
        description="Parse D&D Beyond JSON and export Character as JSON to knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default DNDBEYONDEXAMPLE.json
  python -m scripts.export_character_to_json
  
  # Use custom input file
  python -m scripts.export_character_to_json --input path/to/character.json
  
  # Specify custom output filename
  python -m scripts.export_character_to_json --output my_character.json
  
  # Save to saved_characters folder instead
  python -m scripts.export_character_to_json --destination saved_characters
        """
    )
    parser.add_argument(
        "--input",
        default="DNDBEYONDEXAMPLE.json",
        help="Path to D&D Beyond JSON export file (default: DNDBEYONDEXAMPLE.json)"
    )
    parser.add_argument(
        "--output",
        help="Output filename (default: derived from character name)"
    )
    parser.add_argument(
        "--destination",
        choices=["knowledge_base", "saved_characters"],
        default="knowledge_base",
        help="Destination folder (default: knowledge_base/source)"
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation spaces (default: 2)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress character build output"
    )
    
    args = parser.parse_args()
    
    try:
        # Resolve input file path
        input_path = Path(args.input)
        if not input_path.is_absolute():
            input_path = project_root / input_path
        
        if not input_path.exists():
            print(f"❌ Error: Input file not found: {input_path}")
            sys.exit(1)
        
        print(f"📖 Reading D&D Beyond JSON: {input_path.name}")
        
        # Build character from JSON
        if not args.quiet:
            print()
        
        # Temporarily redirect stdout if quiet mode
        if args.quiet:
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
        
        try:
            character = CharacterBuilder.from_json_file(str(input_path))
        finally:
            if args.quiet:
                sys.stdout = old_stdout
        
        # Determine output path
        if args.destination == "knowledge_base":
            output_dir = project_root / "knowledge_base" / "source"
        else:
            output_dir = project_root / "knowledge_base" / "saved_characters"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine output filename
        if args.output:
            output_filename = args.output
        else:
            # Derive from character name
            char_name = character.character_base.name.replace(" ", "_")
            output_filename = f"{char_name}_parsed.json"
        
        output_path = output_dir / output_filename
        
        print(f"\n💾 Converting Character to JSON...")
        
        # Convert to JSON
        json_output = character_to_json(character, indent=args.indent)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_output)
        
        # Calculate file size
        file_size_kb = output_path.stat().st_size / 1024
        
        print(f"✅ Character exported successfully!")
        print(f"\n📄 Output Details:")
        print(f"   Location: {output_path}")
        print(f"   File size: {file_size_kb:.2f} KB")
        print(f"\n📊 Character Summary:")
        print(f"   Name: {character.character_base.name}")
        print(f"   Race: {character.character_base.race}")
        print(f"   Class: {character.character_base.character_class}")
        print(f"   Level: {character.character_base.total_level}")
        
        # Count data sections
        sections = []
        if character.inventory:
            sections.append("inventory")
        if character.spell_list:
            sections.append("spells")
        if character.features_and_traits:
            sections.append("features")
        if character.action_economy:
            sections.append("actions")
        
        print(f"   Data sections: {', '.join(sections)}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in input file: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: An unexpected error occurred: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
