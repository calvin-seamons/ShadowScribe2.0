"""
System 2: Qwen + FAISS RAG
Modern system: Local Qwen embeddings + FAISS vector similarity search
"""
import sys
import pickle
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from implementations.base_rag import BaseRAG
from config import Config

# Import dependencies
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: FAISS or SentenceTransformers not installed. Install with: uv sync")


class QwenFAISSRAG(BaseRAG):
    """Modern system: Local Qwen embeddings + FAISS vector similarity search"""
    
    def __init__(self, index_path: str = None, metadata_path: str = None):
        """
        Initialize with FAISS index and metadata
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata pickle file
        """
        super().__init__()
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available. Run: uv sync")
        
        # Set default paths
        if index_path is None:
            index_path = Config.FAISS_INDEX_PATH
        if metadata_path is None:
            metadata_path = Config.FAISS_METADATA_PATH
        
        # Initialize Qwen model
        print(f"Loading Qwen model: {Config.QWEN_MODEL_NAME}")
        self.qwen_model = SentenceTransformer(Config.QWEN_MODEL_NAME)
        print("Qwen model loaded successfully")
        
        # Load FAISS index
        print(f"Loading FAISS index: {index_path}")
        self.index = faiss.read_index(index_path)
        print(f"FAISS index loaded: {self.index.ntotal} vectors")
        
        # Load metadata
        print(f"Loading metadata: {metadata_path}")
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.section_ids = metadata['section_ids']
        self.section_metadata = metadata['section_metadata']
        self.category_index = metadata['category_index']
        self.embedding_model = metadata['embedding_model']
        
        print(f"Metadata loaded: {len(self.section_metadata)} sections")
    
    def embed_query(self, query: str) -> List[float]:
        """
        Local Qwen inference
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        embedding = self.qwen_model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
    
    def search(self, query_embedding: List[float], intention: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        FAISS ANN search with category filtering
        
        Args:
            query_embedding: Query vector
            intention: Query intention for filtering
            k: Number of results
            
        Returns:
            List of results with section and similarity_score
        """
        # 1. Get categories for intention
        target_categories = self.intention_mapper.get_category_values(intention)
        
        # 2. Create candidate set based on categories
        if target_categories:
            # Get indices of sections matching target categories
            candidate_indices = set()
            for cat in target_categories:
                if cat in self.category_index:
                    candidate_indices.update(self.category_index[cat])
            
            candidate_indices = list(candidate_indices)
            
            if not candidate_indices:
                # No matching sections for these categories
                return []
        else:
            # No filtering - search all sections
            candidate_indices = list(range(len(self.section_metadata)))
        
        # 3. Prepare query for FAISS
        query_vector = np.array([query_embedding], dtype='float32')
        faiss.normalize_L2(query_vector)  # Normalize for cosine similarity
        
        # 4. Search in FAISS
        if len(candidate_indices) <= k:
            # If candidates <= k, return all with their scores
            search_k = len(candidate_indices)
        else:
            # Search more than k to account for filtering
            search_k = min(k * 3, len(candidate_indices))
        
        # Create a subset index for filtered search (if filtering is active)
        if len(candidate_indices) < len(self.section_metadata):
            # Build temporary index with filtered vectors
            filtered_vectors = np.array([
                self.index.reconstruct(int(idx)) 
                for idx in candidate_indices
            ], dtype='float32')
            
            temp_index = faiss.IndexFlatIP(filtered_vectors.shape[1])  # Inner product (cosine with normalized vectors)
            temp_index.add(filtered_vectors)
            
            distances, indices = temp_index.search(query_vector, min(search_k, temp_index.ntotal))
            
            # Map back to original indices
            original_indices = [candidate_indices[idx] for idx in indices[0]]
        else:
            # Search full index
            distances, indices = self.index.search(query_vector, search_k)
            original_indices = indices[0].tolist()
        
        # 5. Format results
        formatted_results = []
        for idx, distance in zip(original_indices, distances[0]):
            if idx == -1:  # FAISS returns -1 for invalid results
                continue
            
            metadata = self.section_metadata[idx]
            formatted_results.append({
                'section': {
                    'id': metadata['id'],
                    'title': metadata['title'],
                    'content': metadata['content'],
                    'categories': metadata['categories'],
                    'level': metadata['level']
                },
                'similarity_score': float(distance)  # Cosine similarity (0-1)
            })
        
        # Return top k
        return formatted_results[:k]
