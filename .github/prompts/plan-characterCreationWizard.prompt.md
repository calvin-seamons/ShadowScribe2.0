# Plan: Character Creation Wizard with D&D Beyond URL Import, WebSocket Progress, and Full CRUD

A comprehensive multi-step wizard that fetches character JSON from D&D Beyond URLs, streams real-time parsing progress via WebSocket, allows full CRUD editing of all character sections, and saves to the database.

## Architecture Overview

### Data Flow
```
User → Frontend Wizard → WebSocket → Async Character Builder → Database
         ↓                  ↓              ↓
    URL Input        Progress Events   6 Parallel Parsers
         ↓                  ↓              ↓
   Fetch JSON        Real-time UI    Character Dataclass
         ↓                  ↓              ↓
  Section Editors    Loading Bars      MySQL JSON
```

### Key Technical Decisions
1. **D&D Beyond URL import** - Assume 100% reliability, no fallback needed
2. **WebSocket progress** - Stream real-time updates for all 6 parsers
3. **Parallel execution** - All parsers run simultaneously using `asyncio.TaskGroup`
4. **Full CRUD** - Complete add/remove/edit capabilities for all sections
5. **Incremental saves** - `PATCH` endpoints for individual section updates

## Implementation Steps

### Step 1: D&D Beyond Fetcher Service

**Create**: `api/services/dndbeyond_service.py`

**Functionality**:
- Extract character ID from URL using regex: `/characters/(\d+)`
- Fetch JSON from `https://character-service.dndbeyond.com/character/v5/character/{id}`
- Error handling for network failures, invalid URLs, 404s
- Return raw D&D Beyond JSON

**API Endpoint**: Add to `api/routers/characters.py`
```python
POST /api/characters/fetch
Request: { "url": "https://dndbeyond.com/characters/140237850" }
Response: { "json_data": { ...full D&D Beyond JSON... } }
```

**Dependencies**:
- `httpx` for async HTTP requests
- `re` for URL parsing

---

### Step 2: Async Character Builder

**Create**: `src/character_creation/async_character_builder.py`

**Functionality**:
- Convert synchronous `CharacterBuilder` to async
- Use `asyncio.TaskGroup` for parallel parser execution
- Progress callbacks yielding events:
  - `parser_started` - Parser begins execution
  - `parser_progress` - LLM-based parsers report progress
  - `parser_complete` - Parser finishes with timing data
  - `assembly_started` - Character object assembly begins
  - `creation_complete` - Final Character dataclass ready

**Parser Execution Strategy**:
```python
async with asyncio.TaskGroup() as group:
    # All 6 parsers run simultaneously
    core_task = group.create_task(asyncio.to_thread(core_parser.parse))
    inventory_task = group.create_task(asyncio.to_thread(inventory_parser.parse))
    spell_task = group.create_task(asyncio.to_thread(spell_parser.parse))
    features_task = group.create_task(asyncio.to_thread(features_parser.parse))
    background_task = group.create_task(background_parser.parse())  # Already async
    actions_task = group.create_task(actions_parser.parse())  # Already async
```

**Parsers** (all run in parallel, no dependencies):
1. `CoreParser` - ability scores, character base, combat stats
2. `InventoryParser` - equipment, items, weight
3. `SpellParser` - spells, spell slots, spellcasting info
4. `FeaturesParser` - racial traits, class features, feats
5. `BackgroundParser` - backstory, personality (LLM-based, ~2-5s)
6. `ActionsParser` - attacks, abilities, action economy (LLM-based, ~0.5-2s)

**Expected Execution Time**: ~2.5-5.5 seconds total

---

### Step 3: WebSocket Endpoint for Character Creation

**Modify**: `api/routers/websocket.py`

**Add Endpoint**:
```python
@router.websocket("/ws/character/create")
async def character_creation_websocket(websocket: WebSocket):
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data['type'] == 'create_character':
                async for event in create_character_stream(data['json_data']):
                    await websocket.send_json(event)
    
    except WebSocketDisconnect:
        # Cleanup
        pass
```

**Message Types**:
- **Client → Server**:
  - `create_character` - Start character creation with JSON data
  - `ping` - Keep-alive

