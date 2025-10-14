# ShadowScribe 2.0 - Visual Roadmap

**Last Updated**: October 13, 2025  
**Status**: Ready to build

---

## 🎯 Project Vision

Build a production-ready D&D character assistant with a beautiful web interface that connects to the existing Python RAG backend, featuring real-time streaming responses and MySQL persistence.

---

## 📊 Current State vs. Target State

### ✅ Current State (Backend Complete)
```
┌────────────────────────────────────┐
│     COMMAND LINE INTERFACE         │
│  (demo_central_engine.py)          │
│  - Interactive chat                │
│  - Manual character selection      │
│  - No persistence                  │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│        PYTHON BACKEND              │
│  ✅ CentralEngine (RAG)            │
│  ✅ 2-parallel LLM architecture    │
│  ✅ Streaming responses            │
│  ✅ Entity resolution              │
│  ✅ Multi-source querying          │
│  ✅ Character data (pickle files)  │
└────────────────────────────────────┘
```

### 🎯 Target State (6 Weeks)
```
┌────────────────────────────────────┐
│      SVELTEKIT FRONTEND            │
│  - Beautiful D&D-themed UI         │
│  - Real-time chat with streaming   │
│  - Character selection             │
│  - Conversation history            │
│  - Dark/light modes                │
│  - Responsive design               │
└────────────────────────────────────┘
              ↓ WebSocket + HTTP
┌────────────────────────────────────┐
│        FASTAPI WEB API             │
│  - WebSocket chat endpoint         │
│  - REST character endpoints        │
│  - REST conversation endpoints     │
│  - Database session management     │
│  - Error handling & logging        │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│        MYSQL DATABASE              │
│  - Character data (JSON)           │
│  - Conversations                   │
│  - Message history                 │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│        PYTHON BACKEND              │
│  ✅ CentralEngine (RAG)            │
│  ✅ 2-parallel LLM architecture    │
│  ✅ Streaming responses            │
│  ✅ Entity resolution              │
│  ✅ Multi-source querying          │
│  ✅ Character data integration     │
└────────────────────────────────────┘
```

---

## 🗓️ 6-Week Timeline

```
Week 1: Infrastructure & Database
├─ Days 1-2: Phase 0 - Project Setup ✓ (You start here!)
├─ Days 3-5: Phase 1 - Database Layer
└─ Weekend: Buffer

Week 2: API Layer
├─ Days 1-3: WebSocket chat endpoint
├─ Days 4-5: REST character/conversation endpoints
└─ Weekend: Testing & documentation

Week 3: Frontend - Chat Interface
├─ Day 1: SvelteKit structure & routing
├─ Day 2: WebSocket service & stores
├─ Days 3-4: Chat components
├─ Day 5: Dark/light mode & theming
└─ Weekend: Polish

Week 4: Frontend - Character Management
├─ Days 1-2: Character selector & list
├─ Day 3: Character detail page
├─ Day 4: Conversation history UI
├─ Day 5: Responsive design
└─ Weekend: Testing

Week 5: Integration & Testing
├─ Days 1-2: End-to-end integration
├─ Days 3-4: Bug fixes & performance
├─ Day 5: Error handling polish
└─ Weekend: User testing

Week 6: Polish & Launch
├─ Days 1-2: UI/UX final polish
├─ Day 3: Documentation complete
├─ Day 4: Deployment preparation
├─ Day 5: Launch! 🚀
└─ Weekend: Celebrate
```

---

## 📋 Phase Breakdown

### Phase 0: Project Setup (Days 1-2) ← **START HERE**
**Goal**: All services running locally

**Deliverables**:
- ✓ MySQL running with schema
- ✓ FastAPI skeleton responding
- ✓ SvelteKit homepage loading
- ✓ Docker Compose orchestrating
- ✓ Backend integration working

**Time**: 16 hours (2 days)

**Next Step**: See PHASE_0_CHECKLIST.md

---

### Phase 1: Database Layer (Days 3-5)
**Goal**: MySQL persistence for characters & conversations

**Key Components**:
- SQLAlchemy models (Character, Conversation, Message)
- Database repositories (CRUD operations)
- Data migration script (pickle → MySQL)
- Character in database

**Deliverables**:
- ✓ Working database schema
- ✓ Character CRUD operations
- ✓ Conversation CRUD operations
- ✓ Duskryn migrated to MySQL

**Time**: 24 hours (3 days)

---

### Phase 2: API Layer (Week 2)
**Goal**: FastAPI WebSocket & REST endpoints

