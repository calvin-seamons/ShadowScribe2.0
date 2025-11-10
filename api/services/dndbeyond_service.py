"""D&D Beyond character fetching service."""
import re
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException


class DndBeyondService:
    """Service for fetching character data from D&D Beyond."""
    
    # D&D Beyond character service API endpoint
    CHARACTER_API_URL = "https://character-service.dndbeyond.com/character/v5/character/{character_id}"
    
    # Timeout for HTTP requests (30 seconds)
    REQUEST_TIMEOUT = 30.0
    
    @staticmethod
    def extract_character_id(url: str) -> Optional[str]:
        """
        Extract character ID from D&D Beyond URL.
        
        Args:
            url: D&D Beyond character URL
            
        Returns:
            Character ID as string, or None if not found
            
        Examples:
            https://www.dndbeyond.com/characters/152248393 -> "152248393"
            https://dndbeyond.com/characters/140237850 -> "140237850"
        """
        # Pattern matches /characters/{id} where id is one or more digits
        pattern = r'/characters/(\d+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    async def fetch_character_json(character_id: str) -> Dict[str, Any]:
        """
        Fetch character JSON from D&D Beyond character service API.
        
        Args:
            character_id: D&D Beyond character ID
            
        Returns:
            Complete character JSON data from D&D Beyond
            
        Raises:
            HTTPException: If fetching fails or character not found
        """
        url = DndBeyondService.CHARACTER_API_URL.format(character_id=character_id)
        
        async with httpx.AsyncClient(timeout=DndBeyondService.REQUEST_TIMEOUT) as client:
            try:
                response = await client.get(url)
                
                # Handle different response codes
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Character {character_id} not found on D&D Beyond"
                    )
                elif response.status_code == 403:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Character {character_id} is private or access denied"
                    )
                elif response.status_code >= 400:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"D&D Beyond API error: {response.status_code}"
                    )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="Request to D&D Beyond timed out. Please try again."
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to connect to D&D Beyond: {str(e)}"
                )
    
    @staticmethod
    async def fetch_from_url(url: str) -> Dict[str, Any]:
        """
        Fetch character JSON from D&D Beyond URL.
        
        This is a convenience method that combines ID extraction and fetching.
        
        Args:
            url: D&D Beyond character URL
            
        Returns:
            Complete character JSON data from D&D Beyond
            
        Raises:
            HTTPException: If URL is invalid or fetching fails
        """
        # Extract character ID
        character_id = DndBeyondService.extract_character_id(url)
        
        if not character_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid D&D Beyond URL. Expected format: https://dndbeyond.com/characters/{id}"
            )
        
        # Fetch character data
        return await DndBeyondService.fetch_character_json(character_id)