- **Server → Client**:
  - `parser_started` - `{ parser: "core", completed: 0, total: 6 }`
  - `parser_complete` - `{ parser: "core", completed: 1, total: 6, execution_time_ms: 150 }`
  - `creation_complete` - `{ character_id: "duskryn-nightwarden", character: {...} }`
  - `creation_error` - `{ error: "Parser failed: ...", parser: "background" }`
  - `pong` - Keep-alive response

**Integration**: Use async character builder from Step 2 with progress callbacks

---

### Step 4: CRUD API Endpoints

**Modify**: `api/routers/characters.py`

**New Endpoints**:

```python
POST /api/characters
# Create new character from parsed Character dataclass
Request: { "character": { ...Character dataclass as JSON... } }
Response: { "id": "duskryn-nightwarden", "name": "Duskryn Nightwarden", ... }

PUT /api/characters/{id}
# Full character update (replace entire character)
Request: { "character": { ...Complete Character dataclass... } }
Response: { "id": "duskryn-nightwarden", "name": "Duskryn Nightwarden", ... }

PATCH /api/characters/{id}/{section}
# Partial section update for incremental saves
# Sections: ability_scores, combat_stats, inventory, spell_list, 
#           action_economy, features_and_traits, backstory, personality
Request: { "data": { ...section-specific data... } }
Response: { "updated": true, "section": "inventory" }

POST /api/characters/fetch
# Fetch character JSON from D&D Beyond URL
Request: { "url": "https://dndbeyond.com/characters/140237850" }
Response: { "json_data": { ...full D&D Beyond JSON... } }
```

**Repository Integration**: Use existing `CharacterRepository` methods
- `create(character: Character)` → database save
- `update(character_id: str, character: Character)` → full update
- Add `update_section(character_id: str, section: str, data: dict)` → partial update

**Validation**: Add Pydantic schemas for each section's PATCH data

---

### Step 5: Frontend WebSocket Service Extension

**Modify**: `frontend/lib/services/websocket.ts`

**Add Methods**:
```typescript
class WebSocketService {
  private onProgressHandler: ((progress: CharacterCreationProgress) => void) | null = null
  
  /**
   * Register progress callback for character creation
   */
  onProgress(handler: (progress: CharacterCreationProgress) => void) {
    this.onProgressHandler = handler
  }
  
  /**
   * Create character via WebSocket with real-time progress
   * Returns Promise that resolves to character ID when complete
   */
  createCharacter(jsonData: any): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket is not connected'))
        return
      }
      
      const handler = (event: MessageEvent) => {
        const data = JSON.parse(event.data)
        
        switch (data.type) {
          case 'parser_started':
          case 'parser_progress':
          case 'parser_complete':
            this.onProgressHandler?.(data)
            break
          
          case 'creation_complete':
            this.ws?.removeEventListener('message', handler)
            resolve(data.character_id)
            break
          
          case 'creation_error':
            this.ws?.removeEventListener('message', handler)
            reject(new Error(data.error))
            break
        }
      }
      
      this.ws.addEventListener('message', handler)
      
      this.ws.send(JSON.stringify({
        type: 'create_character',
        json_data: jsonData
      }))
    })
  }
}
```

**TypeScript Types**: Add to `frontend/lib/types/character.ts`
```typescript
interface CharacterCreationProgress {
  type: 'parser_started' | 'parser_complete' | 'parser_progress'
  parser: 'core' | 'inventory' | 'spells' | 'features' | 'background' | 'actions'
  completed: number
  total: number
  execution_time_ms?: number
  message?: string
}
```

---

### Step 6: React Hook for Character Creation

**Create**: `frontend/lib/hooks/useCharacterCreation.ts`

