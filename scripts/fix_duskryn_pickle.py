"""
Fix Duskryn pickle file module path

This script loads the Duskryn character pickle file and re-saves it
with the correct module paths.
"""

import sys
import pickle
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import both old and new paths for compatibility
try:
    from src.types.character_types import Character as OldCharacter
except ImportError:
    OldCharacter = None

from src.rag.character.character_types import Character
from src.rag.character.character_manager import CharacterManager

def fix_duskryn_pickle():
    """Load and re-save Duskryn with correct module path."""
    
    pickle_path = Path("knowledge_base/saved_characters/Duskryn Nightwarden.pkl")
    
    if not pickle_path.exists():
        print(f"❌ Character file not found: {pickle_path}")
        return
    
    print(f"📂 Loading character from: {pickle_path}")
    
    # Try to load with module path fixes
    try:
        # Add module path compatibility
        import sys
        
        # Create alias for old module path
        if 'src.types' not in sys.modules:
            import src.rag.character.character_types
            sys.modules['src.types.character_types'] = src.rag.character.character_types
            sys.modules['src.types'] = sys.modules['src.rag.character']
        
        with open(pickle_path, 'rb') as f:
            character = pickle.load(f)
        
        print(f"✅ Successfully loaded: {character.character_base.name}")
        print(f"   Race: {character.character_base.race}")
        print(f"   Class: {character.character_base.character_class}")
        print(f"   Level: {character.character_base.total_level}")
        
        # Re-save with correct module path
        manager = CharacterManager("knowledge_base/saved_characters")
        saved_path = manager.save_character(character)
        print(f"✅ Re-saved character to: {saved_path}")
        
        return character
        
    except Exception as e:
        print(f"❌ Error loading character: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_character_loading():
    """Test that the character can be loaded properly now."""
    print("\n🧪 Testing character loading...")
    
    try:
        manager = CharacterManager("knowledge_base/saved_characters")
        character = manager.load_character("Duskryn Nightwarden")
        
        print(f"✅ Successfully loaded: {character.character_base.name}")
        print(f"   Character type: {type(character)}")
        print(f"   Has inventory: {character.inventory is not None}")
        print(f"   Has spells: {character.spell_list is not None}")
        
        # Test some key data
        if character.inventory:
            equipped_count = sum(len(items) for items in character.inventory.equipped_items.values())
            backpack_count = len(character.inventory.backpack)
            print(f"   Inventory: {equipped_count} equipped, {backpack_count} in backpack")
        
        if character.spell_list and character.spell_list.spells:
            spell_count = sum(
                len(spells) 
                for class_spells in character.spell_list.spells.values()
                for spells in class_spells.values()
            )
            print(f"   Spells: {spell_count} total spells")
        
        return True
        
    except Exception as e:
        print(f"❌ Still cannot load character: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Duskryn Nightwarden pickle file...")
    
    character = fix_duskryn_pickle()
    
    if character:
        success = test_character_loading()
        if success:
            print("\n✅ Character loading fixed! Ready to run tests.")
        else:
            print("\n❌ Character loading still has issues.")
    else:
        print("\n❌ Could not fix character file.")
