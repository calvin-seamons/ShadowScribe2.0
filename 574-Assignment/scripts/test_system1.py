"""Quick test script to verify both systems work"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from implementations import OpenAIInMemoryRAG
from config import Config

def test_system1():
    """Test System 1 (OpenAI + In-Memory)"""
    print("\n" + "="*60)
    print("Testing System 1: OpenAI + In-Memory")
    print("="*60)
    
    try:
        # Initialize
        print("\n1. Initializing system...")
        system = OpenAIInMemoryRAG()
        print("   ✅ System initialized")
        
        # Test query
        print("\n2. Testing query...")
        test_query = "How does concentration work?"
        test_intention = "rule_mechanics"
        test_entities = ["concentration"]
        
        results = system.query(
            user_query=test_query,
            intention=test_intention,
            entities=test_entities,
            k=3
        )
        
        print(f"\n   Query: '{test_query}'")
        print(f"   Found {len(results)} results:")
        
        for i, result in enumerate(results, 1):
            section = result['section']
            score = result['final_score']
            print(f"\n   {i}. {section['title']}")
            print(f"      Score: {score:.4f}")
            print(f"      Semantic: {result['score_components']['semantic']:.4f}")
            print(f"      Entity: {result['score_components']['entity']:.4f}")
            print(f"      Content preview: {section['content'][:100]}...")
        
        print("\n✅ System 1 working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system1()
    sys.exit(0 if success else 1)
