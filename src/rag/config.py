"""
RAG System Configuration
Centralized configuration for embedding models, API keys, and system settings
"""
from typing import Literal, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()


EmbeddingModel = Literal[
    "text-embedding-3-small",  # Fast, good quality (1536 dim)
    "text-embedding-3-large",  # Slower, best quality (3072 dim) 
    "text-embedding-ada-002",  # Legacy, fast (1536 dim)
    "local-minilm-l6",         # Local, very fast (384 dim)
    "local-mpnet-base"         # Local, fast (768 dim)
]


@dataclass
class RAGConfig:
    """Configuration for the RAG system"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Embedding Model Settings
    embedding_model: EmbeddingModel = "text-embedding-3-small"  # Default: fast and good
    
    # Query Engine Settings
    max_results: int = 10
    entity_boost_weight: float = 0.25
    context_hint_weight: float = 0.15
    
    # Caching Settings
    embedding_cache_size: int = 1000
    
    # Local Model Settings (if using local models)
    local_model_device: str = "cpu"  # or "cuda" if GPU available
    
    def __post_init__(self):
        """Validate API keys after initialization"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required but not found in environment variables")
        
        # Anthropic is optional for now
        if not self.anthropic_api_key:
            print("⚠️  ANTHROPIC_API_KEY not found - Claude features will be unavailable")
    
    @classmethod
    def from_env(cls) -> 'RAGConfig':
        """Create config from environment variables with defaults"""
        return cls(
            # API Keys
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            
            # Model Settings
            embedding_model=os.getenv('RAG_EMBEDDING_MODEL', 'text-embedding-3-small'),
            max_results=int(os.getenv('RAG_MAX_RESULTS', '10')),
            entity_boost_weight=float(os.getenv('RAG_ENTITY_BOOST_WEIGHT', '0.25')),
            context_hint_weight=float(os.getenv('RAG_CONTEXT_HINT_WEIGHT', '0.15')),
            embedding_cache_size=int(os.getenv('RAG_CACHE_SIZE', '1000')),
            local_model_device=os.getenv('RAG_LOCAL_DEVICE', 'cpu')
        )
    
    def get_embedding_dimensions(self) -> int:
        """Get the expected embedding dimensions for the current model"""
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "local-minilm-l6": 384,
            "local-mpnet-base": 768
        }
        return dimensions.get(self.embedding_model, 1536)
    
    def is_local_model(self) -> bool:
        """Check if the current model is a local model"""
        return self.embedding_model.startswith("local-")
    
    def validate_openai_key(self) -> bool:
        """Validate that OpenAI API key is present and appears valid"""
        if not self.openai_api_key:
            return False
        return self.openai_api_key.startswith('sk-') and len(self.openai_api_key) > 20
    
    def validate_anthropic_key(self) -> bool:
        """Validate that Anthropic API key is present and appears valid"""
        if not self.anthropic_api_key:
            return False
        return self.anthropic_api_key.startswith('sk-ant-') and len(self.anthropic_api_key) > 20


# Global config instance
_config: Optional[RAGConfig] = None


def get_config() -> RAGConfig:
    """Get the global RAG configuration instance"""
    global _config
    if _config is None:
        _config = RAGConfig.from_env()
    return _config


def set_config(config: RAGConfig) -> None:
    """Set the global RAG configuration instance"""
    global _config
    _config = config


def get_embedding_model() -> EmbeddingModel:
    """Quick helper to get just the embedding model"""
    return get_config().embedding_model
