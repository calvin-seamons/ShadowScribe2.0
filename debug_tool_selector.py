#!/usr/bin/env python
"""
Debug script to test the tool selector and entity extraction
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.llm.central_prompt_manager import CentralPromptManager
from src.rag.context_assembler import ContextAssembler
from src.config import get_config
from src.llm.llm_client import LLMClientFactory

async def test_prompts():
    """Test the prompt generation and LLM responses"""
    
    # Initialize components
    context_assembler = ContextAssembler()
    prompt_manager = CentralPromptManager(context_assembler)
    config = get_config()
    
    # Create LLM clients
    llm_clients = LLMClientFactory.create_default_clients()
    
    # Test queries
    test_queries = [
        "What is Duskryn's alignment and background?",
        "What's my AC?",
        "Tell me about Elara",
        "How does grappling work?",
        "What spells can I cast?",
    ]
    
    character_name = "Duskryn Nightwarden"
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Character: {character_name}")
        print('='*60)
        
        # Get prompts
        tool_prompt = prompt_manager.get_tool_and_intention_selector_prompt(query, character_name)
        entity_prompt = prompt_manager.get_entity_extraction_prompt(query)
        
        # Print prompt samples
        print("\n📝 TOOL SELECTOR PROMPT (first 500 chars):")
        print("-" * 40)
        print(tool_prompt[:500] + "..." if len(tool_prompt) > 500 else tool_prompt)
        
        print("\n📝 ENTITY EXTRACTOR PROMPT (first 500 chars):")
        print("-" * 40)
        print(entity_prompt[:500] + "..." if len(entity_prompt) > 500 else entity_prompt)
        
        # Get LLM responses
        provider = config.router_llm_provider
        client = llm_clients.get(provider)
        
        if client:
            model = config.anthropic_router_model if provider == "anthropic" else config.openai_router_model
            llm_params = config.get_router_llm_params(model)
            
            print(f"\n🤖 Using {provider} with model {model}")
            
            # Tool selector response
            print("\n🔧 TOOL SELECTOR RESPONSE:")
            print("-" * 40)
            try:
                tool_response = await client.generate_json_response(tool_prompt, model=model, **llm_params)
                import json
                # Response is a dict, not an object with success attribute
                print(json.dumps(tool_response, indent=2))
            except Exception as e:
                print(f"Exception: {e}")
            
            # Entity extractor response
            print("\n🔍 ENTITY EXTRACTOR RESPONSE:")
            print("-" * 40)
            try:
                entity_response = await client.generate_json_response(entity_prompt, model=model, **llm_params)
                import json
                # Response is a dict, not an object with success attribute
                print(json.dumps(entity_response, indent=2))
            except Exception as e:
                print(f"Exception: {e}")

if __name__ == "__main__":
    print("🚀 Testing Tool Selector and Entity Extractor Prompts")
    asyncio.run(test_prompts())