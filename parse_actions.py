#!/usr/bin/env python3
"""
D&D Beyond Actions Parser

This script parses a D&D Beyond character JSON export and extracts all possible non-spell actions
the character can perform, including attacks, special abilities, and item actions.

Usage:
    python parse_actions.py <path_to_json_file>
"""

import json
import sys
import re
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ActionActivation:
    """How an action is activated."""
    activationType: Optional[str] = None  # "action", "bonus_action", "reaction", etc.
    activationTime: Optional[int] = None  # Number of time units
    activationCondition: Optional[str] = None  # Special conditions for activation


@dataclass
class ActionUsage:
    """Usage limitations for an action."""
    maxUses: Optional[int] = None
    resetType: Optional[str] = None  # "short_rest", "long_rest", "dawn", etc.
    usesPerActivation: Optional[int] = None


@dataclass
class ActionRange:
    """Range information for an action."""
    range: Optional[int] = None  # Range in feet
    longRange: Optional[int] = None  # Long range in feet
    aoeType: Optional[str] = None  # Area of effect type
    aoeSize: Optional[int] = None  # AOE size in feet
    rangeDescription: Optional[str] = None  # Human-readable range


@dataclass
class ActionDamage:
    """Damage information for an action."""
    diceNotation: Optional[str] = None  # e.g., "1d8+3"
    damageType: Optional[str] = None  # "slashing", "fire", etc.
    fixedDamage: Optional[int] = None
    bonusDamage: Optional[str] = None
    criticalHitDice: Optional[str] = None


@dataclass
class ActionSave:
    """Saving throw information."""
    saveDC: Optional[int] = None
    saveAbility: Optional[str] = None  # "Dexterity", "Wisdom", etc.
    onSuccess: Optional[str] = None
    onFailure: Optional[str] = None


@dataclass
class CharacterAction:
    """A complete character action with all relevant information."""
    name: str
    description: Optional[str] = None
    shortDescription: Optional[str] = None  # Snippet or summary
    
    # Action mechanics
    activation: Optional[ActionActivation] = None
    usage: Optional[ActionUsage] = None
    actionRange: Optional[ActionRange] = None
    damage: Optional[ActionDamage] = None
    save: Optional[ActionSave] = None
    
    # Classification
    actionCategory: Optional[str] = None  # "attack", "feature", "item"
    source: Optional[str] = None  # "class", "race", "feat", "item", "spell"
    sourceFeature: Optional[str] = None  # Name of the feature/item granting this action
    
    # Combat details
    attackBonus: Optional[int] = None
    isWeaponAttack: bool = False
    requiresAmmo: bool = False
    
    # Special properties
    duration: Optional[str] = None
    materials: Optional[str] = None  # Required items or materials


