"""
DEBUG TEST: Central Engine AC Query Issue

This script tests the "What is my character AC" query with detailed debugging
to identify where the issue occurs in the router execution pipeline.
"""

import sys
from pathlib import Path
import asyncio
import json
import traceback

# Standard project root setup
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag.central_engine import CentralEngine
from src.rag.central_prompt_manager import CentralPromptManager
from src.rag.context_assembler import ContextAssembler
from src.rag.config import get_config
from src.utils.character_manager import CharacterManager
from src.rag.rulebook.rulebook_storage import RulebookStorage
from src.rag.session_notes.session_notes_storage import SessionNotesStorage
import pickle
import os


async def debug_test_weapon_query():
    """Test the weapon query with extensive debugging using real storage components."""
    
    print("🚀 DEBUG TEST: Central Engine Weapon Query with Real Storage")
    print("=" * 60)
    
    try:
        # Load storage components
        print("📦 Loading storage components...")
        
        # Load Duskryn character
        character_manager = CharacterManager()
        character_name = "Duskryn Nightwarden"
        try:
            character = character_manager.load_character(character_name)
            print(f"   ✅ Character loaded: {character.character_base.name}")
        except Exception as e:
            print(f"   ⚠️  Failed to load character: {e}")
            character = None
            character_name = "Demo Character"
        
        # Load rulebook storage
        try:
            rulebook_storage = RulebookStorage()
            if rulebook_storage.load_from_disk("rulebook_storage.pkl"):
                print(f"   ✅ Rulebook storage loaded")
            else:
                print(f"   ⚠️  Rulebook storage file not found")
                rulebook_storage = None
        except Exception as e:
            print(f"   ⚠️  Failed to load rulebook storage: {e}")
            rulebook_storage = None
        
        # Load session notes storage
        try:
            session_notes_storage = SessionNotesStorage()
            main_campaign = session_notes_storage.get_campaign("main_campaign")
            if main_campaign:
                print(f"   ✅ Session notes storage loaded for main_campaign")
            else:
                print(f"   ⚠️  Main campaign not found in session notes")
                main_campaign = None
        except Exception as e:
            print(f"   ⚠️  Failed to load session notes: {e}")
            main_campaign = None
        
        # Initialize Central Engine with storage components
        print("📡 Initializing Central Engine with storage...")
        context_assembler = ContextAssembler()
        prompt_manager = CentralPromptManager(context_assembler)
        
        # Create central engine using config with storage components
        engine = CentralEngine.create_from_config(
            prompt_manager,
            character=character,
            rulebook_storage=rulebook_storage,
            campaign_session_notes=main_campaign
        )
        
        print(f"   ✅ Engine initialized with storage")
        print(f"   📊 Available LLM clients: {list(engine.llm_clients.keys())}")
        print(f"   🤖 Router provider: {engine.config.router_llm_provider}")
        print(f"   🎯 Final provider: {engine.config.final_response_llm_provider}")
        print()
        
        # Test query and character
        user_query = "What is the most powerful weapon in Dusks inventory?"
        
        print(f"🎯 Testing Query: '{user_query}'")
        print(f"👤 Character: '{character_name}'")
        print()
        
        # STEP 1: Test Router Decision Phase
        print("🧠 STEP 1: Router Decision Phase")
        print("-" * 40)
        
        try:
            router_outputs = await engine.make_parallel_router_decisions(user_query, character_name)
            print("✅ Router decisions completed")
            
            # Debug Character Router Output
            if router_outputs.character_output:
                print(f"📊 Character Router:")
                print(f"   • Needed: {router_outputs.character_output.is_needed}")
                print(f"   • Intention: {router_outputs.character_output.user_intention}")
                print(f"   • Entities: {len(router_outputs.character_output.entities)} found")
                if router_outputs.character_output.entities:
                    for i, entity in enumerate(router_outputs.character_output.entities):
                        print(f"     {i+1}. {entity}")
            else:
                print("❌ Character Router: No output received")
            
            # Debug Rulebook Router Output  
            if router_outputs.rulebook_output:
                print(f"📚 Rulebook Router:")
                print(f"   • Needed: {router_outputs.rulebook_output.is_needed}")
                print(f"   • Intention: {router_outputs.rulebook_output.user_intention}")
                print(f"   • Entities: {len(router_outputs.rulebook_output.entities)} found")
                print(f"   • Context Hints: {len(router_outputs.rulebook_output.context_hints)} provided")
                if router_outputs.rulebook_output.entities:
                    for i, entity in enumerate(router_outputs.rulebook_output.entities):
                        print(f"     Entity {i+1}: {entity}")
                if router_outputs.rulebook_output.context_hints:
                    for i, hint in enumerate(router_outputs.rulebook_output.context_hints):
                        print(f"     Hint {i+1}: {hint}")
            else:
                print("❌ Rulebook Router: No output received")
            
            # Debug Session Notes Router Output
            if router_outputs.session_notes_output:
                print(f"📝 Session Notes Router:")
                print(f"   • Needed: {router_outputs.session_notes_output.is_needed}")
                print(f"   • Intention: {router_outputs.session_notes_output.user_intention}")
                print(f"   • Entities: {len(router_outputs.session_notes_output.entities)} found")
                print(f"   • Context Hints: {len(router_outputs.session_notes_output.context_hints)} provided")
                if router_outputs.session_notes_output.entities:
                    for i, entity in enumerate(router_outputs.session_notes_output.entities):
                        print(f"     Entity {i+1}: {entity}")
            else:
                print("❌ Session Notes Router: No output received")
            
            print()
            
        except Exception as e:
            print(f"❌ ERROR in Router Decision Phase: {str(e)}")
            print(f"📜 Traceback:")
            traceback.print_exc()
            return
        
        # STEP 2: Test Router Execution Phase  
        print("⚡ STEP 2: Router Execution Phase")
        print("-" * 40)
        
        try:
            # Track which routers should execute
            should_execute = []
            if router_outputs.character_output and router_outputs.character_output.is_needed:
                should_execute.append("Character")
            if router_outputs.rulebook_output and router_outputs.rulebook_output.is_needed and engine.rulebook_router:
                should_execute.append("Rulebook")  
            if router_outputs.session_notes_output and router_outputs.session_notes_output.is_needed and engine.session_notes_router:
                should_execute.append("Session Notes")
            
            print(f"🎯 Routers scheduled for execution: {should_execute}")
            
            # Check router availability
            print("🔍 Router availability check:")
            print(f"   • Character router available: {engine.character_router is not None}")
            print(f"   • Rulebook router available: {engine.rulebook_router is not None}")
            print(f"   • Session Notes router available: {engine.session_notes_router is not None}")
            print()
            
            raw_results = await engine.execute_needed_routers(router_outputs, user_query)
            print(f"✅ Router execution completed")
            print(f"📊 Results obtained from {len(raw_results)} router(s)")
            
            for router_name, result in raw_results.items():
                print(f"   • {router_name.title()} Router: ✅ Success")
                if hasattr(result, '__dict__'):
                    result_summary = {k: str(v)[:100] + "..." if len(str(v)) > 100 else str(v) 
                                    for k, v in result.__dict__.items()}
                    print(f"     Result keys: {list(result_summary.keys())}")
                else:
                    print(f"     Result type: {type(result)}")
            print()
            
        except Exception as e:
            print(f"❌ ERROR in Router Execution Phase: {str(e)}")
            print(f"📜 Traceback:")
            traceback.print_exc()
            return
        
        # STEP 3: Test Final Response Generation
        print("🎨 STEP 3: Final Response Generation")
        print("-" * 40)
        
        try:
            start_time = time.time()
            final_response = await engine.generate_final_response(raw_results, user_query)
            end_time = time.time()
            
            print(f"💬 Response generated in {end_time - start_time:.2f}s")
            print(f"📏 Response length: {len(final_response)} characters")
            print()
            
            print("🎯 FINAL RESPONSE")
            print("=" * 60)
            print(final_response)
            print("=" * 60)
            print()
            
        except Exception as e:
            print(f"❌ ERROR in Final Response Generation: {str(e)}")
            print(f"📜 Traceback:")
            traceback.print_exc()
            return
        
        # Configuration Summary
        print("⚙️  CONFIGURATION USED")
        print("-" * 40)
        print(f"Router Model: {engine.config.openai_router_model if engine.config.router_llm_provider == 'openai' else engine.config.anthropic_router_model}")
        print(f"Router Temp: {engine.config.router_temperature}")
        print(f"Router Max Tokens: {engine.config.router_max_tokens}")
        print(f"Final Model: {engine.config.openai_final_model if engine.config.final_response_llm_provider == 'openai' else engine.config.anthropic_final_model}")
        print(f"Final Temp: {engine.config.final_temperature}")
        print(f"Final Max Tokens: {engine.config.final_max_tokens}")
        print()
        
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {str(e)}")
        print(f"📜 Full Traceback:")
        traceback.print_exc()


async def main():
    """Run the debug test."""
    await debug_test_weapon_query()


if __name__ == "__main__":
    import time
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"\n⏱️  Total execution time: {end_time - start_time:.2f}s")
