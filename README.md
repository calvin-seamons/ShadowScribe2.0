# 🎲 ShadowScribe 2.0

A D&D character management system with an AI-powered chat interface for querying character data, rulebooks, and session notes.

## Overview

ShadowScribe 2.0 is a comprehensive RAG (Retrieval-Augmented Generation) system that combines:
- **Character Data Management**: Complete D&D 5e character information with dataclass-based type system
- **Rulebook Integration**: Vector-embedded D&D 5e rules with semantic search
- **Session Notes**: Campaign history tracking and retrieval
- **AI Chat Interface**: Real-time streaming responses via Claude/GPT models
- **Web Frontend**: Modern Next.js interface with WebSocket streaming

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                         │
│  • Real-time chat with streaming responses                       │
│  • Character selection and management                            │
│  • Conversation history (localStorage)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │ WebSocket + HTTP
┌─────────────────────┴───────────────────────────────────────────┐
│                    API Layer (FastAPI)                           │
│  • WebSocket endpoint: /ws/chat                                  │
│  • REST endpoints: /api/characters                               │
│  • Integration with CentralEngine                                │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Python imports
┌─────────────────────┴───────────────────────────────────────────┐
│                 Backend Core (Python)                            │
│  • CentralEngine: Query orchestration                            │
│  • Tool & Entity Selection: Parallel LLM calls                   │
│  • RAG Routers: Character, Rulebook, Session Notes              │
│  • Entity Search: Multi-source resolution                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────────┐
│                    Database (MySQL 8.0)                          │
│  • Character data (JSON storage)                                 │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
1. **Docker Desktop** installed and running
2. **API Keys** in `.env` file:
   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Start the Application

```bash
# Automated startup (recommended)
./scripts/start.sh

# Or manual startup
docker-compose up -d
```

This starts:
- **MySQL**: Port 3306
- **FastAPI**: Port 8000
- **Next.js**: Port 3000

### Access Points

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Usage

1. Open http://localhost:3000 in your browser
2. Click "Select Character" dropdown
3. Choose a character (e.g., "Duskryn Nightwarden")
4. Ask questions like:
   - "What is my AC?"
   - "Tell me about Eldaryth of Regret"
   - "What spells do I have?"
   - "Summarize the last session"
5. Watch responses stream in real-time! ✨

## Project Structure

```
ShadowScribe2.0/
├── api/                        # FastAPI Backend (NEW)
│   ├── main.py                # App entry point
│   ├── config.py              # Configuration
│   ├── database/              # SQLAlchemy models & repos
│   ├── routers/               # WebSocket & REST endpoints
│   ├── services/              # Business logic
│   └── schemas/               # Pydantic schemas
├── frontend/                   # Next.js Frontend (NEW)
│   ├── app/                   # Pages & layouts
│   ├── components/            # React components
│   └── lib/                   # Stores, services, types
├── src/                       # Core Python RAG System
│   ├── central_engine.py      # Main orchestration
│   ├── config.py              # LLM configuration
│   ├── llm/                   # LLM clients & prompts
│   ├── rag/                   # Query routers
│   │   ├── character/         # Character data system
│   │   ├── rulebook/          # D&D rules system
│   │   └── session_notes/     # Campaign history
│   └── utils/                 # Entity search, managers
├── knowledge_base/            # Data storage
│   ├── saved_characters/      # Character pickle files
│   ├── processed_rulebook/    # Vector embeddings
│   └── processed_session_notes/
├── scripts/                   # Utility scripts
│   ├── start.sh              # Automated startup
│   ├── migrate_characters_to_db.py
│   └── export_character_to_json.py
├── docs/                      # Design & planning docs
├── docker-compose.yml         # Orchestration
└── requirements.txt           # Python dependencies
```

## Features

### ✅ Implemented

#### Real-Time Chat
- WebSocket streaming from CentralEngine
- Conversation history in localStorage
- Automatic reconnection on disconnect
- Error handling with user-friendly messages

