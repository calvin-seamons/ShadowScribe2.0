"""Character repository for database operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from dataclasses import asdict
from datetime import datetime
import re
import json

from api.database.models import Character as CharacterModel
from src.rag.character.character_types import Character as CharacterDataclass


def default_json_serializer(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class CharacterRepository:
    """Repository for character CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, character: CharacterDataclass) -> CharacterModel:
        """Create a new character in the database."""
        character_data = asdict(character)
        
        # Convert to JSON string then back to dict to handle datetime serialization
        character_data_json = json.dumps(character_data, default=default_json_serializer)
        character_data = json.loads(character_data_json)
        
        db_character = CharacterModel(
            id=self._generate_id(character.character_base.name),
            name=character.character_base.name,
            race=character.character_base.race,
            character_class=character.character_base.character_class,
            level=character.character_base.total_level,
            data=character_data
        )
        
        self.session.add(db_character)
        await self.session.flush()
        return db_character
    
    async def get_by_id(self, character_id: str) -> Optional[CharacterModel]:
        """Get character by ID."""
        result = await self.session.execute(
            select(CharacterModel).where(CharacterModel.id == character_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[CharacterModel]:
        """Get character by name."""
        result = await self.session.execute(
            select(CharacterModel).where(CharacterModel.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[CharacterModel]:
        """Get all characters."""
        result = await self.session.execute(select(CharacterModel))
        return list(result.scalars().all())
    
    async def update(self, character_id: str, character: CharacterDataclass) -> Optional[CharacterModel]:
        """Update character."""
        character_data = asdict(character)
        
        # Convert to JSON string then back to dict to handle datetime serialization
        character_data_json = json.dumps(character_data, default=default_json_serializer)
        character_data = json.loads(character_data_json)
        
        await self.session.execute(
            update(CharacterModel)
            .where(CharacterModel.id == character_id)
            .values(
                name=character.character_base.name,
                race=character.character_base.race,
                character_class=character.character_base.character_class,
                level=character.character_base.total_level,
                data=character_data,
                updated_at=datetime.utcnow()
            )
        )
        
        return await self.get_by_id(character_id)
    
    async def delete(self, character_id: str) -> bool:
        """Delete character."""
        result = await self.session.execute(
            delete(CharacterModel).where(CharacterModel.id == character_id)
        )
        return result.rowcount > 0
    
    async def update_section(self, character_id: str, section: str, data: dict) -> Optional[CharacterModel]:
        """
        Update a specific section of a character.
        
        Args:
            character_id: Character ID to update
            section: Section name (e.g., 'ability_scores', 'inventory', 'spell_list')
            data: Dictionary containing the updated section data
            
        Returns:
            Updated CharacterModel or None if character not found
            
        Raises:
            ValueError: If section name is invalid
        """
        # Valid section names based on Character dataclass
        valid_sections = {
            'character_base',
            'characteristics',
            'ability_scores',
            'combat_stats',
            'background_info',
            'personality',
            'backstory',
            'organizations',
            'allies',
            'enemies',
            'proficiencies',
            'damage_modifiers',
            'passive_scores',
            'senses',
            'action_economy',
            'features_and_traits',
            'inventory',
            'spell_list',
            'objectives_and_contracts',
            'notes'
        }
        
        if section not in valid_sections:
            raise ValueError(
                f"Invalid section '{section}'. "
                f"Valid sections: {', '.join(sorted(valid_sections))}"
            )
        
        # Get current character
        character = await self.get_by_id(character_id)
        if not character:
            return None
        
        # Update the specific section in the data JSON
        character_data = character.data.copy()
        character_data[section] = data
        
        # Handle serialization of datetime objects
        character_data_json = json.dumps(character_data, default=default_json_serializer)
        character_data = json.loads(character_data_json)
        
        # Update database record
        await self.session.execute(
            update(CharacterModel)
            .where(CharacterModel.id == character_id)
            .values(
                data=character_data,
                updated_at=datetime.utcnow()
            )
        )
        
        return await self.get_by_id(character_id)
    
    @staticmethod
    def _generate_id(name: str) -> str:
        """Generate URL-safe ID from character name."""
        return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
