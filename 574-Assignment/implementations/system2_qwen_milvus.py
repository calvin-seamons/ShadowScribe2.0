"""
System 2: Qwen + Milvus RAG
Modern system: Local Qwen embeddings + Milvus vector DB
"""
import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from implementations.base_rag import BaseRAG
from config import Config

# Import dependencies
try:
    from sentence_transformers import SentenceTransformer
    from pymilvus import connections, Collection
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: Milvus or SentenceTransformers not installed. Install with: pip install -r requirements.txt")


class QwenMilvusRAG(BaseRAG):
    """Modern system: Local Qwen embeddings + Milvus vector DB"""
    
    def __init__(self, milvus_uri: str = None):
        """
        Initialize with Milvus connection
        
        Args:
            milvus_uri: URI for Milvus Lite database
        """
        super().__init__()
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available. Run: pip install -r requirements.txt")
        
        if milvus_uri is None:
            milvus_uri = Config.MILVUS_URI
        
        # Initialize Qwen model
        print(f"Loading Qwen model: {Config.QWEN_MODEL_NAME}")
        self.qwen_model = SentenceTransformer(Config.QWEN_MODEL_NAME)
        print("Qwen model loaded successfully")
        
        # Connect to Milvus
        print(f"Connecting to Milvus: {milvus_uri}")
        connections.connect("default", uri=milvus_uri)
        
        # Load collection
        self.collection = Collection(Config.MILVUS_COLLECTION_NAME)
        self.collection.load()
        print(f"Milvus collection loaded: {self.collection.num_entities} entities")
    
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
        Milvus ANN search with native category filtering
        
        Args:
            query_embedding: Query vector
            intention: Query intention for filtering
            k: Number of results
            
        Returns:
            List of results with section and similarity_score
        """
        # 1. Get categories for intention
        target_categories = self.intention_mapper.get_category_values(intention)
        
        if not target_categories:
            # No filtering if no categories
            filter_expr = None
        else:
            # Create Milvus filter expression
            # categories is an array field, check if any target category is in it
            filter_expr = " || ".join([f"array_contains(categories, {cat})" for cat in target_categories])
        
        # 2. Milvus search with native filtering
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 100}  # HNSW search parameter
        }
        
        try:
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                expr=filter_expr,
                limit=k,
                output_fields=["section_id", "title", "content", "categories", "level"]
            )
        except Exception as e:
            print(f"Milvus search error: {e}")
            return []
        
        # 3. Convert Milvus results to standard format
        formatted_results = []
        for hit in results[0]:
            formatted_results.append({
                'section': {
                    'id': hit.entity.get('section_id'),
                    'title': hit.entity.get('title'),
                    'content': hit.entity.get('content'),
                    'categories': hit.entity.get('categories'),
                    'level': hit.entity.get('level')
                },
                'similarity_score': hit.score
            })
        
        return formatted_results
