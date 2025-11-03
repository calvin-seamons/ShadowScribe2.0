"""Migration script to load existing characters from pickle files to MySQL database."""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.database.connection import AsyncSessionLocal, init_db
from api.database.repositories.character_repo import CharacterRepository
from src.utils.character_manager import CharacterManager


async def migrate_characters():
    """Migrate characters from pickle files to database."""
    print("Starting character migration...")
    
    # Initialize database
    await init_db()
    print("Database initialized.")
    
    # Load character manager
    character_manager = CharacterManager()
    saved_dir = Path(project_root) / "knowledge_base" / "saved_characters"
    
    if not saved_dir.exists():
        print(f"No saved_characters directory found at {saved_dir}")
        return
    
    # Find all pickle files
    pickle_files = list(saved_dir.glob("*.pkl"))
    print(f"Found {len(pickle_files)} character files.")
    
    if not pickle_files:
        print("No character files to migrate.")
        return
    
    # Migrate each character
    migrated = 0
    failed = 0
    
    async with AsyncSessionLocal() as session:
        repo = CharacterRepository(session)
        
        for pickle_file in pickle_files:
            try:
                # Load character from pickle
                character_name = pickle_file.stem
                print(f"\nMigrating: {character_name}")
                
                character = character_manager.load_character(character_name)
                if not character:
                    print(f"  ❌ Could not load character: {character_name}")
                    failed += 1
                    continue
                
                # Check if already exists
                existing = await repo.get_by_name(character.character_base.name)
                if existing:
                    print(f"  ⚠️  Character already exists in database: {character.character_base.name}")
                    continue
                
                # Create in database
                db_character = await repo.create(character)
                await session.commit()
                
                print(f"  ✅ Migrated: {db_character.name} (ID: {db_character.id})")
                print(f"     Race: {db_character.race}, Class: {db_character.character_class}, Level: {db_character.level}")
                migrated += 1
                
            except Exception as e:
                print(f"  ❌ Error migrating {pickle_file.name}: {e}")
                failed += 1
                await session.rollback()
    
    print(f"\n{'='*60}")
    print(f"Migration complete!")
    print(f"  Migrated: {migrated}")
    print(f"  Failed: {failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(migrate_characters())
