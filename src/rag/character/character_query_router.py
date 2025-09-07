"""
Character Query Router

Simple router that takes a user intention string and entities array,
maps them to character data, and returns all relevant objects.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .character_types import Character
from .character_query_types import UserIntention, EntityType, IntentionDataMapper, CharacterQueryPerformanceMetrics
from .character_manager import CharacterManager
from .entity_matcher import EntityMatcher


@dataclass
class CharacterQueryResult:
    """Result structure containing all relevant character data and objects."""
    character_data: Dict[str, Any]  # The actual character data
    metadata: Dict[str, Any] = field(default_factory=dict)  # Query metadata
    warnings: List[str] = field(default_factory=list)  # Any warnings or issues
    entity_matches: List[Dict[str, Any]] = field(default_factory=list)  # Entity match details
    performance_metrics: Optional[CharacterQueryPerformanceMetrics] = None  # Performance timing data


class CharacterQueryRouter:
    """
    Simple router for character information queries.
    
    Takes:
    - user_intention: string (e.g., "inventory", "spell_list", etc.)
    - entities: array of dicts with entity info (name, type, etc.)
    
    Returns: All relevant character data and nested objects
    """
    
    def __init__(self, character_manager: Optional[CharacterManager] = None):
        """Initialize the query router."""
        self.character_manager = character_manager or CharacterManager()
        self.intention_mapper = IntentionDataMapper()
        self.entity_matcher = EntityMatcher()
    
    def query_character(
        self, 
        character_name: str,
        user_intention: str, 
        entities: List[Dict[str, Any]] = None
    ) -> CharacterQueryResult:
        """
        Main method to query character information.
        
        Args:
            character_name: Name of the character to query
            user_intention: String representing what user wants (e.g., "inventory", "spell_list")
            entities: List of entity dicts with keys like {'name': 'Longsword', 'type': 'weapon'}
        
        Returns:
            QueryResult with all relevant character data and nested objects
        """
        start_time = time.perf_counter()
        
        entities = entities or []
        warnings = []
        
        # Initialize performance tracking
        performance = CharacterQueryPerformanceMetrics()
        performance.entities_processed = len(entities)
        
        # 1. Load the character
        load_start = time.perf_counter()
        try:
            character = self.character_manager.load_character(character_name)
        except Exception as e:
            performance.total_time_ms = (time.perf_counter() - start_time) * 1000
            return CharacterQueryResult(
                character_data={},
                warnings=[f"Could not load character '{character_name}': {str(e)}"],
                performance_metrics=performance
            )
        load_end = time.perf_counter()
        performance.character_loading_ms = (load_end - load_start) * 1000
        
        # 2. Map user intention to UserIntention enum
        intention_start = time.perf_counter()
        try:
            intention_enum = UserIntention(user_intention.lower())
        except ValueError:
            warnings.append(f"Unknown user intention: {user_intention}")
            # Return basic character info as fallback
            fallback_start = time.perf_counter()
            basic_data = {
                "character_base": character.character_base.__dict__,
                "ability_scores": character.ability_scores.__dict__
            }
            fallback_end = time.perf_counter()
            performance.serialization_ms = (fallback_end - fallback_start) * 1000
            performance.total_time_ms = (time.perf_counter() - start_time) * 1000
            performance.fields_extracted = 2
            return CharacterQueryResult(
                character_data=basic_data,
                warnings=warnings,
                performance_metrics=performance
            )
        intention_end = time.perf_counter()
        performance.intention_mapping_ms = (intention_end - intention_start) * 1000
        
        # 3. Get data requirements for this intention
        mapping_start = time.perf_counter()
        mappings = self.intention_mapper.get_mappings()
        if intention_enum not in mappings:
            warnings.append(f"No mapping found for intention: {user_intention}")
            performance.total_time_ms = (time.perf_counter() - start_time) * 1000
            return CharacterQueryResult(
                character_data={}, 
                warnings=warnings,
                performance_metrics=performance
            )
        
        mapping = mappings[intention_enum]
        mapping_end = time.perf_counter()
        performance.intention_mapping_ms += (mapping_end - mapping_start) * 1000
        
        # 4. Extract required character data
        extract_start = time.perf_counter()
        character_data = self._extract_character_data(character, mapping.required_fields)
        extract_end = time.perf_counter()
        performance.data_extraction_ms = (extract_end - extract_start) * 1000
        performance.fields_extracted = len(character_data)
        
        # 5. Filter by entities if provided
        entity_matches = []
        if entities:
            filter_start = time.perf_counter()
            character_data, entity_matches = self._filter_by_entities(character_data, entities)
            filter_end = time.perf_counter()
            performance.entity_filtering_ms = (filter_end - filter_start) * 1000
            performance.entity_matches_found = len(entity_matches)
        
        # 6. Finalize performance metrics
        serialization_start = time.perf_counter()
        # Count serialized objects (approximate by counting nested dictionaries)
        performance.objects_serialized = self._count_serialized_objects(character_data)
        performance.total_character_fields = len(character.__dict__)
        serialization_end = time.perf_counter()
        performance.serialization_ms += (serialization_end - serialization_start) * 1000
        
        # Total time
        performance.total_time_ms = (time.perf_counter() - start_time) * 1000
        
        return CharacterQueryResult(
            character_data=character_data,
            metadata={
                "intention": user_intention,
                "entities": entities,
                "required_fields": list(mapping.required_fields)
            },
            warnings=warnings,
            entity_matches=entity_matches,
            performance_metrics=performance
        )
    
    def _extract_character_data(self, character: Character, required_fields: set) -> Dict[str, Any]:
        """Extract the required fields from character with all nested objects."""
        result = {}
        
        for field_name in required_fields:
            if hasattr(character, field_name):
                field_value = getattr(character, field_name)
                if field_value is not None:
                    result[field_name] = self._serialize_object(field_value)
        
        return result
    
    def _count_serialized_objects(self, data: Any) -> int:
        """Count the number of objects that were serialized (approximate)"""
        count = 0
        if isinstance(data, dict):
            count += 1  # The dict itself
            for value in data.values():
                count += self._count_serialized_objects(value)
        elif isinstance(data, list):
            for item in data:
                count += self._count_serialized_objects(item)
        return count
    
    def _serialize_object(self, obj: Any) -> Any:
        """Convert dataclass objects to dictionaries recursively."""
        if hasattr(obj, '__dict__'):
            # It's a dataclass or similar object
            result = {}
            for key, value in obj.__dict__.items():
                result[key] = self._serialize_object(value)
            return result
        elif isinstance(obj, list):
            return [self._serialize_object(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._serialize_object(value) for key, value in obj.items()}
        else:
            # Primitive type
            return obj
    
    def _filter_by_entities(self, character_data: Dict[str, Any], entities: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Filter character data to only include information related to specified entities."""
        if not entities:
            return character_data, []
        
        filtered_data = {}
        all_entity_matches = []
        
        # For each section of character data, filter based on entities
        for section_name, section_data in character_data.items():
            
            if section_name == 'inventory' and isinstance(section_data, dict):
                # Filter inventory items
                filtered_inventory = {}
                
                # Handle equipped_items
                if 'equipped_items' in section_data and isinstance(section_data['equipped_items'], dict):
                    filtered_equipped_items = {}
                    for slot, items in section_data['equipped_items'].items():
                        if isinstance(items, list):
                            # Convert serialized items back to a format the entity matcher can handle
                            filtered_items, match_results = self.entity_matcher.filter_items_by_entities(items, entities)
                            all_entity_matches.extend(match_results)
                            
                            if filtered_items:
                                filtered_equipped_items[slot] = filtered_items
                    
                    if filtered_equipped_items:
                        filtered_inventory['equipped_items'] = filtered_equipped_items
                
                # Handle backpack items
                if 'backpack' in section_data and isinstance(section_data['backpack'], list):
                    filtered_backpack, match_results = self.entity_matcher.filter_items_by_entities(section_data['backpack'], entities)
                    all_entity_matches.extend(match_results)
                    
                    if filtered_backpack:
                        filtered_inventory['backpack'] = filtered_backpack
                
                # Copy other inventory fields (weight, etc.)
                for key, value in section_data.items():
                    if key not in ['equipped_items', 'backpack']:
                        filtered_inventory[key] = value
                
                if filtered_inventory:
                    filtered_data[section_name] = filtered_inventory
                    
            elif section_name == 'spell_list' and isinstance(section_data, dict):
                # Filter spells
                filtered_spells = {}
                
                for spell_section, spell_data in section_data.items():
                    if spell_section == 'spells' and isinstance(spell_data, dict):
                        filtered_spell_classes = {}
                        
                        for class_name, class_spells in spell_data.items():
                            if isinstance(class_spells, dict):
                                filtered_levels = {}
                                
                                for level, spells in class_spells.items():
                                    if isinstance(spells, list):
                                        filtered_level_spells, match_results = self.entity_matcher.filter_spells_by_entities(spells, entities)
                                        all_entity_matches.extend(match_results)
                                        
                                        if filtered_level_spells:
                                            filtered_levels[level] = filtered_level_spells
                                
                                if filtered_levels:
                                    filtered_spell_classes[class_name] = filtered_levels
                        
                        if filtered_spell_classes:
                            filtered_spells[spell_section] = filtered_spell_classes
                    else:
                        filtered_spells[spell_section] = spell_data
                
                if filtered_spells:
                    filtered_data[section_name] = filtered_spells
            
            else:
                # For other sections, include as-is
                filtered_data[section_name] = section_data
        
        return (filtered_data if filtered_data else character_data), all_entity_matches


# Example usage function
def example_usage():
    """Example of how to use the CharacterQueryRouter."""
    router = CharacterQueryRouter()
    
    # Example 1: Get all inventory
    result = router.query_character(
        character_name="Duskryn Nightwarden",
        user_intention="inventory"
    )
    print("Full inventory:", result.character_data.keys())
    
    # Example 2: Get specific weapon
    result = router.query_character(
        character_name="Duskryn Nightwarden", 
        user_intention="weapons",
        entities=[{"name": "longsword", "type": "weapon"}]
    )
    print("Longsword data:", result.character_data)
    
    # Example 3: Get spell information
    result = router.query_character(
        character_name="Duskryn Nightwarden",
        user_intention="spell_details", 
        entities=[{"name": "eldritch blast", "type": "spell"}]
    )
    print("Eldritch Blast data:", result.character_data)


if __name__ == "__main__":
    example_usage()