**Key Components**:
- WebSocket endpoint for chat
- REST endpoints for characters
- REST endpoints for conversations
- Middleware (CORS, logging, errors)
- Integration with CentralEngine

**Deliverables**:
- ✓ WebSocket streaming working
- ✓ All REST endpoints tested
- ✓ OpenAPI documentation
- ✓ Backend integration complete

**Time**: 40 hours (5 days)

---

### Phase 3: Frontend Core (Weeks 3-4)
**Goal**: Beautiful, functional chat interface

#### Week 3: Chat Interface
**Key Components**:
- SvelteKit routing & layout
- WebSocket service
- Chat stores (state management)
- ChatContainer component
- MessageList with streaming
- MessageInput
- Theme toggle (dark/light)

**Deliverables**:
- ✓ Chat interface working
- ✓ Real-time streaming
- ✓ Dark/light modes
- ✓ D&D theming applied

**Time**: 40 hours (5 days)

#### Week 4: Character Management
**Key Components**:
- Character store
- CharacterSelector component
- Character list page
- Character detail page
- Conversation history UI
- Responsive design

**Deliverables**:
- ✓ Character selection working
- ✓ Character pages complete
- ✓ Conversation history accessible
- ✓ Mobile responsive

**Time**: 40 hours (5 days)

---

### Phase 4: Integration & Polish (Weeks 5-6)
**Goal**: Production-ready application

#### Week 5: Integration & Testing
**Key Components**:
- End-to-end testing
- Performance optimization
- Bug fixes
- Error handling
- Reconnection logic

**Deliverables**:
- ✓ All features working end-to-end
- ✓ Performance targets met
- ✓ Error states handled
- ✓ No critical bugs

**Time**: 40 hours (5 days)

#### Week 6: Polish & Launch
**Key Components**:
- UI polish (spacing, colors, animations)
- Keyboard shortcuts
- Tooltips & help text
- Documentation
- Deployment guide
- Demo video

**Deliverables**:
- ✓ Production-ready app
- ✓ Complete documentation
- ✓ Deployed and accessible
- ✓ Demo video created

**Time**: 40 hours (5 days)

---

## 🎨 Design Language

### D&D Theme Elements

**Colors**:
- **Primary**: Deep purple/indigo (arcane magic)
- **Secondary**: Gold (treasure, important actions)
- **Accent**: Crimson red (damage, warnings)
- **Neutral**: Warm parchment tones
- **Dark mode**: Dark stone/wood textures
- **Light mode**: Clean parchment/paper textures

**Typography**:
- **Headers**: Fantasy serif (Cinzel, Spectral)
- **Body**: Readable sans-serif (Inter, Source Sans)
- **Monospace**: Fira Code (for stats)

**UI Elements**:
- Parchment-style cards
- Leather-textured buttons
- Subtle dice patterns
- Scroll animations
- Hover states with glow effects
- D20 loading spinner

**Layout**:
- Desktop-first (primary use case)
- Sidebar for character selection
- Main chat area (60% width)
- Right panel for character stats (optional)

---

## 🔧 Technology Decisions Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| **Backend API** | FastAPI | Async-native, perfect for streaming |
| **Frontend** | SvelteKit | Lean, fast, great DX, built-in routing |
| **Database** | MySQL 8.0 | Reliable, familiar, JSON support |
| **ORM** | SQLAlchemy | Industry standard, async support |
| **Styling** | Tailwind CSS | Utility-first, rapid development |
| **UI Components** | shadcn-svelte | Beautiful, customizable, D&D themeable |
| **State** | Svelte stores | Built-in, reactive, simple |
| **WebSocket** | Native API | No dependencies needed |
| **Streaming** | WebSocket | Real-time bidirectional |
| **Container** | Docker Compose | Easy local dev, clear separation |
| **Auth** | None (Phase 1) | Single-user initially |

---

## 📈 Success Metrics

### Performance Targets
- **WebSocket latency**: < 500ms
- **Message send**: < 100ms
- **First response chunk**: < 2s
- **Full streaming**: < 10s
- **Character load**: < 500ms
- **Conversation load**: < 1s

### Quality Targets
- **0 critical bugs**
- **< 5 minor bugs**
- **Test coverage**: > 70%
- **Lighthouse score**: > 90
- **Zero console errors**

### User Experience
- **Intuitive**: New users can chat within 30 seconds
- **Fast**: Responses feel instant
- **Beautiful**: D&D theme delights users
- **Reliable**: Reconnects automatically
- **Accessible**: Works on desktop + mobile

---

## 🚀 Quick Start (Phase 0)