**Functionality**:
```typescript
interface ParserProgress {
  parser: string
  status: 'idle' | 'started' | 'in_progress' | 'complete'
  progress?: number
  execution_time_ms?: number
  message?: string
}

export function useCharacterCreation() {
  const [parsers, setParsers] = useState<Record<string, ParserProgress>>({
    core: { parser: 'core', status: 'idle' },
    inventory: { parser: 'inventory', status: 'idle' },
    spells: { parser: 'spells', status: 'idle' },
    features: { parser: 'features', status: 'idle' },
    background: { parser: 'background', status: 'idle' },
    actions: { parser: 'actions', status: 'idle' },
  })
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [characterId, setCharacterId] = useState<string | null>(null)
  
  const createCharacter = async (jsonData: any) => {
    setIsCreating(true)
    setError(null)
    
    websocketService.onProgress((progress) => {
      setParsers(prev => ({
        ...prev,
        [progress.parser]: {
          parser: progress.parser,
          status: progress.type === 'parser_started' ? 'started' : 
                  progress.type === 'parser_complete' ? 'complete' : 'in_progress',
          execution_time_ms: progress.execution_time_ms,
          message: progress.message
        }
      }))
    })
    
    try {
      const id = await websocketService.createCharacter(jsonData)
      setCharacterId(id)
      setIsCreating(false)
      return id
    } catch (err) {
      setError(err.message)
      setIsCreating(false)
      throw err
    }
  }
  
  const resetProgress = () => {
    setParsers({
      core: { parser: 'core', status: 'idle' },
      inventory: { parser: 'inventory', status: 'idle' },
      spells: { parser: 'spells', status: 'idle' },
      features: { parser: 'features', status: 'idle' },
      background: { parser: 'background', status: 'idle' },
      actions: { parser: 'actions', status: 'idle' },
    })
    setError(null)
    setCharacterId(null)
  }
  
  return { 
    createCharacter, 
    parsers, 
    isCreating, 
    error, 
    characterId,
    resetProgress 
  }
}
```

**Integration**: Import and use in wizard component

---

### Step 7: Multi-Step Wizard UI

**Create**: `frontend/components/character/CharacterCreationWizard.tsx`

**Component Structure**:
```tsx
export default function CharacterCreationWizard() {
  const [step, setStep] = useState(1)
  const [characterData, setCharacterData] = useState<any>(null)
  const [dndbeyondUrl, setDndbeyondUrl] = useState('')
  const { createCharacter, parsers, isCreating, error, characterId } = useCharacterCreation()
  
  return (
    <div className="wizard-container">
      <WizardProgress currentStep={step} totalSteps={4} />
      
      {step === 1 && <Step1_UrlInput />}
      {step === 2 && <Step2_ParsingProgress />}
      {step === 3 && <Step3_SectionReview />}
      {step === 4 && <Step4_PreviewAndSave />}
    </div>
  )
}
```

**Step 1: URL Input**
```tsx
function Step1_UrlInput({ onNext, setCharacterData }) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  
  const handleFetch = async () => {
    setLoading(true)
    const response = await fetch('/api/characters/fetch', {
      method: 'POST',
      body: JSON.stringify({ url })
    })
    const data = await response.json()
    setCharacterData(data.json_data)
    onNext()
  }
  
  return (
    <div>
      <h2>Import from D&D Beyond</h2>
      <input 
        type="url"
        placeholder="https://dndbeyond.com/characters/140237850"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button onClick={handleFetch} disabled={loading}>
        {loading ? 'Fetching...' : 'Fetch Character'}
      </button>
    </div>
  )
}
```

**Step 2: Parsing Progress**
```tsx
function Step2_ParsingProgress({ parsers, isCreating }) {
  return (
    <div>
      <h2>Parsing Character Data</h2>
      {Object.values(parsers).map(parser => (
        <ParserProgressBar
          key={parser.parser}
          name={parser.parser}
          status={parser.status}
          executionTime={parser.execution_time_ms}
        />
      ))}
    </div>
  )
}

function ParserProgressBar({ name, status, executionTime }) {
  const labels = {
    core: 'Core Stats & Abilities',
    inventory: 'Inventory & Equipment',
    spells: 'Spells & Spellcasting',
    features: 'Features & Traits',
    background: 'Backstory & Personality',
    actions: 'Actions & Attacks'
  }
  
  return (
    <div className="parser-progress">
      <div className="parser-header">
        <span>{labels[name]}</span>
        {status === 'complete' && <span>{executionTime}ms</span>}
      </div>
      <div className="progress-bar">
        <div 
          className={`progress-fill status-${status}`}
          style={{ width: status === 'complete' ? '100%' : status === 'started' ? '50%' : '0%' }}
        />
      </div>
      <StatusIcon status={status} />
    </div>
  )
}
```

