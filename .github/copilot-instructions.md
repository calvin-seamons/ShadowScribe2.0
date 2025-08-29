# ShadowScribe2.0 - AI Coding Agent Instructions

## Project Overview
ShadowScribe2.0 is a comprehensive D&D/RPG character management system built around a sophisticated dataclass-based type system. The architecture separates character data modeling from business logic through three core layers:

- **`src/types/character_types.py`**: Complete character type system with 20+ dataclasses modeling everything from basic stats to complex spell systems
- **`src/utils/`**: Business logic for character persistence, inspection, and data conversion
- **`scripts/`**: Entry point modules that handle the import complexity

## Critical Development Patterns

### Import System (ESSENTIAL)
**Always run from project root** and use module execution to avoid import issues:
```bash
# Correct way to run scripts
python -m scripts.run_inspector --list
python -m scripts.run_manager

# NOT: python scripts/run_inspector.py
```

**Use absolute imports in all files:**
```python
# Correct imports
from src.utils.character_manager import CharacterManager
from src.types.character_types import Character

# NOT: from .character_manager import CharacterManager
```

### Character Type System Architecture
The `Character` dataclass is the central entity with required core fields and optional modules:
```python
# Required fields (must be present)
character_base: CharacterBase        # Name, race, class, level
ability_scores: AbilityScores       # STR, DEX, CON, etc.
combat_stats: CombatStats          # HP, AC, initiative
background_info: BackgroundInfo    # D&D background system
personality: PersonalityTraits     # Traits, ideals, bonds, flaws
backstory: Backstory              # Rich narrative background

# Optional modules (can be None)
inventory: Optional[Inventory]
spell_list: Optional[SpellList]
action_economy: Optional[ActionEconomy]
```

**Key Pattern**: Use `character.field_name.subfield` access pattern, checking for None on optional fields:
```python
# Always check optional fields
spell_count = len(character.spell_list.spells) if character.spell_list else 0
inventory_items = (
    len(character.inventory.backpack) + 
    sum(len(items) for items in character.inventory.equipped_items.values())
) if character.inventory else 0
```

### Data Persistence & Conversion
Characters are persisted as pickle files in `saved_characters/`. The conversion workflow:

1. **JSON → Character**: `convert_duskryn.py` converts JSON data to Character objects
2. **Character → Pickle**: `CharacterManager.save_character()` handles persistence
3. **Character ← Pickle**: `CharacterManager.load_character()` handles loading

**Example Character Creation Pattern:**
```python
# Always use CharacterManager for persistence
manager = CharacterManager()
character = create_some_character()  # Your creation logic
filepath = manager.save_character(character)  # Auto-generates filename from character.character_base.name
```

### Character Inspector Patterns
The inspector supports three output formats with filtering:
```python
# Text format with filtering (shows matching fields only)
python -m scripts.run_inspector "Character Name" --format text --filter spell

# JSON export for data processing
python -m scripts.run_inspector "Character Name" --format json --output report.json

# Summary for quick overview
python -m scripts.run_inspector "Character Name" --format summary
```

### Entry Point Script Pattern
Create new functionality by adding scripts to `scripts/` directory:
```python
# scripts/my_new_feature.py
import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use absolute imports
from src.utils.character_manager import CharacterManager
from src.types.character_types import Character

def main():
    # Your feature logic here
    pass

if __name__ == "__main__":
    main()
```

## Key Files & Their Roles

- **`src/types/character_types.py`**: Single source of truth for all character data structures (575+ lines)
- **`src/utils/character_manager.py`**: Character CRUD operations and pickle persistence
- **`src/utils/character_inspector.py`**: Debugging/analysis tool with multiple output formats
- **`src/utils/convert_duskryn.py`**: Example converter from JSON → Character (1400+ lines of conversion logic)
- **`Duskryn_Nightwarden/`**: Example character data as JSON files
- **`saved_characters/`**: Pickle storage for Character objects

## Testing & Debugging Commands
```bash
# List all saved characters
python -m scripts.run_inspector --list

# Debug character data structure
python -m scripts.run_inspector "Character Name" --format text --filter field_name

# Recreate character from JSON (if exists)
python -c "import sys; sys.path.insert(0, '.'); from src.utils.character_manager import save_duskryn_character; save_duskryn_character()"

# Run character manager demo
python -m scripts.run_manager
```

## Common Pitfalls to Avoid
1. **Don't run scripts directly** - always use `python -m scripts.script_name`
2. **Don't use relative imports** - always use `from src.utils.module import Class`
3. **Check for None on optional Character fields** before accessing nested attributes
4. **Use `character.character_base.total_level`** not `.level` for character level access
5. **Access inventory as `character.inventory.backpack`** and `character.inventory.equipped_items`**
