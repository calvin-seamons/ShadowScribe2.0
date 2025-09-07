"""
LLM Client Abstraction Layer
Provides a unified interface for different LLM providers (OpenAI, Anthropic)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# LLM client imports
import openai
from anthropic import Anthropic

from .config import get_config


@dataclass
class LLMResponse:
    """Standardized response from LLM calls"""
    content: str
    success: bool = True
    error: Optional[str] = None
    model_used: Optional[str] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_json_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a JSON response from the LLM"""
        pass


class OpenAILLMClient(LLMClient):
    """OpenAI LLM client implementation"""
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI client"""
        config = get_config()
        self.api_key = api_key or config.openai_api_key
        self.default_model = default_model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using OpenAI"""
        try:
            # Extract OpenAI-specific parameters
            model = kwargs.get('model', self.default_model)
            temperature = kwargs.get('temperature', 0.3)
            max_tokens = kwargs.get('max_tokens', 500)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return LLMResponse(
                content=content,
                success=True,
                model_used=model
            )
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                error=str(e),
                model_used=kwargs.get('model', self.default_model)
            )
    
    async def generate_json_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a JSON response using OpenAI"""
        response = await self.generate_response(prompt, **kwargs)
        
        if not response.success:
            return {"error": response.error}
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}


class AnthropicLLMClient(LLMClient):
    """Anthropic (Claude) LLM client implementation"""
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "claude-3-haiku-20240307"):
        """Initialize Anthropic client"""
        config = get_config()
        self.api_key = api_key or config.anthropic_api_key
        self.default_model = default_model
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = Anthropic(api_key=self.api_key)
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Anthropic"""
        try:
            # Extract Anthropic-specific parameters
            model = kwargs.get('model', self.default_model)
            max_tokens = kwargs.get('max_tokens', 500)
            
            response = self.client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            content = response.content[0].text
            return LLMResponse(
                content=content,
                success=True,
                model_used=model
            )
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                error=str(e),
                model_used=kwargs.get('model', self.default_model)
            )
    
    async def generate_json_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a JSON response using Anthropic"""
        response = await self.generate_response(prompt, **kwargs)
        
        if not response.success:
            return {"error": response.error}
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration"""
    
    @staticmethod
    def create_client(provider: str = "openai", **kwargs) -> LLMClient:
        """Create an LLM client based on provider"""
        if provider.lower() == "openai":
            return OpenAILLMClient(**kwargs)
        elif provider.lower() == "anthropic":
            return AnthropicLLMClient(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    def create_default_clients() -> Dict[str, LLMClient]:
        """Create default clients for all available providers"""
        config = get_config()
        clients = {}
        
        # Always create OpenAI client (required)
        if config.openai_api_key:
            clients["openai"] = OpenAILLMClient()
            clients["openai_gpt4"] = OpenAILLMClient(default_model="gpt-4")
        
        # Create Anthropic client if API key is available
        if config.anthropic_api_key:
            clients["anthropic"] = AnthropicLLMClient()
        
        return clients
