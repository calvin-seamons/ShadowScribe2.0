#!/usr/bin/env python3
"""
Entry point script for the character manager.
This allows running the manager without import issues.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and run the main function
from src.utils.character_manager import main

if __name__ == "__main__":
    main()
