#!/usr/bin/env python3
"""
Inspect RulebookSections from the stored .pkl file
Show actual examples of sections at different levels
"""

import sys
from pathlib import Path
import pickle

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook.rulebook_storage import RulebookStorage
from src.rag.rulebook.rulebook_types import RulebookSection


def inspect_sections():
    """Load and inspect actual RulebookSections from the .pkl file"""
    
def main():
    # Path to the storage file
    storage_path = Path(__file__).parent.parent / "knowledge_base" / "processed_rulebook" / "rulebook_storage.pkl"
    
    if not storage_path.exists():
        print(f"❌ Storage file not found at: {storage_path}")
        print("Run 'python -m scripts.build_rulebook_storage' first")
        return
    
    if not storage_path.exists():
        print(f"❌ Storage file not found at: {storage_path}")
        print("Run 'python -m scripts.build_rulebook_storage' first")
        return
    
    print(f"📚 Loading rulebook sections from: {storage_path}")
    
    with open(storage_path, 'rb') as f:
        storage_data = pickle.load(f)
    
    print(f"✅ Loaded data type: {type(storage_data)}")
    
    # Handle both dict and RulebookStorage object formats
    if isinstance(storage_data, dict):
        if 'sections' in storage_data:
            sections = storage_data['sections']
        else:
            sections = storage_data
        print(f"✅ Found {len(sections)} sections (from dict)")
    else:
        sections = storage_data.sections
        print(f"✅ Found {len(sections)} sections (from RulebookStorage object)")
    
    print()
    
    # Convert all sections to RulebookSection objects for consistent handling
    all_sections = []
    sections_dict = {}
    for section_data in sections.values():
        if isinstance(section_data, dict):
            section = RulebookSection.from_dict(section_data)
        else:
            section = section_data
        all_sections.append(section)
        sections_dict[section.id] = section
    
    # Group sections by level
    sections_by_level = {}
    for section in all_sections:
        level = section.level
        if level not in sections_by_level:
            sections_by_level[level] = []
        sections_by_level[level].append(section)
    
    # Show statistics
    print("📊 SECTIONS BY LEVEL:")
    for level in sorted(sections_by_level.keys()):
        count = len(sections_by_level[level])
        print(f"  Level {level}: {count:4d} sections")
    print()
    
    # Show examples for levels 2-4 specifically
    for target_level in [2, 3, 4]:
        if target_level in sections_by_level:
            sections = sections_by_level[target_level]
            print(f"=" * 80)
            print(f"🔍 LEVEL {target_level} SECTION EXAMPLES ({len(sections)} total)")
            print(f"=" * 80)
            
            # Show first 3 examples
            for i, section in enumerate(sections[:3]):
                print(f"\n📄 EXAMPLE {i+1}:")
                print(f"   ID: {section.id}")
                print(f"   Title: {section.title}")
                print(f"   Level: {section.level}")
                print(f"   Parent: {section.parent_id}")
                print(f"   Children: {len(section.children_ids)} children")
                print(f"   Categories: {[cat.name for cat in section.categories]}")
                print(f"   Content length: {len(section.content)} chars")
                print(f"   Has vector: {'Yes' if section.vector else 'No'}")
                
                # Show content preview (first 300 chars)
                content_preview = section.content[:300]
                if len(section.content) > 300:
                    content_preview += "..."
                print(f"   Content preview:")
                print(f"      {repr(content_preview)}")
                
                if section.metadata:
                    print(f"   Metadata: {section.metadata}")
                
                print()
    
    # Show some specific interesting sections
    print(f"=" * 80)
    print(f"🎯 SPECIFIC INTERESTING SECTIONS")
    print(f"=" * 80)
    
    interesting_ids = [
        "section-barbarian",
        "section-spellcasting", 
        "section-combat",
        "section-conditions",
        "rage",
        "fireball",
        "grappled"
    ]
    
    for section_id in interesting_ids:
        if section_id in sections_dict:
            section = sections_dict[section_id]
            print(f"\n🔎 {section_id.upper()}:")
            print(f"   Title: {section.title}")
            print(f"   Level: {section.level}")
            print(f"   Categories: {[cat.name for cat in section.categories]}")
            print(f"   Content: {section.content[:200]}...")
        else:
            print(f"\n❓ {section_id}: Not found")
    
    # Show category distribution
    print(f"\n" + "=" * 80)
    print(f"📊 CATEGORY DISTRIBUTION")
    print(f"=" * 80)
    
    category_counts = {}
    uncategorized_count = 0
    
    for section in all_sections:
        if section.categories:
            for category in section.categories:
                cat_name = category.name
                if cat_name not in category_counts:
                    category_counts[cat_name] = 0
                category_counts[cat_name] += 1
        else:
            uncategorized_count += 1
    
    total_categorized = sum(category_counts.values())
    print(f"📊 CATEGORIZATION SUMMARY:")
    print(f"   Total sections: {len(all_sections):4d}")
    print(f"   Categorized:    {total_categorized:4d}")
    print(f"   Uncategorized:  {uncategorized_count:4d}")
    print(f"   Coverage:       {(total_categorized/len(all_sections)*100):5.1f}%")
    print()
    
    print(f"📊 CATEGORY BREAKDOWN:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category:20s}: {count:4d} sections")
    
    if uncategorized_count > 0:
        print(f"   {'UNCATEGORIZED':20s}: {uncategorized_count:4d} sections")
        
    # Show some examples of uncategorized sections
    print(f"\n🔍 UNCATEGORIZED SECTION EXAMPLES:")
    uncategorized_examples = [s for s in all_sections if not s.categories][:10]
    for i, section in enumerate(uncategorized_examples, 1):
        print(f"   {i:2d}. {section.id:<30s} (Level {section.level}) - {section.title}")
        if i >= 10:
            break
    if len(uncategorized_examples) > 10:
        print(f"   ... and {len(uncategorized_examples)-10} more uncategorized sections")


if __name__ == "__main__":
    main()