### Prerequisites
- Docker Desktop installed
- Node.js 20+ installed
- Git installed
- Code editor (VS Code recommended)

### Get Started
```bash
# 1. Navigate to project
cd /Users/calvinseamons/ShadowScribe2.0

# 2. Follow Phase 0 checklist
open docs/PHASE_0_CHECKLIST.md

# 3. Start building!
```

### First Task
**Create MySQL schema file**:
```bash
mkdir -p api/database
touch api/database/schema.sql
```

Copy schema from IMPLEMENTATION_GUIDE.md and you're off! 🎉

---

## 📚 Documentation Map

All documents are in `docs/`:

1. **FRONTEND_ARCHITECTURE_DESIGN.md** ← Design decisions & architecture
2. **IMPLEMENTATION_GUIDE.md** ← Complete implementation details
3. **PHASE_0_CHECKLIST.md** ← Your step-by-step starting point
4. **VISUAL_ROADMAP.md** ← This document (overview)
5. **TASKS_MASTER.md** ← Backend RAG implementation status

---

## 🎯 Milestones

### Milestone 1: Infrastructure Running (End of Week 1)
- [ ] All services in Docker Compose
- [ ] MySQL with data
- [ ] FastAPI responding
- [ ] SvelteKit homepage
- [ ] Backend integration test passing

### Milestone 2: API Complete (End of Week 2)
- [ ] WebSocket chat working
- [ ] Character endpoints tested
- [ ] Conversation endpoints tested
- [ ] OpenAPI docs complete

### Milestone 3: Chat Interface (End of Week 3)
- [ ] Send message and see response
- [ ] Streaming responses displayed
- [ ] Dark/light mode toggle
- [ ] Basic D&D theming

### Milestone 4: Character Management (End of Week 4)
- [ ] Select character from list
- [ ] View character details
- [ ] Access conversation history
- [ ] Mobile responsive

### Milestone 5: Production Ready (End of Week 6)
- [ ] All features working
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Deployed and accessible
- [ ] Demo video recorded

---

## 🔮 Future Phases (Post-MVP)

### Phase 6: Character Creation Wizard
- D&D Beyond JSON import
- Character preview & refinement
- Manual character creation
- Character export

**Time**: 2 weeks

---

### Phase 7: Objectives & Contracts
- Objective tracking UI
- Contract management
- Quest log
- Progress visualization

**Time**: 1 week

---

### Phase 8: Discord Integration
- Discord bot setup
- Live transcription service
- Voice-to-text integration
- Auto-generate session notes
- Real-time updates

**Time**: 3 weeks

---

### Phase 9: Advanced Features
- Multi-character comparison
- Campaign management
- Dice roller
- Combat tracker
- Spell/item lookup
- Voice I/O
- Image generation
- PDF export

**Time**: 4-6 weeks

---

## 💪 You Got This!

This is an ambitious but totally achievable project. The backend is solid, the design is clear, and you have detailed guides for every step.

### Tips for Success

1. **Follow the phases in order** - each builds on the last
2. **Test as you go** - don't wait until the end
3. **Use the checklists** - they're your friend
4. **Commit often** - small commits = easy rollback
5. **Take breaks** - burnout helps nobody
6. **Ask for help** - when stuck, refer to docs or ask
7. **Celebrate wins** - every milestone matters! 🎉

### Starting Point

**Right now, open** `docs/PHASE_0_CHECKLIST.md` **and start with Task 1.**

You'll be chatting with your AI DM in no time! ⚔️🎲🐉

---

**Built with**: Python • FastAPI • SvelteKit • MySQL • ❤️  
**For**: D&D players who want an AI-powered character assistant  
**Status**: Ready to build

---

## 🎬 What Success Looks Like

**In 6 weeks, you'll have**:

```
User opens http://shadowscribe.local
  ↓
Sees beautiful D&D-themed interface
  ↓
Selects "Duskryn Nightwarden" from sidebar
  ↓
Types: "What combat abilities do I have?"
  ↓
Sees streaming response appear in real-time:
"Based on your character sheet, Duskryn, you have several 
powerful combat abilities:

**Eldritch Blast** - Your primary attack, enhanced by 
Agonizing Blast to add your Charisma modifier (+4) to 
damage...

**Hexblade's Curse** - You can curse a target, adding 
your proficiency bonus to damage rolls against them..."
  ↓
User smiles, clicks next query
  ↓
Conversation history saved automatically
  ↓
User switches to light mode
  ↓
Still looks amazing with parchment theme
  ↓
User shares with D&D group
  ↓
Everyone wants one! 🎉
```

**Let's build it! 🚀**
