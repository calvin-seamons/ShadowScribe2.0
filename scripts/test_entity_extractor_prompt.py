"""
Test Entity Extraction Prompt

Tests the new get_entity_extraction_prompt() method with real LLM calls.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from src.llm.central_prompt_manager import CentralPromptManager
from src.llm.llm_client import OpenAILLMClient

# Load environment variables
load_dotenv()

async def test_entity_extraction():
    """Test entity extractor prompt with diverse queries."""
    
    # Initialize components
    llm_client = OpenAILLMClient(api_key=os.getenv("OPENAI_API_KEY"))
    prompt_manager = CentralPromptManager(context_assembler=None)
    
    # Test queries covering different entity types
    test_queries = [
        "What combat abilities do I have tied to Eldaryth of Regret?",
        "Tell me about my Hexblade's Curse ability",
        "How many spell slots do I have?",
        "Remind me who Elara is and what persuasion abilities I have",
        "How does grappling work and what's my athletics bonus?",
        "What spells can I cast?",
        "Tell me about my weapon",
        "Can I use my Eldritch Blast on the orc?",
        "What's my AC?",
        "Tell me about Shadowfell and the Raven Queen"
    ]
    
    print("="*80)
    print("ENTITY EXTRACTION PROMPT TEST")
    print("="*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/{len(test_queries)}] Query: {query}")
        print("-"*80)
        
        # Get prompt
        prompt = prompt_manager.get_entity_extraction_prompt(query)
        
        # Make LLM call
        response = await llm_client.generate_response(prompt, temperature=0.0)
        
        # Strip markdown code blocks if present
        response_text = response.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            result = json.loads(response_text)
            
            # Validate structure
            assert "entities" in result, "Missing 'entities' field"
            assert isinstance(result["entities"], list), "'entities' must be a list"
            
            # Display results
            if result["entities"]:
                print(f"✅ Entities extracted: {len(result['entities'])}")
                for entity in result["entities"]:
                    print(f"   • {entity['name']} (confidence: {entity['confidence']})")
            else:
                print("✅ No entities found (expected for generic queries)")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Response: {response_text[:200]}")
        except AssertionError as e:
            print(f"❌ Validation error: {e}")
            print(f"Result: {result}")
    
    print("\n" + "="*80)
    print("ENTITY EXTRACTION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_entity_extraction())
