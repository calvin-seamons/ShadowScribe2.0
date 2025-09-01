"""
Simple demo of RulebookQueryEngine usage
"""

import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook import RulebookStorage, RulebookQueryEngine
from src.rag.rulebook.rulebook_types import RulebookQueryIntent


def main():
    """Simple demo of the query engine"""
    print("D&D 5e Rulebook Query Engine Demo")
    print("=" * 40)
    
    # Initialize storage and engine
    storage = RulebookStorage("knowledge_base/processed_rulebook")
    
    try:
        storage.load_from_disk()
        print(f"✓ Loaded {len(storage.sections)} rulebook sections")
    except FileNotFoundError:
        print("✗ No rulebook storage found!")
        print("Please run: python -m scripts.build_rulebook_storage")
        return
    
    engine = RulebookQueryEngine(storage)
    print("✓ Query engine initialized")
    
    # Simple query example
    print("\n" + "=" * 40)
    print("Sample Query: Fireball spell details")
    
    results, performance = engine.query(
        intention=RulebookQueryIntent.SPELL_DETAILS,
        user_query="How does the fireball spell work?",
        entities=["fireball"],
        context_hints=["damage", "area of effect"],
        k=2
    )
    
    print(f"Found {len(results)} results:")
    print(f"Query completed in {performance.total_time_ms:.1f}ms")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.section.title} (Score: {result.score:.3f})")
        print(f"   Categories: {[cat.name for cat in result.section.categories]}")
        print(f"   Matched: {result.matched_entities}")
        
        # Show first 150 chars of content
        preview = result.section.content[:150].replace('\n', ' ')
        if len(result.section.content) > 150:
            preview += "..."
        print(f"   Preview: {preview}")


if __name__ == "__main__":
    main()