**Step 3: Section Review & Edit**
```tsx
function Step3_SectionReview({ character, onSave }) {
  const [activeSection, setActiveSection] = useState<string | null>(null)
  
  const sections = [
    { key: 'ability_scores', label: 'Ability Scores', component: AbilityScoresEditor },
    { key: 'combat_stats', label: 'Combat Stats', component: CombatStatsEditor },
    { key: 'inventory', label: 'Inventory', component: InventoryEditor },
    { key: 'spell_list', label: 'Spells', component: SpellListEditor },
    { key: 'action_economy', label: 'Actions & Attacks', component: ActionsEditor },
    { key: 'features_and_traits', label: 'Features & Traits', component: FeaturesEditor },
    { key: 'backstory', label: 'Backstory', component: BackstoryEditor },
    { key: 'personality', label: 'Personality', component: PersonalityEditor },
  ]
  
  return (
    <div>
      <h2>Review & Edit Character</h2>
      {sections.map(section => (
        <SectionAccordion
          key={section.key}
          isOpen={activeSection === section.key}
          onToggle={() => setActiveSection(activeSection === section.key ? null : section.key)}
          title={section.label}
        >
          <section.component
            data={character[section.key]}
            onSave={(updatedData) => handleSectionSave(section.key, updatedData)}
          />
        </SectionAccordion>
      ))}
    </div>
  )
}
```

**Step 4: Preview & Save**
```tsx
function Step4_PreviewAndSave({ character, onSave }) {
  const [saving, setSaving] = useState(false)
  
  const handleSave = async () => {
    setSaving(true)
    await fetch('/api/characters', {
      method: 'POST',
      body: JSON.stringify({ character })
    })
    setSaving(false)
    // Redirect to character page
  }
  
  return (
    <div>
      <h2>Preview Character</h2>
      <CharacterPreview character={character} />
      <button onClick={handleSave} disabled={saving}>
        {saving ? 'Saving...' : 'Save Character'}
      </button>
    </div>
  )
}
```

---

### Step 8: Section Editor Components

**Create Directory**: `frontend/components/character/editors/`

**Components to Create**:

#### 1. `AbilityScoresEditor.tsx`
```tsx
interface AbilityScoresEditorProps {
  data: AbilityScores
  onSave: (data: AbilityScores) => void
}

export default function AbilityScoresEditor({ data, onSave }) {
  const [scores, setScores] = useState(data)
  
  return (
    <div className="ability-scores-grid">
      {['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'].map(ability => (
        <AbilityScoreInput
          key={ability}
          ability={ability}
          score={scores[ability.toLowerCase()]}
          modifier={Math.floor((scores[ability.toLowerCase()] - 10) / 2)}
          onChange={(value) => setScores({ ...scores, [ability.toLowerCase()]: value })}
        />
      ))}
      <button onClick={() => onSave(scores)}>Save Changes</button>
    </div>
  )
}
```

#### 2. `InventoryEditor.tsx`
```tsx
export default function InventoryEditor({ data, onSave }) {
  const [inventory, setInventory] = useState(data)
  
  const addItem = () => {
    setInventory({
      ...inventory,
      backpack: [...inventory.backpack, { name: '', quantity: 1, weight: 0 }]
    })
  }
  
  const removeItem = (index: number) => {
    setInventory({
      ...inventory,
      backpack: inventory.backpack.filter((_, i) => i !== index)
    })
  }
  
  const updateItem = (index: number, field: string, value: any) => {
    const updated = [...inventory.backpack]
    updated[index] = { ...updated[index], [field]: value }
    setInventory({ ...inventory, backpack: updated })
  }
  
  return (
    <div>
      <h3>Equipped Items</h3>
      {Object.entries(inventory.equipped_items).map(([slot, items]) => (
        <EquippedSlot key={slot} slot={slot} items={items} />
      ))}
      
      <h3>Backpack</h3>
      {inventory.backpack.map((item, index) => (
        <ItemRow
          key={index}
          item={item}
          onUpdate={(field, value) => updateItem(index, field, value)}
          onRemove={() => removeItem(index)}
        />
      ))}
      
      <button onClick={addItem}>Add Item</button>
      <button onClick={() => onSave(inventory)}>Save Inventory</button>
    </div>
  )
}
```

