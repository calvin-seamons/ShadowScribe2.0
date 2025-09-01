#!/usr/bin/env python3
"""
Verify and explore the D&D 5e Rulebook Storage System

This script loads the built storage system and provides detailed statistics
and sample content to verify everything is working correctly.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook.storage import RulebookStorage


def main():
    """Verify the storage system"""
    print("🔍 Verifying D&D 5e Rulebook Storage System")
    print("=" * 50)
    
    # Load storage
    storage = RulebookStorage()
    if not storage.load_from_disk():
        print("❌ Error: Could not load storage system")
        return
    
    # Get detailed statistics
    stats = storage.get_stats()
    
    print(f"📊 Storage Statistics:")
    print(f"Total Sections: {stats['total_sections']}")
    print(f"Embedding Coverage: {stats['embedding_coverage']}")
    print(f"Embedding Model: {stats['embedding_model']}")
    
    print(f"\n📂 Category Distribution:")
    for category, count in sorted(stats['category_counts'].items()):
        if count > 0:
            print(f"  {category}: {count:3d} sections")
    
    print(f"\n📚 Level Distribution:")
    for level, count in sorted(stats['level_counts'].items()):
        print(f"  {level}: {count:3d} sections")
    
    # Show some sample sections from each category
    print(f"\n🎯 Sample Sections by Category:")
    
    for category in storage.category_index:
        if len(storage.category_index[category]) > 0:
            section_ids = list(storage.category_index[category])[:3]  # First 3
            print(f"\n  {category.name}:")
            for section_id in section_ids:
                if section_id in storage.sections:
                    section = storage.sections[section_id]
                    print(f"    • {section.title} (Level {section.level})")
                    # Show content preview
                    content_preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
                    print(f"      Content: {content_preview}")
    
    # Test embedding quality by looking at vector dimensions
    print(f"\n🧠 Embedding Quality Check:")
    sections_with_embeddings = [s for s in storage.sections.values() if s.vector is not None]
    if sections_with_embeddings:
        first_section = sections_with_embeddings[0]
        vector_dim = len(first_section.vector)
        print(f"  Vector Dimension: {vector_dim}")
        print(f"  Sample Vector (first 5): {first_section.vector[:5]}")
        print(f"  Example Section: '{first_section.title}'")
    
    # Show hierarchy examples
    print(f"\n🌳 Hierarchy Examples:")
    chapters = [s for s in storage.sections.values() if s.level == 1][:3]
    for chapter in chapters:
        print(f"\n  Chapter: {chapter.title}")
        if chapter.children_ids:
            for child_id in chapter.children_ids[:2]:  # First 2 children
                if child_id in storage.sections:
                    child = storage.sections[child_id]
                    print(f"    └─ {child.title} (Level {child.level})")
                    if child.children_ids:
                        for grandchild_id in child.children_ids[:2]:  # First 2 grandchildren
                            if grandchild_id in storage.sections:
                                grandchild = storage.sections[grandchild_id]
                                print(f"       └─ {grandchild.title} (Level {grandchild.level})")
    
    print(f"\n✅ Storage system verification complete!")
    print(f"Ready for semantic search and content retrieval operations.")


if __name__ == "__main__":
    main()
