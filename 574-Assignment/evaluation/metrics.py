"""
Standard Information Retrieval Metrics
Precision@k, Recall@k, MRR, nDCG
"""
import numpy as np
from typing import List, Dict


class RetrievalMetrics:
    """Standard information retrieval metrics"""
    
    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """
        Precision@k: % of top-k results that are relevant
        
        Args:
            retrieved: List of retrieved section IDs (in rank order)
            relevant: List of relevant section IDs (ground truth)
            k: Cutoff position
            
        Returns:
            Precision value between 0.0 and 1.0
        """
        retrieved_at_k = retrieved[:k]
        relevant_retrieved = set(retrieved_at_k) & set(relevant)
        return len(relevant_retrieved) / k if k > 0 else 0.0
    
    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """
        Recall@k: % of relevant results found in top-k
        
        Args:
            retrieved: List of retrieved section IDs (in rank order)
            relevant: List of relevant section IDs (ground truth)
            k: Cutoff position
            
        Returns:
            Recall value between 0.0 and 1.0
        """
        retrieved_at_k = retrieved[:k]
        relevant_retrieved = set(retrieved_at_k) & set(relevant)
        return len(relevant_retrieved) / len(relevant) if relevant else 0.0
    
    @staticmethod
    def mean_reciprocal_rank(retrieved: List[str], relevant: List[str]) -> float:
        """
        MRR: 1 / rank of first relevant result
        
        Args:
            retrieved: List of retrieved section IDs (in rank order)
            relevant: List of relevant section IDs (ground truth)
            
        Returns:
            MRR value between 0.0 and 1.0
        """
        for i, section_id in enumerate(retrieved, 1):
            if section_id in relevant:
                return 1.0 / i
        return 0.0
    
    @staticmethod
    def ndcg_at_k(retrieved: List[str], relevance_scores: Dict[str, float], k: int) -> float:
        """
        nDCG@k: Normalized discounted cumulative gain
        
        Args:
            retrieved: List of retrieved section IDs (in rank order)
            relevance_scores: Dict mapping section IDs to relevance scores (0.0 to 1.0)
            k: Cutoff position
            
        Returns:
            nDCG value between 0.0 and 1.0
        """
        if not relevance_scores:
            return 0.0
        
        # DCG calculation with position-based discounting
        dcg = 0.0
        for i, section_id in enumerate(retrieved[:k], 1):
            rel = relevance_scores.get(section_id, 0.0)
            # Use log2(i+1) for discounting
            dcg += rel / np.log2(i + 1)
        
        # IDCG (ideal DCG) - best possible ordering
        ideal_scores = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_scores))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def average_precision(retrieved: List[str], relevant: List[str]) -> float:
        """
        Average Precision: Mean of precision values at each relevant result position
        
        Args:
            retrieved: List of retrieved section IDs (in rank order)
            relevant: List of relevant section IDs (ground truth)
            
        Returns:
            Average precision value between 0.0 and 1.0
        """
        if not relevant:
            return 0.0
        
        precision_sum = 0.0
        relevant_count = 0
        
        for i, section_id in enumerate(retrieved, 1):
            if section_id in relevant:
                relevant_count += 1
                precision_at_i = relevant_count / i
                precision_sum += precision_at_i
        
        return precision_sum / len(relevant) if relevant else 0.0
