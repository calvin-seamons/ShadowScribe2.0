"""
D&D Beyond JSON to Character Data Types Parser

This script parses a D&D Beyond character export JSON and converts it to 
the structured character data types defined in the character_types module.
"""

import json
import sys
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the character types from the proper location
from src.rag.character.character_types import *


class DnDBeyondParser:
    """Parser for D&D Beyond character JSON exports."""
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize parser with JSON data."""
        self.data = json_data
        
    def parse(self) -> Character:
        """Parse the complete character from JSON."""
        return Character(
            character_base=self._parse_character_base(),
            characteristics=self._parse_characteristics(),
            ability_scores=self._parse_ability_scores(),
            combat_stats=self._parse_combat_stats(),
            background_info=self._parse_background_info(),
            personality=self._parse_personality(),
            backstory=self._parse_backstory(),
            organizations=self._parse_organizations(),
            allies=self._parse_allies(),
            enemies=self._parse_enemies(),
            proficiencies=self._parse_proficiencies(),
            damage_modifiers=self._parse_damage_modifiers(),
            passive_scores=self._parse_passive_scores(),
            senses=self._parse_senses(),
            action_economy=self._parse_action_economy(),
            features_and_traits=self._parse_features_and_traits(),
            inventory=self._parse_inventory(),
            spell_list=self._parse_spell_list(),
            objectives_and_contracts=self._parse_objectives(),
            notes=self._parse_notes(),
            created_date=datetime.now(),
            last_updated=datetime.now()
        )
    
    def _parse_character_base(self) -> CharacterBase:
        """Parse basic character information."""
        # Calculate total level from classes
        total_level = sum(cls['level'] for cls in self.data.get('classes', []))
        
        # Get primary class (highest level)
        classes = self.data.get('classes', [])
        primary_class = classes[0]['name'] if classes else 'Unknown'
        
        # Build multiclass dictionary
        multiclass_levels = {}
        if len(classes) > 1:
            for cls in classes:
                multiclass_levels[cls['name']] = cls['level']
        
        # Get alignment from ID (mapping needed)
        alignment_map = {
            1: "Lawful Good", 2: "Neutral Good", 3: "Chaotic Good",
            4: "Lawful Neutral", 5: "True Neutral", 6: "Chaotic Neutral",
            7: "Lawful Evil", 8: "Neutral Evil", 9: "Chaotic Evil"
        }
        alignment = alignment_map.get(self.data.get('alignmentId', 5), "True Neutral")
        
        # Get lifestyle from ID (mapping needed)
        lifestyle_map = {
            1: "Wretched", 2: "Squalid", 3: "Poor", 4: "Modest",
            5: "Comfortable", 6: "Wealthy", 7: "Aristocratic", 8: "Legendary"
        }
        lifestyle = lifestyle_map.get(self.data.get('lifestyleId', 4), "Modest")
        
        return CharacterBase(
            name=self.data.get('name', 'Unknown'),
            race=self.data.get('race', {}).get('base_race', 'Unknown'),
            character_class=primary_class,
            total_level=total_level,
            alignment=alignment,
            background=self.data.get('background', {}).get('name', 'Unknown'),
            subrace=self.data.get('race', {}).get('subrace'),
            multiclass_levels=multiclass_levels if multiclass_levels else None,
            lifestyle=lifestyle
        )
    
    def _parse_characteristics(self) -> PhysicalCharacteristics:
        """Parse physical characteristics."""
        alignment_map = {
            1: "Lawful Good", 2: "Neutral Good", 3: "Chaotic Good",
            4: "Lawful Neutral", 5: "True Neutral", 6: "Chaotic Neutral",
            7: "Lawful Evil", 8: "Neutral Evil", 9: "Chaotic Evil"
        }
        alignment = alignment_map.get(self.data.get('alignmentId', 5), "True Neutral")
        
        # Get size from race
        size_map = {1: "Tiny", 2: "Small", 3: "Small", 4: "Medium", 5: "Large", 6: "Huge", 7: "Gargantuan"}
        size_id = self.data.get('race', {}).get('size_id', 4)
        size = size_map.get(size_id, "Medium")
        
        return PhysicalCharacteristics(
            alignment=alignment,
            gender=self.data.get('gender', 'Unknown'),
            eyes=self.data.get('eyes', 'Unknown'),
            size=size,
            height=self.data.get('height', '5\'0"'),
            hair=self.data.get('hair', 'Unknown'),
            skin=self.data.get('skin', 'Unknown'),
            age=self.data.get('age', 18),
            weight=f"{self.data.get('weight', 150)} lb",
            faith=self.data.get('faith')
        )
    
    def _parse_ability_scores(self) -> AbilityScores:
        """Parse ability scores, including bonuses and overrides."""
        stats = self.data.get('stats', [])
        bonus_stats = self.data.get('bonusStats', [])
        override_stats = self.data.get('overrideStats', [])
        
        # Base scores
        scores = [stat.get('value', 10) for stat in stats]
        
        # Apply bonuses
        for i, bonus in enumerate(bonus_stats):
            if bonus.get('value'):
                scores[i] += bonus['value']
        
        # Apply overrides
        for i, override in enumerate(override_stats):
            if override.get('value'):
                scores[i] = override['value']
        
        # Apply racial bonuses from modifiers
        modifiers = self.data.get('modifiers', {})
        for mod_list in modifiers.values():
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'bonus':
                        if 'strength-score' in mod.get('subType', ''):
                            scores[0] += mod.get('value', 0)
                        elif 'dexterity-score' in mod.get('subType', ''):
                            scores[1] += mod.get('value', 0)
                        elif 'constitution-score' in mod.get('subType', ''):
                            scores[2] += mod.get('value', 0)
                        elif 'intelligence-score' in mod.get('subType', ''):
                            scores[3] += mod.get('value', 0)
                        elif 'wisdom-score' in mod.get('subType', ''):
                            scores[4] += mod.get('value', 0)
                        elif 'charisma-score' in mod.get('subType', ''):
                            scores[5] += mod.get('value', 0)
        
        return AbilityScores(
            strength=scores[0] if len(scores) > 0 else 10,
            dexterity=scores[1] if len(scores) > 1 else 10,
            constitution=scores[2] if len(scores) > 2 else 10,
            intelligence=scores[3] if len(scores) > 3 else 10,
            wisdom=scores[4] if len(scores) > 4 else 10,
            charisma=scores[5] if len(scores) > 5 else 10
        )
    
    def _parse_combat_stats(self) -> CombatStats:
        """Parse combat statistics."""
        # Get HP
        max_hp = self.data.get('overrideHitPoints', 
                               self.data.get('baseHitPoints', 10))
        
        # Calculate AC from equipped armor and shield
        base_ac = 10
        dex_mod = (self._parse_ability_scores().dexterity - 10) // 2
        
        # Check for equipped armor
        for item in self.data.get('inventory', []):
            if item.get('equipped'):
                if item.get('armor_class'):
                    base_ac = item['armor_class']
                    # Check if it's heavy armor (no DEX bonus)
                    if 'Heavy Armor' in item.get('type', ''):
                        dex_mod = 0
                    # Check if it's medium armor (max +2 DEX)
                    elif 'Medium Armor' in item.get('type', ''):
                        dex_mod = min(dex_mod, 2)
        
        # Add shield bonus
        for item in self.data.get('inventory', []):
            if item.get('equipped') and item.get('type') == 'Shield':
                base_ac += item.get('armor_class', 2)
        
        armor_class = base_ac + dex_mod
        
        # Apply AC bonuses from items and features
        modifiers = self.data.get('modifiers', {})
        for mod_list in modifiers.values():
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'bonus' and mod.get('subType') == 'armor-class':
                        armor_class += mod.get('value', 0)
        
        # Calculate initiative bonus
        initiative_bonus = dex_mod
        
        # Get speed (default 30 for most races)
        speed = 30
        if 'dwarf' in self.data.get('race', {}).get('name', '').lower():
            speed = 25
        elif 'halfling' in self.data.get('race', {}).get('name', '').lower():
            speed = 25
        elif 'elf' in self.data.get('race', {}).get('name', '').lower():
            speed = 30
        
        # Get hit dice from classes
        hit_dice = {}
        for cls in self.data.get('classes', []):
            class_name = cls['name']
            level = cls['level']
            # Determine hit die based on class
            die_map = {
                'Warlock': 'd8', 'Paladin': 'd10', 'Fighter': 'd10',
                'Barbarian': 'd12', 'Sorcerer': 'd6', 'Wizard': 'd6',
                'Rogue': 'd8', 'Ranger': 'd10', 'Cleric': 'd8',
                'Druid': 'd8', 'Monk': 'd8', 'Bard': 'd8'
            }
            hit_dice[class_name] = f"{level}{die_map.get(class_name, 'd8')}"
        
        return CombatStats(
            max_hp=max_hp,
            armor_class=armor_class,
            initiative_bonus=initiative_bonus,
            speed=speed,
            hit_dice=hit_dice
        )
    
    def _parse_background_info(self) -> BackgroundInfo:
        """Parse background information."""
        bg = self.data.get('background', {})
        
        return BackgroundInfo(
            name=bg.get('name', 'Unknown'),
            feature=BackgroundFeature(
                name=bg.get('feature_name', 'Unknown'),
                description=bg.get('feature_description', '')
            ),
            skill_proficiencies=bg.get('skill_proficiencies', '').split(', ') if bg.get('skill_proficiencies') else [],
            tool_proficiencies=bg.get('tool_proficiencies', '').split(', ') if bg.get('tool_proficiencies') else [],
            language_proficiencies=bg.get('language_proficiencies', '').split(', ') if bg.get('language_proficiencies') else [],
            equipment=bg.get('equipment', '').split(', ') if bg.get('equipment') else []
        )
    
    def _parse_personality(self) -> PersonalityTraits:
        """Parse personality traits."""
        traits = self.data.get('traits', {})
        
        # Parse multi-line traits
        personality_traits = traits.get('personalityTraits', '').split('\n') if traits.get('personalityTraits') else []
        ideals = traits.get('ideals', '').split('\n') if traits.get('ideals') else []
        bonds = traits.get('bonds', '').split('\n') if traits.get('bonds') else []
        flaws = traits.get('flaws', '').split('\n') if traits.get('flaws') else []
        
        return PersonalityTraits(
            personality_traits=[t.strip() for t in personality_traits if t.strip()],
            ideals=[i.strip() for i in ideals if i.strip()],
            bonds=[b.strip() for b in bonds if b.strip()],
            flaws=[f.strip() for f in flaws if f.strip()]
        )
    
    def _parse_backstory(self) -> Backstory:
        """Parse backstory from notes."""
        notes = self.data.get('notes', {})
        backstory_text = notes.get('backstory', '')
        
        # Try to parse structured sections from backstory
        sections = []
        if backstory_text:
            # Split by double newlines or headers
            parts = backstory_text.split('\n\n')
            for part in parts:
                if part.strip():
                    lines = part.strip().split('\n')
                    if lines:
                        # First line might be a header
                        if lines[0].startswith('**') and lines[0].endswith('**'):
                            heading = lines[0].strip('*').strip()
                            content = '\n'.join(lines[1:]).strip()
                        else:
                            heading = "Section"
                            content = part.strip()
                        sections.append(BackstorySection(heading=heading, content=content))
        
        return Backstory(
            title=f"{self.data.get('name', 'Unknown')}'s Story",
            family_backstory=FamilyBackstory(
                parents="Unknown",  # Not in JSON
                sections=[]
            ),
            sections=sections
        )
    
    def _parse_organizations(self) -> List[Organization]:
        """Parse organizations from notes."""
        notes = self.data.get('notes', {})
        org_text = notes.get('organizations', '')
        
        organizations = []
        if org_text:
            # Parse organizations from text
            org_lines = org_text.split('\n\n')
            for org_line in org_lines:
                if org_line.strip():
                    # Try to extract name and description
                    parts = org_line.split(':', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        description = parts[1].strip()
                    else:
                        name = org_line.strip()
                        description = ""
                    
                    organizations.append(Organization(
                        name=name,
                        role="Member",  # Default role
                        description=description
                    ))
        
        return organizations
    
    def _parse_allies(self) -> List[Ally]:
        """Parse allies from notes."""
        notes = self.data.get('notes', {})
        allies_text = notes.get('allies', '')
        
        allies = []
        if allies_text:
            # Parse allies from numbered list
            ally_lines = allies_text.split('\n')
            for line in ally_lines:
                if line.strip():
                    # Remove numbering
                    import re
                    cleaned = re.sub(r'^\d+\.\s*\*{0,2}', '', line)
                    # Extract name and description
                    parts = cleaned.split(':', 1)
                    if len(parts) == 2:
                        name = parts[0].strip('*').strip()
                        description = parts[1].strip()
                    else:
                        name = cleaned.strip('*').strip()
                        description = ""
                    
                    if name:
                        allies.append(Ally(
                            name=name,
                            description=description,
                            title=None
                        ))
        
        return allies
    
    def _parse_enemies(self) -> List[Enemy]:
        """Parse enemies from notes."""
        notes = self.data.get('notes', {})
        enemies_text = notes.get('enemies', '')
        
        enemies = []
        if enemies_text:
            enemy_lines = enemies_text.split('\n')
            for line in enemy_lines:
                if line.strip():
                    enemies.append(Enemy(
                        name=line.strip(),
                        description=""
                    ))
        
        return enemies
    
    def _parse_proficiencies(self) -> List[Proficiency]:
        """Parse all proficiencies from modifiers."""
        proficiencies = []
        modifiers = self.data.get('modifiers', {})
        
        for mod_list in modifiers.values():
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'proficiency':
                        subtype = mod.get('friendlySubtypeName', '')
                        # Determine proficiency type
                        if 'armor' in subtype.lower():
                            prof_type = 'armor'
                        elif 'weapon' in subtype.lower() or any(w in subtype.lower() for w in ['sword', 'axe', 'hammer', 'bow']):
                            prof_type = 'weapon'
                        elif 'tools' in subtype.lower() or 'kit' in subtype.lower():
                            prof_type = 'tool'
                        elif 'saving' in subtype.lower():
                            prof_type = 'saving_throw'
                        elif any(s in subtype.lower() for s in ['insight', 'perception', 'athletics', 'acrobatics', 'investigation', 'persuasion', 'deception']):
                            prof_type = 'skill'
                        else:
                            prof_type = 'skill'
                        
                        proficiencies.append(Proficiency(
                            type=prof_type,
                            name=subtype
                        ))
        
        # Add languages
        for mod_list in modifiers.values():
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'language':
                        proficiencies.append(Proficiency(
                            type='language',
                            name=mod.get('friendlySubtypeName', '')
                        ))
        
        return proficiencies
    
    def _parse_damage_modifiers(self) -> List[DamageModifier]:
        """Parse damage resistances, immunities, and vulnerabilities."""
        damage_mods = []
        modifiers = self.data.get('modifiers', {})
        
        for mod_list in modifiers.values():
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') in ['resistance', 'immunity', 'vulnerability']:
                        damage_mods.append(DamageModifier(
                            damage_type=mod.get('friendlySubtypeName', ''),
                            modifier_type=mod['type']
                        ))
        
        return damage_mods
    
    def _parse_passive_scores(self) -> PassiveScores:
        """Calculate passive scores."""
        ability_scores = self._parse_ability_scores()
        
        # Calculate modifiers
        wis_mod = (ability_scores.wisdom - 10) // 2
        int_mod = (ability_scores.intelligence - 10) // 2
        dex_mod = (ability_scores.dexterity - 10) // 2
        
        # Base passive scores
        passive_perception = 10 + wis_mod
        passive_investigation = 10 + int_mod
        passive_insight = 10 + wis_mod
        passive_stealth = 10 + dex_mod
        
        # Check for proficiency in skills
        # This would need to check proficiencies and add proficiency bonus
        
        return PassiveScores(
            perception=passive_perception,
            investigation=passive_investigation,
            insight=passive_insight,
            stealth=passive_stealth
        )
    
    def _parse_senses(self) -> Senses:
        """Parse special senses from modifiers."""
        senses_dict = {}
        modifiers = self.data.get('modifiers', {})
        
        for mod_list in modifiers.values():
            if isinstance(mod_list, list):
                for mod in mod_list:
                    if mod.get('type') == 'set-base' and 'darkvision' in mod.get('subType', ''):
                        senses_dict['darkvision'] = mod.get('value', 0)
        
        return Senses(senses=senses_dict)
    
    def _parse_action_economy(self) -> ActionEconomy:
        """Parse action economy from features."""
        # Check for Extra Attack
        attacks_per_action = 1
        for cls in self.data.get('classes', []):
            for feature in cls.get('features', []):
                if 'Extra Attack' in feature.get('name', ''):
                    attacks_per_action = 2
                    break
        
        # Parse special actions
        actions = []
        
        # Add Channel Divinity options if Paladin
        for cls in self.data.get('classes', []):
            if cls.get('name') == 'Paladin':
                for feature in cls.get('features', []):
                    if 'Channel Divinity' in feature.get('name', ''):
                        actions.append(SpecialAction(
                            name=feature['name'],
                            type='action',
                            description=feature.get('description', ''),
                            uses={'per': 'short_rest', 'count': 1}
                        ))
        
        return ActionEconomy(
            attacks_per_action=attacks_per_action,
            actions=actions
        )
    
    def _parse_features_and_traits(self) -> FeaturesAndTraits:
        """Parse all features and traits."""
        features = FeaturesAndTraits()
        
        # Parse class features
        for cls in self.data.get('classes', []):
            class_name = cls['name']
            level = cls['level']
            class_features = []
            
            for feature in cls.get('features', []):
                class_features.append(Feature(
                    name=feature['name'],
                    description=feature.get('description', ''),
                    passive=True,  # Default, would need parsing
                    subclass='subclass' in cls and feature.get('level_required', 0) >= 3
                ))
            
            features.class_features[class_name] = ClassFeatures(
                level=level,
                features=class_features
            )
        
        # Parse racial traits
        race_data = self.data.get('race', {})
        for trait in race_data.get('racial_traits', []):
            features.racial_traits.append(Feature(
                name=trait['name'],
                description=trait.get('description', ''),
                passive=True
            ))
        
        # Parse feats
        for feat in self.data.get('feats', []):
            features.feats.append(Feature(
                name=feat['name'],
                description=feat.get('description', ''),
                passive=True
            ))
        
        return features
    
    def _parse_inventory(self) -> Inventory:
        """Parse inventory items."""
        inventory = Inventory(total_weight=0.0)
        
        for item in self.data.get('inventory', []):
            inv_item = InventoryItem(
                name=item.get('name', 'Unknown'),
                type=item.get('type', 'Gear'),
                rarity=item.get('rarity', 'Common'),
                requires_attunement=item.get('requires_attunement', False),
                equipped=item.get('equipped', False),
                weight=item.get('weight', 0),
                cost=str(item.get('cost', 0)) if item.get('cost') else None,
                quantity=item.get('quantity', 1),
                armor_class=item.get('armor_class')
            )
            
            # Parse damage if present
            if item.get('damage'):
                damage_data = item['damage']
                inv_item.damage = DamageInfo(
                    base=damage_data.get('diceString'),
                    type=item.get('damage_type', 'slashing')
                )
            
            # Parse properties
            if item.get('properties'):
                for prop in item['properties']:
                    inv_item.properties.append(prop.get('name', ''))
            
            # Add to appropriate category
            if inv_item.equipped:
                category = 'armor' if 'armor' in inv_item.type.lower() else 'weapons' if any(w in inv_item.type.lower() for w in ['sword', 'weapon', 'dagger']) else 'other'
                if category not in inventory.equipped_items:
                    inventory.equipped_items[category] = []
                inventory.equipped_items[category].append(inv_item)
            else:
                inventory.backpack.append(inv_item)
            
            # Update total weight
            inventory.total_weight += (inv_item.weight or 0) * inv_item.quantity
        
        # Add currencies as valuables
        currencies = self.data.get('currencies', {})
        for currency, amount in currencies.items():
            if amount > 0:
                inventory.valuables.append({
                    'type': 'currency',
                    'name': currency.upper(),
                    'amount': amount
                })
        
        return inventory
    
    def _parse_spell_list(self) -> SpellList:
        """Parse spells and spellcasting information."""
        spell_list = SpellList()
        
        # Parse spellcasting info for each class
        for cls in self.data.get('classes', []):
            class_name = cls['name']
            spellcasting_ability_id = cls.get('spellcasting_ability_id')
            
            if spellcasting_ability_id:
                # Map ability ID to name
                ability_map = {1: 'strength', 2: 'dexterity', 3: 'constitution',
                              4: 'intelligence', 5: 'wisdom', 6: 'charisma'}
                ability = ability_map.get(spellcasting_ability_id, 'charisma')
                
                # Calculate spell save DC and attack bonus
                ability_scores = self._parse_ability_scores()
                ability_mod = (getattr(ability_scores, ability) - 10) // 2
                prof_bonus = 2 + ((cls['level'] - 1) // 4)  # Proficiency bonus calculation
                
                spell_list.spellcasting[class_name] = SpellcastingInfo(
                    ability=ability,
                    spell_save_dc=8 + prof_bonus + ability_mod,
                    spell_attack_bonus=prof_bonus + ability_mod
                )
        
        # Parse class spells
        for class_spells in self.data.get('classSpells', []):
            class_id = class_spells.get('characterClassId')
            # Find corresponding class name
            class_name = 'Unknown'
            for cls in self.data.get('classes', []):
                # This would need proper ID mapping
                class_name = cls['name']
                break
            
            if class_name not in spell_list.spells:
                spell_list.spells[class_name] = {}
            
            for spell_data in class_spells.get('spells', []):
                spell_def = spell_data.get('definition', {})
                
                # Determine spell level category
                level = spell_def.get('level', 0)
                if level == 0:
                    level_key = 'cantrips'
                else:
                    level_key = f'level_{level}'
                
                if level_key not in spell_list.spells[class_name]:
                    spell_list.spells[class_name][level_key] = []
                
                # Parse components
                components = SpellComponents()
                for comp in spell_def.get('components', []):
                    if comp == 1:
                        components.verbal = True
                    elif comp == 2:
                        components.somatic = True
                    elif comp == 3:
                        components.material = spell_def.get('componentsDescription', True)
                
                spell = Spell(
                    name=spell_def.get('name', 'Unknown'),
                    level=level,
                    school=spell_def.get('school', 'Unknown'),
                    casting_time=spell_def.get('castingTimeDescription', '1 action'),
                    range=spell_def.get('range', {}).get('rangeValue', 0) or 'Self',
                    components=components,
                    duration=f"{spell_def.get('duration', {}).get('durationInterval', 0)} {spell_def.get('duration', {}).get('durationUnit', '')}",
                    description=spell_def.get('description', ''),
                    concentration=spell_def.get('concentration', False),
                    ritual=spell_def.get('ritual', False)
                )
                
                spell_list.spells[class_name][level_key].append(spell)
        
        return spell_list
    
    def _parse_objectives(self) -> ObjectivesAndContracts:
        """Parse objectives and contracts (not in JSON, return empty)."""
        return ObjectivesAndContracts(
            active_contracts=[],
            current_objectives=[],
            completed_objectives=[],
            contract_templates={},
            metadata={'source': 'dndbeyond', 'parsed_date': datetime.now().isoformat()}
        )
    
    def _parse_notes(self) -> Dict[str, Any]:
        """Parse additional notes."""
        notes = self.data.get('notes', {})
        return {
            'other_notes': notes.get('otherNotes', ''),
            'personal_possessions': notes.get('personalPossessions', ''),
            'other_holdings': notes.get('otherHoldings', ''),
            'custom_items': self.data.get('customItems', [])
        }


def load_and_parse_character(file_path: Union[str, Path]) -> Character:
    """
    Load a D&D Beyond JSON file and parse it into a Character object.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Parsed Character object
    """
    file_path = Path(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    parser = DnDBeyondParser(json_data)
    return parser.parse()


def export_character_to_json(character: Character, output_path: Optional[str] = None) -> str:
    """Export a Character object to JSON format."""
    # Convert dataclass to dictionary
    char_dict = asdict(character)
    
    # Convert datetime objects to ISO format strings
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        else:
            return obj
    
    char_dict = convert_datetime(char_dict)
    
    # Generate output filename if not provided
    if output_path is None:
        char_name = character.character_base.name.replace(' ', '_').lower()
        output_path = f"{char_name}_parsed_character.json"
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(char_dict, f, indent=2, ensure_ascii=False)
    
    return output_path


def main():
    """Example usage of the parser."""
    # Default to DNDBEYOND_ULTRA_CLEANED.json if no file specified
    if len(sys.argv) < 2:
        project_root = Path(__file__).parent.parent
        file_path = project_root / "DNDBEYOND_ULTRA_CLEANED.json"
        if not file_path.exists():
            print("Usage: python parse_character.py [json_file_path]")
            print("Default file DNDBEYOND_ULTRA_CLEANED.json not found.")
            sys.exit(1)
        print(f"Using default file: {file_path}")
    else:
        file_path = sys.argv[1]
    
    try:
        character = load_and_parse_character(file_path)
        
        # Print basic character info
        print(f"\n{'='*60}")
        print(f"CHARACTER SHEET: {character.character_base.name}")
        print(f"{'='*60}")
        
        print(f"\n--- BASIC INFO ---")
        print(f"Race: {character.character_base.race}")
        if character.character_base.subrace:
            print(f"Subrace: {character.character_base.subrace}")
        print(f"Class: {character.character_base.character_class} (Level {character.character_base.total_level})")
        if character.character_base.multiclass_levels:
            print(f"Multiclass: {character.character_base.multiclass_levels}")
        print(f"Background: {character.character_base.background}")
        print(f"Alignment: {character.character_base.alignment}")
        print(f"Lifestyle: {character.character_base.lifestyle}")
        
        print(f"\n--- PHYSICAL CHARACTERISTICS ---")
        print(f"Age: {character.characteristics.age}")
        print(f"Gender: {character.characteristics.gender}")
        print(f"Height: {character.characteristics.height}")
        print(f"Weight: {character.characteristics.weight}")
        print(f"Eyes: {character.characteristics.eyes}")
        print(f"Hair: {character.characteristics.hair}")
        print(f"Skin: {character.characteristics.skin}")
        print(f"Size: {character.characteristics.size}")
        if character.characteristics.faith:
            print(f"Faith: {character.characteristics.faith}")
        
        print(f"\n--- ABILITY SCORES ---")
        print(f"STR: {character.ability_scores.strength}")
        print(f"DEX: {character.ability_scores.dexterity}")
        print(f"CON: {character.ability_scores.constitution}")
        print(f"INT: {character.ability_scores.intelligence}")
        print(f"WIS: {character.ability_scores.wisdom}")
        print(f"CHA: {character.ability_scores.charisma}")
        
        print(f"\n--- COMBAT STATS ---")
        print(f"HP: {character.combat_stats.max_hp}")
        print(f"AC: {character.combat_stats.armor_class}")
        print(f"Initiative: +{character.combat_stats.initiative_bonus}")
        print(f"Speed: {character.combat_stats.speed} ft")
        if character.combat_stats.hit_dice:
            print(f"Hit Dice: {character.combat_stats.hit_dice}")
        
        print(f"\n--- PASSIVE SCORES ---")
        if character.passive_scores:
            print(f"Passive Perception: {character.passive_scores.perception}")
            print(f"Passive Investigation: {character.passive_scores.investigation}")
            print(f"Passive Insight: {character.passive_scores.insight}")
            print(f"Passive Stealth: {character.passive_scores.stealth}")
        
        print(f"\n--- SENSES ---")
        if character.senses and character.senses.senses:
            for sense, value in character.senses.senses.items():
                print(f"{sense.capitalize()}: {value} ft")
        
        print(f"\n--- PERSONALITY ---")
        if character.personality.personality_traits:
            print(f"Traits: {', '.join(character.personality.personality_traits)}")
        if character.personality.ideals:
            print(f"Ideals: {', '.join(character.personality.ideals)}")
        if character.personality.bonds:
            print(f"Bonds: {', '.join(character.personality.bonds)}")
        if character.personality.flaws:
            print(f"Flaws: {', '.join(character.personality.flaws)}")
        
        print(f"\n--- PROFICIENCIES ---")
        prof_types = {}
        for prof in character.proficiencies:
            if prof.type not in prof_types:
                prof_types[prof.type] = []
            prof_types[prof.type].append(prof.name)
        
        for prof_type, names in prof_types.items():
            print(f"{prof_type.capitalize()}: {', '.join(names)}")
        
        print(f"\n--- DAMAGE MODIFIERS ---")
        for mod in character.damage_modifiers:
            print(f"{mod.modifier_type.capitalize()}: {mod.damage_type}")
        
        print(f"\n--- INVENTORY ---")
        print(f"Total Weight: {character.inventory.total_weight} {character.inventory.weight_unit}")
        print(f"Equipped Items: {sum(len(items) for items in character.inventory.equipped_items.values())} items")
        print(f"Backpack: {len(character.inventory.backpack)} items")
        if character.inventory.valuables:
            print(f"Valuables:")
            for valuable in character.inventory.valuables:
                if valuable.get('type') == 'currency':
                    print(f"  {valuable['name']}: {valuable['amount']}")
        
        print(f"\n--- SPELLCASTING ---")
        if character.spell_list and character.spell_list.spellcasting:
            for class_name, info in character.spell_list.spellcasting.items():
                print(f"{class_name}:")
                print(f"  Spellcasting Ability: {info.ability.capitalize()}")
                print(f"  Spell Save DC: {info.spell_save_dc}")
                print(f"  Spell Attack Bonus: +{info.spell_attack_bonus}")
        
        if character.spell_list and character.spell_list.spells:
            for class_name, spell_levels in character.spell_list.spells.items():
                print(f"\n{class_name} Spells:")
                for level, spells in spell_levels.items():
                    if spells:
                        spell_names = [s.name for s in spells]
                        print(f"  {level}: {', '.join(spell_names)}")
        
        print(f"\n--- ALLIES ---")
        for ally in character.allies[:5]:  # Show first 5
            print(f"  • {ally.name}: {ally.description}")
        if len(character.allies) > 5:
            print(f"  ... and {len(character.allies) - 5} more")
        
        print(f"\n--- ENEMIES ---")
        for enemy in character.enemies[:5]:  # Show first 5
            print(f"  • {enemy.name}")
        
        print(f"\n--- ORGANIZATIONS ---")
        for org in character.organizations:
            print(f"  • {org.name} ({org.role})")
        
        print(f"\n{'='*60}\n")
        
        # Export to JSON
        output_file = export_character_to_json(character)
        print(f"Character exported to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()