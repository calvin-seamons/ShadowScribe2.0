"""Pydantic schemas for character API."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class CharacterResponse(BaseModel):
    """Character response schema."""
    id: str
    name: str
    race: Optional[str] = None
    character_class: Optional[str] = None
    level: Optional[int] = None
    data: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CharacterListResponse(BaseModel):
    """Character list response schema."""
    characters: List[CharacterResponse]
