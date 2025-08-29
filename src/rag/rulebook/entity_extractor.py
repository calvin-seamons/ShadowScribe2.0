"""
D&D 5e Rulebook Storage System - Entity Extraction
"""

import re
from typing import Dict, List
from .types import DnDEntityType, RulebookSection, DnDEntity


class RulebookEntityExtractor:
    """Handles extraction of D&D 5e game entities from rulebook sections"""
    
    def __init__(self):
        self._storage = None  # Will be set when extraction is called
    
    def extract_entities(self, content: str, sections: Dict[str, RulebookSection], storage=None) -> List[DnDEntity]:
        """Extract all D&D 5e game entities from sections using intelligent parsing"""
        self._storage = storage  # Store reference for use in helper methods
        entities = []
        
        # Extract common D&D 5e entities with fallback for when no rulebook is loaded
        entities.extend(self._extract_default_entities())
        
        # If sections are available, extract from actual content
        if sections:
            entities.extend(self._extract_races(sections))
            entities.extend(self._extract_classes(sections))
            entities.extend(self._extract_spells(sections))
            entities.extend(self._extract_conditions(sections))
        
        return entities
    
    def _extract_default_entities(self) -> List[DnDEntity]:
        """Extract common D&D 5e entities as defaults"""
        entities = []
        
        # Default races
        race_names = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling']
        for race_name in race_names:
            entities.append(DnDEntity(
                name=race_name,
                entity_type=DnDEntityType.RACE,
                section_ids=[],
                aliases=[race_name.lower()]
            ))
        
        # Default classes
        class_names = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']
        for class_name in class_names:
            entities.append(DnDEntity(
                name=class_name,
                entity_type=DnDEntityType.CLASS,
                section_ids=[],
                aliases=[class_name.lower()]
            ))
        
        # Default conditions
        condition_names = ['Blinded', 'Charmed', 'Deafened', 'Frightened', 'Grappled', 'Incapacitated', 'Invisible', 'Paralyzed', 'Petrified', 'Poisoned', 'Prone', 'Restrained', 'Stunned', 'Unconscious']
        for condition_name in condition_names:
            entities.append(DnDEntity(
                name=condition_name,
                entity_type=DnDEntityType.CONDITION,
                section_ids=[],
                aliases=[condition_name.lower()]
            ))
        
        return entities
    
    def _extract_races(self, sections: Dict[str, RulebookSection]) -> List[DnDEntity]:
        """Extract race entities from the races chapter"""
        races = []
        races_chapter_id = 'chapter-races'
        
        if races_chapter_id in sections:
            chapter = sections[races_chapter_id]
            
            # Look for race subsections or parse content for race names
            race_patterns = [
                r'^(Human|Elf|Dwarf|Halfling|Dragonborn|Gnome|Half-Elf|Half-Orc|Tiefling)',
                r'## ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Section headers
            ]
            
            for pattern in race_patterns:
                matches = re.finditer(pattern, chapter.content, re.MULTILINE)
                for match in matches:
                    race_name = match.group(1).strip()
                    if len(race_name) > 2:  # Filter out short matches
                        entity = DnDEntity(
                            name=race_name,
                            entity_type=DnDEntityType.RACE,
                            section_ids=[races_chapter_id],
                            aliases=[race_name.lower()]
                        )
                        races.append(entity)
        
        return races
    
    def _extract_classes(self, sections: Dict[str, RulebookSection]) -> List[DnDEntity]:
        """Extract class entities from the classes chapter"""
        entities = []
        
        # Base classes and their common variations
        base_classes = {
            'Barbarian': ['barbarian', 'barb'],
            'Bard': ['bard'],
            'Cleric': ['cleric'],
            'Druid': ['druid'],
            'Fighter': ['fighter'],
            'Monk': ['monk'],
            'Paladin': ['paladin', 'pally'],
            'Ranger': ['ranger'],
            'Rogue': ['rogue'],
            'Sorcerer': ['sorcerer', 'sorc'],
            'Warlock': ['warlock', 'lock'],
            'Wizard': ['wizard', 'wiz']
        }
        
        # Subclasses/archetypes we should look for
        subclass_patterns = {
            'Barbarian': ['Path of the Berserker', 'Path of the Totem Warrior', 'Path of the Ancestral Guardian'],
            'Bard': ['College of Lore', 'College of Valor', 'College of Glamour'],
            'Cleric': ['Life Domain', 'Light Domain', 'Knowledge Domain', 'War Domain', 'Death Domain'],
            'Druid': ['Circle of the Land', 'Circle of the Moon', 'Circle of Dreams'],
            # Add more as found in content
        }
        
        # Class features that should be entities
        important_features = [
            # Barbarian features
            'Rage', 'Unarmored Defense', 'Reckless Attack', 'Danger Sense', 'Extra Attack',
            'Fast Movement', 'Feral Instinct', 'Brutal Critical', 'Relentless Rage', 
            'Persistent Rage', 'Indomitable Might', 'Primal Champion',
            
            # Bard features
            'Bardic Inspiration', 'Jack of All Trades', 'Song of Rest', 'Expertise',
            'Font of Inspiration', 'Countercharm', 'Magical Secrets', 'Superior Inspiration',
            
            # Cleric features
            'Channel Divinity', 'Turn Undead', 'Divine Intervention', 'Destroy Undead',
            'Divine Strike', 'Blessed Recovery',
            
            # Druid features
            'Wild Shape', 'Druidic', 'Timeless Body', 'Beast Spells', 'Archdruid',
            'Wild Companion', 'Nature\'s Ward',
            
            # Fighter features
            'Action Surge', 'Second Wind', 'Fighting Style', 'Indomitable',
            'Extra Attack', 'Remarkable Athlete',
            
            # Monk features
            'Ki', 'Martial Arts', 'Unarmored Movement', 'Deflect Missiles',
            'Slow Fall', 'Stunning Strike', 'Ki-Empowered Strikes', 'Evasion',
            'Stillness of Mind', 'Purity of Body', 'Diamond Soul', 'Empty Body', 'Perfect Self',
            
            # Paladin features
            'Divine Smite', 'Lay on Hands', 'Divine Sense', 'Aura of Protection',
            'Aura of Courage', 'Improved Divine Smite', 'Cleansing Touch',
            
            # Ranger features
            'Favored Enemy', 'Natural Explorer', 'Primeval Awareness',
            'Land\'s Stride', 'Hide in Plain Sight', 'Vanish', 'Feral Senses', 'Foe Slayer',
            
            # Rogue features
            'Sneak Attack', 'Thieves\' Cant', 'Cunning Action', 'Evasion',
            'Uncanny Dodge', 'Reliable Talent', 'Blindsense', 'Slippery Mind', 'Elusive', 'Stroke of Luck',
            
            # Sorcerer features
            'Sorcery Points', 'Metamagic', 'Font of Magic', 'Sorcerous Restoration',
            
            # Warlock features
            'Eldritch Invocations', 'Pact Boon', 'Mystic Arcanum', 'Eldritch Master',
            
            # Wizard features
            'Arcane Recovery', 'Spell Mastery', 'Signature Spells'
        ]
        
        # Process each section
        for section_id, section in sections.items():
            # Skip if not in classes chapter - but be more liberal about what we include
            if not (section_id.startswith('chapter-classes') or 
                    section_id.startswith('section-') and 
                    (any(cls.lower() in section_id for cls in base_classes) or
                     any(feature.lower().replace(' ', '-').replace('\'', '') in section_id 
                         for feature in important_features))):
                continue
            
            # Get both section content and full content for different purposes
            section_content = section.content
            if self._storage:
                full_content = section.get_full_content(include_children=True, storage=self._storage)
            else:
                full_content = section_content
            content_lower = full_content.lower()
            
            # Extract base classes
            for class_name, aliases in base_classes.items():
                # Check section title first
                if class_name.lower() in section.title.lower():
                    entity = DnDEntity(
                        name=class_name,
                        entity_type=DnDEntityType.CLASS,
                        section_ids=[section_id],
                        aliases=aliases,
                        properties={
                            'category': 'base_class',
                            'source': 'PHB'
                        }
                    )
                    if not self._entity_exists(entities, entity.name):
                        entities.append(entity)
                
                # Also check content for references
                elif any(alias in content_lower for alias in aliases):
                    # Update existing entity's section_ids if found
                    existing = self._find_entity(entities, class_name)
                    if existing and section_id not in existing.section_ids:
                        existing.section_ids.append(section_id)
            
            # Extract subclasses/archetypes
            for base_class, subclasses in subclass_patterns.items():
                for subclass_name in subclasses:
                    if subclass_name.lower() in content_lower or subclass_name.lower() in section.title.lower():
                        entity = DnDEntity(
                            name=subclass_name,
                            entity_type=DnDEntityType.SUBCLASS,
                            section_ids=[section_id],
                            aliases=[subclass_name.lower(), subclass_name.replace(' ', '-').lower()],
                            properties={
                                'base_class': base_class,
                                'category': 'subclass',
                                'source': 'PHB'
                            }
                        )
                        if not self._entity_exists(entities, entity.name):
                            entities.append(entity)
            
            # Extract class features
            for feature_name in important_features:
                feature_lower = feature_name.lower()
                # Look for feature in section title (exact match) or as a heading in content
                title_match = (section.title.lower() == feature_lower or 
                              section.title.lower().startswith(feature_lower + ' ') or
                              section.title.lower().startswith(feature_lower + ':') or
                              section.title.lower().endswith(' ' + feature_lower))
                
                content_match = (f"### {feature_name}" in full_content or
                               f"#### {feature_name}" in full_content or
                               f"## {feature_name}" in full_content or
                               re.search(rf'\*\*{re.escape(feature_name)}\*\*', full_content))
                
                if title_match or content_match:
                    # Determine parent class using section hierarchy
                    parent_class = self._determine_parent_class(section, sections, base_classes)
                    
                    entity = DnDEntity(
                        name=feature_name,
                        entity_type=DnDEntityType.FEATURE,
                        section_ids=[section_id],
                        aliases=[feature_lower, feature_lower.replace(' ', '-')],
                        properties={
                            'category': 'class_feature',
                            'parent_class': parent_class,
                            'source': 'PHB'
                        }
                    )
                    if not self._entity_exists(entities, entity.name):
                        entities.append(entity)
            
            # Extract multiclass references
            multiclass_pattern = r'multiclass(?:ing)?|multiclassed'
            if re.search(multiclass_pattern, content_lower):
                entity = DnDEntity(
                    name='Multiclassing',
                    entity_type=DnDEntityType.RULE,
                    section_ids=[section_id],
                    aliases=['multiclass', 'multi-class', 'multiclassed'],
                    properties={
                        'category': 'character_rule',
                        'source': 'PHB'
                    }
                )
                if not self._entity_exists(entities, entity.name):
                    entities.append(entity)
            
            # Extract level progression tables (useful for queries)
            if (('level' in content_lower and 'proficiency bonus' in content_lower) or 
                'level | proficiency' in content_lower or
                ('| level' in content_lower and 'proficiency' in content_lower)):
                # This section contains a class progression table
                for class_name in base_classes.keys():
                    if (class_name.lower() in section.title.lower() or 
                        class_name.lower() in section_id or
                        class_name.lower() in content_lower[:200]):  # Check beginning of content
                        table_entity = DnDEntity(
                            name=f"{class_name} Progression Table",
                            entity_type=DnDEntityType.TABLE,
                            section_ids=[section_id],
                            aliases=[f"{class_name.lower()}-table", f"{class_name.lower()}-progression"],
                            properties={
                                'category': 'progression_table',
                                'class': class_name,
                                'source': 'PHB'
                            }
                        )
                        if not self._entity_exists(entities, table_entity.name):
                            entities.append(table_entity)
        
        return entities

    def _extract_spells(self, sections: Dict[str, RulebookSection]) -> List[DnDEntity]:
        """Extract spell entities from spell sections"""
        spells = []
        
        # Look for spell-related sections
        spell_section_patterns = ['spell', 'magic']
        
        for section_id, section in sections.items():
            if any(pattern in section_id.lower() for pattern in spell_section_patterns):
                # Use regex to find spell names in spell descriptions
                spell_patterns = [
                    r'^\*([A-Z][a-z\s]+)\*',  # Italic spell names
                    r'^([A-Z][a-z\s]+)\s*\(',  # Spell names followed by parentheses
                    r'## ([A-Z][a-z\s]+)',     # Section headers
                ]
                
                for pattern in spell_patterns:
                    matches = re.finditer(pattern, section.content, re.MULTILINE)
                    for match in matches:
                        spell_name = match.group(1).strip()
                        if len(spell_name) > 3 and ' ' in spell_name:  # Filter for proper spell names
                            entity = DnDEntity(
                                name=spell_name,
                                entity_type=DnDEntityType.SPELL,
                                section_ids=[section_id],
                                aliases=[spell_name.lower()]
                            )
                            spells.append(entity)
        
        return spells
    
    def _extract_conditions(self, sections: Dict[str, RulebookSection]) -> List[DnDEntity]:
        """Extract condition entities from the conditions section"""
        conditions = []
        conditions_section_id = 'section-conditions'
        
        if conditions_section_id in sections:
            section = sections[conditions_section_id]
            
            # Common D&D 5e conditions
            condition_names = [
                'Blinded', 'Charmed', 'Deafened', 'Frightened', 'Grappled',
                'Incapacitated', 'Invisible', 'Paralyzed', 'Petrified',
                'Poisoned', 'Prone', 'Restrained', 'Stunned', 'Unconscious'
            ]
            
            for condition_name in condition_names:
                if condition_name.lower() in section.content.lower():
                    entity = DnDEntity(
                        name=condition_name,
                        entity_type=DnDEntityType.CONDITION,
                        section_ids=[conditions_section_id],
                        aliases=[condition_name.lower()]
                    )
                    conditions.append(entity)
        
        return conditions

    def _entity_exists(self, entities: List[DnDEntity], name: str) -> bool:
        """Check if entity already exists in list"""
        return any(e.name == name for e in entities)

    def _find_entity(self, entities: List[DnDEntity], name: str) -> DnDEntity:
        """Find entity by name in list"""
        for entity in entities:
            if entity.name == name:
                return entity
        return None
    
    def _determine_parent_class(self, section: RulebookSection, sections: Dict[str, RulebookSection], base_classes: dict) -> str:
        """Determine which class a feature belongs to using section hierarchy"""
        
        # Special handling for specific features that are primarily associated with certain classes
        feature_class_mapping = {
            'Channel Divinity': 'Cleric',  # Primary class even though it appears in multiclassing
            'Turn Undead': 'Cleric',
            'Divine Intervention': 'Cleric',
            'Lay on Hands': 'Paladin',
            'Divine Smite': 'Paladin',
            'Bardic Inspiration': 'Bard',
            'Wild Shape': 'Druid',
            'Rage': 'Barbarian',
            'Ki': 'Monk',
            'Sneak Attack': 'Rogue',
            'Eldritch Invocations': 'Warlock',
            'Metamagic': 'Sorcerer',
            'Arcane Recovery': 'Wizard',
            'Action Surge': 'Fighter'
        }
        
        # Check if this is a feature with a known primary class
        if section.title in feature_class_mapping:
            return feature_class_mapping[section.title]
        
        # First check the section itself
        for class_name in base_classes.keys():
            if class_name.lower() in section.title.lower():
                return class_name
        
        # Check parent sections up the hierarchy
        current_section = section
        max_depth = 5  # Prevent infinite loops
        depth = 0
        
        while current_section.parent_id and depth < max_depth:
            parent_id = current_section.parent_id
            if parent_id in sections:
                parent_section = sections[parent_id]
                
                # Check if parent section title contains a class name
                for class_name in base_classes.keys():
                    if class_name.lower() in parent_section.title.lower():
                        return class_name
                
                current_section = parent_section
                depth += 1
            else:
                break
        
        # Fallback: check section ID for class name
        for class_name in base_classes.keys():
            if class_name.lower() in section.id:
                return class_name
        
        return None