#### 3. `SpellListEditor.tsx`
```tsx
export default function SpellListEditor({ data, onSave }) {
  const [spellList, setSpellList] = useState(data)
  
  const addSpell = (level: number) => {
    // Add new spell to specific level
  }
  
  const removeSpell = (className: string, level: number, spellIndex: number) => {
    // Remove spell from list
  }
  
  const updateSpellSlots = (className: string, level: number, slots: number) => {
    // Update available spell slots
  }
  
  return (
    <div>
      {Object.entries(spellList.spells).map(([className, levels]) => (
        <div key={className}>
          <h3>{className} Spells</h3>
          
          {Object.entries(levels).map(([level, spells]) => (
            <SpellLevelSection
              key={level}
              level={parseInt(level)}
              spells={spells}
              slots={spellList.spellcasting[className]?.spell_slots?.[level]}
              onAddSpell={() => addSpell(parseInt(level))}
              onRemoveSpell={(index) => removeSpell(className, parseInt(level), index)}
              onUpdateSlots={(slots) => updateSpellSlots(className, parseInt(level), slots)}
            />
          ))}
        </div>
      ))}
      
      <button onClick={() => onSave(spellList)}>Save Spells</button>
    </div>
  )
}
```

#### 4. `ActionsEditor.tsx`
```tsx
export default function ActionsEditor({ data, onSave }) {
  const [actions, setActions] = useState(data)
  
  const addAction = () => {
    setActions({
      ...actions,
      actions: [...actions.actions, createEmptyAction()]
    })
  }
  
  const removeAction = (index: number) => {
    setActions({
      ...actions,
      actions: actions.actions.filter((_, i) => i !== index)
    })
  }
  
  const updateAction = (index: number, updatedAction: CharacterAction) => {
    const updated = [...actions.actions]
    updated[index] = updatedAction
    setActions({ ...actions, actions: updated })
  }
  
  return (
    <div>
      <div>Attacks per Action: {actions.attacks_per_action}</div>
      
      <h3>Actions</h3>
      {actions.actions.map((action, index) => (
        <ActionCard
          key={index}
          action={action}
          onUpdate={(updated) => updateAction(index, updated)}
          onRemove={() => removeAction(index)}
        />
      ))}
      
      <button onClick={addAction}>Add Action</button>
      <button onClick={() => onSave(actions)}>Save Actions</button>
    </div>
  )
}
```

#### 5. `BackstoryEditor.tsx`
```tsx
export default function BackstoryEditor({ data, onSave }) {
  const [backstory, setBackstory] = useState(data)
  
  return (
    <div>
      <label>Title</label>
      <input
        value={backstory.title}
        onChange={(e) => setBackstory({ ...backstory, title: e.target.value })}
      />
      
      <label>Family History</label>
      <textarea
        value={backstory.family}
        onChange={(e) => setBackstory({ ...backstory, family: e.target.value })}
      />
      
      <label>Early Life</label>
      <textarea
        value={backstory.early_life}
        onChange={(e) => setBackstory({ ...backstory, early_life: e.target.value })}
      />
      
      <label>Defining Moment</label>
      <textarea
        value={backstory.defining_moment}
        onChange={(e) => setBackstory({ ...backstory, defining_moment: e.target.value })}
      />
      
      {/* Additional backstory sections... */}
      
      <button onClick={() => onSave(backstory)}>Save Backstory</button>
    </div>
  )
}
```

#### 6. `PersonalityEditor.tsx`
```tsx
export default function PersonalityEditor({ data, onSave }) {
  const [personality, setPersonality] = useState(data)
  
  return (
    <div>
      <label>Personality Traits</label>
      <textarea
        value={personality.traits}
        onChange={(e) => setPersonality({ ...personality, traits: e.target.value })}
      />
      
      <label>Ideals</label>
      <textarea
        value={personality.ideals}
        onChange={(e) => setPersonality({ ...personality, ideals: e.target.value })}
      />
      
      <label>Bonds</label>
      <textarea
        value={personality.bonds}
        onChange={(e) => setPersonality({ ...personality, bonds: e.target.value })}
      />
      
      <label>Flaws</label>
      <textarea
        value={personality.flaws}
        onChange={(e) => setPersonality({ ...personality, flaws: e.target.value })}
      />
      
      <button onClick={() => onSave(personality)}>Save Personality</button>
    </div>
  )
}
```

