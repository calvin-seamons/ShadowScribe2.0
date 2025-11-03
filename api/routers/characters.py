"""Character REST API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.database.connection import get_db
from api.database.repositories.character_repo import CharacterRepository
from api.schemas.character import CharacterResponse, CharacterListResponse

router = APIRouter()


@router.get("/characters", response_model=CharacterListResponse)
async def list_characters(db: AsyncSession = Depends(get_db)):
    """List all characters."""
    repo = CharacterRepository(db)
    characters = await repo.get_all()
    
    return {
        'characters': [char.to_dict() for char in characters]
    }


@router.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str, db: AsyncSession = Depends(get_db)):
    """Get character by ID."""
    repo = CharacterRepository(db)
    character = await repo.get_by_id(character_id)
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return character.to_dict()


@router.delete("/characters/{character_id}")
async def delete_character(character_id: str, db: AsyncSession = Depends(get_db)):
    """Delete character by ID."""
    repo = CharacterRepository(db)
    deleted = await repo.delete(character_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {'status': 'deleted', 'id': character_id}
