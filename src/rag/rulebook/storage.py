"""
D&D 5e Rulebook Storage System - Main Storage Class
"""

from typing import Dict, List, Optional, Set
import os
import re
from pathlib import Path
from difflib import SequenceMatcher

from .types import (
    RulebookQueryIntent, DnDEntityType, RulebookSection, 
    DnDEntity, RulebookQueryResult
)
from .entity_extractor import RulebookEntityExtractor
from .query_strategies import RulebookQueryStrategies
from .cache import RulebookQueryCache


class RulebookStorage:
    """
    Main storage system for D&D 5e rulebook content with 30 query strategies.
    
    Handles intelligent entity extraction, section hierarchy, and intent-based retrieval.
    """
    
    def __init__(self, rulebook_path: str = "knowledge_base/dnd5rulebook.md"):
        self.rulebook_path = rulebook_path
        self.sections: Dict[str, RulebookSection] = {}
        self.entities: Dict[str, DnDEntity] = {}
        self.entity_aliases: Dict[str, str] = {}  # alias -> canonical_name
        
        # Initialize subsystems
        self.extractor = RulebookEntityExtractor()
        self.strategies = RulebookQueryStrategies(self)
        self.cache = RulebookQueryCache()
        
        # Load if file exists
        if os.path.exists(rulebook_path):
            self.load_rulebook()
    
    def load_rulebook(self) -> None:
        """Load and parse the rulebook markdown file"""
        if not os.path.exists(self.rulebook_path):
            raise FileNotFoundError(f"Rulebook not found: {self.rulebook_path}")
        
        with open(self.rulebook_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        self._parse_sections(content)
        self._extract_entities()
    
    def _parse_sections(self, content: str) -> None:
        """Parse markdown content into hierarchical sections"""
        lines = content.split('\n')
        current_sections = {}  # level -> section_id
        
        for line in lines:
            # Detect headers
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                section_id = self._generate_section_id(title, level)
                
                # Determine parent
                parent_id = None
                for parent_level in range(level - 1, 0, -1):
                    if parent_level in current_sections:
                        parent_id = current_sections[parent_level]
                        break
                
                # Create section
                section = RulebookSection(
                    id=section_id,
                    title=title,
                    level=level,
                    content="",
                    parent_id=parent_id
                )
                
                self.sections[section_id] = section
                current_sections[level] = section_id
                
                # Update parent's children
                if parent_id and parent_id in self.sections:
                    self.sections[parent_id].children_ids.append(section_id)
                
                # Clear deeper levels
                for clear_level in range(level + 1, 10):
                    current_sections.pop(clear_level, None)
            
            else:
                # Add content to current deepest section
                if current_sections:
                    deepest_level = max(current_sections.keys())
                    section_id = current_sections[deepest_level]
                    self.sections[section_id].content += line + '\n'
    
    def _generate_section_id(self, title: str, level: int) -> str:
        """Generate section ID from title"""
        # Convert to lowercase and replace spaces with hyphens
        section_id = re.sub(r'[^\w\s-]', '', title.lower())
        section_id = re.sub(r'[-\s]+', '-', section_id).strip('-')
        
        # Add level prefix
        if level == 1:
            return f"chapter-{section_id}"
        else:
            return f"section-{section_id}"
    
    def _extract_entities(self) -> None:
        """Extract entities from all sections"""
        all_content = '\n'.join(section.content for section in self.sections.values())
        extracted_entities = self.extractor.extract_entities(all_content, self.sections, storage=self)
        
        for entity in extracted_entities:
            self.entities[entity.name] = entity
            
            # Build alias mapping
            for alias in entity.aliases:
                self.entity_aliases[alias.lower()] = entity.name
    
    def resolve_entity(self, name: str, entity_type: Optional[DnDEntityType] = None) -> Optional[DnDEntity]:
        """Resolve entity name to entity object"""
        # Direct lookup
        if name in self.entities:
            entity = self.entities[name]
            if entity_type is None or entity.entity_type == entity_type:
                return entity
        
        # Alias lookup
        name_lower = name.lower()
        if name_lower in self.entity_aliases:
            canonical_name = self.entity_aliases[name_lower]
            entity = self.entities[canonical_name]
            if entity_type is None or entity.entity_type == entity_type:
                return entity
        
        # Fuzzy search
        return self._fuzzy_search_entities(name, entity_type)
    
    def _fuzzy_search_entities(self, name: str, entity_type: Optional[DnDEntityType] = None) -> Optional[DnDEntity]:
        """Find best matching entity using fuzzy search"""
        best_match = None
        best_score = 0.0
        name_lower = name.lower()
        
        for entity_name, entity in self.entities.items():
            if entity_type and entity.entity_type != entity_type:
                continue
            
            # Check main name
            score = SequenceMatcher(None, name_lower, entity_name.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = entity
            
            # Check aliases
            for alias in entity.aliases:
                score = SequenceMatcher(None, name_lower, alias.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_match = entity
        
        return best_match if best_score > 0.7 else None
    
    def _suggest_similar_entities(self, name: str, limit: int = 3) -> List[str]:
        """Suggest similar entity names"""
        suggestions = []
        name_lower = name.lower()
        
        for entity_name in self.entities.keys():
            score = SequenceMatcher(None, name_lower, entity_name.lower()).ratio()
            suggestions.append((score, entity_name))
        
        suggestions.sort(reverse=True)
        return [name for score, name in suggestions[:limit] if score > 0.3]
    
    def query(self, intent: RulebookQueryIntent, entities: List[str]) -> RulebookQueryResult:
        """Execute query using appropriate strategy"""
        # Check cache first
        cache_key = self.cache.get_cache_key(intent.value, entities)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Execute strategy
        strategy_mapping = {
            RulebookQueryIntent.DESCRIBE_ENTITY: self.strategies.describe_entity,
            RulebookQueryIntent.COMPARE_ENTITIES: self.strategies.compare_entities,
            RulebookQueryIntent.LEVEL_PROGRESSION: self.strategies.level_progression,
            RulebookQueryIntent.ACTION_OPTIONS: self.strategies.action_options,
            RulebookQueryIntent.RULE_MECHANICS: self.strategies.rule_mechanics,
            RulebookQueryIntent.CALCULATE_VALUES: self.strategies.calculate_values,
            RulebookQueryIntent.SPELL_DETAILS: self.strategies.spell_details,
            RulebookQueryIntent.CLASS_SPELL_ACCESS: self.strategies.class_spell_access,
            RulebookQueryIntent.MONSTER_STATS: self.strategies.monster_stats,
            RulebookQueryIntent.CONDITION_EFFECTS: self.strategies.condition_effects,
            RulebookQueryIntent.CHARACTER_CREATION: self.strategies.character_creation,
            RulebookQueryIntent.MULTICLASS_RULES: self.strategies.multiclass_rules,
            RulebookQueryIntent.EQUIPMENT_PROPERTIES: self.strategies.equipment_properties,
            RulebookQueryIntent.DAMAGE_TYPES: self.strategies.damage_types,
            RulebookQueryIntent.REST_MECHANICS: self.strategies.rest_mechanics,
            RulebookQueryIntent.SKILL_USAGE: self.strategies.skill_usage,
            RulebookQueryIntent.FIND_BY_CRITERIA: self.strategies.find_by_criteria,
            RulebookQueryIntent.PREREQUISITE_CHECK: self.strategies.prerequisite_check,
            RulebookQueryIntent.INTERACTION_RULES: self.strategies.interaction_rules,
            RulebookQueryIntent.TACTICAL_USAGE: self.strategies.tactical_usage,
            RulebookQueryIntent.ENVIRONMENTAL_RULES: self.strategies.environmental_rules,
            RulebookQueryIntent.CREATURE_ABILITIES: self.strategies.creature_abilities,
            RulebookQueryIntent.SAVING_THROWS: self.strategies.saving_throws,
            RulebookQueryIntent.MAGIC_ITEM_USAGE: self.strategies.magic_item_usage,
            RulebookQueryIntent.PLANAR_PROPERTIES: self.strategies.planar_properties,
            RulebookQueryIntent.DOWNTIME_ACTIVITIES: self.strategies.downtime_activities,
            RulebookQueryIntent.SUBCLASS_FEATURES: self.strategies.subclass_features,
            RulebookQueryIntent.COST_LOOKUP: self.strategies.cost_lookup,
            RulebookQueryIntent.LEGENDARY_MECHANICS: self.strategies.legendary_mechanics,
            RulebookQueryIntent.OPTIMIZATION_ADVICE: self.strategies.optimization_advice,
        }
        
        strategy_func = strategy_mapping.get(intent)
        if not strategy_func:
            return RulebookQueryResult(
                content=f"No strategy implemented for intent: {intent.value}",
                confidence=0.0
            )
        
        try:
            result = strategy_func(entities)
            
            # Cache successful results
            if result.confidence > 0.0:
                self.cache.put(cache_key, result)
            
            return result
            
        except Exception as e:
            return RulebookQueryResult(
                content=f"Error executing query: {str(e)}",
                confidence=0.0
            )
    
    def search_sections(self, query: str, limit: int = 5) -> List[RulebookSection]:
        """Search sections by content"""
        matching_sections = []
        query_lower = query.lower()
        
        for section in self.sections.values():
            content_lower = section.content.lower()
            title_lower = section.title.lower()
            
            # Calculate relevance score
            content_matches = content_lower.count(query_lower)
            title_matches = title_lower.count(query_lower) * 5  # Weight title higher
            
            if content_matches > 0 or title_matches > 0:
                score = content_matches + title_matches
                matching_sections.append((score, section))
        
        # Sort by relevance and return top results
        matching_sections.sort(reverse=True, key=lambda x: x[0])
        return [section for score, section in matching_sections[:limit]]
    
    def get_entity_types(self) -> Set[DnDEntityType]:
        """Get all entity types present in the storage"""
        return {entity.entity_type for entity in self.entities.values()}
    
    def get_entities_by_type(self, entity_type: DnDEntityType) -> List[DnDEntity]:
        """Get all entities of a specific type"""
        return [entity for entity in self.entities.values() 
                if entity.entity_type == entity_type]
    
    def get_entities_by_property(self, property_key: str, property_value: str) -> List[DnDEntity]:
        """Get all entities with a specific property value"""
        return [entity for entity in self.entities.values()
                if entity.properties.get(property_key) == property_value]
    
    def get_class_features(self, class_name: str) -> List[DnDEntity]:
        """Get all feature entities for a specific class"""
        return self.get_entities_by_property('parent_class', class_name)
    
    def get_subclasses_for_class(self, class_name: str) -> List[DnDEntity]:
        """Get all subclass entities for a specific class"""
        return self.get_entities_by_property('base_class', class_name)
    
    def get_stats(self) -> Dict[str, int]:
        """Get storage statistics"""
        return {
            'total_sections': len(self.sections),
            'total_entities': len(self.entities),
            'cache_size': self.cache.size(),
            'entity_types': len(self.get_entity_types())
        }
