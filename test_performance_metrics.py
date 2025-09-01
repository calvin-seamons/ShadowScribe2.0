#!/usr/bin/env python3
"""
Test script for query performance metrics functionality
"""

import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook.rulebook_types import RulebookQueryIntent, QueryPerformanceMetrics
from src.rag.rulebook.rulebook_storage import RulebookStorage
from src.rag.rulebook.rulebook_query_engine import RulebookQueryEngine

def test_performance_metrics():
    """Test that performance metrics are properly tracked"""
    print("Testing query performance metrics...")
    
    # Load storage
    print("Loading rulebook storage...")
    try:
        storage = RulebookStorage()
        if not storage.load_from_disk():
            print("Failed to load storage from disk")
            return False
        print(f"Loaded {len(storage.sections)} sections")
    except Exception as e:
        print(f"Error loading storage: {e}")
        return False
    
    # Create query engine
    engine = RulebookQueryEngine(storage)
    
    # Test query without performance metrics
    print("\n1. Testing query without performance metrics...")
    results, performance = engine.query(
        intention=RulebookQueryIntent.SPELL_DETAILS,
        user_query="What does fireball do?",
        entities=["fireball"],
        k=3,
        include_performance_metrics=False
    )
    
    print(f"Results: {len(results)} sections")
    print(f"Performance metrics: {performance}")
    assert performance is None, "Performance should be None when not requested"
    
    # Test query with performance metrics
    print("\n2. Testing query with performance metrics...")
    results, performance = engine.query(
        intention=RulebookQueryIntent.SPELL_DETAILS,
        user_query="What does fireball do?",
        entities=["fireball"],
        context_hints=["damage", "area effect"],
        k=3,
        include_performance_metrics=True
    )
    
    print(f"Results: {len(results)} sections")
    print(f"Performance metrics provided: {performance is not None}")
    
    if performance:
        print(f"\nPerformance breakdown:")
        print(f"  Total time: {performance.total_time_ms:.2f}ms")
        print(f"  Intention filtering: {performance.intention_filtering_ms:.2f}ms")
        print(f"  Semantic search: {performance.semantic_search_ms:.2f}ms")
        print(f"  Entity boosting: {performance.entity_boosting_ms:.2f}ms")
        print(f"  Context enhancement: {performance.context_enhancement_ms:.2f}ms")
        print(f"  Result assembly: {performance.result_assembly_ms:.2f}ms")
        print(f"  Children inclusion: {performance.children_inclusion_ms:.2f}ms")
        
        print(f"\nEmbedding performance:")
        print(f"  Cache hits: {performance.embedding_cache_hits}")
        print(f"  Cache misses: {performance.embedding_cache_misses}")
        print(f"  API calls: {performance.embedding_api_calls}")
        print(f"  Total embedding time: {performance.embedding_total_ms:.2f}ms")
        
        print(f"\nSearch scope:")
        print(f"  Total sections available: {performance.total_sections_available}")
        print(f"  Sections after filtering: {performance.sections_after_filtering}")
        print(f"  Sections with embeddings: {performance.sections_with_embeddings}")
        print(f"  Results returned: {performance.results_returned}")
        
        # Test conversion to dict
        print(f"\n3. Testing performance metrics to_dict()...")
        perf_dict = performance.to_dict()
        print(f"Dictionary keys: {list(perf_dict.keys())}")
        
        # Verify some key metrics
        assert performance.total_time_ms > 0, "Total time should be positive"
        assert performance.results_returned == len(results), "Results count should match"
        assert performance.total_sections_available > 0, "Should have sections available"
        
        print("✓ All performance metrics tests passed!")
        return True
    else:
        print("✗ Performance metrics not returned when requested")
        return False

if __name__ == "__main__":
    success = test_performance_metrics()
    if success:
        print("\n🎉 Performance metrics implementation working correctly!")
    else:
        print("\n❌ Performance metrics implementation has issues")
        sys.exit(1)