class DNDBeyondActionsParser:
    """Parser for extracting all character actions from D&D Beyond JSON."""
    
    # Action type mappings
    ACTION_TYPE_MAP = {
        1: "action",
        2: "no_action", 
        3: "bonus_action",
        4: "reaction",
        5: "reaction",
        6: "reaction",
        7: "reaction",
        8: "no_action"
    }
    
    RESET_TYPE_MAP = {
        1: "short_rest",
        2: "long_rest",
        3: "dawn",
        4: "dusk",
        5: "recharge",
        6: "turn"
    }
    
    ABILITY_MAP = {
        1: "Strength",
        2: "Dexterity",
        3: "Constitution", 
        4: "Intelligence",
        5: "Wisdom",
        6: "Charisma"
    }
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize parser with D&D Beyond JSON data."""
        self.data = json_data.get("data", {})
        
    def clean_html_description(self, description: str) -> str:
        """Clean HTML tags and format text."""
        if not description:
            return ""
            
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', description)
        
        # Replace HTML entities
        replacements = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&nbsp;': ' ',
            '&rsquo;': "'", '&ldquo;': '"', '&rdquo;': '"'
        }
        for old, new in replacements.items():
            clean_text = clean_text.replace(old, new)
        
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def parse_activation(self, activation_data: Dict[str, Any], action_type: int) -> ActionActivation:
        """Parse activation information."""
        activation = ActionActivation()
        
        if action_type in self.ACTION_TYPE_MAP:
            activation.activationType = self.ACTION_TYPE_MAP[action_type]
        
        if activation_data:
            activation.activationTime = activation_data.get("activationTime")
        
        return activation
    
    def parse_usage(self, limited_use_data: Dict[str, Any]) -> Optional[ActionUsage]:
        """Parse usage limitations."""
        if not limited_use_data:
            return None
            
        max_uses = limited_use_data.get("maxUses")
        if not max_uses:
            return None
            
        usage = ActionUsage()
        usage.maxUses = max_uses
        
        reset_type = limited_use_data.get("resetType")
        if reset_type in self.RESET_TYPE_MAP:
            usage.resetType = self.RESET_TYPE_MAP[reset_type]
        
        usage.usesPerActivation = limited_use_data.get("minNumberConsumed", 1)
        
        return usage
    
    def parse_range(self, range_data: Dict[str, Any]) -> Optional[ActionRange]:
        """Parse range information."""
        if not range_data:
            return None
            
        action_range = ActionRange()
        action_range.range = range_data.get("range")
        action_range.longRange = range_data.get("longRange")
        action_range.aoeSize = range_data.get("aoeSize")
        
        # Convert AOE type
        aoe_type = range_data.get("aoeType")
        if aoe_type == 1:
            action_range.aoeType = "sphere"
        elif aoe_type == 2:
            action_range.aoeType = "cube"
        elif aoe_type == 3:
            action_range.aoeType = "cone"
        elif aoe_type == 4:
            action_range.aoeType = "line"
        
        # Build range description
        if action_range.range:
            action_range.rangeDescription = f"{action_range.range} feet"
            if action_range.longRange:
                action_range.rangeDescription += f" (long: {action_range.longRange} feet)"
        elif action_range.aoeType and action_range.aoeSize:
            action_range.rangeDescription = f"{action_range.aoeSize}-foot {action_range.aoeType}"
        
        return action_range if any(getattr(action_range, f) for f in action_range.__dataclass_fields__) else None
    
    def parse_damage(self, dice_data: Dict[str, Any], damage_type_id: int, fixed_value: int) -> Optional[ActionDamage]:
        """Parse damage information."""
        damage = ActionDamage()
        
        if dice_data and dice_data.get("diceString"):
            damage.diceNotation = dice_data["diceString"]
        elif fixed_value:
            damage.fixedDamage = fixed_value
        
        # Map damage type ID to name (simplified mapping)
        damage_types = {
            1: "bludgeoning", 2: "piercing", 3: "slashing", 4: "necrotic",
            5: "radiant", 6: "fire", 7: "cold", 8: "lightning", 9: "thunder",
            10: "poison", 11: "acid", 12: "psychic", 13: "force"
        }
        
        if damage_type_id in damage_types:
            damage.damageType = damage_types[damage_type_id]
        
        return damage if any(getattr(damage, f) for f in damage.__dataclass_fields__) else None
    
    def parse_save(self, save_dc: int, save_stat_id: int, success_desc: str, fail_desc: str) -> Optional[ActionSave]:
        """Parse saving throw information."""
        if not any([save_dc, save_stat_id, success_desc, fail_desc]):
            return None
            
        save = ActionSave()
        save.saveDC = save_dc
        
        if save_stat_id in self.ABILITY_MAP:
            save.saveAbility = self.ABILITY_MAP[save_stat_id]
        
        save.onSuccess = self.clean_html_description(success_desc) if success_desc else None
        save.onFailure = self.clean_html_description(fail_desc) if fail_desc else None
        
        return save
    
    def parse_basic_actions(self) -> List[CharacterAction]:
        """Parse actions from the actions section."""
        actions = []
        
        actions_data = self.data.get("actions", {})
        
        for category in ["race", "class", "background", "item", "feat"]:
            category_actions = actions_data.get(category, [])
            if not category_actions:
                continue
                
            for action_data in category_actions:
                action = CharacterAction(
                    name=action_data.get("name", "Unknown Action"),
                    description=self.clean_html_description(action_data.get("description")),
                    shortDescription=self.clean_html_description(action_data.get("snippet")),
                    source=category,
                    actionCategory="feature"
                )
                
                # Parse activation
                action.activation = self.parse_activation(
                    action_data.get("activation", {}),
                    action_data.get("actionType", 0)
                )
                
                # Fix specific activation types based on ability descriptions
                action_name = action.name.lower()
                if "aura of the guardian" in action_name or "rebuke the violent" in action_name:
                    # These are clearly reaction-based abilities
                    action.activation.activationType = "reaction"
                elif "create pact weapon" in action_name or "divine sense" in action_name or "lay on hands" in action_name:
                    # These are action-based abilities despite what the data shows
                    action.activation.activationType = "action"
                
                # Parse usage
                action.usage = self.parse_usage(action_data.get("limitedUse", {}))
                
                # Parse range
                action.actionRange = self.parse_range(action_data.get("range", {}))
                
                # Parse damage
                action.damage = self.parse_damage(
                    action_data.get("dice"),
                    action_data.get("damageTypeId"),
                    action_data.get("value")
                )
                
                # Parse save
                action.save = self.parse_save(
                    action_data.get("fixedSaveDc"),
                    action_data.get("saveStatId"),
                    action_data.get("saveSuccessDescription"),
                    action_data.get("saveFailDescription")
                )
                
                # Combat flags
                action.isWeaponAttack = action_data.get("attackType") in [1, 2]  # Melee or ranged
                action.attackBonus = action_data.get("fixedToHit")
                
                actions.append(action)
        
        return actions
    

    
    def parse_weapon_actions(self) -> List[CharacterAction]:
        """Parse weapon attacks from inventory (equipped weapons only)."""
        actions = []
        
        inventory = self.data.get("inventory", [])
        
        for item_data in inventory:
            definition = item_data.get("definition", {})
            
            # Skip non-weapons or unequipped weapons
            if not definition.get("attackType") or not item_data.get("equipped"):
                continue
            
            action = CharacterAction(
                name=f"{definition.get('name', 'Unknown Weapon')} Attack",
                description=self.clean_html_description(definition.get("description")),
                source="item",
                sourceFeature=definition.get("name"),
                actionCategory="attack",
                isWeaponAttack=True
            )
            
            # Weapon activation (usually action)
            action.activation = ActionActivation(activationType="action")
            
            # Weapon damage
            damage_data = definition.get("damage")
            if damage_data:
                action.damage = ActionDamage()
                action.damage.diceNotation = damage_data.get("diceString")
                
                damage_type = definition.get("damageType")
                if damage_type:
                    action.damage.damageType = damage_type.lower()
            
            # Weapon range
            weapon_range = definition.get("range")
            long_range = definition.get("longRange") 
            if weapon_range or long_range:
                action.actionRange = ActionRange()
                action.actionRange.range = weapon_range
                action.actionRange.longRange = long_range
                
                if weapon_range:
                    desc = f"{weapon_range} feet"
                    if long_range:
                        desc += f" (long: {long_range} feet)"
                    action.actionRange.rangeDescription = desc
            
            # Check for ammunition requirement
            properties = definition.get("properties", [])
            for prop in properties:
                if prop.get("name", "").lower() in ["ammunition", "thrown"]:
                    action.requiresAmmo = True
                    break
            
            actions.append(action)
        
        return actions
    
    def parse_unequipped_weapon_actions(self) -> List[CharacterAction]:
        """Parse unequipped weapon attacks from inventory (requires drawing first)."""
        actions = []
        
        inventory = self.data.get("inventory", [])
        
        for item_data in inventory:
            definition = item_data.get("definition", {})
            
            # Only include unequipped weapons
            if not definition.get("attackType") or item_data.get("equipped"):
                continue
            
            action = CharacterAction(
                name=f"{definition.get('name', 'Unknown Weapon')} Attack (Unequipped)",
                description=self.clean_html_description(definition.get("description")),
                shortDescription=f"Requires drawing {definition.get('name', 'weapon')} first (free object interaction or action).",
                source="item",
                sourceFeature=definition.get("name"),
                actionCategory="unequipped_weapon",
                isWeaponAttack=True
            )
            
            # Weapon activation (usually action, but requires drawing)
            action.activation = ActionActivation(activationType="action")
            
            # Weapon damage
            damage_data = definition.get("damage")
            if damage_data:
                action.damage = ActionDamage()
                action.damage.diceNotation = damage_data.get("diceString")
                
                damage_type = definition.get("damageType")
                if damage_type:
                    action.damage.damageType = damage_type.lower()
            
            # Weapon range
            weapon_range = definition.get("range")
            long_range = definition.get("longRange") 
            if weapon_range or long_range:
                action.actionRange = ActionRange()
                action.actionRange.range = weapon_range
                action.actionRange.longRange = long_range
                
                if weapon_range:
                    desc = f"{weapon_range} feet"
                    if long_range:
                        desc += f" (long: {long_range} feet)"
                    action.actionRange.rangeDescription = desc
            
            # Check for ammunition requirement
            properties = definition.get("properties", [])
            for prop in properties:
                if prop.get("name", "").lower() in ["ammunition", "thrown"]:
                    action.requiresAmmo = True
                    break
            
            actions.append(action)
        
        return actions
    
    def parse_all_actions(self) -> List[CharacterAction]:
        """Parse all non-spell character actions."""
        all_actions = []
        
        # Parse different action sources
        all_actions.extend(self.parse_basic_actions())
        all_actions.extend(self.parse_weapon_actions())
        all_actions.extend(self.parse_unequipped_weapon_actions())
        
        # TODO: Parse item-granted spells as actions
        # This requires LLM parsing of spell descriptions to extract:
        # - Spell names from item descriptions
        # - Save DCs and spell effects
        # - Usage limitations (once per dawn, etc.)
        # Example: Eldaryth of Regret grants "call lightning", "divine word", "finger of death"
        # all_actions.extend(self.parse_item_spell_actions())
        
        # TODO: Parse spell actions from weapon descriptions using LLM
        # This requires natural language processing to extract spell-like abilities
        # from complex item descriptions like the Eldaryth of Regret's spell section
        # all_actions.extend(self.parse_weapon_spell_actions())
        
        # TODO: Parse item-granted spell actions from the spells.item section
        # This requires parsing the spells data structure and converting spells to actions
        # all_actions.extend(self.parse_spell_section_actions())
        
        # Remove duplicates and sort by name
        unique_actions = {}
        for action in all_actions:
            key = (action.name, action.source)
            if key not in unique_actions:
                unique_actions[key] = action
        
        return sorted(unique_actions.values(), key=lambda x: x.name)
    
    def print_actions_summary(self, actions: List[CharacterAction]):
        """Print a summary of all character actions."""
        print("\\n" + "="*60)
        print("CHARACTER ACTIONS SUMMARY")
        print("="*60)
        
        # Group by category
        by_category = {}
        for action in actions:
            category = action.actionCategory or "other"
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(action)
        
        # Ensure consistent ordering
        category_order = ["attack", "feature", "unequipped_weapon", "other"]
        ordered_categories = []
        for cat in category_order:
            if cat in by_category:
                ordered_categories.append((cat, by_category[cat]))
        for cat, actions_list in by_category.items():
            if cat not in category_order:
                ordered_categories.append((cat, actions_list))
        
        by_category = dict(ordered_categories)
        
        for category, category_actions in by_category.items():
            category_name = category.upper().replace("_", " ")
            print(f"\\n{category_name} ACTIONS ({len(category_actions)}):")
            print("-" * 40)
            
            for action in category_actions:
                # Build action summary line
                parts = [f"• {action.name}"]
                
                if action.activation and action.activation.activationType:
                    parts.append(f"[{action.activation.activationType}]")
                
                if action.usage and action.usage.maxUses:
                    reset = f" per {action.usage.resetType}" if action.usage.resetType else ""
                    parts.append(f"({action.usage.maxUses} uses{reset})")
                
                if action.damage and (action.damage.diceNotation or action.damage.fixedDamage):
                    damage_str = action.damage.diceNotation or str(action.damage.fixedDamage)
                    if action.damage.damageType:
                        damage_str += f" {action.damage.damageType}"
                    parts.append(f"[{damage_str}]")
                
                if action.actionRange and action.actionRange.rangeDescription:
                    parts.append(f"({action.actionRange.rangeDescription})")
                
                print("  " + " ".join(parts))


def clean_dict_for_json(obj):
    """Remove None values and empty collections."""
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            cleaned_value = clean_dict_for_json(value)
            if cleaned_value is not None and cleaned_value != [] and cleaned_value != {}:
                cleaned[key] = cleaned_value
        return cleaned if cleaned else None
    elif isinstance(obj, list):
        cleaned = [clean_dict_for_json(item) for item in obj]
        cleaned = [item for item in cleaned if item is not None]
        return cleaned if cleaned else None
    else:
        return obj


def main():
    """Main function to parse D&D Beyond JSON and extract all non-spell actions."""
    if len(sys.argv) != 2:
        print("Usage: python parse_actions.py <path_to_json_file>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    try:
        # Load JSON data
        print(f"Loading D&D Beyond character data from: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Parse actions
        parser = DNDBeyondActionsParser(json_data)
        actions = parser.parse_all_actions()
        
        # Print summary
        parser.print_actions_summary(actions)
        
        # Save to output file
        output_file = json_file_path.replace('.json', '_actions_parsed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert to dict and clean
            from dataclasses import asdict
            actions_dict = [asdict(action) for action in actions]
            cleaned_dict = clean_dict_for_json(actions_dict)
            json.dump(cleaned_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\\n" + "="*60)
        print(f"Found {len(actions)} total actions")
        print(f"Actions data saved to: {output_file}")
        print("="*60)
        
        return actions
        
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{json_file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()