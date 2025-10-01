"""
Character Manager

A simple class for saving and loading Character objects to/from files.
"""

import json
import pickle
from pathlib import Path
from typing import Optional
from datetime import datetime
from src.rag.character.character_types import Character


class CharacterManager:
    """Simple manager for saving and loading Character objects."""
    
    def __init__(self, save_directory: str = "knowledge_base/saved_characters"):
        """Initialize the character manager with a save directory."""
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
    
    def save_character(self, character: Character, filename: Optional[str] = None) -> str:
        """
        Save a Character object to a pickle file.
        
        Args:
            character: The Character object to save
            filename: Optional filename. If not provided, uses character name
            
        Returns:
            The filepath where the character was saved
        """
        if filename is None:
            # Use character name as filename, sanitized for filesystem
            safe_name = "".join(c for c in character.character_base.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}.pkl"
        
        if not filename.endswith('.pkl'):
            filename += '.pkl'
            
        filepath = self.save_directory / filename
        
        # Update the last_updated timestamp
        character.last_updated = datetime.now()
        
        with open(filepath, 'wb') as f:
            pickle.dump(character, f)
            
        return str(filepath)
    
    def load_character(self, filename: str) -> Character:
        """
        Load a Character object from a pickle file.
        
        Args:
            filename: The filename to load from
            
        Returns:
            The loaded Character object
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not filename.endswith('.pkl'):
            filename += '.pkl'
            
        filepath = self.save_directory / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Character file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            character = pickle.load(f)
            
        return character
    
    def list_saved_characters(self) -> list[str]:
        """
        List all saved character files.
        
        Returns:
            List of character filenames (without .pkl extension)
        """
        character_files = []
        for pkl_file in self.save_directory.glob("*.pkl"):
            character_files.append(pkl_file.stem)
        
        return sorted(character_files)
    
    def delete_character(self, filename: str) -> bool:
        """
        Delete a saved character file.
        
        Args:
            filename: The filename to delete
            
        Returns:
            True if deleted successfully, False if file didn't exist
        """
        if not filename.endswith('.pkl'):
            filename += '.pkl'
            
        filepath = self.save_directory / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        
        return False
