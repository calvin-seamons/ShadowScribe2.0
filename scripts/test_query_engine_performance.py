"""
Performance Testing Script for RulebookQueryEngine
Tests query speed, memory usage, and efficiency metrics
"""

import sys
from pathlib import Path
import time
import tracemalloc
from datetime import datetime

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook import RulebookStorage, RulebookQueryEngine
from src.rag.rulebook.rulebook_types import RulebookQueryIntent


def performance_test():
    """Run performance tests on the query engine"""
    
    print("RulebookQueryEngine Performance Test")
    print("=" * 40)
    
    # Setup
    try:
        tracemalloc.start()
        setup_start = time.time()
        
        storage = RulebookStorage("knowledge_base/processed_rulebook")
        storage.load_from_disk()
        engine = RulebookQueryEngine(storage)
        
        setup_time = time.time() - setup_start
        print(f"✓ Setup completed in {setup_time:.2f} seconds")
        print(f"✓ Loaded {len(storage.sections)} sections")
        
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return
    
    # Performance test cases
    test_queries = [
        # Simple queries
        {
            "name": "Simple Spell Query",
            "intention": RulebookQueryIntent.SPELL_DETAILS,
            "query": "fireball",
            "entities": ["fireball"],
            "context_hints": [],
            "k": 3
        },
        {
            "name": "Simple Class Query", 
            "intention": RulebookQueryIntent.CHARACTER_CREATION,
            "query": "wizard",
            "entities": ["wizard"],
            "context_hints": [],
            "k": 3
        },
        # Complex queries with context hints
        {
            "name": "Complex Spell Query",
            "intention": RulebookQueryIntent.SPELL_DETAILS,
            "query": "What are the best damage spells for a 5th level wizard?",
            "entities": ["damage", "spells", "wizard", "5th level"],
            "context_hints": ["fireball", "lightning bolt", "spell slots", "evocation"],
            "k": 5
        },
        {
            "name": "Complex Combat Query",
            "intention": RulebookQueryIntent.ACTION_OPTIONS,
            "query": "How do I optimize action economy in combat with spellcasting and weapon attacks?",
            "entities": ["action economy", "combat", "spellcasting", "weapon attacks"],
            "context_hints": ["bonus action", "reaction", "opportunity attack", "concentration"],
            "k": 5
        },
        # Broad search queries
        {
            "name": "Broad Search Query",
            "intention": RulebookQueryIntent.FIND_BY_CRITERIA,
            "query": "Find all abilities that grant advantage on saving throws",
            "entities": ["abilities", "advantage", "saving throws"],
            "context_hints": ["resistance", "immunity", "proficiency", "magic resistance"],
            "k": 10
        }
    ]
    
    results_log = []
    results_log.append(f"Performance Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results_log.append("=" * 60)
    results_log.append(f"Setup Time: {setup_time:.2f} seconds")
    results_log.append(f"Total Sections: {len(storage.sections)}")
    results_log.append("")
    
    total_start_time = time.time()
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Running: {test['name']}")
        results_log.append(f"{i}. {test['name']}")
        
        # Memory snapshot before query
        snapshot_before = tracemalloc.take_snapshot()
        
        # Time the query
        query_start = time.time()
        
        try:
            results = engine.query(
                intention=test['intention'],
                user_query=test['query'],
                entities=test['entities'],
                context_hints=test['context_hints'],
                k=test['k']
            )
            
            query_time = time.time() - query_start
            
            # Memory snapshot after query
            snapshot_after = tracemalloc.take_snapshot()
            top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
            
            # Calculate memory usage
            total_memory = sum(stat.size for stat in top_stats)
            memory_mb = total_memory / 1024 / 1024
            
            # Results analysis
            result_count = len(results)
            avg_score = sum(r.score for r in results) / len(results) if results else 0
            entity_matches = sum(1 for r in results if r.matched_entities)
            context_matches = sum(1 for r in results if r.matched_context)
            
            # Output metrics
            print(f"   Time: {query_time:.3f}s")
            print(f"   Memory: {memory_mb:.2f}MB")
            print(f"   Results: {result_count}")
            print(f"   Avg Score: {avg_score:.3f}")
            print(f"   Entity Matches: {entity_matches}/{result_count}")
            print(f"   Context Matches: {context_matches}/{result_count}")
            
            # Log detailed metrics
            results_log.append(f"  Query: {test['query']}")
            results_log.append(f"  Entities: {test['entities']}")
            results_log.append(f"  Context Hints: {test['context_hints']}")
            results_log.append(f"  Time: {query_time:.3f} seconds")
            results_log.append(f"  Memory Usage: {memory_mb:.2f} MB")
            results_log.append(f"  Results Count: {result_count}")
            results_log.append(f"  Average Score: {avg_score:.3f}")
            results_log.append(f"  Entity Match Rate: {entity_matches}/{result_count}")
            results_log.append(f"  Context Match Rate: {context_matches}/{result_count}")
            
            # Performance assessment
            if query_time < 1.0 and memory_mb < 10 and result_count > 0:
                assessment = "✓ EXCELLENT"
            elif query_time < 3.0 and memory_mb < 25 and result_count > 0:
                assessment = "~ GOOD"
            elif query_time < 5.0 and result_count > 0:
                assessment = "- ACCEPTABLE"
            else:
                assessment = "✗ POOR"
            
            print(f"   Assessment: {assessment}")
            results_log.append(f"  Assessment: {assessment}")
            
            # Top result details
            if results:
                top_result = results[0]
                results_log.append(f"  Top Result: {top_result.section.title}")
                results_log.append(f"  Top Score: {top_result.score:.4f}")
                results_log.append(f"  Top Matched Entities: {top_result.matched_entities}")
            
            results_log.append("")
            
        except Exception as e:
            error_msg = f"Error: {e}"
            print(f"   ✗ {error_msg}")
            results_log.append(f"  {error_msg}")
            results_log.append("")
    
    total_time = time.time() - total_start_time
    
    # Overall summary
    print(f"\n{'='*40}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*40}")
    print(f"Total test time: {total_time:.2f} seconds")
    print(f"Average time per query: {total_time/len(test_queries):.2f} seconds")
    
    results_log.append("=" * 40)
    results_log.append("PERFORMANCE SUMMARY")
    results_log.append("=" * 40)
    results_log.append(f"Total Test Time: {total_time:.2f} seconds")
    results_log.append(f"Average Time Per Query: {total_time/len(test_queries):.2f} seconds")
    results_log.append(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Stop memory tracking
    tracemalloc.stop()
    
    # Save results
    output_file = f"performance_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in results_log:
                f.write(line + '\n')
        print(f"\n✓ Performance results saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Could not save results: {e}")


if __name__ == "__main__":
    performance_test()
