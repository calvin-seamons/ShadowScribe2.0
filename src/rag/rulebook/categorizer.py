"""
D&D 5e Rulebook Section Categorizer
Provides consistent categorization logic for all rulebook sections
"""

import re
from typing import List, Dict, Tuple, Any, Optional
from .rulebook_types import (
    RulebookCategory,
    RULEBOOK_CATEGORY_ASSIGNMENTS,
    PATTERN_RULES,
    MULTI_CATEGORY_SECTIONS
)


class RulebookCategorizer:
    """
    Handles categorization of D&D 5e rulebook sections using the same logic
    as the category coverage checker.
    """
    
    def __init__(self):
        # Category names for display and conversion
        self.category_names = {
            1: "CHARACTER_CREATION",
            2: "CLASS_FEATURES", 
            3: "SPELLCASTING",
            4: "COMBAT",
            5: "CONDITIONS",
            6: "EQUIPMENT",
            7: "CORE_MECHANICS",
            8: "EXPLORATION",
            9: "CREATURES",
            10: "WORLD_LORE"
        }
        
        # Reverse mapping for enum conversion
        self.category_enums = {
            "CHARACTER_CREATION": RulebookCategory.CHARACTER_CREATION,
            "CLASS_FEATURES": RulebookCategory.CLASS_FEATURES,
            "SPELLCASTING": RulebookCategory.SPELLCASTING,
            "COMBAT": RulebookCategory.COMBAT,
            "CONDITIONS": RulebookCategory.CONDITIONS,
            "EQUIPMENT": RulebookCategory.EQUIPMENT,
            "CORE_MECHANICS": RulebookCategory.CORE_MECHANICS,
            "EXPLORATION": RulebookCategory.EXPLORATION,
            "CREATURES": RulebookCategory.CREATURES,
            "WORLD_LORE": RulebookCategory.WORLD_LORE
        }
    
    def check_pattern_match(self, section_id: str, patterns: Dict[str, List[int]]) -> List[int]:
        """
        Check if a section ID matches any pattern rules.
        Returns the categories if matched, empty list otherwise.
        """
        for pattern_key, categories in patterns.items():
            if pattern_key.startswith("contains:"):
                # Extract the pattern after "contains:"
                pattern = pattern_key[9:]
                if re.search(pattern, section_id, re.IGNORECASE):
                    return categories
        return []

    def check_wildcard_match(self, section_id: str, assignments: Dict[str, List[int]]) -> List[int]:
        """
        Check if a section ID matches any wildcard patterns in assignments.
        Returns the categories if matched, empty list otherwise.
        """
        for pattern_key, categories in assignments.items():
            if '*' in pattern_key:
                # Convert wildcard pattern to regex
                regex_pattern = pattern_key.replace('*', '.*')
                if re.match(regex_pattern, section_id, re.IGNORECASE):
                    return categories
        return []

    def get_categories_for_section(
        self, 
        section_id: str, 
        title: str, 
        level: int, 
        all_headers: Optional[List[Tuple[str, int, str]]] = None, 
        current_index: Optional[int] = None
    ) -> List[int]:
        """
        Determine which categories a section belongs to.
        Returns list of category numbers (1-10).
        
        This is the exact same logic as in check_category_coverage.py
        """
        categories = []
        
        # 1. Check direct assignment
        if section_id in RULEBOOK_CATEGORY_ASSIGNMENTS:
            categories.extend(RULEBOOK_CATEGORY_ASSIGNMENTS[section_id])
        
        # 2. Check multi-category sections
        if section_id in MULTI_CATEGORY_SECTIONS:
            for cat in MULTI_CATEGORY_SECTIONS[section_id]:
                if cat not in categories:
                    categories.append(cat)
        
        # 3. Check wildcard patterns in assignments
        if not categories:
            wildcard_cats = self.check_wildcard_match(section_id, RULEBOOK_CATEGORY_ASSIGNMENTS)
            categories.extend(wildcard_cats)
        
        # 4. Check pattern rules
        if not categories:
            pattern_cats = self.check_pattern_match(section_id, PATTERN_RULES)
            categories.extend(pattern_cats)
        
        # 5. Parent inheritance for level 3+ sections if all_headers is provided
        if not categories and all_headers and current_index is not None and level >= 3:
            # Look backwards for the nearest parent at level 2 (but not level 1)
            for i in range(current_index - 1, -1, -1):
                parent_section_id, parent_level, parent_title = all_headers[i]
                
                # Stop if we reach a level 1 section (don't inherit from level 1)
                if parent_level == 1:
                    break
                    
                # If we find a level 2 parent, check if it has categories
                if parent_level == 2:
                    # Don't pass headers to avoid infinite recursion, just check basic categorization
                    parent_categories = self.get_categories_for_section(parent_section_id, parent_title, parent_level)
                    if parent_categories:
                        categories.extend(parent_categories)
                        break
        
        # 6. Apply automatic categorization rules based on level and content
        if not categories:
            # Level 4 sections: Individual creature entries -> CREATURES
            if level == 4:
                categories.append(9)  # CREATURES
            
            # Level 5 sections: Actions and Legendary Actions under creatures -> CREATURES  
            elif level == 5:
                if any(word in section_id.lower() for word in ['actions', 'legendary-actions']):
                    categories.append(9)  # CREATURES
            
            # Level 3+ sections: Common class features -> CLASS_FEATURES
            elif level >= 3:
                if any(word in section_id.lower() for word in ['hit-points', 'proficiencies', 'equipment']):
                    categories.append(2)  # CLASS_FEATURES
                elif any(word in section_id.lower() for word in ['cantrips', 'ritual-casting', 'flexible-casting']):
                    categories.append(3)  # SPELLCASTING
        
        # 7. Special handling for spell descriptions
        if not categories and level >= 4:  # Individual spell entries (#### level)
            # Check if parent might be spell-descriptions
            if 'spell' in title.lower() or section_id.startswith('spell-'):
                categories.append(3)  # SPELLCASTING
        
        # 8. Special handling for individual class features (level 3+ under class sections)
        if not categories and level >= 3:
            # Check common class feature patterns
            class_features = [
                'rage', 'unarmored-defense', 'reckless-attack', 'danger-sense',
                'bardic-inspiration', 'jack-of-all-trades', 'song-of-rest',
                'channel-divinity', 'divine-domain', 'wild-shape', 'druid-circle',
                'fighting-style', 'second-wind', 'action-surge', 'martial-arts',
                'ki', 'divine-sense', 'lay-on-hands', 'divine-smite',
                'favored-enemy', 'natural-explorer', 'sneak-attack', 'expertise',
                'font-of-magic', 'metamagic', 'eldritch-invocations', 'pact-boon',
                'arcane-recovery', 'arcane-tradition'
            ]
            if any(feature in section_id for feature in class_features):
                categories.append(2)  # CLASS_FEATURES
        
        # 9. Parent inheritance: inherit categories from nearest categorized parent only if no explicit assignment
        # Check if this section has any explicit assignment (direct, multi-category, or wildcard)
        has_explicit_assignment = (
            section_id in RULEBOOK_CATEGORY_ASSIGNMENTS or 
            section_id in MULTI_CATEGORY_SECTIONS or
            self.check_wildcard_match(section_id, RULEBOOK_CATEGORY_ASSIGNMENTS)
        )
        
        if not has_explicit_assignment and all_headers and current_index is not None:
            # Look for parent categories (going up the hierarchy)
            for j in range(current_index - 1, -1, -1):
                parent_id, parent_level, parent_title = all_headers[j]
                if parent_level < level:  # Found a parent at higher level
                    parent_categories = self.get_categories_for_section(parent_id, parent_title, parent_level, all_headers, j)
                    if parent_categories:
                        # Inherit all parent categories
                        for parent_cat in parent_categories:
                            if parent_cat not in categories:
                                categories.append(parent_cat)
                        break  # Stop at first categorized parent
        
        # Remove duplicates and sort
        categories = sorted(list(set(categories)))
        
        return categories
    
    def get_category_enums(
        self, 
        section_id: str, 
        title: str, 
        level: int, 
        all_headers: Optional[List[Tuple[str, int, str]]] = None, 
        current_index: Optional[int] = None
    ) -> List[RulebookCategory]:
        """
        Get categories as RulebookCategory enum values.
        """
        category_numbers = self.get_categories_for_section(
            section_id, title, level, all_headers, current_index
        )
        
        category_enums = []
        for cat_num in category_numbers:
            if cat_num in self.category_names:
                cat_name = self.category_names[cat_num]
                if cat_name in self.category_enums:
                    category_enums.append(self.category_enums[cat_name])
        
        return category_enums
    
    def categorize_all_sections(self, headers: List[Tuple[str, int, str]]) -> Dict[str, List[RulebookCategory]]:
        """
        Categorize all sections in a list of headers.
        Returns a dictionary mapping section_id to list of categories.
        """
        categorizations = {}
        
        for i, (section_id, level, title) in enumerate(headers):
            categories = self.get_category_enums(section_id, title, level, headers, i)
            categorizations[section_id] = categories
        
        return categorizations
