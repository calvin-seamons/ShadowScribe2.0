"""
Base RAG Interface
Abstract base class ensuring both systems implement the same API
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.intention_mapper import IntentionMapper
from shared.result_enhancer import ResultEnhancer
from config import Config


class BaseRAG(ABC):
    """Abstract interface ensuring both systems implement same API"""
    
    def __init__(self):
        """Initialize shared components"""
        self.intention_mapper = IntentionMapper()
        self.result_enhancer = ResultEnhancer(
            semantic_weight=Config.SEMANTIC_WEIGHT,
            entity_weight=Config.ENTITY_WEIGHT,
            context_weight=Config.CONTEXT_WEIGHT
        )
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """
        Embed query text into vector
        
        Args:
            query: Query text string
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], intention: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Search with intention-based filtering
        
        Args:
            query_embedding: Embedded query vector
            intention: Query intention for category filtering
            k: Number of results to return
            
        Returns:
            List of dicts with 'section' and 'similarity_score' keys
        """
        pass
    
    def query(
        self, 
        user_query: str, 
        intention: str, 
        entities: List[str], 
        context_hints: List[str] = None,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Complete query pipeline (same for both systems)
        
        Args:
            user_query: User's query string
            intention: Query intention
            entities: Extracted entities
            context_hints: Optional context phrases
            k: Number of final results
            
        Returns:
            List of enhanced results sorted by final score
        """
        if context_hints is None:
            context_hints = []
        
        # 1. Embed query (system-specific)
        query_embedding = self.embed_query(user_query)
        
        # 2. Search with filtering (system-specific)
        # Get more results than k for better post-processing
        raw_results = self.search(query_embedding, intention, k=50)
        
        # 3. Post-processing (shared)
        enhanced_results = self.result_enhancer.enhance_results(
            raw_results, entities, context_hints
        )
        
        # 4. Return top-k
        return enhanced_results[:k]