#### Character Management
- Load characters from MySQL database
- Select character from dropdown
- View character details (race, class, level)
- Automatic character migration from pickle files

#### RAG Query System
- **2-Parallel LLM Architecture**: Tool selection + entity extraction
- **Multi-Source Querying**: Character data, rulebook, session notes
- **Entity Resolution**: Smart search across all data sources
- **Streaming Responses**: Real-time token-by-token output

#### Data Types
- **Character Data**: 20+ dataclasses modeling D&D characters
- **Rulebook**: Vector-embedded D&D 5e rules with semantic search
- **Session Notes**: Campaign history with entity tracking

### 🎯 Key Components

#### CentralEngine (`src/central_engine.py`)
Main query processor with streaming support:
```python
async for chunk in engine.process_query_stream(query, character_name):
    # Yields response chunks as they arrive
```

#### Character Types (`src/rag/character/character_types.py`)
Complete D&D character modeling:
- `Character`: Main dataclass with required/optional modules
- `AbilityScores`, `CombatStats`, `Inventory`, `SpellList`
- `ActionEconomy`, `BackgroundInfo`, `PersonalityTraits`

#### Query Routers
- **CharacterQueryRouter**: Combat, abilities, inventory, spells, backstory
- **RulebookQueryRouter**: Rules, spell details, monster stats
- **SessionNotesQueryRouter**: NPCs, events, locations, quests

## Development

### Environment Setup

**ALWAYS activate virtual environment first:**
```bash
# On macOS/Linux
source .venv/bin/activate

# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### Local Development (Without Docker)

**Backend:**
```bash
# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn[standard] websockets sqlalchemy[asyncio] aiomysql

# Run MySQL
docker run -d -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=shadowscribe_root \
  -e MYSQL_DATABASE=shadowscribe \
  -e MYSQL_USER=shadowscribe \
  -e MYSQL_PASSWORD=shadowscribe_pass \
  mysql:8.0

# Run API
uvicorn api.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Testing

**Interactive Demo (Best for Testing):**
```bash
# Activate venv first!
source .venv/bin/activate

# Interactive mode
python demo_central_engine.py

# Single query
python demo_central_engine.py -q "What is my AC?"

# Multiple queries (maintains context)
python demo_central_engine.py -q "What is my AC?" -q "What about my HP?"
```

**Character Inspector:**
```bash
# List all characters
python -m scripts.run_inspector --list

# Inspect character
python -m scripts.run_inspector "Duskryn Nightwarden" --format summary
```

### Common Commands

```bash
# View Docker logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f mysql

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Run character migration
docker-compose exec api python scripts/migrate_characters_to_db.py

# Check database
docker-compose exec mysql mysql -ushadowscribe -pshadowscribe_pass shadowscribe
```

## API Documentation

### REST Endpoints

**Characters:**
- `GET /api/characters` - List all characters
- `GET /api/characters/{id}` - Get character details
- `DELETE /api/characters/{id}` - Delete character

**Health:**
- `GET /health` - Health check
- `GET /` - API info

### WebSocket API

**Connection:** `ws://localhost:8000/ws/chat`

**Client → Server:**
```json
{
  "type": "message",
  "message": "What is my AC?",
  "character_name": "Duskryn Nightwarden"
}
```

**Server → Client (Streaming):**
```json
// Message received
{"type": "message_received"}

// Response chunks
{"type": "response_chunk", "content": "Your"}
{"type": "response_chunk", "content": " Armor"}
{"type": "response_chunk", "content": " Class"}

// Complete
{"type": "response_complete"}

// Error
{"type": "error", "error": "Error message"}
```

## Critical Development Patterns

### Import System
**Always use absolute imports and module execution:**
```bash
# ✅ Correct
python -m scripts.run_inspector --list

# ❌ Wrong
python scripts/run_inspector.py
```

### Character Access Patterns
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

### Virtual Environment
**ALWAYS activate before running Python code:**
```bash
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows
```

## Configuration

