# ShadowScribe 2.0 - Frontend Implementation Guide

**Document Version**: 1.0  
**Date**: October 13, 2025  
**Status**: Active Implementation Plan

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Technology Stack (Decided)](#technology-stack-decided)
3. [Current System State](#current-system-state)
4. [Architecture Overview](#architecture-overview)
5. [Implementation Phases](#implementation-phases)
6. [Detailed Task Breakdown](#detailed-task-breakdown)
7. [Database Schema Design](#database-schema-design)
8. [API Specifications](#api-specifications)
9. [Frontend Component Structure](#frontend-component-structure)
10. [Development Workflow](#development-workflow)
11. [Future Enhancements](#future-enhancements)

---

## Executive Summary

### Mission
Build a production-ready web interface for ShadowScribe 2.0, connecting a D&D-themed frontend to the existing Python RAG backend via a FastAPI WebSocket layer, with MySQL persistence for character data and conversation history.

### Decisions Made

| Category | Decision | Rationale |
|----------|----------|-----------|
| **Backend API** | FastAPI | Async-native, perfect for streaming LLM responses |
| **Frontend** | Next.js (React) | Most popular, huge ecosystem, SSR support |
| **Streaming** | WebSocket | Real-time bidirectional communication needed |
| **Session Management** | Frontend-only | localStorage for conversations and history |
| **Authentication** | None (for now) | Single-user deployment initially |
| **Deployment** | Docker Compose | All-in-one local development, separate for production |
| **Error Handling** | Comprehensive | Detailed error states and retry logic |
| **Rate Limiting** | None | Single-user deployment, not needed |
| **Testing** | TBD | Strategy to be defined during implementation |
| **Character Creation** | Future Phase | Not in MVP scope |
| **UI Theme** | D&D-themed, Dark/Light modes | Desktop-first, parchment aesthetics |
| **Database** | MySQL | Character data backup and conversation history |
| **Performance** | Standard best practices | Caching, lazy loading, code splitting |

### Timeline Estimate
- **Phase 1-2**: Database + API Layer (2 weeks)
- **Phase 3-4**: Frontend Core (3 weeks)
- **Phase 5**: Integration & Polish (1 week)
- **Total**: ~6 weeks for MVP

---

## Technology Stack (Decided)

### Backend Layer
```yaml
API Framework: FastAPI 0.104+
Language: Python 3.10+
WebSocket: Built-in FastAPI WebSocket support
Database: MySQL 8.0+
ORM: SQLAlchemy 2.0+ with async support
Data Validation: Pydantic v2
CORS: FastAPI CORSMiddleware
Environment: python-dotenv
Testing: pytest + pytest-asyncio
```

### Frontend Layer
```yaml
Framework: Next.js 14+ (React with App Router)
Language: TypeScript 5.0+
Styling: Tailwind CSS 3.4+
UI Components: shadcn/ui (D&D themed)
State Management: Zustand + React Context
WebSocket: Native WebSocket API
Build Tool: Built-in (Next.js/Turbopack)
Testing: Vitest + React Testing Library
```

### Infrastructure
```yaml
Development: Docker Compose
Database: MySQL 8.0 (containerized)
Backend API: Uvicorn ASGI server
Frontend Dev: Next.js dev server
Production: TBD (separate services recommended)
```

---

## Current System State

### ✅ What Exists (Backend Complete)

#### Core RAG System
- **CentralEngine** (`src/central_engine.py`):
  - 2-parallel LLM call architecture (tool selector + entity extractor)
  - Streaming support via `process_query_stream()`
  - Entity resolution with EntitySearchEngine
  - Multi-source querying (character, session notes, rulebook)
  
- **Query Routers**:
  - `CharacterQueryRouter`: Character data queries
  - `SessionNotesQueryRouter`: Campaign history queries
  - `RulebookQueryRouter`: D&D rules queries

- **Data Management**:
  - `CharacterManager`: Character CRUD with pickle storage
  - `CharacterBuilder`: D&D Beyond JSON parser
  - `RulebookStorage`: Vector storage for rulebook
  - `CampaignSessionNotesStorage`: Session notes storage

- **LLM Integration**:
  - `LLMClient`: Abstract LLM client with OpenAI/Anthropic support
  - `CentralPromptManager`: Prompt templates
  - JSON repair and validation

#### Data Storage
- **Character Data**: Pickle files in `knowledge_base/saved_characters/`
  - Currently: 1 character (Duskryn Nightwarden)
- **Session Notes**: Markdown files in `knowledge_base/processed_session_notes/`
- **Rulebook**: Vector embeddings in `knowledge_base/processed_rulebook/`

#### Working Demo
- `demo_central_engine.py`: CLI demo with streaming responses
- Supports interactive queries and conversation history

### ⏳ What Needs to Be Built

#### Database Layer
- MySQL schema for characters and conversations
- SQLAlchemy models and migrations
- Data migration from pickle to MySQL
- Character CRUD operations via database

#### API Layer
- FastAPI application setup
- WebSocket endpoint for chat
- REST endpoints for character management
- Database session management
- Error handling and logging
- CORS configuration

#### Frontend Application
- Next.js project setup with App Router
- Chat interface with streaming
- Character selector
- Conversation history UI (stored in localStorage)
- Dark/light mode theming
- D&D-themed styling
- Responsive layout

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  App Router Pages                                           │ │
│  │  ├─ app/page.tsx (chat page)                               │ │
│  │  ├─ app/characters/page.tsx (character list)               │ │
│  │  └─ app/characters/[id]/page.tsx (character detail)        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Components                                                 │ │
│  │  ├─ ChatContainer.tsx                                      │ │
│  │  ├─ MessageList.tsx                                        │ │
│  │  ├─ MessageInput.tsx                                       │ │
│  │  ├─ CharacterSelector.tsx                                  │ │
│  │  └─ ThemeToggle.tsx                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  State Management (Zustand)                                 │ │
│  │  ├─ stores/chatStore.ts (messages, active conversation)    │ │
│  │  ├─ stores/characterStore.ts (selected character)          │ │
│  │  └─ stores/themeStore.ts (dark/light mode)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Services                                                   │ │
│  │  ├─ websocket.ts (WebSocket connection manager)            │ │
│  │  └─ api.ts (REST API calls)                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ WebSocket + HTTP
                           │
┌──────────────────────────┴───────────────────────────────────────┐
│                      WEB API LAYER (FastAPI)                      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  WebSocket Endpoints                                         ││
│  │  └─ /ws/chat (real-time chat streaming)                     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  REST Endpoints                                              ││
│  │  ├─ GET  /api/characters (list characters)                  ││
│  │  ├─ GET  /api/characters/{id} (get character)               ││
│  │  ├─ POST /api/characters (create character)                 ││
│  │  ├─ PUT  /api/characters/{id} (update character)            ││
│  │  └─ DELETE /api/characters/{id} (delete character)          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Middleware                                                  ││
│  │  ├─ CORS (allow frontend origin)                            ││
│  │  ├─ Error handling (custom exception handlers)              ││
│  │  └─ Logging (request/response logging)                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Database Layer (SQLAlchemy)                                 ││
│  │  └─ Character model (character data only)                    ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ Python imports
                            │
┌───────────────────────────┴───────────────────────────────────────┐
│                 BACKEND CORE (Existing Python)                     │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  CentralEngine                                                ││
│  │  ├─ process_query_stream() (streaming responses)             ││
│  │  ├─ Tool selector + Entity extractor (parallel LLM calls)    ││
│  │  └─ Query router orchestration                               ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  Query Routers                                                ││
│  │  ├─ CharacterQueryRouter (character data queries)            ││
│  │  ├─ SessionNotesQueryRouter (campaign history)               ││
│  │  └─ RulebookQueryRouter (D&D rules)                          ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  Data Management                                              ││
│  │  ├─ CharacterManager (character CRUD)                        ││
│  │  ├─ EntitySearchEngine (entity resolution)                   ││
│  │  └─ Storage components (rulebook, session notes)             ││
│  └──────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────┴───────────────────────────────────────┐
│                         DATABASE (MySQL)                           │
│                                                                    │
│  Tables:                                                           │
│  ├─ characters (character data as JSON)                           │
│  ├─ conversations (conversation metadata)                          │
│  └─ messages (individual messages in conversations)                │
└────────────────────────────────────────────────────────────────────┘
```

### Data Flow: User Query

```
1. USER TYPES MESSAGE
   ↓
2. Frontend: ChatContainer.tsx
   └─ messageInput dispatches message submit
   ↓
3. Frontend: websocket.ts
   └─ sendMessage() → WebSocket.send(JSON)
   ↓
4. API: /ws/chat endpoint receives message
   ↓
5. API: Call CentralEngine.process_query_stream()
   ↓
6. Backend: CentralEngine
   ├─ Tool selector LLM call (parallel)
   └─ Entity extractor LLM call (parallel)
   ↓
7. Backend: EntitySearchEngine.resolve_entities()
   ├─ Search character data
   ├─ Search session notes
   └─ Search rulebook
   ↓
8. Backend: Query routers (parallel)
   ├─ CharacterQueryRouter
   ├─ SessionNotesQueryRouter
   └─ RulebookQueryRouter
   ↓
9. Backend: Final LLM call (streaming)
   └─ Yields response chunks
   ↓
10. API: Stream chunks via WebSocket
    └─ await websocket.send_text(chunk)
    ↓
11. Frontend: websocket.ts receives chunks
    └─ Update chatStore (Zustand) with new chunks
    ↓
12. Frontend: MessageList.tsx re-renders
    └─ Display streaming message to user
    ↓
13. Frontend: Save conversation to localStorage
    └─ Persist messages for history
```

---

## Implementation Phases

### Phase 0: Project Setup (Week 1, Days 1-2)

**Goal**: Set up development environment and project structure

**Tasks**:
1. Create MySQL database schema (characters only)
2. Set up FastAPI project structure
3. Set up Next.js project structure
4. Configure Docker Compose for all services
5. Install and verify all dependencies
6. Create development configuration files

**Deliverables**:
- MySQL running in Docker with character schema created
- FastAPI app skeleton running on http://localhost:8000
- Next.js app skeleton running on http://localhost:3000
- Docker Compose orchestrating all services
- All services communicating successfully

---

### Phase 1: Database Layer (Week 1, Days 3-5)

**Goal**: Implement MySQL persistence for characters only

**Tasks**:
1. Create SQLAlchemy models (Character model only)
2. Implement database connection and session management
3. Create Alembic migrations
4. Implement character repository (CRUD operations)
5. Write unit tests for character repository
6. Create data migration script (pickle → MySQL)
7. Migrate existing Duskryn character to database

**Deliverables**:
- Working character database schema
- Character CRUD operations
- Duskryn character in MySQL database
- Migration script for future characters

---

### Phase 2: API Layer (Week 2)

**Goal**: Build FastAPI WebSocket and REST endpoints

**Tasks**:
1. Implement WebSocket endpoint for chat
   - Connection management
   - Message routing to CentralEngine
   - Streaming response handling
   - Error handling
2. Implement REST endpoints for characters
   - List characters
   - Get character by ID
   - Create character
   - Update character
   - Delete character
3. Add middleware (CORS, logging, error handling)
4. Write integration tests
5. Test with CentralEngine streaming
6. Document all endpoints (OpenAPI)

**Deliverables**:
- Working WebSocket endpoint
- All REST endpoints tested
- OpenAPI documentation
- Integration with existing backend working

---

### Phase 3: Frontend Core (Week 3-4)

**Goal**: Build chat interface and character management

#### Week 3: Chat Interface
**Tasks**:
1. Set up Next.js project structure (App Router)
2. Configure Tailwind CSS and shadcn/ui
3. Set up Zustand stores for state management
4. Implement WebSocket service
5. Create chat stores (chatStore, messageStore)
6. Create localStorage service for conversation persistence
7. Build ChatContainer component
8. Build MessageList component with streaming
9. Build MessageInput component
10. Implement dark/light mode toggle
11. Add loading states and error handling

**Deliverables**:
- Working chat interface
- Real-time streaming messages
- Conversation history persisted in localStorage
- Dark/light mode working
- Error states handled gracefully

#### Week 4: Character Management
**Tasks**:
1. Create character store
2. Build CharacterSelector component
3. Build character list page
4. Build character detail page
5. Implement character API integration
6. Add conversation history UI
7. Polish and refine UI/UX
8. Add animations and transitions
9. Responsive design testing
10. Cross-browser testing

**Deliverables**:
- Character selection working
- Character list and detail pages
- Conversation history accessible
- Responsive on desktop and mobile

---

### Phase 4: Integration & Polish (Week 5-6)

**Goal**: End-to-end testing, bug fixes, and polish

**Week 5: Integration Testing**
**Tasks**:
1. End-to-end testing with real queries
2. Performance testing and optimization
3. Fix identified bugs
4. Add retry logic for failed connections
5. Implement reconnection handling
6. Add user feedback for all actions
7. Test with multiple characters
8. Test conversation persistence
9. Test error scenarios
10. Load testing (if applicable)

**Week 6: Polish & Documentation**
**Tasks**:
1. UI polish (spacing, colors, fonts)
2. Add keyboard shortcuts
3. Add tooltips and help text
4. Improve error messages
5. localStorage data management (export/import conversations)
6. Write user documentation
7. Write deployment guide
8. Create README for frontend
8. Create README for API
9. Record demo video
10. Prepare for production deployment

**Deliverables**:
- Production-ready application
- Complete documentation
- Deployment guide
- Demo video

---

## Detailed Task Breakdown

### Phase 0: Project Setup

#### Task 0.1: Database Setup (4 hours)

**Create MySQL Schema**:

```sql
-- File: api/database/schema.sql

CREATE DATABASE IF NOT EXISTS shadowscribe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shadowscribe;

-- Characters table
CREATE TABLE characters (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    race VARCHAR(100),
    character_class VARCHAR(100),
    level INT,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Note**: Conversation and message history is stored in **frontend localStorage only**. No database tables needed for conversations.

**Docker Compose Configuration**:

```yaml
# File: docker-compose.yml

version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: shadowscribe_mysql
    environment:
      MYSQL_ROOT_PASSWORD: shadowscribe_root
      MYSQL_DATABASE: shadowscribe
      MYSQL_USER: shadowscribe
      MYSQL_PASSWORD: shadowscribe_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./api/database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: shadowscribe_api
    environment:
      DATABASE_URL: mysql+aiomysql://shadowscribe:shadowscribe_pass@mysql:3306/shadowscribe
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./api:/app
      - ./src:/app/src  # Mount existing backend code
      - ./knowledge_base:/app/knowledge_base
    depends_on:
      mysql:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: shadowscribe_frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      PUBLIC_API_URL: http://localhost:8000
      PUBLIC_WS_URL: ws://localhost:8000
    command: npm run dev -- --host

volumes:
  mysql_data:
```

---

#### Task 0.2: FastAPI Project Setup (2 hours)

**Project Structure**:

```
api/
├── main.py                    # FastAPI app entry point
├── Dockerfile
├── requirements.txt
├── .env
├── config.py                  # Configuration
├── database/
│   ├── __init__.py
│   ├── schema.sql
│   ├── connection.py          # Database connection
│   ├── models.py              # SQLAlchemy models
│   └── repositories/
│       ├── __init__.py
│       ├── character_repo.py
│       ├── conversation_repo.py
│       └── message_repo.py
├── routers/
│   ├── __init__.py
│   ├── websocket.py           # WebSocket endpoint
│   └── characters.py          # Character REST endpoints
├── services/
│   ├── __init__.py
│   ├── chat_service.py        # Chat business logic
│   └── character_service.py   # Character business logic
├── schemas/
│   ├── __init__.py
│   └── character.py           # Pydantic schemas
└── middleware/
    ├── __init__.py
    ├── cors.py
    ├── error_handler.py
    └── logging.py
```

**requirements.txt**:

```txt
# API Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0

# Database
sqlalchemy[asyncio]==2.0.23
aiomysql==0.2.0
alembic==1.12.1

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Environment
python-dotenv==1.0.0

# Existing backend dependencies
# (These should already be in root requirements.txt)
# Just ensure they're available in the container
```

---

#### Task 0.3: Next.js Project Setup (2 hours)

**Create Project**:

```bash
# In project root
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
npm install

# Install UI components (shadcn/ui)
npx shadcn-ui@latest init

# Install Zustand for state management
npm install zustand

# Install date utilities
npm install date-fns

# Install additional dev dependencies
npm install -D @types/node
```

**Project Structure**:

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Chat page (/)
│   ├── globals.css             # Global styles
│   └── characters/
│       ├── page.tsx            # Character list
│       └── [id]/
│           └── page.tsx        # Character detail
├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageInput.tsx
│   │   └── MessageBubble.tsx
│   ├── character/
│   │   ├── CharacterSelector.tsx
│   │   ├── CharacterCard.tsx
│   │   └── CharacterSheet.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── ThemeToggle.tsx
├── lib/
│   ├── stores/
│   │   ├── chatStore.ts        # Zustand store
│   │   ├── characterStore.ts   # Zustand store
│   │   └── themeStore.ts       # Zustand store
│   ├── services/
│   │   ├── websocket.ts
│   │   ├── api.ts
│   │   └── localStorage.ts     # Conversation persistence
│   └── types/
│       ├── character.ts
│       ├── conversation.ts
│       └── message.ts
├── public/
│   └── images/
│       └── dice-icon.svg
├── styles/
│   ├── colors.css              # D&D color palette
│   └── fonts.css               # D&D-style fonts
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── Dockerfile.dev
```

---

### Phase 1: Database Layer

#### Task 1.1: SQLAlchemy Models (3 hours)

**File: `api/database/models.py`**

```python
from sqlalchemy import Column, String, Integer, Text, JSON, TIMESTAMP, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class Character(Base):
    """Character model - stores full character data as JSON."""
    __tablename__ = 'characters'
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    race = Column(String(100))
    character_class = Column(String(100))
    level = Column(Integer)
    data = Column(JSON, nullable=False)  # Full Character object as JSON
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Note**: No conversation or message models needed - chat history managed in frontend localStorage.

---

#### Task 1.2: Database Connection (2 hours)

**File: `api/database/connection.py`**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+aiomysql://shadowscribe:shadowscribe_pass@localhost:3306/shadowscribe')

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Dependency for FastAPI to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database (create tables)."""
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Close database connection."""
    await engine.dispose()
```

---

#### Task 1.3: Character Repository (4 hours)

**File: `api/database/repositories/character_repo.py`**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
import json
from datetime import datetime

from ..models import Character as CharacterModel
from src.rag.character.character_types import Character as CharacterDataclass

class CharacterRepository:
    """Repository for character CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, character: CharacterDataclass) -> CharacterModel:
        """Create a new character in the database."""
        # Convert Character dataclass to JSON
        character_data = self._dataclass_to_dict(character)
        
        # Create database model
        db_character = CharacterModel(
            id=self._generate_id(character.character_base.name),
            name=character.character_base.name,
            race=character.character_base.race,
            character_class=character.character_base.character_class,
            level=character.character_base.total_level,
            data=character_data
        )
        
        self.session.add(db_character)
        await self.session.flush()
        return db_character
    
    async def get_by_id(self, character_id: str) -> Optional[CharacterModel]:
        """Get character by ID."""
        result = await self.session.execute(
            select(CharacterModel).where(CharacterModel.id == character_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[CharacterModel]:
        """Get all characters."""
        result = await self.session.execute(select(CharacterModel))
        return result.scalars().all()
    
    async def update(self, character_id: str, character: CharacterDataclass) -> Optional[CharacterModel]:
        """Update character."""
        character_data = self._dataclass_to_dict(character)
        
        await self.session.execute(
            update(CharacterModel)
            .where(CharacterModel.id == character_id)
            .values(
                name=character.character_base.name,
                race=character.character_base.race,
                character_class=character.character_base.character_class,
                level=character.character_base.total_level,
                data=character_data,
                updated_at=datetime.utcnow()
            )
        )
        
        return await self.get_by_id(character_id)
    
    async def delete(self, character_id: str) -> bool:
        """Delete character."""
        result = await self.session.execute(
            delete(CharacterModel).where(CharacterModel.id == character_id)
        )
        return result.rowcount > 0
    
    def to_dataclass(self, db_character: CharacterModel) -> CharacterDataclass:
        """Convert database model to Character dataclass."""
        # Deserialize JSON back to Character dataclass
        return self._dict_to_dataclass(db_character.data)
    
    @staticmethod
    def _generate_id(name: str) -> str:
        """Generate URL-safe ID from character name."""
        import re
        return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    
    @staticmethod
    def _dataclass_to_dict(character: CharacterDataclass) -> dict:
        """Convert Character dataclass to JSON-serializable dict."""
        from dataclasses import asdict
        return asdict(character)
    
    @staticmethod
    def _dict_to_dataclass(data: dict) -> CharacterDataclass:
        """Convert dict to Character dataclass."""
        # TODO: Implement proper deserialization with nested dataclasses
        # This is a placeholder - needs proper implementation
        from dacite import from_dict
        return from_dict(data_class=CharacterDataclass, data=data)
```

---

(Continue with Task 1.4-1.8 for conversation repository, migration script, etc.)

---

### Phase 2: API Layer

#### Task 2.1: WebSocket Chat Endpoint (6 hours)

**File: `api/routers/websocket.py`**

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
import json
import uuid
import asyncio

from ..database.connection import get_db
from ..database.repositories.conversation_repo import ConversationRepository
from ..database.repositories.message_repo import MessageRepository
from ..services.chat_service import ChatService

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@router.websocket("/ws/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    connection_id = str(uuid.uuid4())
    active_connections[connection_id] = websocket
    
    # Initialize services
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    chat_service = ChatService(conversation_repo, message_repo)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract message details
            user_message = message_data.get('message')
            character_name = message_data.get('character_name')
            
            # Validate input
            if not user_message or not character_name:
                await websocket.send_json({
                    'type': 'error',
                    'error': 'Missing required fields: message, character_name'
                })
                continue
            
            # Send acknowledgment
            await websocket.send_json({
                'type': 'message_received'
            })
            
            # Stream response from CentralEngine
            try:
                assistant_message = ""
                async for chunk in chat_service.process_query_stream(user_message, character_name):
                    assistant_message += chunk
                    
                    # Send chunk to client
                    await websocket.send_json({
                        'type': 'response_chunk',
                        'content': chunk
                    })
                
                # Send completion signal
                await websocket.send_json({
                    'type': 'response_complete'
                })
                
            except Exception as e:
                await websocket.send_json({
                    'type': 'error',
                    'error': f'Error processing query: {str(e)}'
                })
    
    except WebSocketDisconnect:
        print(f"Client disconnected: {connection_id}")
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        try:
            await websocket.send_json({
                'type': 'error',
                'error': str(e)
            })
        except:
            pass
    finally:
        # Clean up connection
        if connection_id in active_connections:
            del active_connections[connection_id]
        try:
            await websocket.close()
        except:
            pass
```

**Note**: Conversation history is managed entirely in the frontend using localStorage. The API only streams responses without persisting conversation data.

---

(Continue with additional API endpoints, services, frontend components, etc.)

---

## Database Schema Design

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────┐
│              characters                  │
├─────────────────────────────────────────┤
│ id (PK)               VARCHAR(255)       │
│ name                  VARCHAR(255)       │
│ race                  VARCHAR(100)       │
│ character_class       VARCHAR(100)       │
│ level                 INT                │
│ data                  JSON               │
│ created_at            TIMESTAMP          │
│ updated_at            TIMESTAMP          │
└─────────────────────────────────────────┘
```

**Note**: Conversations and messages are stored in **frontend localStorage only** - no database tables needed.

### Data Examples

**Character JSON Structure**:
```json
{
  "character_base": {
    "name": "Duskryn Nightwarden",
    "race": "Half-Elf",
    "character_class": "Warlock",
    "total_level": 5,
    ...
  },
  "ability_scores": {
    "strength": 10,
    "dexterity": 14,
    ...
  },
  "combat_stats": {
    "max_hp": 38,
    "armor_class": 16,
    ...
  },
  ...
}
```

---

## API Specifications

### WebSocket API

**Connection**: `ws://localhost:8000/ws/chat`

**Client → Server Messages**:

```typescript
// Send a chat message
{
  type: 'message',
  message: string,
  character_name: string
}

// Ping (keep-alive)
{
  type: 'ping'
}
```

**Server → Client Messages**:

```typescript
// Message received acknowledgment
{
  type: 'message_received'
}

// Response chunk (streaming)
{
  type: 'response_chunk',
  content: string
}

// Response complete
{
  type: 'response_complete'
}

// Error
{
  type: 'error',
  error: string
}

// Pong (keep-alive response)
{
  type: 'pong'
}
```

### REST API

**Base URL**: `http://localhost:8000/api`

#### Characters

```
GET /characters
Response: { characters: Character[] }

GET /characters/{id}
Response: Character

POST /characters
Body: { data: CharacterJSON }
Response: Character

PUT /characters/{id}
Body: { data: CharacterJSON }
Response: Character

DELETE /characters/{id}
Response: { status: 'deleted', id: string }
```

#### Conversations

```
GET /conversations
Query: character_id (optional)
Response: { conversations: Conversation[] }

GET /conversations/{id}
Response: { conversation: Conversation, messages: Message[] }

DELETE /conversations/{id}
Response: { status: 'deleted', id: string }
```

---

## Frontend Component Structure

### Store Architecture

**chatStore.ts**:
```typescript
import { writable, derived } from 'svelte/store';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  conversationId: string | null;
  isStreaming: boolean;
  error: string | null;
}

function createChatStore() {
  const { subscribe, set, update } = writable<ChatState>({
    messages: [],
    conversationId: null,
    isStreaming: false,
    error: null
  });

  return {
    subscribe,
    addMessage: (message: Message) => update(state => ({
      ...state,
      messages: [...state.messages, message]
    })),
    updateLastMessage: (content: string) => update(state => {
      const messages = [...state.messages];
      if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
        messages[messages.length - 1].content += content;
      }
      return { ...state, messages };
    }),
    setStreaming: (isStreaming: boolean) => update(state => ({ ...state, isStreaming })),
    setError: (error: string | null) => update(state => ({ ...state, error })),
    setConversationId: (id: string) => update(state => ({ ...state, conversationId: id })),
    reset: () => set({
      messages: [],
      conversationId: null,
      isStreaming: false,
      error: null
    })
  };
}

export const chatStore = createChatStore();
```

---

## Development Workflow

### Daily Development Loop

1. **Morning**: Pull latest, activate venv, start Docker Compose
2. **Development**: Make changes, test locally
3. **Testing**: Run unit tests, integration tests
4. **Evening**: Commit changes, push to repo

### Commands Reference

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Run backend tests
docker-compose exec api pytest

# Run frontend tests
docker-compose exec frontend npm run test

# Database migrations
docker-compose exec api alembic upgrade head

# Stop all services
docker-compose down

# Rebuild after dependency changes
docker-compose up --build
```

---

## Future Enhancements

### Phase 6: Character Creation Wizard (Future)
- D&D Beyond URL/JSON import
- Character preview and refinement
- Manual character creation form
- Character export functionality

### Phase 7: Objectives & Contracts (Future)
- Objective tracking UI
- Contract management
- Quest log
- Progress visualization

### Phase 8: Discord Integration (Future)
- Discord bot setup
- Live transcription service
- Voice-to-text integration
- Session note auto-generation from transcriptions
- Real-time session notes updates

### Phase 9: Advanced Features (Future)
- Multi-character comparison
- Campaign management
- Dice roller integration
- Combat tracker
- Spell/item lookup
- Voice input/output
- Image generation for characters
- Export to PDF character sheets

---

## Success Criteria

### MVP Definition of Done
- [ ] User can select a character
- [ ] User can send messages and receive streaming responses
- [ ] Conversations are persisted to database
- [ ] Chat history is accessible
- [ ] Character data is viewable
- [ ] Dark and light modes work
- [ ] D&D-themed UI looks great
- [ ] Error states are handled gracefully
- [ ] WebSocket reconnection works
- [ ] Application is responsive (desktop + mobile)

### Performance Targets
- WebSocket connection: < 500ms
- Message send latency: < 100ms
- First response chunk: < 2s
- Full response streaming: < 10s (for complex queries)
- Character load time: < 500ms
- Conversation load time: < 1s

### Quality Metrics
- 0 known critical bugs
- < 5 known minor bugs
- Test coverage > 70%
- No console errors in production
- Lighthouse score > 90 (performance, accessibility)

---

## Appendix

### Environment Variables

**API (.env)**:
```bash
DATABASE_URL=mysql+aiomysql://shadowscribe:shadowscribe_pass@mysql:3306/shadowscribe
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Useful Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **React**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **shadcn/ui**: https://ui.shadcn.com/
- **Zustand**: https://zustand-demo.pmnd.rs/

---

**Document Status**: Active Implementation Guide  
**Last Updated**: [Current Date]  
**Next Review**: After Phase 0 completion
