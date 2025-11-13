"""Test script to verify character loading from database."""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.database.connection import AsyncSessionLocal
from src.utils.character_manager import CharacterManager


async def test_character_loading():
    """Test loading character from database."""
    print("Testing character loading from database...\n")
    
    # Test with database session
    async with AsyncSessionLocal() as session:
        manager = CharacterManager(db_session=session)
        
        try:
            # Try to load character
            character_name = "Duskryn Nightwarden"
            print(f"Loading character: {character_name}")
            
            character = await manager.load_character_async(character_name)
            
            if character:
                print(f"✅ Successfully loaded character from database!")
                print(f"\nCharacter Details:")
                print(f"  Name: {character.character_base.name}")
                print(f"  Race: {character.character_base.race}")
                print(f"  Class: {character.character_base.character_class}")
                print(f"  Level: {character.character_base.total_level}")
                print(f"  Max HP: {character.combat_stats.max_hp}")
                print(f"  AC: {character.combat_stats.armor_class}")
                
                # Check optional fields
                spell_count = len(character.spell_list.spells) if character.spell_list else 0
                print(f"  Spells: {spell_count}")
                
                inventory_items = 0
                if character.inventory:
                    inventory_items = len(character.inventory.backpack) + sum(
                        len(items) for items in character.inventory.equipped_items.values()
                    )
                print(f"  Inventory Items: {inventory_items}")
                
                print(f"\n✅ Character loaded successfully with all data intact!")
                return True
            else:
                print(f"❌ Character not found")
                return False
                
        except Exception as e:
            print(f"❌ Error loading character: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_character_loading())
    sys.exit(0 if success else 1)
