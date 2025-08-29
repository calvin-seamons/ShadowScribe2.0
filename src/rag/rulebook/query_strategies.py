"""
D&D 5e Rulebook Storage System - Query Strategies
"""

import re
from typing import List, Optional
from .types import RulebookQueryResult, DnDEntityType, DnDEntity, RulebookSection


class RulebookQueryStrategies:
    """Handles all query strategies for different D&D 5e rulebook intentions"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def describe_entity(self, entities: List[str]) -> RulebookQueryResult:
        """Direct section grab for entity description"""
        if not entities:
            return RulebookQueryResult(
                content="No entity specified",
                confidence=0.0
            )
        
        entity = self.storage.resolve_entity(entities[0])
        if not entity:
            return RulebookQueryResult(
                content=f"Entity '{entities[0]}' not found",
                confidence=0.0,
                fallback_suggestions=self.storage._suggest_similar_entities(entities[0])
            )
        
        sections = []
        content_parts = []
        
        for section_id in entity.section_ids:
            if section_id in self.storage.sections:
                section = self.storage.sections[section_id]
                sections.append(section)
                content_parts.append(section.get_full_content())
        
        return RulebookQueryResult(
            content='\n\n'.join(content_parts),
            sections=sections,
            entities=[entity],
            confidence=0.9
        )
    
    def compare_entities(self, entities: List[str]) -> RulebookQueryResult:
        """Multi-section grab for entity comparison"""
        if len(entities) < 2:
            return RulebookQueryResult(
                content="Need at least 2 entities to compare",
                confidence=0.0
            )
        
        resolved_entities = []
        sections = []
        content_parts = []
        
        for entity_name in entities[:3]:  # Limit to 3 for comparison
            entity = self.storage.resolve_entity(entity_name)
            if entity:
                resolved_entities.append(entity)
                for section_id in entity.section_ids:
                    if section_id in self.storage.sections:
                        section = self.storage.sections[section_id]
                        sections.append(section)
                        content_parts.append(f"## {entity.name}\n{section.content}")
        
        if len(resolved_entities) < 2:
            return RulebookQueryResult(
                content="Could not find enough entities to compare",
                confidence=0.3
            )
        
        return RulebookQueryResult(
            content='\n\n---\n\n'.join(content_parts),
            sections=sections,
            entities=resolved_entities,
            confidence=0.85
        )
    
    def level_progression(self, entities: List[str]) -> RulebookQueryResult:
        """Get class features at specific level"""
        if not entities:
            return RulebookQueryResult(
                content="No class specified",
                confidence=0.0
            )
        
        # First entity should be class name
        class_entity = self.storage.resolve_entity(entities[0], DnDEntityType.CLASS)
        if not class_entity:
            return RulebookQueryResult(
                content=f"Class '{entities[0]}' not found",
                confidence=0.0
            )
        
        # Extract level if provided
        level = None
        for entity in entities[1:]:
            if entity.isdigit():
                level = int(entity)
                break
        
        sections = []
        content_parts = []
        
        # Try to find the progression table entity first
        table_name = f"{class_entity.name} Progression Table"
        table_entity = self.storage.resolve_entity(table_name, DnDEntityType.TABLE)
        if table_entity:
            for section_id in table_entity.section_ids:
                if section_id in self.storage.sections:
                    section = self.storage.sections[section_id]
                    sections.append(section)
                    if level:
                        # Filter content for specific level
                        content = section.content
                        level_pattern = rf'^.*{level}(?:st|nd|rd|th).*$'
                        level_lines = [line for line in content.split('\n') 
                                     if re.search(level_pattern, line, re.MULTILINE | re.IGNORECASE)]
                        if level_lines:
                            content_parts.append(f"## Level {level} Features\n" + '\n'.join(level_lines))
                        else:
                            content_parts.append(content)
                    else:
                        content_parts.append(section.content)
        
        # Fallback to class sections
        if not content_parts:
            for section_id in class_entity.section_ids:
                if section_id in self.storage.sections:
                    section = self.storage.sections[section_id]
                    sections.append(section)
                    
                    if level:
                        # Filter content for specific level
                        content_parts.append(f"## {class_entity.name} - Level {level}\n")
                        # Would parse and filter for level-specific features
                        content_parts.append(section.content)
                    else:
                        content_parts.append(section.get_full_content(include_children=True, storage=self.storage))
        
        return RulebookQueryResult(
            content='\n\n'.join(content_parts),
            sections=sections,
            entities=[class_entity],
            confidence=0.9
        )
    
    def action_options(self, entities: List[str]) -> RulebookQueryResult:
        """Get combat actions section"""
        action_section_id = 'section-actions-in-combat'
        
        if action_section_id in self.storage.sections:
            section = self.storage.sections[action_section_id]
            return RulebookQueryResult(
                content=section.get_full_content(include_children=True, storage=self.storage),
                sections=[section],
                confidence=0.95
            )
        
        # Fallback to combat chapter
        combat_chapter_id = 'chapter-combat'
        if combat_chapter_id in self.storage.sections:
            section = self.storage.sections[combat_chapter_id]
            return RulebookQueryResult(
                content=section.get_full_content(include_children=True, storage=self.storage),
                sections=[section],
                confidence=0.8
            )
        
        return RulebookQueryResult(
            content="Combat actions section not found",
            confidence=0.0
        )
    
    def rule_mechanics(self, entities: List[str]) -> RulebookQueryResult:
        """Semantic search for specific rule mechanics"""
        if not entities:
            return RulebookQueryResult(
                content="No rule mechanic specified",
                confidence=0.0
            )
        
        # Try to find as a feature entity first
        feature_entity = self.storage.resolve_entity(entities[0], DnDEntityType.FEATURE)
        if feature_entity:
            return self.describe_entity([feature_entity.name])
        
        # Try to find as a rule entity
        rule_entity = self.storage.resolve_entity(entities[0], DnDEntityType.RULE)
        if rule_entity:
            return self.describe_entity([rule_entity.name])
        
        # Fallback to section search
        mechanic = entities[0].lower()
        relevant_sections = []
        
        # Search for sections containing the mechanic
        for section_id, section in self.storage.sections.items():
            if mechanic in section.content.lower() or mechanic in section.title.lower():
                relevant_sections.append(section)
        
        if not relevant_sections:
            return RulebookQueryResult(
                content=f"No information found about '{mechanic}'",
                confidence=0.0
            )
        
        # Sort by relevance (simple frequency-based)
        relevant_sections.sort(
            key=lambda s: s.content.lower().count(mechanic) + 
                         (10 if mechanic in s.title.lower() else 0),
            reverse=True
        )
        
        # Take top 3 most relevant
        top_sections = relevant_sections[:3]
        content_parts = [s.content for s in top_sections]
        
        return RulebookQueryResult(
            content='\n\n---\n\n'.join(content_parts),
            sections=top_sections,
            confidence=0.8
        )
    
    def calculate_values(self, entities: List[str]) -> RulebookQueryResult:
        """Get calculation rules (AC, damage, etc.)"""
        # Would need specific calculation sections
        return self.rule_mechanics(entities)
    
    def spell_details(self, entities: List[str]) -> RulebookQueryResult:
        """Get spell description"""
        if not entities:
            return RulebookQueryResult(
                content="No spell specified",
                confidence=0.0
            )
        
        spell_entity = self.storage.resolve_entity(entities[0], DnDEntityType.SPELL)
        if spell_entity:
            return self.describe_entity([spell_entity.name])
        
        # Search in spell descriptions section
        spell_section_id = 'section-spell-descriptions'
        if spell_section_id in self.storage.sections:
            section = self.storage.sections[spell_section_id]
            spell_name = entities[0].lower()
            
            # Search for spell in content
            if spell_name in section.content.lower():
                # Extract spell description (simplified)
                return RulebookQueryResult(
                    content=f"Spell: {entities[0]}\n{section.content}",
                    sections=[section],
                    confidence=0.7
                )
        
        return RulebookQueryResult(
            content=f"Spell '{entities[0]}' not found",
            confidence=0.0
        )
    
    def class_spell_access(self, entities: List[str]) -> RulebookQueryResult:
        """Get spell list for a class"""
        if not entities:
            return RulebookQueryResult(
                content="No class specified",
                confidence=0.0
            )
        
        class_name = entities[0]
        spell_list_section_id = f'section-{class_name.lower()}-spells'
        
        if spell_list_section_id in self.storage.sections:
            section = self.storage.sections[spell_list_section_id]
            return RulebookQueryResult(
                content=section.get_full_content(include_children=True, storage=self.storage),
                sections=[section],
                confidence=0.95
            )
        
        return RulebookQueryResult(
            content=f"Spell list for {class_name} not found",
            confidence=0.0
        )
    
    def monster_stats(self, entities: List[str]) -> RulebookQueryResult:
        """Get monster stat block"""
        if not entities:
            return RulebookQueryResult(
                content="No monster specified",
                confidence=0.0
            )
        
        monster_entity = self.storage.resolve_entity(entities[0], DnDEntityType.MONSTER)
        if monster_entity:
            return self.describe_entity([monster_entity.name])
        
        return RulebookQueryResult(
            content=f"Monster '{entities[0]}' not found",
            confidence=0.0
        )
    
    def condition_effects(self, entities: List[str]) -> RulebookQueryResult:
        """Get condition description"""
        if not entities:
            # Return all conditions
            conditions_section_id = 'section-conditions'
            if conditions_section_id in self.storage.sections:
                section = self.storage.sections[conditions_section_id]
                return RulebookQueryResult(
                    content=section.get_full_content(),
                    sections=[section],
                    confidence=0.95
                )
        
        condition_entity = self.storage.resolve_entity(entities[0], DnDEntityType.CONDITION)
        if condition_entity:
            # Extract specific condition from conditions section
            conditions_section_id = 'section-conditions'
            if conditions_section_id in self.storage.sections:
                section = self.storage.sections[conditions_section_id]
                # Would extract specific condition text
                return RulebookQueryResult(
                    content=f"Condition: {condition_entity.name}\n{section.content}",
                    sections=[section],
                    entities=[condition_entity],
                    confidence=0.9
                )
        
        return RulebookQueryResult(
            content=f"Condition '{entities[0]}' not found",
            confidence=0.0
        )
    
    def character_creation(self, entities: List[str]) -> RulebookQueryResult:
        """Get character creation overview"""
        relevant_section_ids = [
            'chapter-races',
            'chapter-classes',
            'section-ability-scores-and-modifiers',
            'section-backgrounds',
            'chapter-equipment'
        ]
        
        sections = []
        content_parts = []
        
        for section_id in relevant_section_ids:
            if section_id in self.storage.sections:
                section = self.storage.sections[section_id]
                sections.append(section)
                content_parts.append(section.content)
        
        return RulebookQueryResult(
            content='\n\n---\n\n'.join(content_parts),
            sections=sections,
            confidence=0.85
        )
    
    def multiclass_rules(self, entities: List[str]) -> RulebookQueryResult:
        """Get multiclassing rules"""
        multiclass_section_id = 'section-multiclassing'
        
        if multiclass_section_id in self.storage.sections:
            section = self.storage.sections[multiclass_section_id]
            content = section.get_full_content(include_children=True, storage=self.storage)
            
            # If specific classes mentioned, add their requirements
            if entities:
                for class_name in entities:
                    class_entity = self.storage.resolve_entity(class_name, DnDEntityType.CLASS)
                    if class_entity:
                        # Would add class-specific multiclass requirements
                        pass
            
            return RulebookQueryResult(
                content=content,
                sections=[section],
                confidence=0.9
            )
        
        return RulebookQueryResult(
            content="Multiclassing rules not found",
            confidence=0.0
        )
    
    def equipment_properties(self, entities: List[str]) -> RulebookQueryResult:
        """Get weapon/armor properties"""
        if not entities:
            # Return general properties section
            weapons_section_id = 'section-weapons'
            if weapons_section_id in self.storage.sections:
                section = self.storage.sections[weapons_section_id]
                return RulebookQueryResult(
                    content=section.get_full_content(include_children=True, storage=self.storage),
                    sections=[section],
                    confidence=0.85
                )
        
        property_name = entities[0].lower()
        # Search for property in weapons section
        weapons_section_id = 'section-weapons'
        if weapons_section_id in self.storage.sections:
            section = self.storage.sections[weapons_section_id]
            if property_name in section.content.lower():
                return RulebookQueryResult(
                    content=f"Property: {property_name}\n{section.content}",
                    sections=[section],
                    confidence=0.8
                )
        
        return RulebookQueryResult(
            content=f"Property '{entities[0]}' not found",
            confidence=0.0
        )
    
    def damage_types(self, entities: List[str]) -> RulebookQueryResult:
        """Get damage type information"""
        if not entities:
            return RulebookQueryResult(
                content="No damage type specified",
                confidence=0.0
            )
        
        damage_type = entities[0].lower()
        relevant_sections = []
        
        # Search combat and damage sections
        search_sections = ['section-damage-and-healing', 'chapter-combat']
        for section_id in search_sections:
            if section_id in self.storage.sections:
                section = self.storage.sections[section_id]
                if damage_type in section.content.lower():
                    relevant_sections.append(section)
        
        if relevant_sections:
            content_parts = [s.content for s in relevant_sections]
            return RulebookQueryResult(
                content='\n\n'.join(content_parts),
                sections=relevant_sections,
                confidence=0.75
            )
        
        return RulebookQueryResult(
            content=f"Damage type '{entities[0]}' not found",
            confidence=0.0
        )
    
    def rest_mechanics(self, entities: List[str]) -> RulebookQueryResult:
        """Get rest rules"""
        rest_section_id = 'section-resting'
        
        if rest_section_id in self.storage.sections:
            section = self.storage.sections[rest_section_id]
            return RulebookQueryResult(
                content=section.get_full_content(include_children=True, storage=self.storage),
                sections=[section],
                confidence=0.95
            )
        
        return RulebookQueryResult(
            content="Rest mechanics section not found",
            confidence=0.0
        )
    
    def skill_usage(self, entities: List[str]) -> RulebookQueryResult:
        """Get skill usage rules"""
        skills_section_id = 'section-ability-checks'
        
        if skills_section_id in self.storage.sections:
            section = self.storage.sections[skills_section_id]
            content = section.get_full_content(include_children=True, storage=self.storage)
            
            # If specific skills mentioned, filter for those
            if entities:
                skill_content = []
                for skill in entities:
                    if skill.lower() in content.lower():
                        skill_content.append(f"## {skill}\n")
                        # Would extract skill-specific content
                if skill_content:
                    content = '\n'.join(skill_content) + '\n\n' + content
            
            return RulebookQueryResult(
                content=content,
                sections=[section],
                confidence=0.9
            )
        
        return RulebookQueryResult(
            content="Skills section not found",
            confidence=0.0
        )
    
    def find_by_criteria(self, entities: List[str]) -> RulebookQueryResult:
        """Find entities matching criteria"""
        if not entities:
            return RulebookQueryResult(
                content="No search criteria specified",
                confidence=0.0
            )
        
        criteria = entities[0].lower()
        matching_entities = []
        
        # Search through all entities for matching properties
        for entity_name, entity in self.storage.entities.items():
            # Check if criteria appears in entity's sections
            for section_id in entity.section_ids:
                if section_id in self.storage.sections:
                    section = self.storage.sections[section_id]
                    if criteria in section.content.lower():
                        matching_entities.append(entity)
                        break
        
        if not matching_entities:
            return RulebookQueryResult(
                content=f"No entities found matching criteria: {criteria}",
                confidence=0.0
            )
        
        # Format results
        result_parts = []
        for entity in matching_entities[:10]:  # Limit to 10 results
            result_parts.append(f"- {entity.name} ({entity.entity_type.value})")
        
        content = f"Entities matching '{criteria}':\n" + '\n'.join(result_parts)
        
        return RulebookQueryResult(
            content=content,
            entities=matching_entities[:10],
            confidence=0.7
        )
    
    def prerequisite_check(self, entities: List[str]) -> RulebookQueryResult:
        """Get prerequisites for feat/multiclass/etc."""
        if not entities:
            return RulebookQueryResult(
                content="No entity specified for prerequisite check",
                confidence=0.0
            )
        
        entity = self.storage.resolve_entity(entities[0])
        if not entity:
            return RulebookQueryResult(
                content=f"Entity '{entities[0]}' not found",
                confidence=0.0
            )
        
        # Get entity content and look for prerequisite patterns
        sections = []
        content_parts = []
        
        for section_id in entity.section_ids:
            if section_id in self.storage.sections:
                section = self.storage.sections[section_id]
                sections.append(section)
                content = section.content
                
                # Look for prerequisite keywords
                if any(keyword in content.lower() for keyword in ['prerequisite', 'require', 'must have']):
                    content_parts.append(content)
        
        if content_parts:
            return RulebookQueryResult(
                content='\n\n'.join(content_parts),
                sections=sections,
                entities=[entity],
                confidence=0.8
            )
        
        return RulebookQueryResult(
            content=f"No prerequisites found for {entity.name}",
            confidence=0.5
        )
    
    def interaction_rules(self, entities: List[str]) -> RulebookQueryResult:
        """Get rules for how concepts interact"""
        if len(entities) < 2:
            return RulebookQueryResult(
                content="Need at least 2 concepts to check interactions",
                confidence=0.0
            )
        
        concept1, concept2 = entities[0].lower(), entities[1].lower()
        relevant_sections = []
        
        # Find sections containing both concepts
        for section_id, section in self.storage.sections.items():
            content_lower = section.content.lower()
            if concept1 in content_lower and concept2 in content_lower:
                relevant_sections.append(section)
        
        if not relevant_sections:
            return RulebookQueryResult(
                content=f"No interaction rules found between '{entities[0]}' and '{entities[1]}'",
                confidence=0.0
            )
        
        content_parts = [s.content for s in relevant_sections]
        return RulebookQueryResult(
            content='\n\n---\n\n'.join(content_parts),
            sections=relevant_sections,
            confidence=0.7
        )
    
    def tactical_usage(self, entities: List[str]) -> RulebookQueryResult:
        """Get tactical advice for using abilities/spells"""
        if not entities:
            return RulebookQueryResult(
                content="No ability/spell specified for tactical usage",
                confidence=0.0
            )
        
        # This would typically involve strategic analysis
        # For now, return the basic description plus combat context
        entity_result = self.describe_entity(entities)
        
        # Add combat context if available
        combat_section_id = 'chapter-combat'
        if combat_section_id in self.storage.sections:
            combat_section = self.storage.sections[combat_section_id]
            entity_result.content += f"\n\n## Combat Context\n{combat_section.content[:500]}..."
        
        entity_result.confidence = 0.6  # Lower confidence for tactical advice
        return entity_result
    
    def environmental_rules(self, entities: List[str]) -> RulebookQueryResult:
        """Get environmental hazard/condition rules"""
        environment_section_id = 'section-environment'
        
        if environment_section_id in self.storage.sections:
            section = self.storage.sections[environment_section_id]
            content = section.get_full_content(include_children=True, storage=self.storage)
            
            # Filter for specific environment if provided
            if entities:
                env_type = entities[0].lower()
                if env_type in content.lower():
                    # Would extract environment-specific content
                    content = f"## {entities[0]} Environment\n{content}"
            
            return RulebookQueryResult(
                content=content,
                sections=[section],
                confidence=0.85
            )
        
        return RulebookQueryResult(
            content="Environmental rules section not found",
            confidence=0.0
        )
    
    def creature_abilities(self, entities: List[str]) -> RulebookQueryResult:
        """Get special abilities of creatures"""
        if not entities:
            return RulebookQueryResult(
                content="No creature specified",
                confidence=0.0
            )
        
        creature_entity = self.storage.resolve_entity(entities[0], DnDEntityType.MONSTER)
        if creature_entity:
            return self.describe_entity([creature_entity.name])
        
        # Search in monsters chapter
        monsters_section_id = 'chapter-monsters'
        if monsters_section_id in self.storage.sections:
            section = self.storage.sections[monsters_section_id]
            creature_name = entities[0].lower()
            
            if creature_name in section.content.lower():
                return RulebookQueryResult(
                    content=f"Creature: {entities[0]}\n{section.content}",
                    sections=[section],
                    confidence=0.7
                )
        
        return RulebookQueryResult(
            content=f"Creature '{entities[0]}' not found",
            confidence=0.0
        )
    
    def saving_throws(self, entities: List[str]) -> RulebookQueryResult:
        """Get saving throw rules"""
        saves_section_id = 'section-saving-throws'
        
        if saves_section_id in self.storage.sections:
            section = self.storage.sections[saves_section_id]
            content = section.get_full_content(include_children=True, storage=self.storage)
            
            # Filter for specific save type if provided
            if entities:
                save_type = entities[0].lower()
                if save_type in content.lower():
                    content = f"## {entities[0]} Saving Throws\n{content}"
            
            return RulebookQueryResult(
                content=content,
                sections=[section],
                confidence=0.9
            )
        
        return RulebookQueryResult(
            content="Saving throws section not found",
            confidence=0.0
        )
    
    def magic_item_usage(self, entities: List[str]) -> RulebookQueryResult:
        """Get magic item details"""
        if not entities:
            return RulebookQueryResult(
                content="No magic item specified",
                confidence=0.0
            )
        
        item_entity = self.storage.resolve_entity(entities[0], DnDEntityType.MAGIC_ITEM)
        if item_entity:
            return self.describe_entity([item_entity.name])
        
        # Search in magic items chapter
        magic_items_section_id = 'chapter-magic-items'
        if magic_items_section_id in self.storage.sections:
            section = self.storage.sections[magic_items_section_id]
            item_name = entities[0].lower()
            
            if item_name in section.content.lower():
                return RulebookQueryResult(
                    content=f"Magic Item: {entities[0]}\n{section.content}",
                    sections=[section],
                    confidence=0.7
                )
        
        return RulebookQueryResult(
            content=f"Magic item '{entities[0]}' not found",
            confidence=0.0
        )
    
    def planar_properties(self, entities: List[str]) -> RulebookQueryResult:
        """Get plane of existence details"""
        planes_section_id = 'chapter-the-planes-of-existence'
        
        if planes_section_id in self.storage.sections:
            section = self.storage.sections[planes_section_id]
            content = section.get_full_content(include_children=True, storage=self.storage)
            
            # Filter for specific plane if provided
            if entities:
                plane_name = entities[0].lower()
                if plane_name in content.lower():
                    content = f"## {entities[0]}\n{content}"
            
            return RulebookQueryResult(
                content=content,
                sections=[section],
                confidence=0.85
            )
        
        return RulebookQueryResult(
            content="Planes of existence section not found",
            confidence=0.0
        )
    
    def downtime_activities(self, entities: List[str]) -> RulebookQueryResult:
        """Get downtime activity rules"""
        downtime_section_id = 'section-between-adventures'
        
        if downtime_section_id in self.storage.sections:
            section = self.storage.sections[downtime_section_id]
            content = section.get_full_content(include_children=True, storage=self.storage)
            
            # Filter for specific activity if provided
            if entities:
                activity_name = entities[0].lower()
                if activity_name in content.lower():
                    content = f"## {entities[0]} Activity\n{content}"
            
            return RulebookQueryResult(
                content=content,
                sections=[section],
                confidence=0.85
            )
        
        return RulebookQueryResult(
            content="Downtime activities section not found",
            confidence=0.0
        )
    
    def subclass_features(self, entities: List[str]) -> RulebookQueryResult:
        """Get subclass feature details"""
        if not entities:
            return RulebookQueryResult(
                content="No subclass specified",
                confidence=0.0
            )
        
        # Try to resolve as subclass entity first
        subclass_entity = self.storage.resolve_entity(entities[0], DnDEntityType.SUBCLASS)
        if subclass_entity:
            return self.describe_entity([subclass_entity.name])
        
        # If we have both class and subclass names
        if len(entities) >= 2:
            class_name = entities[0].lower()
            subclass_name = entities[1].lower()
            
            # Try the second entity as subclass
            subclass_entity = self.storage.resolve_entity(entities[1], DnDEntityType.SUBCLASS)
            if subclass_entity:
                return self.describe_entity([subclass_entity.name])
        
        # Fallback to section-based search
        if len(entities) >= 2:
            class_name = entities[0].lower()
            subclass_name = entities[1].lower()
            
            # Look for subclass sections
            possible_section_ids = [
                f'section-{class_name}-{subclass_name}',
                f'section-{subclass_name}',
                f'section-{class_name}-archetypes',
                f'section-{class_name}-paths'
            ]
            
            for section_id in possible_section_ids:
                if section_id in self.storage.sections:
                    section = self.storage.sections[section_id]
                    if subclass_name in section.content.lower():
                        return RulebookQueryResult(
                            content=section.get_full_content(include_children=True, storage=self.storage),
                            sections=[section],
                            confidence=0.9
                        )
        
        return RulebookQueryResult(
            content=f"Subclass '{entities[0]}' not found",
            confidence=0.0
        )
    
    def cost_lookup(self, entities: List[str]) -> RulebookQueryResult:
        """Get item/service costs"""
        if not entities:
            return RulebookQueryResult(
                content="No item specified for cost lookup",
                confidence=0.0
            )
        
        # Search equipment tables
        equipment_section_id = 'chapter-equipment'
        if equipment_section_id in self.storage.sections:
            section = self.storage.sections[equipment_section_id]
            item_name = entities[0].lower()
            
            if item_name in section.content.lower():
                # Would extract cost table information
                return RulebookQueryResult(
                    content=f"Cost for {entities[0]}:\n{section.content}",
                    sections=[section],
                    confidence=0.8
                )
        
        return RulebookQueryResult(
            content=f"Cost information for '{entities[0]}' not found",
            confidence=0.0
        )
    
    def legendary_mechanics(self, entities: List[str]) -> RulebookQueryResult:
        """Get legendary action/resistance rules"""
        # Search for legendary creatures or rules
        legendary_keywords = ['legendary', 'lair action', 'legendary resistance']
        relevant_sections = []
        
        for section_id, section in self.storage.sections.items():
            content_lower = section.content.lower()
            if any(keyword in content_lower for keyword in legendary_keywords):
                relevant_sections.append(section)
        
        if entities:
            # Filter for specific creature
            creature_name = entities[0].lower()
            relevant_sections = [s for s in relevant_sections 
                               if creature_name in s.content.lower()]
        
        if relevant_sections:
            content_parts = [s.content for s in relevant_sections]
            return RulebookQueryResult(
                content='\n\n---\n\n'.join(content_parts),
                sections=relevant_sections,
                confidence=0.8
            )
        
        return RulebookQueryResult(
            content="No legendary mechanics information found",
            confidence=0.0
        )
    
    def optimization_advice(self, entities: List[str]) -> RulebookQueryResult:
        """Get optimization advice for builds/concepts"""
        if not entities:
            return RulebookQueryResult(
                content="No build concept specified for optimization",
                confidence=0.0
            )
        
        concept = entities[0].lower()
        relevant_entities = []
        relevant_sections = []
        
        # Find entities related to the concept
        for entity_name, entity in self.storage.entities.items():
            if concept in entity.name.lower() or any(concept in alias for alias in entity.aliases):
                relevant_entities.append(entity)
                
                # Get their sections
                for section_id in entity.section_ids:
                    if section_id in self.storage.sections:
                        relevant_sections.append(self.storage.sections[section_id])
        
        if not relevant_entities:
            return RulebookQueryResult(
                content=f"No optimization information found for '{entities[0]}'",
                confidence=0.0
            )
        
        # Format optimization advice
        content_parts = [f"# Optimization for {entities[0]}"]
        for entity in relevant_entities:
            content_parts.append(f"## {entity.name} ({entity.entity_type.value})")
        
        for section in relevant_sections[:5]:  # Limit to avoid too much content
            content_parts.append(section.content)
        
        return RulebookQueryResult(
            content='\n\n'.join(content_parts),
            sections=relevant_sections,
            entities=relevant_entities,
            confidence=0.6  # Lower confidence for optimization advice
        )
    
    def get_class_features(self, class_name: str, level: Optional[int] = None) -> List[DnDEntity]:
        """Helper method to get all features for a class"""
        features = []
        
        # Get all feature entities that belong to this class
        for entity_name, entity in self.storage.entities.items():
            if (entity.entity_type == DnDEntityType.FEATURE and 
                entity.properties.get('parent_class') == class_name):
                features.append(entity)
        
        # If level specified, could filter features available at that level
        # This would require parsing the level requirements from content
        
        return features
    
    def get_available_subclasses(self, class_name: str) -> List[DnDEntity]:
        """Helper method to get all subclasses for a class"""
        subclasses = []
        
        for entity_name, entity in self.storage.entities.items():
            if (entity.entity_type == DnDEntityType.SUBCLASS and 
                entity.properties.get('base_class') == class_name):
                subclasses.append(entity)
        
        return subclasses
