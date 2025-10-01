#!/usr/bin/env python3
"""
D&D Beyond Core Character Parser

This script parses a D&D Beyond character JSON export and extracts the core character information:
- AbilityScores (STR, DEX, CON, INT, WIS, CHA)
- CharacterBase (name, race, class, level, alignment, background)  
- PhysicalCharacteristics (physical appearance and traits)
- CombatStats (HP, AC, initiative, speed, hit dice)
- Proficiency (skills, tools, languages, weapons, armor)
- DamageModifier (resistances, immunities, vulnerabilities)
- PassiveScores (passive perception, investigation, insight, stealth)
- Senses (darkvision, blindsight, etc.)

Usage:
    python parse_core_character.py <path_to_json_file>

Output:
    Parsed core character data in JSON format
"""

import json
from typing import Dict, List, Optional, Any, Union, Literal
from dataclasses import dataclass, field
from pathlib import Path

from src.rag.character.character_types import (
    AbilityScores, CharacterBase, PhysicalCharacteristics, CombatStats,
    Proficiency, DamageModifier, PassiveScores, Senses
)

# Reference mappings
ALIGNMENT_MAP = {
    1: "Lawful Good", 2: "Neutral Good", 3: "Chaotic Good",
    4: "Lawful Neutral", 5: "True Neutral", 6: "Chaotic Neutral", 
    7: "Lawful Evil", 8: "Neutral Evil", 9: "Chaotic Evil"
}

SIZE_MAP = {
    1: "Tiny", 2: "Small", 3: "Medium", 4: "Large", 5: "Huge", 6: "Gargantuan"
}

LIFESTYLE_MAP = {
    1: "Wretched", 2: "Squalid", 3: "Poor", 4: "Modest",
    5: "Comfortable", 6: "Wealthy", 7: "Aristocratic"
}