---

## Technical Architecture Details

### Backend Stack
- **FastAPI** - Async web framework
- **WebSocket** - Real-time bidirectional communication
- **asyncio.TaskGroup** - Parallel parser execution
- **httpx** - Async HTTP client for D&D Beyond API
- **SQLAlchemy** - ORM for MySQL database
- **Pydantic** - Request/response validation

### Frontend Stack
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **WebSocket API** - Native browser WebSocket
- **TailwindCSS** - Styling
- **React Hooks** - State management

### Database Schema
```sql
CREATE TABLE characters (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    race VARCHAR(100),
    character_class VARCHAR(100),
    level INT,
    data JSON NOT NULL,  -- Full Character dataclass
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
```

### Parser Architecture
- **6 Parallel Parsers**: All run simultaneously, no dependencies
- **Execution Time**: ~2.5-5.5 seconds total
- **LLM Integration**: Background and Actions parsers use async LLM calls
- **Progress Reporting**: Real-time WebSocket events for each parser

---

## User Experience Flow

### Happy Path
1. User enters D&D Beyond URL → Click "Fetch"
2. Frontend fetches JSON from backend → Success
3. Frontend opens WebSocket connection → Sends `create_character` message
4. Backend starts 6 parsers in parallel → Streams progress events
5. User sees real-time progress bars for each parser (Core → 100ms, Inventory → 150ms, etc.)
6. All parsers complete → Character dataclass created
7. Frontend displays "Parsing Complete" → Auto-advances to Step 3
8. User reviews each section in accordion UI → Makes edits as needed
9. Each section save triggers `PATCH /api/characters/{id}/{section}`
10. User clicks "Preview" → Sees final character summary
11. User clicks "Save Character" → `POST /api/characters`
12. Redirect to character page with success message

### Error Handling
- **Invalid URL**: Show error, prompt to re-enter
- **D&D Beyond API failure**: Retry with exponential backoff (3 attempts)
- **Parser failure**: Display error for specific parser, allow retry
- **WebSocket disconnect**: Auto-reconnect with progress preservation
- **Validation errors**: Inline validation messages on section editors
- **Database save failure**: Show error, allow retry, preserve draft data

---

## Open Questions for Refinement

### 1. WebSocket vs REST for Parsing
**Question**: Should parsing happen exclusively through WebSocket for progress streaming, or should we also offer a `POST /api/characters/parse` REST endpoint for testing/automation?

**Options**:
- **A**: WebSocket only (simpler, consistent UX)
- **B**: Both WebSocket and REST (more flexible, easier testing)
- **C**: REST endpoint that returns a job ID, poll for status (no WebSocket required)

**Recommendation**: Option B - WebSocket for UI, REST for testing/API consumers

---

### 2. Draft vs Final Saves
**Question**: Should the wizard support "Save Draft" functionality with a `is_draft: boolean` flag in the database, or only allow saving once all sections are validated?

**Options**:
- **A**: Draft mode enabled - User can save partial characters and resume later
- **B**: No drafts - Must complete all sections before saving
- **C**: Auto-save drafts to localStorage, only final save to database

**Recommendation**: Option C - localStorage auto-save, database for final only

---

### 3. Validation Strictness
**Question**: Should section editors enforce D&D 5e rules (e.g., max ability score 20, spell level restrictions, proficiency bonus calculations), or allow free-form editing for homebrew content?

**Options**:
- **A**: Strict D&D 5e validation - Enforce all RAW rules
- **B**: Soft validation - Warnings for rule violations, but allow override
- **C**: No validation - Free-form editing for maximum flexibility

**Recommendation**: Option B - Soft validation with homebrew toggle

---

### 4. Section Edit Scope
**Question**: Should section-by-section editing allow inline quick edits only, or full CRUD operations (add/remove spells, items, features)?

