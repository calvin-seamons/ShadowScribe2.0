#!/usr/bin/env python3
"""
Check D&D 5e Rulebook Category Coverage
Now uses the RulebookCategorizer for consistency with the storage system
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
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Count leading # characters to determine level
            level = 0
            i = 0
            while i < len(line) and line[i] == '#':
                level += 1
                i += 1
            
            if level == 0:
                continue
            
            # Extract title part after #'s and spaces
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


def main(headers_file: str = None, output_file: str = None):
    """Main function to check category coverage"""
    
    if headers_file is None:
        headers_file = str(Path(__file__).parent.parent / "dnd5rulebook_headers.txt")
    if output_file is None:
        output_file = str(Path(__file__).parent.parent / "uncategorized_sections_report.txt")
    
    print("Parsing headers file...")
    headers = parse_headers_file(headers_file)
    print(f"Found {len(headers)} total headers")
    print(f"Writing report to: {output_file}\n")
    
    # Use the categorizer to get consistent categorizations
    categorizer = RulebookCategorizer()
    
    # Find uncategorized sections and track all categorizations
    uncategorized = []
    categorized = []
    
    for i, (section_id, level, title) in enumerate(headers):
        categories = categorizer.get_categories_for_section(section_id, title, level, headers, i)
        
        if categories:
            categorized.append((section_id, level, title, categories))
        else:
            uncategorized.append((section_id, level, title))
    
    # Write comprehensive report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPLETE CATEGORIZATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total headers: {len(headers)}\n")
        f.write(f"Categorized: {len(categorized)} ({len(categorized)/len(headers)*100:.1f}%)\n")
        f.write(f"Uncategorized: {len(uncategorized)} ({len(uncategorized)/len(headers)*100:.1f}%)\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("ALL SECTIONS WITH ASSIGNED CATEGORIES:\n")
        f.write("=" * 80 + "\n")
        
        for section_id, level, title, categories in categorized:
            prefix = "#" * level
            category_names_list = [categorizer.category_names[cat] for cat in categories] if categories else ["UNCATEGORIZED"]
            cat_display = ", ".join(category_names_list) if category_names_list != ["UNCATEGORIZED"] else "UNCATEGORIZED"
            f.write(f"{prefix} [{section_id}] {title} → {cat_display}\n")
        
        for section_id, level, title in uncategorized:
            prefix = "#" * level
            f.write(f"{prefix} [{section_id}] {title} → UNCATEGORIZED\n")
        
        # Statistics by category
        f.write(f"\n" + "=" * 80 + "\n")
        f.write("CATEGORY STATISTICS:\n")
        f.write("=" * 80 + "\n")
        
        category_counts = {}
        for _, _, _, categories in categorized:
            for cat_num in categories:
                if cat_num not in category_counts:
                    category_counts[cat_num] = 0
                category_counts[cat_num] += 1
        
        for cat_num in sorted(category_counts.keys()):
            count = category_counts[cat_num]
            f.write(f"{categorizer.category_names[cat_num]:20s}: {count:4d} sections\n")
        
        f.write(f"{'UNCATEGORIZED':20s}: {len(uncategorized):4d} sections\n")
    
    print(f"Complete categorization report written to: {output_file}")
    print(f"Categorized: {len(categorized)} sections")
    print(f"Uncategorized: {len(uncategorized)} sections")
    print(f"Total: {len(headers)} sections")


if __name__ == "__main__":
    main()