class DNDBeyondCoreParser:
    """Parser for D&D Beyond character JSON core data."""
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize parser with JSON data."""
        self.json_data = json_data
        self.data = json_data.get('data', {})
        
    def parse_ability_scores(self) -> AbilityScores:
        """Parse the six core ability scores from D&D Beyond JSON.
        
        EXTRACTION PATHS:
        - stats[0-5].value for base scores (ids 1-6 map to STR-CHA)
        - bonusStats[0-5].value for racial/other bonuses
        - overrideStats[0-5].value for manual overrides
        - Apply modifiers from equipment/features
        """
        # Get base stats (should be 6 entries for STR, DEX, CON, INT, WIS, CHA)
        stats = self.data.get('stats', [])
        bonus_stats = self.data.get('bonusStats', [])
        override_stats = self.data.get('overrideStats', [])
        
        # Initialize with defaults
        scores = [10, 10, 10, 10, 10, 10]  # Default ability scores
        
        # Extract base scores
        for i, stat in enumerate(stats[:6]):
            if stat.get('value') is not None:
                scores[i] = stat['value']
        
        # Apply bonus stats
        for i, bonus in enumerate(bonus_stats[:6]):
            if bonus and bonus.get('value') is not None:
                scores[i] += bonus['value']
        
        # Apply overrides (takes precedence)
        for i, override in enumerate(override_stats[:6]):
            if override and override.get('value') is not None:
                scores[i] = override['value']
        
        # Apply ability score modifiers from equipment, feats, etc.
        modifiers = self.data.get('modifiers', {})
        for category in ['race', 'class', 'background', 'item', 'feat']:
            mod_list = modifiers.get(category, [])
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if (mod.get('type') == 'bonus' and 
                        mod.get('subType') in ['strength-score', 'dexterity-score', 'constitution-score', 
                                              'intelligence-score', 'wisdom-score', 'charisma-score']):
                        ability_index = {
                            'strength-score': 0, 'dexterity-score': 1, 'constitution-score': 2,
                            'intelligence-score': 3, 'wisdom-score': 4, 'charisma-score': 5
                        }.get(mod['subType'])
                        if ability_index is not None:
                            value = mod.get('value')
                            if value is not None:
                                scores[ability_index] += value
        
        return AbilityScores(
            strength=scores[0],
            dexterity=scores[1], 
            constitution=scores[2],
            intelligence=scores[3],
            wisdom=scores[4],
            charisma=scores[5]
        )
    
    def parse_character_base(self) -> CharacterBase:
        """Parse basic character information.
        
        EXTRACTION PATHS:
        - name: data.name
        - race: race.fullName or race.baseName  
        - character_class: classes[0].definition.name (primary class)
        - total_level: sum of all classes[].level
        - alignment: lookup alignmentId in ALIGNMENT_MAP
        - background: background.definition.name
        - subrace: race.subRaceShortName (if isSubRace)
        - multiclass_levels: {class_name: level} for multiple classes
        - lifestyle: lookup lifestyleId in LIFESTYLE_MAP
        """
        # Basic character info
        name = self.data.get('name', 'Unknown')
        
        # Race information
        race_data = self.data.get('race', {})
        if race_data.get('isSubRace'):
            race = race_data.get('fullName', race_data.get('baseRaceName', 'Unknown'))
            subrace = race_data.get('subRaceShortName')
        else:
            race = race_data.get('baseName', race_data.get('fullName', 'Unknown'))
            subrace = None
        
        # Class information
        classes = self.data.get('classes', [])
        if classes:
            # Primary class is the first one or the starting class
            primary_class = None
            for cls in classes:
                if cls.get('isStartingClass', False):
                    primary_class = cls['definition']['name']
                    break
            if not primary_class:
                primary_class = classes[0]['definition']['name']
            
            # Calculate total level
            total_level = sum(cls['level'] for cls in classes)
            
            # Build multiclass dictionary if needed
            multiclass_levels = None
            if len(classes) > 1:
                multiclass_levels = {}
                for cls in classes:
                    multiclass_levels[cls['definition']['name']] = cls['level']
        else:
            primary_class = 'Unknown'
            total_level = 1
            multiclass_levels = None
        
        # Alignment
        alignment_id = self.data.get('alignmentId')
        alignment = ALIGNMENT_MAP.get(alignment_id, 'True Neutral')
        
        # Background
        background_data = self.data.get('background', {})
        if background_data.get('hasCustomBackground'):
            background_name = background_data.get('customBackground', {}).get('name', 'Custom Background')
        else:
            background_name = background_data.get('definition', {}).get('name', 'Unknown')
        
        # Lifestyle
        lifestyle_id = self.data.get('lifestyleId')
        lifestyle = LIFESTYLE_MAP.get(lifestyle_id) if lifestyle_id else None
        
        return CharacterBase(
            name=name,
            race=race,
            character_class=primary_class,
            total_level=total_level,
            alignment=alignment,
            background=background_name,
            subrace=subrace,
            multiclass_levels=multiclass_levels,
            lifestyle=lifestyle
        )
    
    def parse_physical_characteristics(self) -> PhysicalCharacteristics:
        """Parse physical appearance and traits.
        
        EXTRACTION PATHS:
        - alignment: lookup alignmentId in ALIGNMENT_MAP
        - gender: data.gender
        - eyes: data.eyes  
        - size: lookup race.sizeId in SIZE_MAP
        - height: data.height
        - hair: data.hair
        - skin: data.skin
        - age: data.age
        - weight: data.weight (add "lb" unit)
        - faith: data.faith
        """
        # Get alignment (same as character base)
        alignment_id = self.data.get('alignmentId')
        alignment = ALIGNMENT_MAP.get(alignment_id, 'True Neutral')
        
        # Physical appearance
        gender = self.data.get('gender', 'Unknown')
        eyes = self.data.get('eyes', 'Unknown')
        hair = self.data.get('hair', 'Unknown') 
        skin = self.data.get('skin', 'Unknown')
        height = self.data.get('height', "5'0\"")
        age = self.data.get('age', 18)
        
        # Weight with units
        weight_value = self.data.get('weight', 150)
        weight = f"{weight_value} lb" if isinstance(weight_value, (int, float)) else str(weight_value)
        
        # Size from race
        race_data = self.data.get('race', {})
        size_id = race_data.get('sizeId', 3)  # Default to Medium
        size = SIZE_MAP.get(size_id, 'Medium')
        
        # Faith (optional)
        faith = self.data.get('faith')
        
        return PhysicalCharacteristics(
            alignment=alignment,
            gender=gender,
            eyes=eyes,
            size=size,
            height=height,
            hair=hair,
            skin=skin,
            age=age,
            weight=weight,
            faith=faith
        )
    
    def parse_combat_stats(self) -> CombatStats:
        """Parse core combat statistics.
        
        EXTRACTION PATHS:
        - max_hp: overrideHitPoints or (baseHitPoints + bonusHitPoints)
        - armor_class: calculate from equipped armor + DEX mod + bonuses
        - initiative_bonus: DEX modifier + bonuses from modifiers
        - speed: race.weightSpeeds.normal.walk
        - hit_dice: classes[].definition.hitDice per class level
        """
        # Hit Points
        max_hp = self.data.get('overrideHitPoints')
        if max_hp is None:
            base_hp = self.data.get('baseHitPoints', 0)
            bonus_hp = self.data.get('bonusHitPoints') or 0
            max_hp = base_hp + bonus_hp
        
        # Armor Class calculation
        armor_class = self._calculate_armor_class()
        
        # Initiative bonus (DEX modifier + bonuses)
        initiative_bonus = self._calculate_initiative_bonus()
        
        # Speed from race
        race_data = self.data.get('race', {})
        weight_speeds = race_data.get('weightSpeeds', {})
        normal_speeds = weight_speeds.get('normal', {})
        speed = normal_speeds.get('walk', 30)
        
        # Hit dice from classes
        hit_dice = self._calculate_hit_dice()
        
        return CombatStats(
            max_hp=max_hp,
            armor_class=armor_class,
            initiative_bonus=initiative_bonus,
            speed=speed,
            hit_dice=hit_dice
        )
    
    def _calculate_armor_class(self) -> int:
        """Calculate armor class from equipped items and bonuses."""
        base_ac = 10
        dex_mod = self._get_ability_modifier('dexterity')
        
        # Look for equipped armor
        inventory = self.data.get('inventory', [])
        armor_ac = None
        max_dex_bonus = None
        
        for item in inventory:
            if item.get('equipped') and item.get('definition', {}).get('armorClass'):
                armor_def = item['definition']
                if armor_def.get('armorClass'):
                    armor_ac = armor_def['armorClass']
                    # Some armors limit DEX bonus
                    if armor_def.get('type') in ['Heavy Armor']:
                        max_dex_bonus = 0
                    elif armor_def.get('type') in ['Medium Armor']:
                        max_dex_bonus = 2
        
        # Calculate AC
        if armor_ac is not None:
            ac = armor_ac
            if max_dex_bonus is not None:
                ac += min(dex_mod, max_dex_bonus)
            else:
                ac += dex_mod
        else:
            ac = base_ac + dex_mod
        
        # Add AC bonuses from modifiers
        ac += self._get_ac_bonuses()
        
        return max(ac, 1)  # AC can't be less than 1
    
    def _calculate_initiative_bonus(self) -> int:
        """Calculate initiative bonus."""
        dex_mod = self._get_ability_modifier('dexterity')
        
        # Add initiative bonuses from modifiers
        init_bonuses = 0
        modifiers = self.data.get('modifiers', {})
        for category in ['race', 'class', 'background', 'item', 'feat']:
            mod_list = modifiers.get(category, [])
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'bonus' and mod.get('subType') == 'initiative':
                        value = mod.get('value', 0)
                        if value is not None:
                            init_bonuses += value
        
        return dex_mod + init_bonuses
    
    def _calculate_hit_dice(self) -> Optional[Dict[str, str]]:
        """Calculate hit dice from classes."""
        classes = self.data.get('classes', [])
        if not classes:
            return None
        
        hit_dice = {}
        for cls in classes:
            class_name = cls['definition']['name']
            hit_die = cls['definition'].get('hitDice', 8)
            level = cls['level']
            hit_dice[class_name] = f"{level}d{hit_die}"
        
        return hit_dice
    
    def parse_proficiencies(self) -> List[Proficiency]:
        """Parse character proficiencies from modifiers.
        
        EXTRACTION PATHS:
        - Extract from modifiers[category] where type == "proficiency"
        - Map subType to appropriate proficiency category
        - Use friendlySubtypeName for display name
        - Apply filtering rules to remove duplicates and non-informative entries
        """
        proficiencies = []
        seen_proficiencies = set()  # Track duplicates
        modifiers = self.data.get('modifiers', {})
        
        for category in ['race', 'class', 'background', 'item', 'feat']:
            mod_list = modifiers.get(category, [])
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'proficiency':
                        sub_type = mod.get('subType', '')
                        friendly_name = mod.get('friendlySubtypeName', sub_type)
                        
                        # Apply filtering rules
                        if not self._should_include_proficiency(friendly_name, sub_type, category):
                            continue
                        
                        # Map subType to proficiency type
                        prof_type = self._map_proficiency_type(sub_type)
                        if prof_type:
                            # Create a unique key to prevent duplicates
                            prof_key = (prof_type, friendly_name.lower())
                            if prof_key not in seen_proficiencies:
                                seen_proficiencies.add(prof_key)
                                proficiencies.append(Proficiency(
                                    type=prof_type,
                                    name=friendly_name
                                ))
        
        return proficiencies
    
    def _should_include_proficiency(self, friendly_name: str, sub_type: str, category: str) -> bool:
        """Determine if a proficiency should be included based on filtering rules."""
        
        # Rule 1: Skip placeholder/selection prompts
        placeholder_patterns = [
            'choose a', 'choose an', 'select a', 'select an',
            'pick a', 'pick an', 'any one', 'one of'
        ]
        if any(pattern in friendly_name.lower() for pattern in placeholder_patterns):
            return False
        
        # Rule 2: Skip overly generic weapon/armor proficiencies from class features
        # These are usually granted automatically and not character-defining
        if category == 'class':
            generic_combat_profs = {
                'simple weapons', 'martial weapons', 'light armor', 
                'medium armor', 'heavy armor', 'shields'
            }
            if friendly_name.lower() in generic_combat_profs:
                return False
        
        # Rule 3: Handle saving throw proficiencies more intelligently
        # Keep only unique saving throws (avoid multiclass duplicates)
        if 'saving throws' in friendly_name.lower():
            # This will be handled by the duplicate detection system
            return True
        
        # Rule 4: Skip empty or invalid names
        if not friendly_name or friendly_name.isspace():
            return False
        
        # Rule 5: Prioritize specific/unique proficiencies
        # Keep tool proficiencies, specific weapons, skills, languages
        specific_categories = {'skill', 'tool', 'language'}
        if any(cat in sub_type.lower() for cat in specific_categories):
            return True
        
        # Rule 6: Keep racial proficiencies (they're usually character-defining)
        if category == 'race':
            return True
        
        # Rule 7: Keep background proficiencies (character background is important)
        if category == 'background':
            return True
        
        # Rule 8: Keep feat/item proficiencies (chosen/earned abilities)
        if category in ['feat', 'item']:
            return True
        
        # Rule 9: For class proficiencies, be more selective
        if category == 'class':
            # Keep specific named weapons (not generic categories)
            specific_weapons = [
                'longsword', 'shortsword', 'rapier', 'scimitar', 'warhammer', 
                'battleaxe', 'handaxe', 'javelin', 'trident', 'net'
            ]
            if any(weapon in friendly_name.lower() for weapon in specific_weapons):
                return True
            
            # Keep all skills (always character-defining)
            skill_names = [
                'acrobatics', 'animal handling', 'arcana', 'athletics', 'deception',
                'history', 'insight', 'intimidation', 'investigation', 'medicine',
                'nature', 'perception', 'performance', 'persuasion', 'religion',
                'sleight of hand', 'stealth', 'survival'
            ]
            if any(skill in friendly_name.lower() for skill in skill_names):
                return True
            
            # Also check subType for skills
            if 'skill' in sub_type.lower():
                return True
        
        # Default: exclude if we can't categorize it as valuable
        return False
    
    def parse_damage_modifiers(self) -> List[DamageModifier]:
        """Parse damage resistances, immunities, and vulnerabilities.
        
        EXTRACTION PATHS:
        - Extract from modifiers[category] where type in ["resistance", "immunity", "vulnerability"]
        - damage_type: modifier.subType
        - modifier_type: modifier.type
        """
        damage_modifiers = []
        modifiers = self.data.get('modifiers', {})
        
        for category in ['race', 'class', 'background', 'item', 'feat']:
            mod_list = modifiers.get(category, [])
            if isinstance(mod_list, list):
                for mod in mod_list:
                    mod_type = mod.get('type')
                    if mod_type in ['resistance', 'immunity', 'vulnerability']:
                        damage_type = mod.get('subType', 'unknown')
                        damage_modifiers.append(DamageModifier(
                            damage_type=damage_type,
                            modifier_type=mod_type
                        ))
        
        return damage_modifiers
    
    def parse_passive_scores(self) -> PassiveScores:
        """Parse passive scores (calculated from ability scores + proficiencies + bonuses).
        
        EXTRACTION PATHS:
        - Calculate as: 10 + ability modifier + proficiency bonus (if proficient) + other bonuses
        - Base ability scores from stats/bonusStats/overrideStats
        - Proficiency bonus based on character level
        - Skill proficiencies from modifiers
        - Look for additional bonuses from feats, items, etc.
        """
        ability_scores = self.parse_ability_scores()
        proficiencies = self.parse_proficiencies()
        
        # Get proficiency bonus based on total level
        character_base = self.parse_character_base()
        prof_bonus = self._get_proficiency_bonus(character_base.total_level)
        
        # Get skill proficiencies
        skill_profs = {p.name.lower() for p in proficiencies if p.type == 'skill'}
        
        # Calculate passive scores with additional bonuses
        wis_mod = (ability_scores.wisdom - 10) // 2
        int_mod = (ability_scores.intelligence - 10) // 2
        dex_mod = (ability_scores.dexterity - 10) // 2
        
        # Check for additional bonuses to passive abilities
        perception_bonus = self._get_passive_bonus('perception')
        investigation_bonus = self._get_passive_bonus('investigation')  
        insight_bonus = self._get_passive_bonus('insight')
        stealth_bonus = self._get_passive_bonus('stealth')
        
        # Check if Perception is actually proficient (might be granted by feat/class feature)
        has_perception_prof = self._has_perception_proficiency()
        
        perception = 10 + wis_mod + (prof_bonus if has_perception_prof else 0) + perception_bonus
        investigation = 10 + int_mod + (prof_bonus if 'investigation' in skill_profs else 0) + investigation_bonus if ('investigation' in skill_profs or investigation_bonus > 0) else None
        insight = 10 + wis_mod + (prof_bonus if 'insight' in skill_profs else 0) + insight_bonus if ('insight' in skill_profs or insight_bonus > 0) else None
        stealth = 10 + dex_mod + (prof_bonus if 'stealth' in skill_profs else 0) + stealth_bonus if ('stealth' in skill_profs or stealth_bonus > 0) else None
        
        return PassiveScores(
            perception=perception,
            investigation=investigation,
            insight=insight,
            stealth=stealth
        )
    
    def _has_perception_proficiency(self) -> bool:
        """Check if character has Perception proficiency from any source."""
        modifiers = self.data.get('modifiers', {})
        
        for category in modifiers:
            if isinstance(modifiers[category], list):
                for mod in modifiers[category]:
                    if (mod.get('type') == 'proficiency' and 
                        'perception' in mod.get('subType', '').lower()):
                        return True
        return False
    
    def _get_passive_bonus(self, skill_name: str) -> int:
        """Get additional bonuses to passive abilities from feats, items, etc."""
        bonus = 0
        modifiers = self.data.get('modifiers', {})
        
        for category in modifiers:
            if isinstance(modifiers[category], list):
                for mod in modifiers[category]:
                    mod_type = mod.get('type', '')
                    sub_type = mod.get('subType', '').lower()
                    value = mod.get('value', 0)
                    
                    # Check for direct passive bonuses
                    if (mod_type == 'bonus' and 
                        f'passive-{skill_name}' in sub_type):
                        bonus += value or 0
                    
                    # Check for general skill bonuses
                    elif (mod_type == 'bonus' and skill_name in sub_type):
                        bonus += value or 0
                        
                    # Check for Wisdom ability bonuses (affects perception/insight)
                    elif (mod_type == 'bonus' and 
                          sub_type == 'wisdom-ability-checks' and 
                          skill_name in ['perception', 'insight']):
                        bonus += value or 0
                        
                    # Check for Intelligence ability bonuses (affects investigation)
                    elif (mod_type == 'bonus' and 
                          sub_type == 'intelligence-ability-checks' and 
                          skill_name == 'investigation'):
                        bonus += value or 0
                        
        return bonus
    
    def parse_senses(self) -> Senses:
        """Parse special senses from modifiers.
        
        EXTRACTION PATHS:
        - Extract from modifiers[category] where type == "set-base" and subType contains sense names
        - Common senses: darkvision, blindsight, tremorsense, truesight
        - Value is typically range in feet
        """
        senses = {}
        modifiers = self.data.get('modifiers', {})
        
        for category in ['race', 'class', 'background', 'item', 'feat']:
            mod_list = modifiers.get(category, [])
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'set-base':
                        sub_type = mod.get('subType', '').lower()
                        value = mod.get('value')
                        
                        # Check for known sense types
                        if any(sense in sub_type for sense in ['darkvision', 'blindsight', 'tremorsense', 'truesight']):
                            sense_name = sub_type.replace('-', '_')
                            if value:
                                senses[sense_name] = value
                            else:
                                senses[sense_name] = "Present"
        
        return Senses(senses=senses)
    
    def _map_proficiency_type(self, sub_type: str) -> Optional[Literal["armor", "weapon", "tool", "language", "skill", "saving_throw"]]:
        """Map D&D Beyond subType to proficiency category."""
        sub_type_lower = sub_type.lower()
        
        # Skill proficiencies
        skills = {
            'acrobatics', 'animal-handling', 'arcana', 'athletics', 'deception',
            'history', 'insight', 'intimidation', 'investigation', 'medicine',
            'nature', 'perception', 'performance', 'persuasion', 'religion',
            'sleight-of-hand', 'stealth', 'survival'
        }
        
        # Saving throws
        saving_throws = {
            'strength-saving-throws', 'dexterity-saving-throws', 'constitution-saving-throws',
            'intelligence-saving-throws', 'wisdom-saving-throws', 'charisma-saving-throws'
        }
        
        # Armor types
        armor_types = {
            'light-armor', 'medium-armor', 'heavy-armor', 'shields'
        }
        
        # Check categories
        if sub_type_lower in skills:
            return 'skill'
        elif sub_type_lower in saving_throws:
            return 'saving_throw'
        elif sub_type_lower in armor_types:
            return 'armor'
        elif 'tool' in sub_type_lower or 'kit' in sub_type_lower:
            return 'tool'
        elif 'language' in sub_type_lower or sub_type_lower in {'common', 'elvish', 'dwarvish', 'halfling', 'draconic', 'giant', 'gnomish', 'goblin', 'orcish'}:
            return 'language'
        else:
            # Assume weapons for everything else
            return 'weapon'
    
    def _get_proficiency_bonus(self, level: int) -> int:
        """Calculate proficiency bonus based on character level."""
        return 2 + ((level - 1) // 4)
    
    def _get_ability_modifier(self, ability_name: str) -> int:
        """Get ability modifier for given ability."""
        scores = self.parse_ability_scores()
        score = getattr(scores, ability_name, 10)
        return (score - 10) // 2
    
    def _get_ac_bonuses(self) -> int:
        """Get AC bonuses from modifiers."""
        ac_bonus = 0
        modifiers = self.data.get('modifiers', {})
        
        for category in ['race', 'class', 'background', 'item', 'feat']:
            mod_list = modifiers.get(category, [])
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if (mod.get('type') == 'bonus' and 
                        mod.get('subType') == 'armor-class'):
                        value = mod.get('value', 0)
                        if value is not None:
                            ac_bonus += value
        
        return ac_bonus
    
    def parse_all_core_data(self):
        """
        Parse all core character data and return as a namespace object.
        
        Returns:
            Object with all core data as attributes
        """
        from types import SimpleNamespace
        
        return SimpleNamespace(
            character_base=self.parse_character_base(),
            characteristics=self.parse_physical_characteristics(),
            ability_scores=self.parse_ability_scores(),
            combat_stats=self.parse_combat_stats(),
            proficiencies=self.parse_proficiencies(),
            damage_modifiers=self.parse_damage_modifiers(),
            passive_scores=self.parse_passive_scores(),
            senses=self.parse_senses()
        )


