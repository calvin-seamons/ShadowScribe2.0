"""
Spell Calculation Utilities

Helper functions for calculating spell save DC, spell attack bonus, 
and other spellcasting-related statistics.
"""

from typing import Dict
from .character_types import Character, SpellcastingInfo


def calculate_ability_modifier(ability_score: int) -> int:
    """Calculate ability modifier from ability score."""
    return (ability_score - 10) // 2


def calculate_proficiency_bonus(character_level: int) -> int:
    """Calculate proficiency bonus based on character level."""
    if character_level >= 17:
        return 6
    elif character_level >= 13:
        return 5
    elif character_level >= 9:
        return 4
    elif character_level >= 5:
        return 3
    else:
        return 2


def get_spellcasting_ability_modifier(character: Character, spellcasting_ability: str) -> int:
    """Get the modifier for a specific spellcasting ability."""
    ability_map = {
        'strength': character.ability_scores.strength,
        'dexterity': character.ability_scores.dexterity,
        'constitution': character.ability_scores.constitution,
        'intelligence': character.ability_scores.intelligence,
        'wisdom': character.ability_scores.wisdom,
        'charisma': character.ability_scores.charisma
    }
    
    ability_score = ability_map.get(spellcasting_ability.lower(), 10)
    return calculate_ability_modifier(ability_score)


def calculate_spell_save_dc(character: Character, spellcasting_ability: str) -> int:
    """Calculate spell save DC: 8 + proficiency bonus + ability modifier."""
    prof_bonus = calculate_proficiency_bonus(character.character_base.total_level)
    ability_mod = get_spellcasting_ability_modifier(character, spellcasting_ability)
    return 8 + prof_bonus + ability_mod


def calculate_spell_attack_bonus(character: Character, spellcasting_ability: str) -> int:
    """Calculate spell attack bonus: proficiency bonus + ability modifier."""
    prof_bonus = calculate_proficiency_bonus(character.character_base.total_level)
    ability_mod = get_spellcasting_ability_modifier(character, spellcasting_ability)
    return prof_bonus + ability_mod


def update_spellcasting_calculations(character: Character) -> Character:
    """Update all spell save DCs and attack bonuses for a character."""
    if not character.spell_list or not character.spell_list.spellcasting:
        return character
    
    # Update each spellcasting class
    for class_name, casting_info in character.spell_list.spellcasting.items():
        # Calculate correct values
        spell_dc = calculate_spell_save_dc(character, casting_info.ability)
        spell_attack = calculate_spell_attack_bonus(character, casting_info.ability)
        
        # Update the spellcasting info
        casting_info.spell_save_dc = spell_dc
        casting_info.spell_attack_bonus = spell_attack
    
    return character


def get_spellcasting_summary(character: Character) -> Dict[str, Dict[str, int]]:
    """Get a summary of spellcasting stats for all classes."""
    summary = {}
    
    if character.spell_list and character.spell_list.spellcasting:
        for class_name, casting_info in character.spell_list.spellcasting.items():
            summary[class_name] = {
                'spell_save_dc': casting_info.spell_save_dc,
                'spell_attack_bonus': casting_info.spell_attack_bonus,
                'ability': casting_info.ability
            }
    
    return summary
