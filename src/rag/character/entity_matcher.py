"""
Entity Matching Utilities

Enhanced entity matching with fuzzy string matching, case-insensitive search,
and detailed match reporting.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, remove special chars)."""
    return re.sub(r'[^\w\s]', '', text.lower().strip())


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two strings."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    return SequenceMatcher(None, norm1, norm2).ratio()


def fuzzy_match(target: str, candidates: List[str], threshold: float = 0.6) -> List[Tuple[str, float]]:
    """Find fuzzy matches for target string in candidates."""
    matches = []
    for candidate in candidates:
        similarity = calculate_similarity(target, candidate)
        if similarity >= threshold:
            matches.append((candidate, similarity))
    
    # Sort by similarity score (highest first)
    return sorted(matches, key=lambda x: x[1], reverse=True)


class EntityMatcher:
    """Enhanced entity matching with detailed reporting."""
    
    def __init__(self, fuzzy_threshold: float = 0.6):
        """Initialize with fuzzy matching threshold."""
        self.fuzzy_threshold = fuzzy_threshold
        self.match_results = []
    
    def clear_results(self):
        """Clear previous match results."""
        self.match_results = []
    
    def match_entity_in_item(self, entity: Dict[str, Any], item: Any) -> Optional[Dict[str, Any]]:
        """
        Check if an entity matches an item and return match details.
        
        Args:
            entity: Dictionary with entity search criteria
            item: Item to check (can be dict or dataclass object)
        
        Returns:
            Dict with match details if found, None otherwise
        """
        entity_name = entity.get('name', '').strip()
        entity_type = entity.get('type', '').strip()
        
        # Handle both dict and dataclass objects
        if hasattr(item, '__dict__'):
            # It's a dataclass object
            item_name = getattr(item, 'name', '').strip()
            item_type = getattr(item, 'type', '').strip()
        elif isinstance(item, dict):
            # It's a dictionary
            item_name = item.get('name', '').strip()
            item_type = item.get('type', '').strip()
        else:
            # Can't process this item type
            return None
        
        if not entity_name and not entity_type:
            return None
        
        match_details = {
            'entity': entity,
            'item': {'name': item_name, 'type': item_type},  # Normalize to dict
            'match_type': None,
            'similarity': 0.0,
            'reason': None
        }
        
        # When BOTH name and type are specified, require name matching AND type compatibility
        if entity_name and entity_type:
            # Check name matches first
            name_match_type = None
            name_similarity = 0.0
            
            # Exact name match
            if normalize_text(entity_name) == normalize_text(item_name):
                name_match_type = 'exact_name'
                name_similarity = 1.0
            else:
                # Partial name match
                norm_entity = normalize_text(entity_name)
                norm_item = normalize_text(item_name)
                
                if norm_entity in norm_item or norm_item in norm_entity:
                    name_match_type = 'partial_name'
                    name_similarity = calculate_similarity(entity_name, item_name)
                else:
                    # Fuzzy name match
                    similarity = calculate_similarity(entity_name, item_name)
                    if similarity >= self.fuzzy_threshold:
                        name_match_type = 'fuzzy_name'
                        name_similarity = similarity
            
            # If name matches, check type compatibility
            if name_match_type and self._types_are_compatible(entity_type, item_type):
                match_details.update({
                    'match_type': f'{name_match_type}_with_type',
                    'similarity': name_similarity,
                    'reason': f"{name_match_type.replace('_', ' ').title()} with compatible type: '{entity_name}' ~ '{item_name}', type '{entity_type}' ~ '{item_type}'"
                })
                return match_details
            
            # If name doesn't match but the name might be in the type field (e.g., "longsword" in "Weapon (Longsword)")
            elif not name_match_type and self._types_are_compatible(entity_type, item_type):
                norm_entity_name = normalize_text(entity_name)
                norm_item_type = normalize_text(item_type)
                
                if norm_entity_name in norm_item_type:
                    type_name_similarity = calculate_similarity(entity_name, item_type)
                    match_details.update({
                        'match_type': 'type_contains_name',
                        'similarity': type_name_similarity,
                        'reason': f"Type contains entity name: '{entity_name}' found in type '{item_type}', compatible with '{entity_type}'"
                    })
                    return match_details
        
        # When ONLY name is specified
        elif entity_name and not entity_type:
            # Exact name match
            if normalize_text(entity_name) == normalize_text(item_name):
                match_details.update({
                    'match_type': 'exact_name',
                    'similarity': 1.0,
                    'reason': f"Exact name match: '{entity_name}' == '{item_name}'"
                })
                return match_details
            
            # Partial name match
            norm_entity = normalize_text(entity_name)
            norm_item = normalize_text(item_name)
            
            if norm_entity in norm_item or norm_item in norm_entity:
                similarity = calculate_similarity(entity_name, item_name)
                match_details.update({
                    'match_type': 'partial_name',
                    'similarity': similarity,
                    'reason': f"Partial name match: '{entity_name}' ~ '{item_name}'"
                })
                return match_details
            
            # Fuzzy name match
            similarity = calculate_similarity(entity_name, item_name)
            if similarity >= self.fuzzy_threshold:
                match_details.update({
                    'match_type': 'fuzzy_name',
                    'similarity': similarity,
                    'reason': f"Fuzzy name match: '{entity_name}' ~ '{item_name}' ({similarity:.2f})"
                })
                return match_details
        
        # When ONLY type is specified
        elif not entity_name and entity_type:
            if self._types_are_compatible(entity_type, item_type):
                type_similarity = calculate_similarity(entity_type, item_type)
                match_details.update({
                    'match_type': 'type_only_match',
                    'similarity': type_similarity,
                    'reason': f"Type-only match: '{entity_type}' ~ '{item_type}' ({type_similarity:.2f})"
                })
                return match_details
        
        return None
    
    def _types_are_compatible(self, entity_type: str, item_type: str) -> bool:
        """Check if entity type and item type are compatible."""
        if not entity_type or not item_type:
            return False
            
        norm_entity_type = normalize_text(entity_type)
        norm_item_type = normalize_text(item_type)
        
        # Exact match
        if norm_entity_type == norm_item_type:
            return True
        
        # High similarity
        similarity = calculate_similarity(entity_type, item_type)
        if similarity >= 0.8:
            return True
        
        # Entity type is contained in item type (weapon -> Weapon (Longsword))
        if norm_entity_type in norm_item_type and len(norm_entity_type) >= 3:
            # More restrictive conditions for containment
            if (norm_item_type.startswith(norm_entity_type) or 
                f"({norm_entity_type})" in norm_item_type):
                return True
        
        # Item type is contained in entity type
        if norm_item_type in norm_entity_type and len(norm_item_type) >= 3:
            if norm_entity_type.startswith(norm_item_type):
                return True
        
        # Special semantic relationships
        # "item" is a broad category that should match most D&D item types
        if norm_entity_type == "item":
            # "item" should match various D&D item categories
            item_categories = [
                "magic item", "wondrous item", "weapon", "armor", "shield", "tool", "potion", "scroll", 
                "rod", "wand", "staff", "ring", "amulet", "cloak", "boots", "gloves",
                "helm", "helmet", "gauntlets", "bracers", "belt", "bag", "pack"
            ]
            if any(category in norm_item_type for category in item_categories):
                return True
        
        # Also handle reverse - if someone searches for "weapon" and item is "item"
        if norm_item_type == "item":
            weapon_types = ["weapon", "sword", "bow", "crossbow", "dagger", "axe", "hammer", "mace"]
            if any(weapon_type in norm_entity_type for weapon_type in weapon_types):
                return True
        
        return False

    def filter_items_by_entities(self, items: List[Any], entities: List[Dict[str, Any]]) -> Tuple[List[Any], List[Dict[str, Any]]]:
        """
        Filter items by entities and return both filtered items and match details.
        
        Args:
            items: List of items (can be dicts or dataclass objects)
            entities: List of entity search criteria
        
        Returns:
            Tuple of (filtered_items, match_results)
        """
        self.clear_results()
        filtered_items = []
        
        for item in items:
            for entity in entities:
                match_result = self.match_entity_in_item(entity, item)
                if match_result:
                    filtered_items.append(item)
                    self.match_results.append(match_result)
                    break  # Don't double-add items that match multiple entities
        
        return filtered_items, self.match_results
    
    def filter_spells_by_entities(self, spells: List[Any], entities: List[Dict[str, Any]]) -> Tuple[List[Any], List[Dict[str, Any]]]:
        """
        Filter spells by entities (same logic as items).
        
        Returns:
            Tuple of (filtered_spells, match_results)
        """
        return self.filter_items_by_entities(spells, entities)
    
    def get_match_summary(self) -> Dict[str, Any]:
        """Get summary of all matches found."""
        if not self.match_results:
            return {'total_matches': 0, 'match_types': {}, 'matches': []}
        
        match_types = {}
        for result in self.match_results:
            match_type = result['match_type']
            match_types[match_type] = match_types.get(match_type, 0) + 1
        
        return {
            'total_matches': len(self.match_results),
            'match_types': match_types,
            'matches': self.match_results
        }


# Test the entity matcher
def test_entity_matcher():
    """Test the entity matcher with sample data."""
    matcher = EntityMatcher()
    
    # Sample items
    items = [
        {'name': 'Eldaryth of Regret', 'type': 'Weapon (Longsword)'},
        {'name': 'Dagger', 'type': 'Weapon'},
        {'name': 'Splint, +1', 'type': 'Armor (Splint)'},
        {'name': 'Rod of the Pact Keeper, +2', 'type': 'Rod'}
    ]
    
    # Sample entities
    entities = [
        {'name': 'longsword', 'type': 'weapon'},
        {'name': 'rod', 'type': 'item'}
    ]
    
    filtered_items, match_results = matcher.filter_items_by_entities(items, entities)
    
    print("Test Results:")
    print(f"Original items: {len(items)}")
    print(f"Filtered items: {len(filtered_items)}")
    print(f"Matches found: {len(match_results)}")
    
    for result in match_results:
        print(f"  - {result['reason']}")


if __name__ == "__main__":
    test_entity_matcher()