**Options**:
- **A**: Quick edits only - Text changes, number adjustments (simpler UI)
- **B**: Full CRUD - Add/remove/reorder all items (more powerful, more complex)
- **C**: Hybrid - Quick edits in Step 3, full CRUD in separate "Character Manager" tool

**Current Decision**: Option B - Full CRUD in wizard (per user request)

---

### 5. Progress Persistence
**Question**: If parsing fails mid-way (e.g., network error, LLM timeout), should we preserve partial results?

**Options**:
- **A**: Fail fast - Discard all progress, retry from scratch
- **B**: Partial results - Save completed parsers, retry failed ones
- **C**: Idempotent parsers - Each parser can run independently, merge results

**Recommendation**: Option C - Design parsers to be idempotent

---

### 6. Character Update Strategy
**Question**: When user edits sections in Step 3, should changes be:

**Options**:
- **A**: Saved immediately with `PATCH` on every field change (auto-save)
- **B**: Saved per section with explicit "Save Section" button
- **C**: Saved only at the end with "Save All Changes" in Step 4

**Current Decision**: Option B - Explicit save per section (per plan)

---

### 7. Multiclass Characters
**Question**: D&D Beyond JSON can have multiple classes. How should we handle multiclass in the wizard?

**Options**:
- **A**: Display all classes, allow editing each class's features/spells separately
- **B**: Flatten to single "primary class" for simplicity
- **C**: Show class breakdown in preview, but edit features as single list

**Recommendation**: Option A - Full multiclass support with class breakdown

---

### 8. Character Images & Assets
**Question**: D&D Beyond includes avatar URLs, decorations, and backdrops. Should we:

**Options**:
- **A**: Fetch and store images locally (requires storage setup)
- **B**: Store D&D Beyond URLs only (depends on external hosting)
- **C**: Allow custom image upload (requires file storage)
- **D**: Skip images entirely for MVP

**Recommendation**: Option B for MVP, Option C for future enhancement

---

### 9. Real-time Collaboration
**Question**: Should multiple users be able to edit the same character simultaneously?

**Options**:
- **A**: Yes - WebSocket-based real-time sync (complex)
- **B**: No - Last write wins (simple, potential data loss)
- **C**: Optimistic locking - Detect conflicts, prompt user to resolve

**Recommendation**: Option B for MVP (single-user editing)

---

### 10. Testing Strategy
**Question**: What's the testing priority for the wizard?

**Options**:
- **A**: Unit tests for parsers and API endpoints
- **B**: Integration tests for WebSocket flow
- **C**: E2E tests for full wizard user journey
- **D**: All of the above

**Recommendation**: Start with A (parser tests exist), add B for WebSocket, defer C

---

## Estimated Development Timeline

### Phase 1: Backend Foundation (Days 1-3)
- Day 1: D&D Beyond fetcher service + `/fetch` endpoint
- Day 2: Async character builder wrapper with progress callbacks
- Day 3: WebSocket endpoint for character creation

**Deliverable**: Working backend that can fetch, parse, and stream progress

---

### Phase 2: API Endpoints (Day 4)
- Add `POST /api/characters` endpoint
- Add `PUT /api/characters/{id}` endpoint
- Add `PATCH /api/characters/{id}/{section}` endpoint
- Add Pydantic schemas for validation

**Deliverable**: Complete CRUD API for characters

---

### Phase 3: Frontend Infrastructure (Days 5-6)
- Day 5: Extend WebSocketService with `createCharacter()` method
- Day 5: Create `useCharacterCreation` React hook
- Day 6: Create wizard shell with step navigation

**Deliverable**: Frontend infrastructure ready for UI components

---

### Phase 4: Wizard UI (Days 7-10)
- Day 7: Step 1 (URL input) + Step 2 (progress display)
- Day 8: Step 3 (section accordion) + Step 4 (preview/save)
- Day 9: Polish wizard flow, error handling, loading states
- Day 10: Responsive design, accessibility, UX refinements

**Deliverable**: Complete wizard navigation flow

---

