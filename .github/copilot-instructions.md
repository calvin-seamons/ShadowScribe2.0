# ShadowScribe2.0 - AI Coding Agent Instructions

## Project Overview
ShadowScribe2.0 is a comprehensive D&D/RPG character management system built around a sophisticated dataclass-based type system. The architecture separates character data modeling from business logic through three core layers:

- **`src/rag/character/character_types.py`**: Complete character type system with 20+ dataclasses modeling everything from basic stats to complex spell systems
- **`src/utils/`**: Business logic for character persistence, inspection, and data conversion
- **`scripts/`**: Entry point modules that handle the import complexity

## Environment Setup

### API Keys Configuration
The project includes a `.env` file with API keys for external services:

- **OpenAI API Key**: `OPENAI_API_KEY` - Used for OpenAI GPT models and embeddings
- **Anthropic API Key**: `ANTHROPIC_API_KEY` - Used for Claude models

**CRITICAL**: When writing tests or running code that requires API calls, **ALWAYS use the actual API keys from the .env file**. Never simulate API responses or use mock data unless explicitly requested. The project is designed to work with real API integrations.

**API Key Loading Pattern**:
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access API keys
openai_key = os.getenv('OPENAI_API_KEY')
anthropic_key = os.getenv('ANTHROPIC_API_KEY')

# Initialize clients
if openai_key:
    import openai
    openai.api_key = openai_key

if anthropic_key:
    from anthropic import Anthropic
    client = Anthropic(api_key=anthropic_key)
```

## Critical Development Patterns

### Virtual Environment (ESSENTIAL)
**ALWAYS activate the virtual environment before running any Python CODE AT ALL!!**:
```bash
# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# On Windows (Command Prompt)
.venv\Scripts\activate.bat

# On Linux/Mac
source .venv/bin/activate

# Verify activation - you should see (.venv) in your prompt
```

### Import System (ESSENTIAL)
**Always run from project root** and use module execution to avoid import issues:
```bash
# Correct way to run scripts (with venv activated)
python -m scripts.run_inspector --list
python -m scripts.run_manager

# NOT: python scripts/run_inspector.py
```

**Use absolute imports in all files:**
```python
# Correct imports
from src.utils.character_manager import CharacterManager
from src.rag.character.character_types import Character

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
from src.rag.character.character_types import Character

def main():
    # Your feature logic here
    pass

if __name__ == "__main__":
    main()
```

## Key Files & Their Roles

- **`src/rag/character/character_types.py`**: Single source of truth for all character data structures (575+ lines)
- **`src/utils/character_manager.py`**: Character CRUD operations and pickle persistence
- **`src/utils/character_inspector.py`**: Debugging/analysis tool with multiple output formats
- **`src/utils/convert_duskryn.py`**: Example converter from JSON → Character (1400+ lines of conversion logic)
- **`Duskryn_Nightwarden/`**: Example character data as JSON files
- **`saved_characters/`**: Pickle storage for Character objects

## Testing & Debugging Commands
```bash
# ALWAYS activate virtual environment FIRST
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# OR .venv\Scripts\activate.bat  # Windows Command Prompt
# OR source .venv/bin/activate  # Linux/Mac

# List all saved characters
python -m scripts.run_inspector --list

# Debug character data structure
python -m scripts.run_inspector "Character Name" --format text --filter field_name

# Recreate character from JSON (if exists)
python -c "import sys; sys.path.insert(0, '.'); from src.utils.character_manager import save_duskryn_character; save_duskryn_character()"

# Run character manager demo
python -m scripts.run_manager
```

## Test File Management
**Important**: When creating test scripts for experimentation or one-time verification:

1. **Use descriptive names** - prefix with `test_` for easy identification
2. **Document purpose** - include a docstring explaining what the test validates
3. **Clean up afterward** - delete temporary test files that won't be used again
4. **Keep essential tests** - preserve tests that validate core functionality or might be reused

**Test File Cleanup Pattern**:
```bash
# After successful testing, remove one-time test files
rm scripts/test_embeddings.py  # If no longer needed
rm scripts/test_temporary_feature.py

# Keep essential tests in place
# Keep: scripts/test_rag_system.py (core functionality)
# Keep: any test that validates API integrations or main features
```

## Code Modernization & Legacy Management
**Critical Philosophy**: This project prioritizes clean, modern code over backward compatibility.

### Legacy Code Removal
1. **Always delete obsolete code** - don't comment out or leave unused functions/classes
2. **Remove deprecated patterns** - replace old implementations entirely
3. **Clean up imports** - remove unused imports after code changes
4. **Delete dead files** - remove entire files that are no longer needed

### Backward Compatibility Rules
**NEVER maintain backward compatibility unless:**
- It's required for external API contracts (rare in this project)
- The change would break critical user data persistence (character saves)
- There's a compelling business reason documented in code

### Let things fail! 
**Don't put so many safeguards in place that you prevent failures from happening.**
- Embrace failure as a learning opportunity
- Simplify error handling to focus on critical issues
- Let failures happen and learn from them

**Default approach**: Break things and fix them properly rather than maintaining legacy cruft.

**Legacy Cleanup Pattern**:
```python
# BAD - leaving old code commented out
def new_implementation():
    pass
    
# def old_implementation():  # TODO: remove
#     legacy_code()

# GOOD - clean replacement
def new_implementation():
    pass
```

## Common Pitfalls to Avoid
1. **ALWAYS activate virtual environment FIRST** - use `.\.venv\Scripts\Activate.ps1` before running any Python code
2. **Don't run scripts directly** - always use `python -m scripts.script_name`
3. **Don't use relative imports** - always use `from src.utils.module import Class`
4. **Check for None on optional Character fields** before accessing nested attributes
5. **Use `character.character_base.total_level`** not `.level` for character level access
6. **Access inventory as `character.inventory.backpack`** and `character.inventory.equipped_items`**
6. **Clean up test files** - remove temporary test scripts after use to avoid clutter
7. **Delete legacy code** - never leave commented-out code or obsolete implementations
8. **Avoid backward compatibility** - break and fix cleanly rather than maintaining cruft
9. **Let things fail!** - Don't put so many safeguards in place that you prevent failures from happening.
