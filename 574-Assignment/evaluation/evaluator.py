"""
RAG Evaluator
Orchestrates experiments and collects comparative metrics
"""
import time
import numpy as np
from typing import List, Dict, Any
from scipy.stats import spearmanr

from evaluation.metrics import RetrievalMetrics


class RAGEvaluator:
    """Run experiments and collect comparative metrics"""
    
    def __init__(self, system1, system2):
        """
        Initialize evaluator with two RAG systems
        
        Args:
            system1: First RAG system (BaseRAG instance)
            system2: Second RAG system (BaseRAG instance)
        """
        self.system1 = system1
        self.system2 = system2
        self.metrics = RetrievalMetrics()
    
    def evaluate_all(
        self, 
        test_questions: List[Dict[str, Any]], 
        k_values: List[int] = None
    ) -> Dict[str, Any]:
        """
        Run both systems on all test questions
        
        Args:
            test_questions: List of test question dicts
            k_values: List of k values for metrics (default: [1, 3, 10])
            
        Returns:
            Dict with results for both systems and comparative metrics
        """
        if k_values is None:
            k_values = [1, 3, 10]
        
        results = {
            'system1': [],
            'system2': [],
            'comparative_metrics': {},
            'config': {
                'k_values': k_values,
                'num_questions': len(test_questions)
            }
        }
        
        print(f"\n{'='*60}")
        print(f"Running evaluation on {len(test_questions)} questions")
        print(f"{'='*60}\n")
        
        for idx, question in enumerate(test_questions, 1):
            print(f"Question {idx}/{len(test_questions)}: {question['query'][:60]}...")
            
            # Run System 1
            start = time.perf_counter()
            s1_results = self.system1.query(
                question['query'],
                question['intention'],
                question['entities'],
                context_hints=question.get('context_hints', []),
                k=max(k_values)
            )
            s1_time = (time.perf_counter() - start) * 1000
            
            # Run System 2
            start = time.perf_counter()
            s2_results = self.system2.query(
                question['query'],
                question['intention'],
                question['entities'],
                context_hints=question.get('context_hints', []),
                k=max(k_values)
            )
            s2_time = (time.perf_counter() - start) * 1000
            
            # Compute metrics for each k
            s1_metrics = self._compute_metrics(s1_results, question, k_values)
            s2_metrics = self._compute_metrics(s2_results, question, k_values)
            
            # Extract section IDs
            s1_section_ids = [r['section']['id'] for r in s1_results]
            s2_section_ids = [r['section']['id'] for r in s2_results]
            
            # Compute overlap
            overlap = self._compute_overlap(s1_section_ids, s2_section_ids, k_values)
            
            results['system1'].append({
                'question_id': question['id'],
                'query': question['query'],
                'latency_ms': s1_time,
                'metrics': s1_metrics,
                'retrieved_sections': s1_section_ids
            })
            
            results['system2'].append({
                'question_id': question['id'],
                'query': question['query'],
                'latency_ms': s2_time,
                'metrics': s2_metrics,
                'retrieved_sections': s2_section_ids
            })
            
            print(f"  System 1: {s1_time:.1f}ms | System 2: {s2_time:.1f}ms")
            print(f"  Overlap@10: {overlap['overlap@10']:.2%}\n")
        
        # Aggregate metrics
        results['comparative_metrics'] = self._aggregate_results(results)
        
        return results
    
    def _compute_metrics(
        self, 
        results: List[Dict[str, Any]], 
        question: Dict[str, Any], 
        k_values: List[int]
    ) -> Dict[str, float]:
        """
        Compute all metrics for a single query
        
        Args:
            results: List of search results
            question: Test question dict
            k_values: List of k values
            
        Returns:
            Dict of metric name to value
        """
        retrieved_ids = [r['section']['id'] for r in results]
        expected_ids = question['expected_sections']
        relevance_scores = question.get('relevance_scores', {})
        
        metrics = {}
        for k in k_values:
            metrics[f'precision@{k}'] = self.metrics.precision_at_k(retrieved_ids, expected_ids, k)
            metrics[f'recall@{k}'] = self.metrics.recall_at_k(retrieved_ids, expected_ids, k)
            metrics[f'ndcg@{k}'] = self.metrics.ndcg_at_k(retrieved_ids, relevance_scores, k)
        
        metrics['mrr'] = self.metrics.mean_reciprocal_rank(retrieved_ids, expected_ids)
        metrics['average_precision'] = self.metrics.average_precision(retrieved_ids, expected_ids)
        
        return metrics
    
    def _compute_overlap(
        self, 
        s1_ids: List[str], 
        s2_ids: List[str], 
        k_values: List[int]
    ) -> Dict[str, float]:
        """
        Compute overlap between two result lists
        
        Args:
            s1_ids: System 1 section IDs
            s2_ids: System 2 section IDs
            k_values: List of k values
            
        Returns:
            Dict of overlap metrics
        """
        overlap = {}
        for k in k_values:
            s1_k = set(s1_ids[:k])
            s2_k = set(s2_ids[:k])
            if s1_k or s2_k:
                overlap[f'overlap@{k}'] = len(s1_k & s2_k) / k
            else:
                overlap[f'overlap@{k}'] = 0.0
        
        return overlap
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate metrics across all queries
        
        Args:
            results: Full results dict
            
        Returns:
            Dict of aggregated comparative metrics
        """
        s1_results = results['system1']
        s2_results = results['system2']
        
        # Aggregate latencies
        s1_latencies = [r['latency_ms'] for r in s1_results]
        s2_latencies = [r['latency_ms'] for r in s2_results]
        
        # Aggregate metrics
        metric_keys = list(s1_results[0]['metrics'].keys())
        s1_aggregated = {}
        s2_aggregated = {}
        
        for key in metric_keys:
            s1_values = [r['metrics'][key] for r in s1_results]
            s2_values = [r['metrics'][key] for r in s2_results]
            
            s1_aggregated[key] = {
                'mean': np.mean(s1_values),
                'std': np.std(s1_values),
                'min': np.min(s1_values),
                'max': np.max(s1_values)
            }
            
            s2_aggregated[key] = {
                'mean': np.mean(s2_values),
                'std': np.std(s2_values),
                'min': np.min(s2_values),
                'max': np.max(s2_values)
            }
        
        # Compute overlap statistics
        k_values = results['config']['k_values']
        overlap_stats = {}
        for k in k_values:
            overlaps = []
            for i in range(len(s1_results)):
                s1_ids = set(s1_results[i]['retrieved_sections'][:k])
                s2_ids = set(s2_results[i]['retrieved_sections'][:k])
                if s1_ids or s2_ids:
                    overlaps.append(len(s1_ids & s2_ids) / k)
            
            overlap_stats[f'overlap@{k}'] = {
                'mean': np.mean(overlaps) if overlaps else 0.0,
                'std': np.std(overlaps) if overlaps else 0.0
            }
        
        # Compute rank correlation
        rank_correlations = []
        for i in range(len(s1_results)):
            s1_ids = s1_results[i]['retrieved_sections'][:10]
            s2_ids = s2_results[i]['retrieved_sections'][:10]
            
            # Create rank vectors (only for shared items)
            shared_ids = set(s1_ids) & set(s2_ids)
            if len(shared_ids) > 1:
                s1_ranks = [s1_ids.index(sid) for sid in shared_ids if sid in s1_ids]
                s2_ranks = [s2_ids.index(sid) for sid in shared_ids if sid in s2_ids]
                
                if len(s1_ranks) > 1:
                    corr, _ = spearmanr(s1_ranks, s2_ranks)
                    if not np.isnan(corr):
                        rank_correlations.append(corr)
        
        return {
            'system1': {
                'latency': {
                    'mean_ms': np.mean(s1_latencies),
                    'std_ms': np.std(s1_latencies),
                    'min_ms': np.min(s1_latencies),
                    'max_ms': np.max(s1_latencies)
                },
                'metrics': s1_aggregated
            },
            'system2': {
                'latency': {
                    'mean_ms': np.mean(s2_latencies),
                    'std_ms': np.std(s2_latencies),
                    'min_ms': np.min(s2_latencies),
                    'max_ms': np.max(s2_latencies)
                },
                'metrics': s2_aggregated
            },
            'overlap': overlap_stats,
            'rank_correlation': {
                'mean': np.mean(rank_correlations) if rank_correlations else None,
                'std': np.std(rank_correlations) if rank_correlations else None,
                'n_samples': len(rank_correlations)
            }
        }
