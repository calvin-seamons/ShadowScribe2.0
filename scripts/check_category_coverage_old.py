"""
Script to verify that all D&D 5e rulebook headers have category assignments.
Reads the headers file and checks against the rulebook_assignments.py mappings.
"""

import sys
from pathlib import Path
import re
from typing import List, Dict, Set, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook.categorizer import RulebookCategorizer


def parse_headers_file(filepath: str) -> List[Tuple[str, int, str]]:
    """
    Parse the headers file and extract all section IDs with their levels and titles.
    Returns list of (section_id, level, title) tuples.
    """
    headers = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
            
        # Count the number of # symbols to determine level
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break
        
        if level == 0:
            continue
            
        # Extract the title and section ID
        title_part = line[level:].strip()
        
        # Check if there's an ID in the format {#section-id}
        id_match = re.search(r'\{#([^}]+)\}', title_part)
        if id_match:
            section_id = id_match.group(1)
            title = title_part[:id_match.start()].strip()
        else:
            # Generate section ID from title for subsections without explicit IDs
            title = title_part
            # Convert title to section ID format
            section_id = title.lower()
            section_id = re.sub(r'[^a-z0-9\s-]', '', section_id)
            section_id = re.sub(r'\s+', '-', section_id)
        
        headers.append((section_id, level, title))
    
    return headers


def check_pattern_match(section_id: str, patterns: Dict[str, List[int]]) -> List[int]:
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


def check_wildcard_match(section_id: str, assignments: Dict[str, List[int]]) -> List[int]:
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


