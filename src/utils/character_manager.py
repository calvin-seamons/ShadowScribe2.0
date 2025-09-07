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


# Example usage functions
def save_duskryn_character():
    """Example: Save Duskryn character using the converter."""
    from src.utils.convert_duskryn import create_duskryn_character
    
    # Create character from JSON files (using correct path)
    duskryn = create_duskryn_character("knowledge_base/legacy_json/Duskryn_Nightwarden")
    
    # Save the character
    manager = CharacterManager()
    filepath = manager.save_character(duskryn)
    
    print(f"Duskryn character saved to: {filepath}")
    return filepath


def load_duskryn_character() -> Character:
    """Example: Load Duskryn character."""
    manager = CharacterManager()
    
    try:
        character = manager.load_character("Duskryn Nightwarden")
        print(f"Loaded character: {character.character_base.name}")
        return character
    except FileNotFoundError:
        print("Duskryn character not found. Creating and saving...")
        save_duskryn_character()
        return manager.load_character("Duskryn Nightwarden")


def main():
    """Main function for character manager demo."""
    # Demo the character manager
    print("=== Character Manager Demo ===")
    
    # Save Duskryn
    save_duskryn_character()
    
    # List saved characters
    manager = CharacterManager()
    saved_chars = manager.list_saved_characters()
    print(f"Saved characters: {saved_chars}")
    
    # Load and display basic info
    character = load_duskryn_character()
    print(f"Character: {character.character_base.name}")
    print(f"Race: {character.character_base.race}")
    print(f"Class: {character.character_base.character_class}")
    print(f"Level: {character.character_base.total_level}")


if __name__ == "__main__":
    main()
