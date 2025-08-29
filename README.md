# ShadowScribe2.0 - RPG Character Management System

A comprehensive tool for managing D&D and other RPG characters with support for character creation, inspection, and data management.

## Quick Start

### Option 1: Using Python modules (Recommended)
```bash
# From project root directory
python -m scripts.run_inspector --list
python -m scripts.run_manager

# Or run with specific arguments
python -m scripts.run_inspector "Duskryn Nightwarden" --format json
python -m scripts.run_inspector "Duskryn Nightwarden" --output report.txt
```

### Option 2: Direct script execution (Alternative)
```bash
# From project root directory
python scripts/run_inspector.py --list
python scripts/run_manager.py
```

### Option 3: Install as a package (For development)
```bash
# Install in development mode
pip install -e .

# Then run from anywhere:
shadowscribe-inspect --list
shadowscribe-manage
```

## Project Structure
```
ShadowScribe2.0/
├── src/                       # Source code
│   ├── __init__.py
│   ├── types/
│   │   ├── __init__.py
│   │   └── character_types.py
│   └── utils/
│       ├── __init__.py
│       ├── character_inspector.py
│       └── character_manager.py
├── scripts/                   # Entry point scripts
│   ├── run_inspector.py
│   └── run_manager.py
├── saved_characters/          # Character save files
├── setup.py                   # Package configuration
└── requirements.txt
```

## Development Guidelines

### Creating New Scripts
When creating new Python scripts in this project, follow these guidelines to avoid import issues:

1. **Always run from project root**: Execute commands from the `ShadowScribe2.0/` directory
2. **Use module execution**: Use `python -m scripts.script_name` instead of direct execution
3. **Proper imports**: Use absolute imports like `from src.utils.module import Class`
4. **Entry points**: Create entry point scripts in the `scripts/` directory for convenience

### Example: Creating a new script
```python
# scripts/my_new_script.py
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use absolute imports
from src.utils.character_manager import CharacterManager
from src.types.character_types import Character

def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()
```

Then run it with:
```bash
python -m scripts.my_new_script
```

## Features

- **Character Inspector**: Debug and analyze character objects with multiple output formats
- **Character Manager**: Create, load, save, and manage RPG characters
- **Multiple Import Methods**: Flexible import system that works in various execution contexts
- **Cross-Platform**: Works on Windows, Linux, and macOS