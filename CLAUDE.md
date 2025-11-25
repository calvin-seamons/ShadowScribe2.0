# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShadowScribe 2.0 is a D&D character management system with RAG (Retrieval-Augmented Generation) capabilities. It combines character data, rulebook embeddings, and session notes with AI chat through a Next.js frontend and FastAPI backend.

## Architecture

```
Frontend (Next.js 14)     →  WebSocket/HTTP  →  API (FastAPI)  →  CentralEngine (Python)
    ↓                                              ↓                     ↓
Zustand stores                              MySQL 8.0            RAG Routers (Character,
React components                            Characters              Rulebook, Session Notes)
```

**Core RAG Engine**: `src/central_engine.py` uses 2-parallel LLM calls:
1. Tool & Intention Selector (fast routing with Haiku)
2. Entity Extractor (extract named entities)
Then executes appropriate RAG routers and generates streaming responses with Sonnet.

## Build, Test & Run Commands

### Docker (Recommended)
```bash
docker-compose up -d              # Start all services
docker-compose logs -f api        # View API logs
docker-compose down               # Stop services
```

### Frontend (Next.js)
```bash
cd frontend
npm run dev                       # Development server (port 3000)
npm run build                     # Production build
npm run lint                      # ESLint
```

### Backend (Python) - Always use `uv run`
```bash
uv run python demo_central_engine.py                  # Interactive RAG testing (PRIMARY)
uv run python demo_central_engine.py -q "What is my AC?"  # Single query test
uv run python -m scripts.run_inspector --list         # List characters
uv run python -m scripts.run_inspector "Name" --format text  # Inspect character
```

## Critical Development Patterns

### Python Execution
**Always use `uv run`** - it manages the virtual environment automatically:
```bash
# Correct
uv run python -m scripts.run_inspector --list
uv run python demo_central_engine.py

# Wrong - don't run directly
python scripts/run_inspector.py
```

### Import System
Always use absolute imports and run from project root:
```python
# Correct
from src.utils.character_manager import CharacterManager
from src.rag.character.character_types import Character

# Wrong
from .character_manager import CharacterManager
```

### Character Type Access
```python
# Required fields (always present)
character.character_base.name
character.ability_scores.strength
character.combat_stats.armor_class

# Optional fields (check for None)
if character.inventory:
    items = character.inventory.backpack
if character.spell_list:
    spells = character.spell_list.spells
```

### API Keys
Use real API integrations - never mock. Keys in `.env`:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Key Files

| File | Purpose |
|------|---------|
| `src/central_engine.py` | Main query orchestrator with streaming |
| `src/rag/character/character_types.py` | 20+ dataclasses for D&D characters |
| `src/config.py` | RAG configuration (models, temperatures) |
| `api/main.py` | FastAPI entry point |
| `api/routers/websocket.py` | WebSocket `/ws/chat` endpoint |
| `demo_central_engine.py` | Primary testing tool for RAG system |

## API Endpoints

- `GET /api/characters` - List characters
- `GET /api/characters/{id}` - Character details
- `ws://localhost:8000/ws/chat` - Streaming chat (WebSocket)

## Code Philosophy

1. **Delete obsolete code** - no commented-out code or legacy cruft
2. **No backward compatibility** unless required for data persistence
3. **Name code as fundamental** - no `_new`, `_v2` suffixes
4. **Let things fail** - don't over-engineer error handling
5. **Clean up test files** - delete temporary scripts after use

## Frontend Architecture

- **State**: Zustand stores (`chatStore`, `characterStore`, `metadataStore`)
- **Streaming**: WebSocket connection for real-time responses
- **Styling**: Tailwind CSS with dark mode support
- **Path alias**: `@/*` maps to `frontend/*`
