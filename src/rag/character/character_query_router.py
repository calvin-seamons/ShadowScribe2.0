"""
Character Query Router

Simple router that takes a user intention string and entities array,
maps them to character data, and returns all relevant objects.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .character_types import Character
from .character_query_types import (
    UserIntention, IntentionDataMapper, CharacterQueryPerformanceMetrics
)


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
    
    def __init__(self, character: Optional[Character] = None):
        """Initialize the query router with a character object.
        
        Args:
            character: Character object to query
        """
        self.character = character
        self.intention_mapper = IntentionDataMapper()
    
    def query_character(
        self, 
        user_intentions: List[str], 
        entities: List[Dict[str, Any]] = None
    ) -> CharacterQueryResult:
        """
        Main method to query character information.
        
        Args:
            user_intentions: List of intention strings (max 2) representing what user wants (e.g., ["inventory", "spell_list"])
            entities: List of entity dicts with keys like {'name': 'Longsword', 'type': 'weapon'}
        
        Returns:
            QueryResult with all relevant character data and nested objects
        """
        start_time = time.perf_counter()
        
        entities = entities or []
        warnings = []
        
        # Validate intentions count
        if len(user_intentions) == 0:
            warnings.append("No intentions provided")
        elif len(user_intentions) > 2:
            raise ValueError(f"Maximum 2 intentions allowed, got {len(user_intentions)}")
        
        # Initialize performance tracking
        performance = CharacterQueryPerformanceMetrics()
        performance.entities_processed = len(entities)
        
        # 1. Check if character is available
        if not self.character:
            performance.total_time_ms = (time.perf_counter() - start_time) * 1000
            return CharacterQueryResult(
                character_data={},
                warnings=["No character loaded in query router"],
                performance_metrics=performance
            )
        
        character = self.character
        
        # 2. Map user intentions to UserIntention enums and get mappings
        intention_start = time.perf_counter()
        intention_enums = []
        individual_mappings = []
        mappings = self.intention_mapper.get_mappings()
        
        for user_intention in user_intentions:
            try:
                intention_enum = UserIntention(user_intention.lower())
                intention_enums.append(intention_enum)
                
                if intention_enum not in mappings:
                    warnings.append(f"No mapping found for intention: {user_intention}")
                    continue
                    
                individual_mappings.append(mappings[intention_enum])
                
            except ValueError:
                warnings.append(f"Unknown user intention: {user_intention}")
        
        # If no valid mappings found, return basic character info as fallback
        if not individual_mappings:
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
        
        # 3. Combine mappings if multiple intentions
        mapping_start = time.perf_counter()
        if len(individual_mappings) == 1:
            combined_mapping = individual_mappings[0]
        else:
            combined_mapping = self.intention_mapper.combine_mappings(individual_mappings)
        
        mapping_end = time.perf_counter()
        intention_end = time.perf_counter()
        performance.intention_mapping_ms = (intention_end - intention_start) * 1000
        
        # 4. Extract required character data (including optional fields)
        extract_start = time.perf_counter()
        all_fields = combined_mapping.required_fields.union(combined_mapping.optional_fields)
        character_data = self._extract_character_data(character, all_fields)
        extract_end = time.perf_counter()
        performance.data_extraction_ms = (extract_end - extract_start) * 1000
        performance.fields_extracted = len(character_data)
        
        # NOTE: Entity resolution and auto-include logic removed.
        # Phase 3 CentralEngine will handle entity resolution and pass auto_include sections.
        
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
                "intentions": user_intentions,
                "entities": entities,
                "required_fields": list(combined_mapping.required_fields)
            },
            warnings=warnings,
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
