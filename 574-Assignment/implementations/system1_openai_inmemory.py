"""
System 1: OpenAI + In-Memory RAG
Current system: OpenAI embeddings + in-memory NumPy search
"""
import pickle
import numpy as np
import openai
from typing import List, Dict, Any, Set
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from implementations.base_rag import BaseRAG
from config import Config


class OpenAIInMemoryRAG(BaseRAG):
    """Current system: OpenAI embeddings + in-memory NumPy search"""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize with pickle storage
        
        Args:
            storage_path: Path to pickle file with embeddings
        """
        super().__init__()
        
        if storage_path is None:
            storage_path = str(Config.OPENAI_STORAGE_PATH)
        
        # Load data from pickle
        print(f"Loading OpenAI embeddings from: {storage_path}")
        with open(storage_path, 'rb') as f:
            data = pickle.load(f)
        
        self.sections = data['sections']
        self.category_index = data['category_index']
        self.embedding_model = data.get('embedding_model', Config.OPENAI_EMBEDDING_MODEL)
        
        print(f"Loaded {len(self.sections)} sections with {self.embedding_model}")
        
        # Initialize OpenAI
        openai.api_key = Config.OPENAI_API_KEY
        
        # Query embedding cache (LRU)
        self.embedding_cache = {}
        self.cache_max_size = 1000
    
    def embed_query(self, query: str) -> List[float]:
        """
        OpenAI API call with caching
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        if query in self.embedding_cache:
            return self.embedding_cache[query]
        
        # Call OpenAI API
        response = openai.embeddings.create(
            model=self.embedding_model,
            input=query
        )
        embedding = response.data[0].embedding
        
        # Cache result
        if len(self.embedding_cache) >= self.cache_max_size:
            # Simple eviction: remove first item
            self.embedding_cache.pop(next(iter(self.embedding_cache)))
        self.embedding_cache[query] = embedding
        
        return embedding
    
    def search(self, query_embedding: List[float], intention: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Python category filtering + NumPy cosine similarity
        
        Args:
            query_embedding: Query vector
            intention: Query intention for filtering
            k: Number of results
            
        Returns:
            List of results with section and similarity_score
        """
        # 1. Filter by categories (Python)
        target_categories = self.intention_mapper.get_category_values(intention)
        
        candidate_section_ids: Set[str] = set()
        for cat_value in target_categories:
            if cat_value in self.category_index:
                candidate_section_ids.update(self.category_index[cat_value])
        
        # Get candidate sections
        candidate_sections = [
            self.sections[sid] for sid in candidate_section_ids 
            if sid in self.sections and self.sections[sid].get('vector') is not None
        ]
        
        if not candidate_sections:
            return []
        
        # 2. Cosine similarity (NumPy linear scan)
        results = []
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        for section in candidate_sections:
            section_vec = np.array(section['vector'])
            section_norm = np.linalg.norm(section_vec)
            
            # Cosine similarity
            if query_norm > 0 and section_norm > 0:
                similarity = np.dot(query_vec, section_vec) / (query_norm * section_norm)
            else:
                similarity = 0.0
            
            results.append({
                'section': section,
                'similarity_score': float(similarity)
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:k]