### Phase 5: Section Editors (Days 11-15)
- Day 11: `AbilityScoresEditor` + `CombatStatsEditor`
- Day 12: `InventoryEditor` (with add/remove items)
- Day 13: `SpellListEditor` (with spell CRUD)
- Day 14: `ActionsEditor` + `FeaturesEditor`
- Day 15: `BackstoryEditor` + `PersonalityEditor`

**Deliverable**: Full CRUD editing for all character sections

---

### Phase 6: Testing & Polish (Days 16-18)
- Day 16: Backend unit tests (parsers, API endpoints)
- Day 17: WebSocket integration tests
- Day 18: Bug fixes, UX improvements, edge case handling

**Deliverable**: Production-ready character creation wizard

---

**Total Estimated Time**: 18 days (3.5 weeks) for single developer
**With Parallelization**: ~12 days if frontend/backend developed simultaneously

---

## Success Metrics

### Functional Requirements ✅
- [ ] User can paste D&D Beyond URL and fetch character JSON
- [ ] All 6 parsers run in parallel with progress display
- [ ] WebSocket streams real-time parsing updates
- [ ] User can edit all character sections with full CRUD
- [ ] Character saves to MySQL database with proper schema
- [ ] Multi-step wizard with clear navigation

### Performance Requirements 📊
- [ ] Character fetch from D&D Beyond < 2 seconds
- [ ] Total parsing time < 6 seconds
- [ ] WebSocket progress updates every ~500ms
- [ ] Section save (PATCH) < 500ms
- [ ] Full character save (POST) < 1 second

### User Experience Requirements 🎨
- [ ] Clear visual feedback during parsing
- [ ] Intuitive section editing with validation
- [ ] Mobile-responsive design
- [ ] Error messages guide user to resolution
- [ ] Auto-save progress to prevent data loss

---

## Future Enhancements (Post-MVP)

1. **Manual Character Creation** - Form-based builder for non-D&D Beyond users
2. **Character Templates** - Pre-built character templates for quick creation
3. **Bulk Import** - Import multiple characters from CSV/JSON
4. **Character Comparison** - Side-by-side comparison of two characters
5. **Version History** - Track character changes over time
6. **Character Sharing** - Share read-only character view via URL
7. **PDF Export** - Generate printable character sheet PDF
8. **Custom Image Upload** - User-uploaded character portraits
9. **Homebrew Content Support** - Custom races, classes, spells, items
10. **Multi-user Collaboration** - Real-time co-editing for DM/player

---

## Dependencies & Prerequisites

### Backend Dependencies
```
fastapi
uvicorn
websockets
httpx
sqlalchemy
pymysql
pydantic
python-dotenv
asyncio
```

### Frontend Dependencies
```
next
react
typescript
tailwindcss
```

### External Services
- D&D Beyond Character Service API (unofficial)
- OpenAI API (for LLM-based parsers)
- MySQL 8.0+ database

### Development Tools
- Docker (for database)
- VS Code (IDE)
- Postman/Thunder Client (API testing)

---

## Risk Assessment

### High Risk 🔴
- **D&D Beyond API reliability**: Unofficial API may break or rate limit
  - **Mitigation**: Implement retry logic, cache responses, provide manual upload fallback

### Medium Risk 🟡
- **LLM parser consistency**: Background/Actions parsers depend on LLM quality
  - **Mitigation**: Add fallback to basic text extraction if LLM fails
  
- **WebSocket connection stability**: Network issues could interrupt parsing
  - **Mitigation**: Auto-reconnect, preserve progress, allow resume from checkpoint

### Low Risk 🟢
- **Database schema changes**: Character dataclass might evolve
  - **Mitigation**: JSON column stores full data, easy to migrate
  
- **Frontend complexity**: Many editor components to build
  - **Mitigation**: Reusable component library, incremental development

---

## Conclusion

This plan provides a comprehensive roadmap for implementing a production-ready character creation wizard with:

- ✅ D&D Beyond URL import (100% reliability assumed)
- ✅ WebSocket-based real-time progress streaming
- ✅ Parallel parser execution for optimal performance
- ✅ Full CRUD editing for all character sections
- ✅ Multi-step wizard with intuitive UX
- ✅ Robust error handling and validation
- ✅ Scalable architecture for future enhancements

**Next Steps**: Review open questions, finalize technical decisions, begin Phase 1 implementation.
