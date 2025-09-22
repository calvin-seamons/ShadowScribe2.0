#!/usr/bin/env python3
"""
D&D Beyond JSON Spell Parser

This script parses a D&D Beyond character JSON file and creates a complete SpellList object
according to the extraction paths defined in the character_types.py comments.

Features:
- Parses all spell sources (class, race, item, feat, background)
- Maps spellcasting ability IDs to ability names
- Calculates spell save DCs and attack bonuses
- Organizes spells by class and level
- Handles both regular spell slots and pact magic
- Outputs complete JSON representation of SpellList object
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field, asdict
import re
from html import unescape

# Import the character types
sys.path.append(str(Path(__file__).parent / "src"))
from rag.character.character_types import (
    SpellComponents, SpellRite, Spell, SpellcastingInfo, SpellList
)

# Ability ID to name mapping
ABILITY_ID_TO_NAME = {
    1: "strength",
    2: "dexterity", 
    3: "constitution",
    4: "intelligence",
    5: "wisdom",
    6: "charisma"
}

# Activation type mapping
ACTIVATION_TYPE_MAP = {
    1: "1 action",
    2: "1 bonus action",
    3: "1 reaction",
    4: "1 minute",
    5: "10 minutes",
    6: "1 hour",
    7: "8 hours",
    8: "no action"
}

# Duration unit mapping
DURATION_UNIT_MAP = {
    "Minute": "minute",
    "Hour": "hour", 
    "Day": "day",
    "Round": "round",
    "Turn": "turn",
    "Instantaneous": "instantaneous",
    "Permanent": "permanent"
}

# School name mapping (in case we get IDs)
SPELL_SCHOOL_MAP = {
    "Divination": "Divination",
    "Enchantment": "Enchantment",
    "Evocation": "Evocation",
    "Illusion": "Illusion",
    "Necromancy": "Necromancy",
    "Abjuration": "Abjuration",
    "Conjuration": "Conjuration",
    "Transmutation": "Transmutation"
}

def clean_html(text: str) -> str:
    """Clean HTML tags and decode HTML entities from text."""
    if not text:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    clean = unescape(clean)
    # Clean up extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def parse_spell_components(components: List[int], components_description: str = "") -> SpellComponents:
    """Parse spell components from component array and description."""
    # Component array: 1=verbal, 2=somatic, 3=material
    verbal = 1 in components
    somatic = 2 in components
    material = 3 in components
    
    # If material component, use description if available
    if material and components_description:
        material = components_description
    
    return SpellComponents(
        verbal=verbal,
        somatic=somatic,
        material=material
    )

def format_duration(duration_data: Dict[str, Any]) -> str:
    """Format duration from duration object."""
    if not duration_data:
        return "instantaneous"
    
    interval = duration_data.get("durationInterval", 1)
    unit = duration_data.get("durationUnit", "Instantaneous")
    duration_type = duration_data.get("durationType", "")
    
    # Handle None values
    if unit is None:
        unit = "Instantaneous"
    
    # Map unit to readable format
    unit_str = DURATION_UNIT_MAP.get(unit, unit.lower() if unit else "instantaneous")
    
    # Format duration string
    if unit == "Instantaneous":
        result = "instantaneous"
    elif interval == 1:
        result = f"1 {unit_str}"
    else:
        result = f"{interval} {unit_str}s"
    
    # Add concentration if applicable
    if duration_type == "Concentration":
        result = f"Concentration, up to {result}"
    
    return result

def format_casting_time(activation_data: Dict[str, Any]) -> str:
    """Format casting time from activation object."""
    if not activation_data:
        return "1 action"
    
    activation_time = activation_data.get("activationTime", 1)
    activation_type = activation_data.get("activationType", 1)
    
    # Get base time string
    time_str = ACTIVATION_TYPE_MAP.get(activation_type, "1 action")
    
    # Modify for non-standard activation times
    if activation_time != 1 and activation_type in [4, 5, 6, 7]:  # Minute, 10 min, hour, 8 hours
        if activation_type == 4:  # minutes
            return f"{activation_time} minute{'s' if activation_time > 1 else ''}"
        elif activation_type == 5:  # 10-minute intervals
            total_minutes = activation_time * 10
            return f"{total_minutes} minute{'s' if total_minutes > 1 else ''}"
        elif activation_type == 6:  # hours
            return f"{activation_time} hour{'s' if activation_time > 1 else ''}"
        elif activation_type == 7:  # 8-hour intervals
            total_hours = activation_time * 8
            return f"{total_hours} hour{'s' if total_hours > 1 else ''}"
    
    return time_str

def format_range(range_data: Dict[str, Any]) -> str:
    """Format range from range object."""
    if not range_data:
        return "touch"
    
    origin = range_data.get("origin", "Self")
    range_value = range_data.get("rangeValue", 0)
    aoe_type = range_data.get("aoeType")
    aoe_value = range_data.get("aoeValue")
    
    # Handle different range types
    if origin == "Self":
        if aoe_type and aoe_value and isinstance(aoe_type, str):
            return f"Self ({aoe_value}-foot {aoe_type.lower()})"
        return "Self"
    elif origin == "Touch":
        return "Touch"
    elif origin == "Sight":
        return "Sight"
    elif origin == "Ranged" and range_value:
        if aoe_type and aoe_value and isinstance(aoe_type, str):
            return f"{range_value} feet ({aoe_value}-foot {aoe_type.lower()})"
        return f"{range_value} feet"
    elif range_value:
        return f"{range_value} feet"
    
    return "touch"

def format_area(range_data: Dict[str, Any]) -> Optional[str]:
    """Extract area of effect from range data."""
    if not range_data:
        return None
    
    aoe_type = range_data.get("aoeType")
    aoe_value = range_data.get("aoeValue")
    
    if aoe_type and aoe_value and isinstance(aoe_type, str):
        return f"{aoe_value}-foot {aoe_type.lower()}"
    
    return None

def parse_spell_from_definition(spell_data: Dict[str, Any]) -> Spell:
    """Parse a spell from D&D Beyond spell data."""
    definition = spell_data.get("definition", {})
    
    # Basic spell info
    name = definition.get("name", "Unknown Spell")
    level = definition.get("level", 0)
    school = definition.get("school", "Unknown")
    
    # Handle None school values
    if school is None:
        school = "Unknown"
    school = SPELL_SCHOOL_MAP.get(school, school)
    
    # Casting info
    casting_time = format_casting_time(definition.get("activation", {}))
    range_str = format_range(definition.get("range", {}))
    duration = format_duration(definition.get("duration", {}))
    
    # Components
    components_list = definition.get("components", [])
    components_desc = definition.get("componentsDescription", "")
    components = parse_spell_components(components_list, components_desc)
    
    # Description
    description = clean_html(definition.get("description", ""))
    
    # Spell properties
    concentration = definition.get("concentration", False)
    ritual = definition.get("ritual", False) or spell_data.get("castOnlyAsRitual", False)
    
    # Tags
    tags = definition.get("tags", [])
    
    # Area of effect
    area = format_area(definition.get("range", {}))
    
    # Charges (for item spells)
    charges = spell_data.get("charges")
    
    return Spell(
        name=name,
        level=level,
        school=school,
        casting_time=casting_time,
        range=range_str,
        components=components,
        duration=duration,
        description=description,
        concentration=concentration,
        ritual=ritual,
        tags=tags,
        area=area,
        rites=None,  # D&D Beyond doesn't use rites
        charges=charges
    )

def calculate_proficiency_bonus(total_level: int) -> int:
    """Calculate proficiency bonus from total character level."""
    if total_level >= 17:
        return 6
    elif total_level >= 13:
        return 5
    elif total_level >= 9:
        return 4
    elif total_level >= 5:
        return 3
    else:
        return 2

def calculate_ability_modifier(score: int) -> int:
    """Calculate ability modifier from ability score."""
    return (score - 10) // 2

def get_ability_score(data: Dict[str, Any], ability_id: int) -> int:
    """Get ability score, checking overrides first."""
    # Check overrideStats first
    override_stats = data.get("overrideStats", [])
    for stat in override_stats:
        if stat.get("id") == ability_id and stat.get("value") is not None:
            return stat["value"]
    
    # Fall back to base stats
    stats = data.get("stats", [])
    for stat in stats:
        if stat.get("id") == ability_id:
            return stat.get("value", 10)
    
    return 10  # Default

def parse_spellcasting_info(class_data: Dict[str, Any], character_data: Dict[str, Any]) -> Optional[SpellcastingInfo]:
    """Parse spellcasting info for a class."""
    class_def = class_data.get("definition", {})
    
    # Check if class can cast spells
    if not class_def.get("canCastSpells", False):
        return None
    
    # Get spellcasting ability
    ability_id = class_def.get("spellCastingAbilityId")
    if not ability_id:
        return None
    
    ability_name = ABILITY_ID_TO_NAME.get(ability_id, "charisma")
    
    # Get ability score and calculate modifier
    ability_score = get_ability_score(character_data, ability_id)
    ability_modifier = calculate_ability_modifier(ability_score)
    
    # Calculate total level for proficiency bonus
    total_level = sum(cls.get("level", 1) for cls in character_data.get("classes", []))
    proficiency_bonus = calculate_proficiency_bonus(total_level)
    
    # Calculate save DC and attack bonus
    spell_save_dc = 8 + proficiency_bonus + ability_modifier
    spell_attack_bonus = proficiency_bonus + ability_modifier
    
    # Calculate spell slots based on class level and spell progression
    spell_slots = {}
    class_level = class_data.get("level", 1)
    
    # Get spell rules from class definition
    spell_rules = class_def.get("spellRules", {})
    level_spell_slots = spell_rules.get("levelSpellSlots", [])
    
    # Use the class level to get the correct spell slot array (index = level - 1)
    if class_level <= len(level_spell_slots):
        slot_array = level_spell_slots[class_level - 1]
        for slot_level, count in enumerate(slot_array, 1):
            if count > 0:  # Only include levels with available slots
                spell_slots[slot_level] = count
    
    # For Warlock, pact magic overrides regular spell slots
    class_name = class_def.get("name", "")
    if class_name.lower() == "warlock":
        # Warlock uses pact magic instead of regular spell slots
        spell_slots = {}
        
        # Warlock spell slot progression (based on level)
        warlock_slots = {
            1: {3: 1},   # Level 1: 1 3rd-level slot
            2: {3: 2},   # Level 2: 2 3rd-level slots  
            3: {3: 2},   # Level 3: 2 3rd-level slots
            4: {3: 2},   # Level 4: 2 3rd-level slots
            5: {3: 2},   # Level 5: 2 3rd-level slots
            6: {3: 2},   # Level 6: 2 3rd-level slots
            7: {4: 2},   # Level 7: 2 4th-level slots
            8: {4: 2},   # Level 8: 2 4th-level slots
            9: {4: 2},   # Level 9: 2 4th-level slots
            10: {4: 2},  # Level 10: 2 4th-level slots
            11: {5: 3},  # Level 11: 3 5th-level slots
            12: {5: 3},  # Level 12: 3 5th-level slots
            13: {5: 3},  # Level 13: 3 5th-level slots
            14: {5: 3},  # Level 14: 3 5th-level slots
            15: {5: 3},  # Level 15: 3 5th-level slots
            16: {5: 3},  # Level 16: 3 5th-level slots
            17: {5: 4},  # Level 17: 4 5th-level slots
            18: {5: 4},  # Level 18: 4 5th-level slots
            19: {5: 4},  # Level 19: 4 5th-level slots
            20: {5: 4},  # Level 20: 4 5th-level slots
        }
        
        if class_level in warlock_slots:
            spell_slots = warlock_slots[class_level]
    
    return SpellcastingInfo(
        ability=ability_name,
        spell_save_dc=spell_save_dc,
        spell_attack_bonus=spell_attack_bonus,
        cantrips_known=[],  # Will be filled later
        spells_known=[],    # Will be filled later
        spell_slots=spell_slots
    )

def organize_spells_by_level(spells: List[Spell]) -> Dict[str, List[Spell]]:
    """Organize spells by level using string keys."""
    level_map = {
        0: "cantrip",
        1: "1st_level",
        2: "2nd_level", 
        3: "3rd_level",
        4: "4th_level",
        5: "5th_level",
        6: "6th_level",
        7: "7th_level",
        8: "8th_level",
        9: "9th_level"
    }
    
    organized = {}
    for spell in spells:
        level_key = level_map.get(spell.level, f"{spell.level}th_level")
        if level_key not in organized:
            organized[level_key] = []
        organized[level_key].append(spell)
    
    return organized

def parse_dndbeyond_spelllist(json_file_path: str) -> SpellList:
    """Parse D&D Beyond JSON file and create SpellList object."""
    
    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract character data
    character_data = data.get("data", {})
    
    # Parse spellcasting info for each class
    spellcasting_info = {}
    classes = character_data.get("classes", [])
    
    # Create class ID to name mapping
    class_id_to_name = {}
    for class_data in classes:
        class_def = class_data.get("definition", {})
        class_name = class_def.get("name", "Unknown")
        class_id = class_data.get("id")  # This should be the character class instance ID, not definition ID
        if class_id:
            class_id_to_name[class_id] = class_name
        
        # Parse spellcasting info if class can cast spells
        spell_info = parse_spellcasting_info(class_data, character_data)
        if spell_info:
            spellcasting_info[class_name] = spell_info
    
    # Parse spells organized by class
    spells_by_class = {}
    
    # Get spells from classSpells section (most accurate for class organization)
    class_spells_data = character_data.get("classSpells", [])
    
    for class_spell_data in class_spells_data:
        character_class_id = class_spell_data.get("characterClassId")
        class_name = class_id_to_name.get(character_class_id, "Unknown")
        
        # Only process if this class can cast spells
        if class_name not in spellcasting_info:
            continue
        
        class_spells = []
        cantrips_known = []
        spells_known = []
        
        # Parse spells for this class
        spells_list = class_spell_data.get("spells", [])
        for spell_data in spells_list:
            try:
                spell = parse_spell_from_definition(spell_data)
                class_spells.append(spell)
                
                # Track spell names for spellcasting info
                if spell.level == 0:
                    cantrips_known.append(spell.name)
                else:
                    spells_known.append(spell.name)
                    
            except Exception as e:
                spell_name = "Unknown"
                try:
                    spell_name = spell_data.get("definition", {}).get("name", "Unknown")
                except:
                    pass
                print(f"Error parsing class spell '{spell_name}' for {class_name}: {e}")
                continue
        
        # Update spellcasting info with actual spell names
        if class_name in spellcasting_info:
            spellcasting_info[class_name].cantrips_known = cantrips_known
            spellcasting_info[class_name].spells_known = spells_known
        
        # Organize spells by level for this class
        if class_spells:
            spells_by_class[class_name] = organize_spells_by_level(class_spells)
    
    # Also parse spells from other sources (race, item, feat, background)
    other_spells = []
    spells_data = character_data.get("spells", {})
    
    for source in ["race", "item", "feat"]:
        source_spells = spells_data.get(source, [])
        for spell_data in source_spells:
            try:
                spell = parse_spell_from_definition(spell_data)
                other_spells.append(spell)
            except Exception as e:
                spell_name = "Unknown"
                try:
                    spell_name = spell_data.get("definition", {}).get("name", "Unknown")
                except:
                    pass
                print(f"Error parsing spell '{spell_name}' from {source}: {e}")
                continue
    
    # Background spells (may be null)
    bg_spells = spells_data.get("background")
    if bg_spells:
        for spell_data in bg_spells:
            try:
                spell = parse_spell_from_definition(spell_data)
                other_spells.append(spell)
            except Exception as e:
                spell_name = "Unknown"
                try:
                    spell_name = spell_data.get("definition", {}).get("name", "Unknown")
                except:
                    pass
                print(f"Error parsing background spell '{spell_name}': {e}")
                continue
    
    # Add other spells to the primary spellcasting class or create a separate category
    if other_spells and spellcasting_info:
        primary_class = list(spellcasting_info.keys())[0]
        
        # Add other spell names to spellcasting info
        for spell in other_spells:
            if spell.level == 0:
                if spell.name not in spellcasting_info[primary_class].cantrips_known:
                    spellcasting_info[primary_class].cantrips_known.append(spell.name)
            else:
                if spell.name not in spellcasting_info[primary_class].spells_known:
                    spellcasting_info[primary_class].spells_known.append(spell.name)
        
        # Merge other spells into class spell list
        other_spells_by_level = organize_spells_by_level(other_spells)
        
        if primary_class not in spells_by_class:
            spells_by_class[primary_class] = {}
        
        # Merge the spell levels
        for level, spells in other_spells_by_level.items():
            if level not in spells_by_class[primary_class]:
                spells_by_class[primary_class][level] = []
            spells_by_class[primary_class][level].extend(spells)
    
    return SpellList(
        spellcasting=spellcasting_info,
        spells=spells_by_class
    )

def main():
    """Main function to parse D&D Beyond JSON and output SpellList."""
    
    # Default file path
    json_file = "DNDBEYONDEXAMPLE.json"
    
    # Check if file exists
    if not Path(json_file).exists():
        print(f"Error: {json_file} not found in current directory")
        return
    
    try:
        # Parse the spell list
        print("Parsing D&D Beyond JSON file...")
        spell_list = parse_dndbeyond_spelllist(json_file)
        
        # Convert to dict for JSON serialization
        spell_list_dict = asdict(spell_list)
        
        # Output JSON
        output_file = "parsed_spelllist.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spell_list_dict, f, indent=2, ensure_ascii=False)
        
        print(f"SpellList object saved to {output_file}")
        
        # Print summary
        print("\n=== SPELL LIST SUMMARY ===")
        print(f"Spellcasting classes: {len(spell_list.spellcasting)}")
        
        for class_name, casting_info in spell_list.spellcasting.items():
            print(f"\n{class_name}:")
            print(f"  Spellcasting ability: {casting_info.ability}")
            print(f"  Spell save DC: {casting_info.spell_save_dc}")
            print(f"  Spell attack bonus: +{casting_info.spell_attack_bonus}")
            print(f"  Cantrips known: {len(casting_info.cantrips_known)}")
            print(f"  Spells known: {len(casting_info.spells_known)}")
            print(f"  Spell slots: {casting_info.spell_slots}")
        
        # Count spells by level
        total_spells = 0
        for class_name, levels in spell_list.spells.items():
            print(f"\n{class_name} spells by level:")
            for level, spells in levels.items():
                print(f"  {level}: {len(spells)} spells")
                total_spells += len(spells)
        
        print(f"\nTotal spells parsed: {total_spells}")
        
    except Exception as e:
        print(f"Error parsing spell list: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()