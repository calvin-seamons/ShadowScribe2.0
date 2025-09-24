#!/usr/bin/env python3
"""
Script to extract inventory items from D&D Beyond JSON export.

This script creates InventoryItem objects from the character JSON and outputs them to a JSON file.
"""

import json
import sys
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CleanedModifier:
    """Cleaned modifier with only essential fields."""
    type: Optional[str] = None
    subType: Optional[str] = None
    restriction: Optional[str] = None
    friendlyTypeName: Optional[str] = None
    friendlySubtypeName: Optional[str] = None
    duration: Optional[Dict[str, Any]] = None
    fixedValue: Optional[int] = None
    diceString: Optional[str] = None


@dataclass
class CleanedLimitedUse:
    """Cleaned limited use with only static fields."""
    maxUses: Optional[int] = None
    resetType: Optional[str] = None
    resetTypeDescription: Optional[str] = None


@dataclass
class CleanedInventoryItemDefinition:
    """Cleaned definition with only desired fields."""
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    canAttune: Optional[bool] = None
    attunementDescription: Optional[str] = None
    rarity: Optional[str] = None
    weight: Optional[Union[int, float]] = None
    capacity: Optional[str] = None
    capacityWeight: Optional[int] = None
    canEquip: Optional[bool] = None
    magic: Optional[bool] = None
    tags: Optional[List[str]] = None
    grantedModifiers: Optional[List[CleanedModifier]] = None
    damage: Optional[Dict[str, Any]] = None
    damageType: Optional[str] = None
    attackType: Optional[int] = None
    range: Optional[int] = None
    longRange: Optional[int] = None
    isContainer: Optional[bool] = None
    isCustomItem: Optional[bool] = None


@dataclass
class CleanedInventoryItem:
    """Cleaned item with only desired fields."""
    definition: CleanedInventoryItemDefinition
    quantity: int
    isAttuned: bool
    equipped: bool
    limitedUse: Optional[CleanedLimitedUse] = None


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file and return the data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{file_path}': {e}")
        sys.exit(1)


def extract_inventory_items(data: Dict[str, Any]) -> List[CleanedInventoryItem]:
    """Extract and clean inventory items from the JSON data."""
    items = []
    
    # Access inventory under data key
    if 'data' not in data or 'inventory' not in data['data']:
        print("No 'inventory' key found in JSON data")
        return items
    
    inventory = data['data']['inventory']
    if not isinstance(inventory, list):
        print("Inventory is not a list")
        return items
    
    for item_data in inventory:
        # Extract and clean definition fields
        def_data = item_data.get('definition', {})
        
        # Clean granted modifiers
        granted_modifiers = []
        if def_data.get('grantedModifiers'):
            for mod in def_data['grantedModifiers']:
                dice = mod.get('dice', {})
                cleaned_mod = CleanedModifier(
                    type=mod.get('type'),
                    subType=mod.get('subType'),
                    restriction=mod.get('restriction'),
                    friendlyTypeName=mod.get('friendlyTypeName'),
                    friendlySubtypeName=mod.get('friendlySubtypeName'),
                    duration=mod.get('duration'),
                    fixedValue=mod.get('fixedValue'),
                    diceString=dice.get('diceString') if dice else None
                )
                # Only add if it has meaningful data
                if any(getattr(cleaned_mod, field) is not None for field in cleaned_mod.__dataclass_fields__):
                    granted_modifiers.append(cleaned_mod)
        
        # Clean description
        description = def_data.get('description')
        if description:
            description = clean_html(description)
        
        definition = CleanedInventoryItemDefinition(
            name=def_data.get('name'),
            type=def_data.get('type'),
            description=description,
            canAttune=def_data.get('canAttune'),
            attunementDescription=def_data.get('attunementDescription'),
            rarity=def_data.get('rarity'),
            weight=def_data.get('weight'),
            capacity=def_data.get('capacity'),
            capacityWeight=def_data.get('capacityWeight'),
            canEquip=def_data.get('canEquip'),
            magic=def_data.get('magic'),
            tags=def_data.get('tags'),
            grantedModifiers=granted_modifiers if granted_modifiers else None,
            damage=def_data.get('damage'),
            damageType=def_data.get('damageType'),
            attackType=def_data.get('attackType'),
            range=def_data.get('range'),
            longRange=def_data.get('longRange'),
            isContainer=def_data.get('isContainer'),
            isCustomItem=def_data.get('isCustomItem')
        )
        
        # Clean limited use
        limited_use = None
        if item_data.get('limitedUse'):
            lu = item_data['limitedUse']
            limited_use = CleanedLimitedUse(
                maxUses=lu.get('maxUses'),
                resetType=lu.get('resetType'),
                resetTypeDescription=lu.get('resetTypeDescription')
            )
            # Only keep if it has meaningful data
            if not any(getattr(limited_use, field) is not None for field in limited_use.__dataclass_fields__):
                limited_use = None
        
        # Create CleanedInventoryItem
        item = CleanedInventoryItem(
            definition=definition,
            quantity=item_data.get('quantity', 1),
            isAttuned=item_data.get('isAttuned', False),
            equipped=item_data.get('equipped', False),
            limitedUse=limited_use
        )
        
        items.append(item)
    
    # Merge items with same name and description
    merged_items = {}
    for item in items:
        key = (item.definition.name, item.definition.description)
        if key in merged_items:
            merged_items[key].quantity += item.quantity
            # For other fields, keep the first one (assuming they are the same)
        else:
            merged_items[key] = item
    
    return list(merged_items.values())


def clean_html(text: str) -> str:
    """Clean HTML tags and formatting from text."""
    if not text:
        return text
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up extra whitespace and line breaks
    text = re.sub(r'\r\n', ' ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def should_include_field(key: str, value: Any) -> bool:
    """Determine if a field should be included in the output."""
    # Always exclude null values
    if value is None:
        return False
    
    # Exclude zero values for certain fields
    if key in ['weight', 'capacityWeight'] and value == 0:
        return False
    
    # Exclude empty strings
    if isinstance(value, str) and value.strip() == "":
        return False
    
    # Exclude empty lists
    if isinstance(value, list) and len(value) == 0:
        return False
    
    return True


def save_inventory_to_json(items: List[CleanedInventoryItem], output_file: str):
    """Save the cleaned inventory items to a JSON file."""
    # Convert dataclasses to dictionaries, filtering out None and unwanted values
    def dataclass_to_dict(obj, field_name=None):
        if obj is None:
            return None
        if isinstance(obj, list):
            return [dataclass_to_dict(item) for item in obj if item is not None]
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field in obj.__dataclass_fields__:
                value = getattr(obj, field)
                if should_include_field(field, value):
                    result[field] = dataclass_to_dict(value, field)
            return result
        return obj
    
    items_dict = [dataclass_to_dict(item) for item in items]
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(items_dict, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(items)} cleaned inventory items to {output_file}")
    except Exception as e:
        print(f"Error saving to file: {e}")


def main():
    """Main function."""
    if len(sys.argv) != 3:
        print("Usage: python validate_inventory.py <input_json_file> <output_json_file>")
        print("Example: python validate_inventory.py DNDBEYONDEXAMPLE.json inventory_output.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Loading JSON file: {input_file}")
    data = load_json_file(input_file)

    print("Extracting inventory items...")
    items = extract_inventory_items(data)

    print(f"Found {len(items)} inventory items")
    
    if len(items) != 37:
        print(f"Note: After merging duplicates, found {len(items)} unique items")

    print(f"Saving to {output_file}...")
    save_inventory_to_json(items, output_file)


if __name__ == "__main__":
    main()