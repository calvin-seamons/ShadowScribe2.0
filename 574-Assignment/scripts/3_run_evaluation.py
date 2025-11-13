"""
Script 3: Run Evaluation
Main experiment runner - evaluates both systems and generates reports
"""
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from implementations import OpenAIInMemoryRAG, QwenMilvusRAG
from evaluation import RAGEvaluator
from config import Config


def generate_comparison_report(results: dict, output_path: Path):
    """Generate CSV comparison report"""
    
    # Extract aggregated metrics
    comp = results['comparative_metrics']
    
    # Create comparison dataframe
    metrics = []
    for metric_name in comp['system1']['metrics'].keys():
        s1_data = comp['system1']['metrics'][metric_name]
        s2_data = comp['system2']['metrics'][metric_name]
        
        metrics.append({
            'Metric': metric_name,
            'System 1 (OpenAI) Mean': f"{s1_data['mean']:.4f}",
            'System 1 Std': f"{s1_data['std']:.4f}",
            'System 2 (Qwen) Mean': f"{s2_data['mean']:.4f}",
            'System 2 Std': f"{s2_data['std']:.4f}",
            'Difference': f"{s2_data['mean'] - s1_data['mean']:+.4f}"
        })
    
    df = pd.DataFrame(metrics)
    df.to_csv(output_path, index=False)
    print(f"\n✅ Comparison report saved to: {output_path}")


def print_summary(results: dict):
    """Print summary to console"""
    comp = results['comparative_metrics']
    
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    print("\n📊 LATENCY COMPARISON")
    print(f"  System 1 (OpenAI + In-Memory):")
    print(f"    Mean: {comp['system1']['latency']['mean_ms']:.1f}ms")
    print(f"    Range: {comp['system1']['latency']['min_ms']:.1f}ms - {comp['system1']['latency']['max_ms']:.1f}ms")
    
    print(f"\n  System 2 (Qwen + Milvus):")
    print(f"    Mean: {comp['system2']['latency']['mean_ms']:.1f}ms")
    print(f"    Range: {comp['system2']['latency']['min_ms']:.1f}ms - {comp['system2']['latency']['max_ms']:.1f}ms")
    
    speedup = comp['system1']['latency']['mean_ms'] / comp['system2']['latency']['mean_ms']
    print(f"\n  ⚡ System 2 is {speedup:.2f}x faster")
    
    print("\n📈 RETRIEVAL QUALITY")
    for k in Config.K_VALUES:
        s1_prec = comp['system1']['metrics'][f'precision@{k}']['mean']
        s2_prec = comp['system2']['metrics'][f'precision@{k}']['mean']
        print(f"\n  Precision@{k}:")
        print(f"    System 1: {s1_prec:.4f}")
        print(f"    System 2: {s2_prec:.4f}")
        print(f"    Difference: {s2_prec - s1_prec:+.4f}")
    
    print("\n🔗 RESULT AGREEMENT")
    for k in Config.K_VALUES:
        overlap = comp['overlap'][f'overlap@{k}']['mean']
        print(f"  Overlap@{k}: {overlap:.2%}")
    
    if comp['rank_correlation']['mean'] is not None:
        print(f"\n  Rank Correlation (Spearman): {comp['rank_correlation']['mean']:.3f}")
    
    print("\n" + "="*60)


def main():
    """Main evaluation runner"""
    print("="*60)
    print("574 ASSIGNMENT: RAG SYSTEM COMPARISON")
    print("="*60)
    
    # 1. Load test questions
    print("\n1. Loading test questions...")
    questions_path = Path(__file__).parent.parent / "ground_truth" / "test_questions.json"
    
    if not questions_path.exists():
        print(f"Error: Test questions not found at {questions_path}")
        return False
    
    with open(questions_path) as f:
        test_questions = json.load(f)
    
    print(f"   Loaded {len(test_questions)} test questions")
    
    # 2. Initialize both systems
    print("\n2. Initializing RAG systems...")
    
    try:
        print("   Loading System 1 (OpenAI + In-Memory)...")
        system1 = OpenAIInMemoryRAG()
        print("   ✅ System 1 ready")
    except Exception as e:
        print(f"   ❌ Error initializing System 1: {e}")
        return False
    
    try:
        print("   Loading System 2 (Qwen + Milvus)...")
        system2 = QwenMilvusRAG()
        print("   ✅ System 2 ready")
    except Exception as e:
        print(f"   ❌ Error initializing System 2: {e}")
        print("   Make sure to run: uv run python 574-Assignment/scripts/2_build_qwen_milvus.py")
        return False
    
    # 3. Run evaluation
    print("\n3. Running evaluation...")
    evaluator = RAGEvaluator(system1, system2)
    results = evaluator.evaluate_all(test_questions, k_values=Config.K_VALUES)
    
    # 4. Save results
    print("\n4. Saving results...")
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    with open(results_dir / f"system1_results_{timestamp}.json", 'w') as f:
        json.dump(results['system1'], f, indent=2)
    print(f"   ✅ System 1 results saved")
    
    with open(results_dir / f"system2_results_{timestamp}.json", 'w') as f:
        json.dump(results['system2'], f, indent=2)
    print(f"   ✅ System 2 results saved")
    
    # Save comparative metrics
    with open(results_dir / f"comparative_metrics_{timestamp}.json", 'w') as f:
        json.dump(results['comparative_metrics'], f, indent=2)
    print(f"   ✅ Comparative metrics saved")
    
    # Generate CSV report
    generate_comparison_report(results, results_dir / f"comparison_report_{timestamp}.csv")
    
    # 5. Print summary
    print_summary(results)
    
    print(f"\n✅ Evaluation complete!")
    print(f"   Results directory: {results_dir}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
