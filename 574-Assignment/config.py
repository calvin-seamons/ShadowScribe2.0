"""
Configuration for 574 Assignment RAG Comparison
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration for RAG system comparison"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
    GROUND_TRUTH_DIR = PROJECT_ROOT / "ground_truth"
    RESULTS_DIR = PROJECT_ROOT / "results"
    
    # System 1: OpenAI + In-Memory
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_EMBEDDING_MODEL = 'text-embedding-3-large'
    OPENAI_EMBEDDING_DIM = 3072
    OPENAI_STORAGE_PATH = EMBEDDINGS_DIR / "openai_embeddings.pkl"
    
    # System 2: Qwen + Milvus
    QWEN_MODEL_NAME = 'Qwen/Qwen2.5-Coder-0.5B-Instruct'  # Smaller, faster model
    QWEN_EMBEDDING_DIM = 512
    MILVUS_URI = str(EMBEDDINGS_DIR / "qwen_milvus.db")
    MILVUS_COLLECTION_NAME = "rulebook_sections"
    
    # Evaluation settings
    K_VALUES = [1, 3, 10]  # Precision@k, Recall@k, nDCG@k values
    
    # Scoring weights (from existing system)
    SEMANTIC_WEIGHT = 0.75
    ENTITY_WEIGHT = 0.25
    CONTEXT_WEIGHT = 0.15
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Create directories if they don't exist
        cls.EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        return True


# Validate on import
Config.validate()
