#!/usr/bin/env python3
"""
Integration test for the complete system:
- Character loading
- Campaign session notes loading  
- CentralEngine creation and operation
"""

from src.rag.session_notes.session_notes_storage import SessionNotesStorage
from src.utils.character_manager import CharacterManager  
from src.rag.central_engine import CentralEngine
from src.rag.llm_client import LLMClientFactory

def test_system_integration():
    """Test the complete integrated system."""
    print("=== System Integration Test ===\n")
    
    # 1. Load character
    print("1. Loading character...")
    char_manager = CharacterManager()
    character = char_manager.load_character('Duskryn Nightwarden')
    print(f"   ✓ Character: {character.character_base.name}")
    print(f"   ✓ Class: {character.character_base.character_class}")
    print(f"   ✓ Level: {character.character_base.total_level}")
    
    # 2. Load campaign session notes
    print("\n2. Loading campaign session notes...")
    storage = SessionNotesStorage()
    campaign_notes = storage.get_campaign('main_campaign')
    print(f"   ✓ Campaign: {campaign_notes.campaign_name}")
    print(f"   ✓ Sessions: {len(campaign_notes.sessions)}")
    print(f"   ✓ Entities: {len(campaign_notes.entities)}")
    print(f"   ✓ Session IDs: {list(campaign_notes.sessions.keys())}")
    
    # 3. Create LLM clients and prompt manager (mock)
    print("\n3. Setting up LLM components...")
    llm_clients = LLMClientFactory.create_default_clients()
    print(f"   ✓ LLM Clients: {list(llm_clients.keys())}")
    
    # Mock prompt manager for now
    class MockPromptManager:
        def get_prompt(self, prompt_name, **kwargs):
            return f"Mock prompt for {prompt_name}"
    
    prompt_manager = MockPromptManager()
    print("   ✓ Prompt Manager: MockPromptManager")
    
    # 4. Create central engine
    print("\n4. Creating CentralEngine...")
    engine = CentralEngine(
        llm_clients=llm_clients,
        prompt_manager=prompt_manager,
        character=character,
        campaign_session_notes=campaign_notes
    )
    print("   ✓ CentralEngine created successfully")
    
    # 5. Test basic functionality
    print("\n5. Testing basic functionality...")
    
    # Test character query router
    if engine.character_router:
        print("   ✓ Character router available")
        # We won't make actual LLM calls, just test the setup
    
    # Test session notes query router  
    if engine.session_notes_router:
        print("   ✓ Session notes router available")
        
        # Test session search - get all sessions without date filter
        all_sessions = list(engine.session_notes_router.campaign_storage.sessions.values())
        print(f"   ✓ Found sessions: {len(all_sessions)}")
        
        # Test entity search
        entities = list(engine.session_notes_router.campaign_storage.entities.keys())[:5]
        print(f"   ✓ Sample entities: {entities}")
        
        # Test getting a specific session
        if all_sessions:
            first_session = all_sessions[0]
            print(f"   ✓ Sample session: #{first_session.session_number}, Date: {first_session.date}")
            print(f"   ✓ Session title: {first_session.title}")
            print(f"   ✓ Session summary: {first_session.summary[:100]}...")
    
    # Test that we can access character data through the engine
    if engine.character_router and engine.character_router.character:
        char = engine.character_router.character
        print(f"   ✓ Engine has character: {char.character_base.name}")
        spell_count = sum(len(spells_by_level) for class_spells in char.spell_list.spells.values() for spells_by_level in class_spells.values()) if char.spell_list else 0
        print(f"   ✓ Character total spells: {spell_count}")
        
        # Count all inventory items (backpack + equipped items)
        inventory_count = 0
        if char.inventory:
            if char.inventory.backpack:
                inventory_count += len(char.inventory.backpack)
            if char.inventory.equipped_items:
                inventory_count += sum(len(items) for items in char.inventory.equipped_items.values())
        print(f"   ✓ Character inventory items: {inventory_count}")
    
    print("\n=== Integration Test PASSED ===")
    return True

if __name__ == "__main__":
    try:
        test_system_integration()
    except Exception as e:
        print(f"\n❌ Integration Test FAILED: {e}")
        import traceback
        traceback.print_exc()