def get_categories_for_section(section_id: str, title: str, level: int, all_headers: List[Tuple[str, int, str]] = None, current_index: int = None) -> List[int]:
    """
    Determine which categories a section belongs to.
    Returns list of category numbers (1-10).
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
        wildcard_cats = check_wildcard_match(section_id, RULEBOOK_CATEGORY_ASSIGNMENTS)
        categories.extend(wildcard_cats)
    
    # 4. Check pattern rules
    if not categories:
        pattern_cats = check_pattern_match(section_id, PATTERN_RULES)
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
                parent_categories = get_categories_for_section(parent_section_id, parent_title, parent_level)
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
        check_wildcard_match(section_id, RULEBOOK_CATEGORY_ASSIGNMENTS)
    )
    
    if not has_explicit_assignment and all_headers and current_index is not None:
        # Look for parent categories (going up the hierarchy)
        for j in range(current_index - 1, -1, -1):
            parent_id, parent_level, parent_title = all_headers[j]
            if parent_level < level:  # Found a parent at higher level
                parent_categories = get_categories_for_section(parent_id, parent_title, parent_level, all_headers, j)
                if parent_categories:
                    # Inherit all parent categories
                    for parent_cat in parent_categories:
                        if parent_cat not in categories:
                            categories.append(parent_cat)
                    break  # Stop at first categorized parent
    
    # Remove duplicates and sort
    categories = sorted(list(set(categories)))
    
    return categories


def main():
    """Main function to check category coverage - showing only uncategorized sections."""
    
    # Path to headers file and output file
    headers_file = project_root / "dnd5rulebook_headers.txt"
    output_file = project_root / "uncategorized_sections_report.txt"
    
    if not headers_file.exists():
        print(f"Error: Headers file not found at {headers_file}")
        return
    
    # Parse headers
    print("Parsing headers file...")
    headers = parse_headers_file(headers_file)
    print(f"Found {len(headers)} total headers")
    print(f"Writing report to: {output_file}\n")
    
    # Category names for display
    category_names = {
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
    
    # Find uncategorized sections and track all categorizations
    uncategorized = []
    categorized = []
    all_sections = []
    
    # Check each header
    for i, (section_id, level, title) in enumerate(headers):
        categories = get_categories_for_section(section_id, title, level, headers, i)
        
        if not categories:
            uncategorized.append((section_id, level, title))
        else:
            categorized.append((section_id, level, title, categories))
        
        all_sections.append((section_id, level, title, categories))
    
    # Write results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPLETE CATEGORIZATION REPORT\n")
        f.write("=" * 80 + "\n")
        
        f.write(f"\nTotal headers: {len(headers)}\n")
        f.write(f"Categorized: {len(categorized)} ({len(categorized)*100/len(headers):.1f}%)\n")
        f.write(f"Uncategorized: {len(uncategorized)} ({len(uncategorized)*100/len(headers):.1f}%)\n")
        
        # Write all sections with their categories
        f.write("\n" + "=" * 80 + "\n")
        f.write("ALL SECTIONS WITH ASSIGNED CATEGORIES:\n")
        f.write("=" * 80 + "\n")
        
        # Write sections in original file order
        for section_id, level, title, categories in all_sections:
            category_names_list = [category_names[cat] for cat in categories] if categories else ["UNCATEGORIZED"]
            cat_display = ", ".join(category_names_list) if category_names_list != ["UNCATEGORIZED"] else "UNCATEGORIZED"
            level_indicator = "#" * level
            f.write(f"{level_indicator} [{section_id}] {title} → {cat_display}\n")
        
        # Write category distribution
        f.write("\n" + "=" * 80 + "\n")
        f.write("CATEGORY DISTRIBUTION:\n")
        f.write("=" * 80 + "\n")
        
        category_counts = {i: 0 for i in range(1, 11)}
        for _, _, _, categories in categorized:
            for cat in categories:
                category_counts[cat] += 1
        
        for cat_num, count in sorted(category_counts.items()):
            f.write(f"{category_names[cat_num]:20s}: {count:4d} sections\n")
        
        # Write uncategorized sections (if any)
        if uncategorized:
            f.write("\n" + "=" * 80 + "\n")
            f.write("UNCATEGORIZED SECTIONS (need assignment):\n")
            f.write("=" * 80 + "\n")
            
            # Group by level for better readability
            uncategorized_by_level = {}
            for section_id, level, title in uncategorized:
                if level not in uncategorized_by_level:
                    uncategorized_by_level[level] = []
                uncategorized_by_level[level].append((section_id, title))
            
            for level in sorted(uncategorized_by_level.keys()):
                f.write(f"\nLevel {level} ({'#' * level}):\n")
                for section_id, title in uncategorized_by_level[level]:
                    f.write(f"  [{section_id}] {title}\n")
        
            # Write suggested assignments for uncategorized sections
            f.write("\n" + "=" * 80 + "\n")
            f.write("SUGGESTED ASSIGNMENTS FOR UNCATEGORIZED SECTIONS:\n")
            f.write("=" * 80 + "\n")
            
            suggestions = []
            for section_id, level, title in uncategorized:
                suggested_cats = []
                
                # Suggest based on title keywords
                title_lower = title.lower()
                
                if any(word in title_lower for word in ['hit points', 'proficiencies', 'equipment']):
                    suggested_cats.append(2)  # CLASS_FEATURES
                elif any(word in title_lower for word in ['cantrips', 'spell', 'ritual', 'casting']):
                    suggested_cats.append(3)  # SPELLCASTING
                elif any(word in title_lower for word in ['actions', 'reactions', 'legendary']):
                    suggested_cats.append(9)  # CREATURES
                elif any(word in title_lower for word in ['variant', 'optional']):
                    suggested_cats.append(7)  # CORE_MECHANICS
                
                if suggested_cats:
                    suggestions.append((section_id, title, suggested_cats))
            
            if suggestions:
                f.write("\nAdd these to RULEBOOK_CATEGORY_ASSIGNMENTS:\n")
                for section_id, title, cats in suggestions:
                    cat_names_list = [category_names[cat] for cat in cats]
                    f.write(f'    "{section_id}": {cats},  # {title} - {", ".join(cat_names_list)}\n')
            else:
                f.write("\nNo automatic suggestions available for these sections.\n")
        else:
            f.write("\n✅ All sections have been categorized!\n")
    
    print(f"Complete categorization report written to: {output_file}")
    print(f"Categorized: {len(categorized)} sections")
    print(f"Uncategorized: {len(uncategorized)} sections")
    print(f"Total: {len(headers)} sections")


if __name__ == "__main__":
    main()