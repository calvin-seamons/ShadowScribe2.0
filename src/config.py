"""
RAG System Configuration
Centralized configuration for embedding models, API keys, and system settings
"""
from typing import Literal, Optional
from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables at module level - find .env in project root
project_root = Path(__file__).parent.parent  # Go up from src/config.py to project root
env_path = project_root / '.env'
load_dotenv(env_path)


EmbeddingModel = Literal[
    "text-embedding-3-small",  # Fast, good quality (1536 dim)
    "text-embedding-3-large",  # Slower, best quality (3072 dim) 
    "text-embedding-ada-002",  # Legacy, fast (1536 dim)
    "local-minilm-l6",         # Local, very fast (384 dim)
    "local-mpnet-base"         # Local, fast (768 dim)
]

# OpenAI Model Categories - Different models require different parameters
OpenAIStandardModel = Literal[
    # Standard models - support temperature, max_tokens
    "gpt-4o",                  # High quality, multimodal
    "gpt-4o-mini",            # Fast, cost-effective
    "gpt-4-turbo",            # High quality, large context
    "gpt-4",                  # High quality, standard
    "gpt-3.5-turbo",          # Legacy, fast
    "gpt-3.5-turbo-16k"       # Legacy, large context
]

OpenAIReasoningModel = Literal[
    # Reasoning models - no temperature/max_tokens, use max_completion_tokens
    "o1",                     # Advanced reasoning
    "o1-mini",                # Fast reasoning
    "gpt-5",                  # Latest flagship reasoning
    "gpt-5-mini",             # Fast flagship reasoning  
    "gpt-5-nano"              # Ultra-fast reasoning
]

AnthropicModel = Literal[
    # Claude 4 models - Latest generation
    "claude-opus-4-1-20250805",   # Latest Claude 4 Opus
    "claude-opus-4-1",            # Claude 4 Opus (alias)
    "claude-opus-4-20250514",     # Claude 4 Opus (May 2025)
    "claude-opus-4-0",            # Claude 4 Opus (alias)
    "claude-sonnet-4-20250514",   # Claude 4 Sonnet
    "claude-sonnet-4-0",          # Claude 4 Sonnet (alias)
    
    # Claude 3.7 models - Advanced reasoning
    "claude-3-7-sonnet-20250219", # Claude 3.7 Sonnet
    "claude-3-7-sonnet-latest",   # Claude 3.7 Sonnet (latest alias)
    
    # Claude 3.5 models - Balanced quality/speed
    "claude-3-5-haiku-20241022",  # Claude 3.5 Haiku (specific version)
    "claude-3-5-haiku-latest",    # Claude 3.5 Haiku (latest alias) - Fast, cost-effective
    "claude-3-5-sonnet-latest",   # Claude 3.5 Sonnet (latest alias) - Balanced quality/speed
    
    # Claude 3 models - Stable versions
    "claude-3-opus-latest",       # Claude 3 Opus (highest quality)
    "claude-3-haiku-20240307"     # Claude 3 Haiku (specific version)
]