### Environment Variables

**Backend (`.env` in root):**
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=mysql+aiomysql://shadowscribe:shadowscribe_pass@mysql:3306/shadowscribe
```

**Frontend (`frontend/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### LLM Configuration (`src/config.py`)

```python
# Router LLM (fast decisions)
router_llm_provider = "anthropic"  # or "openai"
anthropic_router_model = "claude-3-5-haiku-latest"

# Final Response LLM (quality responses)
final_response_llm_provider = "anthropic"
anthropic_final_model = "claude-sonnet-4-5-20250929"
```

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker info

# Check port conflicts
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :3306  # MySQL

# View service logs
docker-compose logs [service-name]
```

### No characters appear
```bash
# Check database
docker-compose exec mysql mysql -ushadowscribe -pshadowscribe_pass shadowscribe -e "SELECT * FROM characters;"

# Run migration
docker-compose exec api python scripts/migrate_characters_to_db.py
```

### WebSocket connection fails
```bash
# Check API is running
curl http://localhost:8000/health

# Check WebSocket endpoint
wscat -c ws://localhost:8000/ws/chat
```

### Import errors in Python
```bash
# Ensure venv is activated
source .venv/bin/activate

# Run from project root with module syntax
python -m scripts.script_name
```

### Frontend TypeScript errors
These are expected until dependencies are installed:
```bash
cd frontend
npm install
```

## Data Migration

**Migrate existing characters from pickle to MySQL:**
```bash
docker-compose exec api python scripts/migrate_characters_to_db.py
```

**Export character to JSON:**
```bash
python -m scripts.export_character_to_json
```

## Code Philosophy

### Clean Code Principles
- **Delete obsolete code** - don't comment out or leave unused functions
- **No backward compatibility** unless required for data persistence
- **Break things and fix properly** rather than maintaining legacy cruft
- **Name code as fundamental**, not "new" or "v2"

### Development Workflow
1. Make changes
2. Test with `demo_central_engine.py`
3. Commit and document
4. Delete temporary test files

## Future Enhancements

### Phase 6: UI Polish
- [ ] Dark mode toggle implementation
- [ ] D&D themed styling (parchment, dice, fonts)
- [ ] Loading animations
- [ ] Toast notifications

### Phase 7: Advanced Features
- [ ] Character creation wizard
- [ ] Session notes viewer/editor
- [ ] Dice roller integration
- [ ] Multi-character comparison
- [ ] Export conversation history

### Phase 8: Discord Integration
- [ ] Discord bot setup
- [ ] Live transcription
- [ ] Voice-to-text integration
- [ ] Auto-generation of session notes

## Documentation

- **`docs/DESIGN_RAG_ORCHESTRATION.md`**: RAG architecture design
- **`docs/IMPLEMENTATION_GUIDE.md`**: Original frontend planning
- **`docs/character-questions.md`**: Test questions for character queries
- **`docs/session_notes_template.md`**: Session note format
- **`.github/copilot-instructions.md`**: Development guidelines

## Success Criteria

✅ User can select a character  
✅ User can send messages and receive streaming responses  
✅ Conversations are persisted to localStorage  
✅ Character data is viewable  
✅ WebSocket reconnection works  
✅ Error states are handled gracefully  
✅ Application is responsive  

## Contributing

This project prioritizes:
- Clean, modern code over backward compatibility
- Type safety with dataclasses and TypeScript
- Real LLM API integration (no mocks)
- Comprehensive testing via demo scripts
- Clear documentation

## License

[Your License Here]

## Support

For issues:
1. Check Docker logs: `docker-compose logs [service]`
2. Review API docs: http://localhost:8000/docs
3. Check browser console for frontend errors
4. Test backend directly: `python demo_central_engine.py`

---

**Built with:** Python 3.10+, FastAPI, Next.js 14, MySQL 8.0, Claude Sonnet 4, OpenAI GPT-4

**Status:** Core functionality complete, ready for testing and UI polish 🎉
