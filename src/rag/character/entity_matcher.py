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
        
        # Exact name match (case-insensitive)
        if entity_name and normalize_text(entity_name) == normalize_text(item_name):
            match_details.update({
                'match_type': 'exact_name',
                'similarity': 1.0,
                'reason': f"Exact name match: '{entity_name}' == '{item_name}'"
            })
            return match_details
        
        # Partial name match (entity name in item name or vice versa)
        if entity_name:
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
        if entity_name:
            similarity = calculate_similarity(entity_name, item_name)
            if similarity >= self.fuzzy_threshold:
                match_details.update({
                    'match_type': 'fuzzy_name',
                    'similarity': similarity,
                    'reason': f"Fuzzy name match: '{entity_name}' ~ '{item_name}' ({similarity:.2f})"
                })
                return match_details
        
        # Type match
        if entity_type and item_type:
            norm_entity_type = normalize_text(entity_type)
            norm_item_type = normalize_text(item_type)
            
            if norm_entity_type in norm_item_type or norm_item_type in norm_entity_type:
                match_details.update({
                    'match_type': 'type_match',
                    'similarity': 0.8,
                    'reason': f"Type match: '{entity_type}' ~ '{item_type}'"
                })
                return match_details
        
        return None
    
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