@dataclass
class RAGConfig:
    """Configuration for the RAG system"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # LLM Client Settings
    primary_llm_provider: str = "anthropic"  # "openai" or "anthropic"
    router_llm_provider: str = "anthropic"   # Provider for router decisions
    final_response_llm_provider: str = "anthropic"  # Provider for final response

    # Model Settings - Updated with latest available models (as of Sept 2025)
    # OpenAI Models
    openai_router_model: str = "gpt-4o-mini"  # Fast, cost-effective for routing
    openai_final_model: str = "gpt-4o"        # High quality for final responses
    
    # Anthropic Models  
    anthropic_router_model: str = "claude-3-5-haiku-latest"   # Fast, cost-effective for routing
    anthropic_final_model: str = "claude-3-5-haiku-latest"    # Latest, highest quality Claude 4
    
    # Embedding Model Settings
    embedding_model: EmbeddingModel = "text-embedding-3-small"  # Default: fast and good
    
    # LLM Generation Settings
    # Router LLM Settings (fast, cheaper models for routing decisions)
    router_temperature: float = 0.3
    router_max_tokens: int = 2000
    router_max_completion_tokens: int = 2000  # For reasoning models
    
    # Final Response LLM Settings (higher quality models for final responses)
    final_temperature: float = 0.7
    final_max_tokens: int = 2000
    final_max_completion_tokens: int = 2000  # For reasoning models
    
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
        # Only require the API key for the providers you're actually using
        providers_needed = {self.router_llm_provider, self.final_response_llm_provider, self.primary_llm_provider}
        
        if "openai" in providers_needed and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required but not found in environment variables")
        
        if "anthropic" in providers_needed and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required but not found in environment variables")
        
        # Warn about unused API keys
        if "openai" not in providers_needed and self.openai_api_key:
            print("ℹ️  OpenAI API key found but not needed with current provider settings")
        
        if "anthropic" not in providers_needed and self.anthropic_api_key:
            print("ℹ️  Anthropic API key found but not needed with current provider settings")
    
    @classmethod
    def from_env(cls) -> 'RAGConfig':
        """Create config from environment variables with defaults"""
        return cls(
            # API Keys
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            
            # LLM Provider Settings
            primary_llm_provider=os.getenv('RAG_PRIMARY_LLM_PROVIDER', 'anthropic'),
            router_llm_provider=os.getenv('RAG_ROUTER_LLM_PROVIDER', 'anthropic'),
            final_response_llm_provider=os.getenv('RAG_FINAL_LLM_PROVIDER', 'anthropic'),
            
            # Model Settings - Updated defaults
            openai_router_model=os.getenv('RAG_OPENAI_ROUTER_MODEL', 'gpt-4o-mini'),
            openai_final_model=os.getenv('RAG_OPENAI_FINAL_MODEL', 'gpt-4o'),
            anthropic_router_model=os.getenv('RAG_ANTHROPIC_ROUTER_MODEL', 'claude-3-5-haiku-latest'),
            anthropic_final_model=os.getenv('RAG_ANTHROPIC_FINAL_MODEL', 'claude-opus-4-1'),
            
            # Embedding and Query Settings
            embedding_model=os.getenv('RAG_EMBEDDING_MODEL', 'text-embedding-3-small'),
            
            # LLM Generation Settings
            router_temperature=float(os.getenv('RAG_ROUTER_TEMPERATURE', '0.3')),
            router_max_tokens=int(os.getenv('RAG_ROUTER_MAX_TOKENS', '2000')),
            router_max_completion_tokens=int(os.getenv('RAG_ROUTER_MAX_COMPLETION_TOKENS', '2000')),
            final_temperature=float(os.getenv('RAG_FINAL_TEMPERATURE', '0.7')),
            final_max_tokens=int(os.getenv('RAG_FINAL_MAX_TOKENS', '2000')),
            final_max_completion_tokens=int(os.getenv('RAG_FINAL_MAX_COMPLETION_TOKENS', '2000')),
            
            max_results=int(os.getenv('RAG_MAX_RESULTS', '10')),
            entity_boost_weight=float(os.getenv('RAG_ENTITY_BOOST_WEIGHT', '0.25')),
            context_hint_weight=float(os.getenv('RAG_CONTEXT_HINT_WEIGHT', '0.15')),
            embedding_cache_size=int(os.getenv('RAG_CACHE_SIZE', '1000')),
            local_model_device=os.getenv('RAG_LOCAL_DEVICE', 'cpu')
        )
    
    @classmethod
    def from_defaults(cls) -> 'RAGConfig':
        """Create config using class defaults, only overriding with environment for API keys"""
        # Get API keys from environment first
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Create instance with defaults, including the API keys
        config = cls(
            openai_api_key=openai_key,
            anthropic_api_key=anthropic_key
        )
        
        return config
    
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

    def is_reasoning_model(self, model: str) -> bool:
        """Check if a model is a reasoning model that requires special parameters"""
        reasoning_models = {"o1", "o1-mini", "gpt-5", "gpt-5-mini", "gpt-5-nano"}
        return model in reasoning_models
    
    def is_standard_model(self, model: str) -> bool:
        """Check if a model supports standard parameters (temperature, max_tokens)"""
        return not self.is_reasoning_model(model)
    
    def get_available_openai_models(self) -> dict:
        """Get all available OpenAI models categorized by type"""
        return {
            "standard": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
            "reasoning": ["o1", "o1-mini", "gpt-5", "gpt-5-mini", "gpt-5-nano"]
        }
    
    def get_available_anthropic_models(self) -> dict:
        """Get all available Anthropic models categorized by generation"""
        return {
            "claude_4": [
                "claude-opus-4-1-20250805", "claude-opus-4-1", 
                "claude-opus-4-20250514", "claude-opus-4-0",
                "claude-sonnet-4-20250514", "claude-sonnet-4-0"
            ],
            "claude_3_7": [
                "claude-3-7-sonnet-20250219", "claude-3-7-sonnet-latest"
            ],
            "claude_3_5": [
                "claude-3-5-haiku-20241022", "claude-3-5-haiku-latest"
                # Removed claude-3-5-sonnet-latest - returns 404
            ],
            "claude_3": [
                "claude-3-haiku-20240307"
                # Removed claude-3-opus-latest - returns 404
            ]
        }
    
    def get_router_llm_params(self, model: Optional[str] = None) -> dict:
        """Get LLM parameters for router calls (fast, cheaper models)"""
        model = model or (
            self.openai_router_model if self.router_llm_provider == "openai" 
            else self.anthropic_router_model
        )
        
        if self.is_reasoning_model(model):
            # Reasoning models don't support temperature
            return {
                "max_completion_tokens": self.router_max_completion_tokens
            }
        else:
            # Standard models
            return {
                "temperature": self.router_temperature,
                "max_tokens": self.router_max_tokens
            }
    
    def get_final_llm_params(self, model: Optional[str] = None) -> dict:
        """Get LLM parameters for final response calls (higher quality models)"""
        model = model or (
            self.openai_final_model if self.final_response_llm_provider == "openai" 
            else self.anthropic_final_model
        )
        
        if self.is_reasoning_model(model):
            # Reasoning models don't support temperature
            return {
                "max_completion_tokens": self.final_max_completion_tokens
            }
        else:
            # Standard models
            return {
                "temperature": self.final_temperature,
                "max_tokens": self.final_max_tokens
            }


# Global config instance
_config: Optional[RAGConfig] = None


def get_config() -> RAGConfig:
    """Get the global RAG configuration instance"""
    global _config
    if _config is None:
        _config = RAGConfig.from_defaults()  # Use class defaults instead of env defaults
    return _config


def set_config(config: RAGConfig) -> None:
    """Set the global RAG configuration instance"""
    global _config
    _config = config


def get_embedding_model() -> EmbeddingModel:
    """Quick helper to get just the embedding model"""
    return get_config().embedding_model
