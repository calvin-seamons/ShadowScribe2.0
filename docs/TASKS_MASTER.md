# ShadowScribe 2.0 - Master Implementation Tasks

**Status**: In Progress  
**Start Date**: October 1, 2025  
**Target Completion**: 20 hours (2-3 days)  

---

## Executive Summary

This document consolidates all remaining tasks to complete the new RAG orchestration architecture. The new system replaces:
1. **Old**: 3 sequential LLM router calls (character, session notes, rulebook)
2. **New**: 2 parallel LLM calls (tool selector + entity extractor)

**Key Documents**:
- Architecture Design: [docs/DESIGN_RAG_ORCHESTRATION.md](DESIGN_RAG_ORCHESTRATION.md)
- Legacy Entity Search Tasks: [docs/TASKS_ENTITY_SEARCH_LEGACY.md](TASKS_ENTITY_SEARCH_LEGACY.md)
- RAG Orchestration Tasks: [docs/TASKS_RAG_ORCHESTRATION.md](TASKS_RAG_ORCHESTRATION.md)

---

## Justification: Why This Refactor?

### The Problem with the Old System

**Architecture**: 3 Sequential LLM Router Calls
```
User Query
    ↓
CharacterQueryRouter LLM call: "Need character data? Extract entities, guess search_contexts"
    ↓ (wait for response)
SessionNotesQueryRouter LLM call: "Need session notes? Extract entities, guess search_contexts"
    ↓ (wait for response)
RulebookQueryRouter LLM call: "Need rulebook? Extract entities, guess search_contexts"
    ↓
Combine results
```

**Critical Flaws**:
1. **Wasteful**: All 3 LLM calls happen even if only 1 tool needed (67% waste on simple queries)
2. **Redundant**: Each router extracts entities independently → inconsistent results
3. **Sequential Bottleneck**: Must wait for each call to complete (3x latency)
4. **Confused Logic**: LLM guesses `search_contexts` per entity instead of deriving from tool selection
5. **Poor Separation**: Tool selection + entity extraction + intention classification all mixed together

**Real-World Impact**:
- Simple query "What's my AC?" → 3 LLM calls (only needs character_data)
- Complex query "What spells do I have?" → 3 redundant entity extractions for same entities
- Average query latency: 6-9 seconds (3 sequential calls)
- Token waste: ~3000 tokens per query (2/3 often unnecessary)

### The Entity Search Journey

**Phase 1-3.5 Completed** (70% of entity search implementation):
- ✅ Created `EntitySearchEngine` with unified search across all data sources
- ✅ Implemented 3-strategy matching (exact, substring, fuzzy)
- ✅ Character data entity search complete
- ✅ Session notes entity search complete
- ✅ Rulebook entity search complete
- ✅ Consolidated 3 separate modules into 1 unified class (~767 lines eliminated)

**Why Continue?**: This work is the foundation! The entity search system is solid. We just need to integrate it properly with the new architecture.

### The New Architecture Solution

**Architecture**: 2 Parallel LLM Calls
```
User Query
    ↓
asyncio.gather([Tool Selector, Entity Extractor])  ← PARALLEL
    ├─ Tool Selector: Returns tools needed + intentions
    └─ Entity Extractor: Returns entity names only
    ↓ (both complete simultaneously)
Combine results → derive search_contexts from selected tools
    ↓
EntitySearchEngine.resolve_entities(entities, selected_tools)  ← Uses our Phase 1-3.5 work!
    ↓
Execute RAG queries in parallel for selected tools only
```

**Benefits**:
1. **50% Fewer LLM Calls**: 2 instead of 3 (33% reduction)
2. **Faster Execution**: Parallel calls eliminate sequential bottleneck (estimated 40-60% latency reduction)
3. **No Redundancy**: Single entity extraction, consistent results
4. **Proper Logic**: search_contexts derived from tool selection (not guessed)
5. **Clean Separation**: Tool selection ≠ entity extraction ≠ intention classification
6. **Token Savings**: Simple queries only call necessary tools (estimated 30-50% token reduction)

**The Path Forward**: Phase 1-3.5 built the engine. Phases 1-6 connect it to the new orchestrator.

---

## Progress Overview

### Completed Work (Foundation)
- ✅ **Entity Search System** (Phase 1-3.5): 19/27 tasks complete
  - EntitySearchEngine created and tested
  - Character, session notes, rulebook search implemented
  - 3-strategy matching working
  - Consolidated into single unified class

### Remaining Work (Integration)
- [x] **Phase 1**: Update Data Models (2 hours) - 4/4 tasks ✅ **COMPLETE**
- [ ] **Phase 2**: Create New LLM Prompts (3 hours) - 1/3 tasks ✅ In Progress
- [ ] **Phase 3**: Refactor Central Orchestrator (4 hours) - 0/5 tasks
- [ ] **Phase 4**: Finalize EntitySearchEngine (2 hours) - 0/4 tasks
- [ ] **Phase 5**: Update Query Routers (3 hours) - 0/3 tasks
- [ ] **Phase 6**: Integration & Testing (4 hours) - 0/4 tasks
- [ ] **Phase 7**: Polish from Legacy Tasks (2 hours) - 0/5 tasks

**Total**: 5/28 tasks complete | Estimated: ~16.5 hours remaining

---

## Phase 1: Update Data Models (2 hours)

### Task 1.1: Update QueryEntity Dataclass ✅
**File**: `src/rag/character/character_query_types.py`  
**Time**: 15 min  
**Status**: ✅ Complete

**Actions**:
- [x] Remove `search_contexts` field from `QueryEntity` dataclass
- [x] Remove unused `attributes` field from `QueryEntity` dataclass
- [x] Verify only fields remaining: `name`, `confidence`
- [x] Update docstring to explain search scope determined by tool selector
- [x] Verify no syntax errors

**Completion Notes**:
- Time taken: 20 minutes
- Removed search_contexts and attributes fields (both unused)
- Verified fields: ['name', 'confidence'] ✅
- Docstring updated to reference new architecture
- No syntax errors, imports work correctly

**Why**: The new architecture derives search contexts from tool selection, not per-entity LLM guessing.

---

### Task 1.2: Update EntitySearchEngine Signature ✅
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ✅ Complete

**Actions**:
- [x] Update `resolve_entities()` method signature - added `selected_tools` parameter
- [x] Remove any references to `search_contexts` in entity dicts
- [x] Update docstring with new parameter descriptions
- [x] Keep all internal search methods unchanged (no changes needed)

**New Signature**:
```python
def resolve_entities(
    self,
    entities: List[Dict[str, Any]],  # Just {"name": "X", "confidence": 0.95}
    selected_tools: List[str],        # ["character_data", "session_notes", "rulebook"]
    character: Character,
    session_notes_storage: Optional[CampaignSessionNotesStorage] = None,
    rulebook_storage: Optional[RulebookStorage] = None
) -> Dict[str, List[EntitySearchResult]]:
```

**Completion Notes**:
- Time taken: 30 minutes
- Verified signature: ['self', 'entities', 'selected_tools', 'character', 'session_notes_storage', 'rulebook_storage'] ✅
- Docstring updated with tool-based filtering explanation
- Also completed Task 1.3 tool filtering logic implementation

**Why**: Tool selection determines which data sources to search, not individual entity properties.

---

### Task 1.3: Implement Tool Filtering Logic ✅
**File**: `src/rag/entity_search_engine.py`  
**Time**: 45 min  
**Status**: ✅ Complete (done with Task 1.2)

**Actions**:
- [x] Update `resolve_entities()` body to check `selected_tools` before searching
- [x] Add conditional logic for character_data, session_notes, rulebook
- [x] Keep existing search methods unchanged
- [x] Add inline comments explaining tool filtering

**Implementation**:
- Replaced complex SearchContext enum checking with simple `if 'tool_name' in selected_tools`
- Removed dependency on SearchContext enum from resolve_entities
- Clean, readable conditional logic for each data source

**Completion Notes**:
- Time taken: Completed simultaneously with Task 1.2 (~15 additional minutes)
- All three tool filters implemented: character_data, session_notes, rulebook
- Removed redundant SearchContext checks
- Code is cleaner and more maintainable

**Why**: Efficiency! Only search data sources the LLM selected as relevant.

---

### Task 1.4: Find and Update Existing Callers ✅
**Files**: Any files calling `resolve_entities()`  
**Time**: 30 min  
**Status**: ✅ Complete

**Actions**:
- [x] Search for all calls to `resolve_entities()`: Found 1 caller in `character_query_router.py`
- [x] Update each caller to pass `selected_tools` parameter
- [x] Temporary compatibility: Pass `["character_data", "session_notes", "rulebook"]` (search all)
- [x] Clean up legacy code: Removed unused `EntityType` and `SearchContext` imports
- [x] Clean up legacy code: Removed obsolete `_expand_by_entity_matches()` method
- [x] Verify no syntax errors: `python -c "from src.rag.character.character_query_router import CharacterQueryRouter"`

**Completion Notes**:
- Time taken: 30 minutes
- Updated `character_query_router.py` line 170 to include `selected_tools` parameter
- Removed legacy imports: `EntityType`, `SearchContext` (no longer exist in new architecture)
- Deleted obsolete method: `_expand_by_entity_matches()` (relied on removed EntityType enum)
- All imports successful, no syntax errors ✅
- Clean deletion following project philosophy: break things cleanly, fix properly

**Note**: This is temporary. Phase 3 will replace these calls with proper tool selection.

**Why**: Maintain working system while we build the new orchestrator.

---

## Phase 2: Create New LLM Prompts (3 hours)

### Task 2.1: Create Tool & Intention Selector Prompt ✅
**File**: `src/rag/central_prompt_manager.py`  
**Time**: 90 min  
**Status**: ✅ Complete

**Actions**:
- [x] Create new method: `get_tool_and_intention_selector_prompt(user_query: str, character_name: str) -> str`
- [x] Define prompt structure with all 3 tools and their intentions
- [x] Provide 5 examples for common query types
- [x] Specify JSON output format
- [x] Test prompt with real LLM: `python -m scripts.test_tool_selector_prompt`

**Completion Notes**:
- Time taken: 90 minutes
- Created comprehensive prompt with 3 tools: character_data, session_notes, rulebook
- **Dynamically injects intentions** from CharacterPromptHelper, SessionNotesPromptHelper, RulebookPromptHelper
- Intentions automatically stay in sync with type system definitions
- Added 5 example query/response pairs
- Tested with 6 diverse queries - all returned valid JSON ✅
- Tool selection accuracy: 100% across all test cases
- Intention mapping: Correct for all queries (uses actual definitions from helpers)
- Handles both single-tool and multi-tool queries properly

**Test Results**:
- "What's my AC?" → character_data (combat_info) ✅
- "What combat abilities tied to Eldaryth?" → character_data (combat_info) ✅
- "Who is Elara and my persuasion?" → session_notes (npc_history) + character_data (abilities_info) ✅
- "How does grappling work and my athletics?" → rulebook (rule_mechanics) + character_data (abilities_info) ✅
- "What spells can I cast?" → character_data (magic_info) ✅
- "Tell me about my weapon" → character_data (inventory_info) ✅

**Expected Output Format**:
```json
{
  "tools_needed": [
    {
      "tool": "character_data",
      "intention": "combat_info",
      "confidence": 0.95
    }
  ]
}
```

**Intentions to Document**:
- **character_data**: `character_basics`, `combat_info`, `abilities_info`, `inventory_info`, `magic_info`, `story_info`, `social_info`, `progress_info`
- **session_notes**: `npc_history`, `location_history`, `event_recap`, `decision_history`, `quest_status`, `combat_recap`, `character_development`
- **rulebook**: `describe_entity`, `compare_entities`, `level_progression`, `rule_mechanics`, `spell_details`, etc.

**Why**: Single call to determine all tools needed + how each will be used = efficiency + context.

---

### Task 2.2: Create Entity Extraction Prompt
**File**: `src/rag/central_prompt_manager.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create new method: `get_entity_extraction_prompt(user_query: str) -> str`
- [ ] Define prompt structure:
  - Explain entity types: character names, item names, spell names, NPC names, location names, rule terms
  - Provide extraction guidelines (exact names, confidence scoring)
  - Specify JSON output format (no `search_contexts` field!)
  - Add 5-10 example queries with expected entities
- [ ] Test prompt with real LLM: `python -m scripts.test_entity_extractor_prompt`

**Expected Output Format**:
```json
{
  "entities": [
    {
      "name": "Eldaryth of Regret",
      "confidence": 1.0
    },
    {
      "name": "Hexblade's Curse",
      "confidence": 0.95
    }
  ]
}
```

**Why**: Simple, focused prompt = better entity extraction. No confusion with tool selection.

---

### Task 2.3: Remove Old Router Prompts
**File**: `src/rag/central_prompt_manager.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Search for old router prompt methods: `grep_search "router_prompt"`
- [ ] Identify methods to delete:
  - `get_character_router_prompt()` (or similar)
  - `get_session_notes_router_prompt()` (or similar)
  - `get_rulebook_router_prompt()` (or similar)
- [ ] **Delete** these methods entirely (no commenting out!)
- [ ] Search for any calls to deleted methods and remove them
- [ ] Verify imports still work: `python -c "from src.rag.central_prompt_manager import CentralPromptManager"`

**Why**: Clean codebase = maintainable codebase. Old routers are obsolete.

---

## Phase 3: Refactor Central Orchestrator (4 hours)

### Task 3.1: Review/Create CentralEngine Class
**File**: `src/rag/central_engine.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Check if `central_engine.py` exists: `ls src/rag/central_engine.py`
- [ ] If exists, read and review current structure
- [ ] If not exists, create new file with basic structure:
  - Import dependencies: `asyncio`, `LLMClient`, `EntitySearchEngine`, `CharacterQueryRouter`, etc.
  - Define `CentralEngine` class
  - Add `__init__` method with all required components
  - Add placeholder `process_query()` method
- [ ] Document the class purpose and architecture

**Basic Structure** (if creating new):
```python
class CentralEngine:
    """Central orchestrator for RAG queries using 2-parallel-call architecture."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        prompt_manager: CentralPromptManager,
        entity_search_engine: EntitySearchEngine,
        character_query_router: CharacterQueryRouter,
        session_notes_query_router: Optional[SessionNotesQueryRouter] = None,
        rulebook_query_router: Optional[RulebookQueryRouter] = None,
        context_assembler: Optional[ContextAssembler] = None
    ):
        # Store components
        pass
    
    async def process_query(
        self,
        user_query: str,
        character_name: str
    ) -> str:
        # To be implemented in next tasks
        pass
```

**Why**: Central orchestrator is the brain of the new system.

---

### Task 3.2: Implement Parallel LLM Calls
**File**: `src/rag/central_engine.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Add async helper method: `_call_tool_selector(user_query, character_name)`
- [ ] Add async helper method: `_call_entity_extractor(user_query)`
- [ ] Implement parallel execution in `process_query()`:
  - Use `asyncio.gather()` to call both methods
  - Handle JSON parsing for both responses
  - Add error handling for failed LLM calls
  - Add JSON repair if parsing fails
- [ ] Test with example query

**Implementation Pattern**:
```python
async def process_query(self, user_query: str, character_name: str) -> str:
    # 1. Parallel LLM calls
    tool_selection_raw, entities_raw = await asyncio.gather(
        self._call_tool_selector(user_query, character_name),
        self._call_entity_extractor(user_query)
    )
    
    # 2. Parse JSON responses (with repair if needed)
    tool_selection = self._parse_json_with_repair(tool_selection_raw)
    entities = self._parse_json_with_repair(entities_raw)
    
    # Continue in next task...
```

**Why**: Parallel calls = 40-60% faster than sequential. This is the performance win!

---

### Task 3.3: Implement Entity Resolution Flow
**File**: `src/rag/central_engine.py`  
**Time**: 45 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Extract selected tools from tool selection response
- [ ] Call `entity_search_engine.resolve_entities()` with:
  - `entities` from entity extractor
  - `selected_tools` from tool selector
  - Character, session notes storage, rulebook storage
- [ ] Store entity resolution results for next step
- [ ] Log entity resolution results in debug mode

**Implementation**:
```python
# 3. Derive search contexts from selected tools
selected_tools = [t["tool"] for t in tool_selection["tools_needed"]]

# 4. Resolve entities ONLY in selected tools
entity_results = self.entity_search_engine.resolve_entities(
    entities=entities["entities"],
    selected_tools=selected_tools,
    character=self.character,
    session_notes_storage=self.session_notes_storage,
    rulebook_storage=self.rulebook_storage
)
```

**Why**: This is where our Phase 1-3.5 work pays off! EntitySearchEngine does the heavy lifting.

---

### Task 3.4: Implement Entity Distribution to RAG Queries
**File**: `src/rag/central_engine.py`  
**Time**: 45 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create helper method: `_distribute_entities_to_rag_queries(entity_results, tool_selection)`
- [ ] Implement logic to:
  - Map entity search results to RAG tools
  - Create dict of tool → entity list
  - Handle multi-location entities (include in all relevant tools)
- [ ] Create helper method: `_section_to_tool(section_name)` to map sections to tools
- [ ] Test with entities found in multiple places

**Implementation**:
```python
def _distribute_entities_to_rag_queries(
    self,
    entity_results: Dict[str, List[EntitySearchResult]],
    tool_selection: List[Dict]
) -> Dict[str, List[str]]:
    """Map entities to tools based on where they were found.
    
    Multi-location entities are GOOD - they're passed to all relevant tools.
    """
    tool_entities = {}
    
    for entity_name, results in entity_results.items():
        for result in results:
            tool = self._section_to_tool(result.get_primary_section())
            
            if tool not in tool_entities:
                tool_entities[tool] = []
            
            if entity_name not in tool_entities[tool]:
                tool_entities[tool].append(entity_name)
    
    return tool_entities
```

**Why**: Multi-location entities provide richer context. Use them all!

---

### Task 3.5: Implement RAG Query Execution
**File**: `src/rag/central_engine.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create method: `_execute_rag_queries(tool_selection, entity_distribution, entity_results)`
- [ ] For each selected tool, call appropriate query router:
  - `CharacterQueryRouter.query_character()`
  - `SessionNotesQueryRouter.query_session_notes()` (if exists)
  - `RulebookQueryRouter.query_rulebook()` (if exists)
- [ ] Pass intentions, entities, and auto-include sections to each router
- [ ] Execute queries in parallel if possible
- [ ] Collect all results in a dict

**Implementation Pattern**:
```python
async def _execute_rag_queries(
    self,
    tool_selection: List[Dict],
    entity_distribution: Dict[str, List[str]],
    entity_results: Dict[str, List[EntitySearchResult]]
) -> Dict[str, Any]:
    results = {}
    
    for tool_info in tool_selection["tools_needed"]:
        tool = tool_info["tool"]
        intention = tool_info["intention"]
        entities = entity_distribution.get(tool, [])
        
        if tool == "character_data":
            results["character_data"] = self.character_query_router.query_character(
                intentions=[intention],
                entities=entities,
                auto_include=self._extract_auto_include_sections(entities, entity_results, tool)
            )
        elif tool == "session_notes" and self.session_notes_query_router:
            results["session_notes"] = self.session_notes_query_router.query_session_notes(
                intention=intention,
                entities=entities,
                auto_include=self._extract_auto_include_sections(entities, entity_results, tool)
            )
        elif tool == "rulebook" and self.rulebook_query_router:
            results["rulebook"] = self.rulebook_query_router.query_rulebook(
                intention=intention,
                entities=entities,
                auto_include=self._extract_auto_include_sections(entities, entity_results, tool)
            )
    
    return results
```

**Why**: Auto-include sections from entity resolution = better context for RAG queries.

---

## Phase 4: Finalize EntitySearchEngine (2 hours)

### Task 4.1: Verify Tool Filtering Implementation
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Review `resolve_entities()` method from Phase 1.3
- [ ] Verify tool filtering logic is working correctly
- [ ] Test with different `selected_tools` combinations:
  - `["character_data"]` - should only search character
  - `["session_notes", "rulebook"]` - should skip character
  - `["character_data", "session_notes", "rulebook"]` - should search all
- [ ] Create manual test script: `scripts/test_entity_search_filtering.py`
- [ ] Run tests and verify output

**Why**: Critical that we don't search unnecessary data sources.

---

### Task 4.2: Add Section-to-Tool Mapping Helper
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create helper method: `get_tool_from_section(section_name: str) -> str`
- [ ] Map section names to tools:
  - Character sections (inventory, spell_list, etc.) → `"character_data"`
  - Session notes sections → `"session_notes"`
  - Rulebook sections → `"rulebook"`
- [ ] Add comprehensive docstring with examples
- [ ] Test with various section names

**Implementation**:
```python
def get_tool_from_section(self, section_name: str) -> str:
    """Map a section name to its parent tool.
    
    Examples:
        "inventory" -> "character_data"
        "session_notes.npc" -> "session_notes"
        "rulebook.combat.grappling" -> "rulebook"
    """
    if section_name.startswith("rulebook."):
        return "rulebook"
    elif section_name.startswith("session_notes."):
        return "session_notes"
    else:
        return "character_data"  # Default for character sections
```

**Why**: Central Orchestrator needs this for entity distribution.

---

### Task 4.3: Optimize Rulebook Caching
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Review existing `_rulebook_cache` implementation
- [ ] Add cache size limit (e.g., max 100 entities)
- [ ] Implement LRU cache eviction policy (use `functools.lru_cache` or manual dict)
- [ ] Add cache statistics tracking (hits/misses)
- [ ] Add method to clear cache if needed
- [ ] Test with multiple queries to verify caching works

**Why**: Rulebook searches can be slow. Caching prevents redundant work.

---

### Task 4.4: Add Entity Resolution Debug Logging
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Add debug logging to `resolve_entities()`:
  - Log which tools are being searched
  - Log how many results found per entity
  - Log cache hits/misses for rulebook
  - Log total resolution time
- [ ] Use Python's `logging` module (not print statements)
- [ ] Add optional `debug` parameter to enable verbose logging
- [ ] Test with verbose logging enabled

**Why**: Debugging and performance monitoring. Essential for optimization.

---

## Phase 5: Update Query Routers (3 hours)

### Task 5.1: Update CharacterQueryRouter
**File**: `src/rag/character/character_query_router.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Review current `query_character()` method signature
- [ ] Ensure accepts new entity format (just entity names, no `search_contexts` field)
- [ ] Update `auto_include` parameter handling:
  - Accept list of section names from entity resolution
  - Merge with intention-based sections
  - Avoid duplicates
- [ ] Remove old `_resolve_entities()` method if it still references old entity format
- [ ] Test with example query

**Why**: Router must work with new entity format from Central Orchestrator.

---

### Task 5.2: Create/Update SessionNotesQueryRouter
**File**: `src/rag/session_notes/session_notes_query_router.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Check if `SessionNotesQueryRouter` exists
- [ ] If not, create new router class with `query_session_notes()` method
- [ ] Ensure method accepts:
  - `intention` (string)
  - `entities` (list of entity names)
  - `auto_include` (list of section names)
- [ ] Implement query logic (similar to CharacterQueryRouter pattern):
  - Map intention to session note sections
  - Include auto-include sections
  - Return formatted context
- [ ] Test with session notes example

**Why**: Session notes need their own router for proper intention handling.

---

### Task 5.3: Create/Update RulebookQueryRouter
**File**: `src/rag/rulebook/rulebook_query_router.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Check if `RulebookQueryRouter` exists
- [ ] If not, create new router class with `query_rulebook()` method
- [ ] Ensure method accepts:
  - `intention` (string)
  - `entities` (list of entity names)
  - `auto_include` (list of section names)
- [ ] Implement query logic:
  - Use `RulebookStorage.search()` with entity names
  - Filter by auto-include sections if provided
  - Map intention to rulebook categories
  - Format results for context assembler
- [ ] Test with rulebook example

**Why**: Rulebook needs its own router for proper intention handling.

---

## Phase 6: Integration & Testing (4 hours)

### Task 6.1: Create Integration Test Suite
**File**: `tests/test_central_engine_integration.py`  
**Time**: 90 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create test file with pytest fixtures
- [ ] Implement 3 test cases from design doc:
  - **Test 1**: "What combat abilities do I have tied to Eldaryth of Regret?"
  - **Test 2**: "Remind me who Elara is and what persuasion abilities I have"
  - **Test 3**: "How does grappling work and what's my athletics bonus?"
- [ ] Mock LLM responses for tool selector and entity extractor
- [ ] Verify entity resolution produces expected results
- [ ] Verify RAG queries called with correct parameters
- [ ] Verify final context includes all expected data
- [ ] Run tests: `python -m pytest tests/test_central_engine_integration.py -v`

**Why**: Automated tests catch regressions and validate core functionality.

---

### Task 6.2: End-to-End Manual Testing
**File**: `scripts/test_rag_orchestration.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create manual test script using real LLM calls (not mocked)
- [ ] Load test character from saved_characters
- [ ] Test with command: `python -m scripts.test_rag_orchestration "Character Name" "Query"`
- [ ] Run all 3 example queries from design doc
- [ ] Run additional test queries:
  - "What's my AC?"
  - "What spells can I cast?"
  - "Tell me about my weapon"
- [ ] Verify outputs are sensible and complete
- [ ] Check logs for proper tool selection and entity resolution
- [ ] Document any issues found

**Why**: Real LLM calls reveal issues mocks miss. Essential for production readiness.

---

### Task 6.3: Performance Benchmarking
**File**: `scripts/benchmark_rag_system.py`  
**Time**: 45 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create benchmark script to compare old vs new system (if old system still exists)
- [ ] Measure metrics:
  - Total LLM calls per query
  - Total tokens used per query
  - End-to-end latency (seconds)
  - Entity resolution time (ms)
- [ ] Run 10 diverse test queries and average results
- [ ] Document performance in a table
- [ ] Update design doc with actual benchmark results
- [ ] Target validation: 50% reduction in LLM calls, 30%+ faster execution

**Why**: Quantify the improvement. Data justifies the refactor.

---

### Task 6.4: Update Documentation
**Files**: `docs/DESIGN_RAG_ORCHESTRATION.md`, `README.md`  
**Time**: 45 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Update design doc with actual implementation notes
- [ ] Add performance benchmark results to design doc
- [ ] Document any deviations from original plan
- [ ] Update README with new architecture overview
- [ ] Add usage examples for CentralEngine
- [ ] Create migration guide (if needed for external consumers)
- [ ] Update copilot-instructions.md if architecture changes affect development patterns

**Why**: Documentation is the gift to your future self (and teammates).

---

## Phase 7: Polish & Remaining Legacy Tasks (2 hours)

These tasks come from the legacy entity search implementation (Phase 4-6 of old tasks).

### Task 7.1: Implement Multi-Strategy Matching Verification
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Verify 3-stage matching is working correctly:
  1. Exact match (case-insensitive) → confidence = 1.0
  2. Substring match (partial name) → confidence = 0.9
  3. Fuzzy similarity match → confidence = similarity score
- [ ] Add test cases for each strategy
- [ ] Document strategy priority in code comments

**Why**: Already implemented, just need verification.

---

### Task 7.2: Add Dynamic Threshold Adjustment (Optional)
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Consider adjusting fuzzy threshold based on entity name length:
  - Short names (< 5 chars): threshold = 0.9
  - Medium names (5-15 chars): threshold = 0.75
  - Long names (> 15 chars): threshold = 0.65
- [ ] Implement if useful, skip if current thresholds work well
- [ ] Document threshold logic

**Why**: May improve matching accuracy, but test first to see if needed.

---

### Task 7.3: Add Debug Output for Entity Resolution
**File**: `src/rag/central_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Add optional `debug` flag to `process_query()` method
- [ ] Output entity resolution results when debug=True
- [ ] Show which sections were auto-included
- [ ] Show match confidence scores
- [ ] Format output cleanly (use JSON or tables)

**Why**: Debugging and transparency. Helps understand system behavior.

---

### Task 7.4: Add "Did You Mean?" Suggestions (Optional)
**File**: `src/rag/entity_search_engine.py`  
**Time**: 30 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] When entity not found, find closest matches
- [ ] Return top 3 suggestions with confidence scores
- [ ] Add to EntitySearchResult or create new result type
- [ ] Include in final response (e.g., "Did you mean: 'Eldritch Blast'?")

**Why**: Better UX when user misspells entity names.

---

### Task 7.5: Create Comprehensive Entity Search Tests
**File**: `tests/test_entity_search.py`  
**Time**: 60 min  
**Status**: ⬜ Not Started

**Actions**:
- [ ] Create test file with pytest fixtures
- [ ] Test exact name matches
- [ ] Test fuzzy matches with typos
- [ ] Test partial name matches
- [ ] Test entity not found cases
- [ ] Test entity found in multiple sections
- [ ] Test all search strategies (exact, substring, fuzzy)
- [ ] Use actual character data for tests
- [ ] Run tests: `python -m pytest tests/test_entity_search.py -v`

**Why**: EntitySearchEngine is critical. Needs comprehensive test coverage.

---

## Testing Checklist

### Unit Tests
- [ ] QueryEntity dataclass tests
- [ ] EntitySearchEngine.resolve_entities() with different selected_tools
- [ ] EntitySearchEngine 3-strategy matching tests
- [ ] Tool selector prompt parsing tests
- [ ] Entity extractor prompt parsing tests
- [ ] Entity distribution logic tests
- [ ] Section-to-tool mapping tests

### Integration Tests
- [ ] End-to-end query flow with mocked LLM
- [ ] All 3 example queries from design doc
- [ ] Multi-location entity handling
- [ ] Error handling (failed LLM calls, missing storage)
- [ ] Parallel LLM call execution

### Manual Tests
- [ ] Real LLM calls with test character
- [ ] Edge cases (no entities, no tools selected, all tools selected)
- [ ] Performance vs old system (if comparable)
- [ ] Logging and debugging output
- [ ] Various query types (combat, magic, story, rules)

---

## Cleanup Tasks

### Post-Implementation Cleanup
- [ ] Delete any temporary test scripts created during development
- [ ] Remove old router prompt methods (done in Phase 2)
- [ ] Clean up any commented-out code
- [ ] Remove unused imports across all files
- [ ] Run linter: `pylint src/rag/`
- [ ] Format code: `black src/rag/` (if using Black)
- [ ] Update .gitignore if needed

---

## Important Reminders

### Development Workflow
1. **Always activate virtual environment first**: `.\.venv\Scripts\Activate.ps1`
2. **Use module execution**: `python -m scripts.script_name`
3. **Test incrementally**: Don't wait until end to test
4. **Multi-location entities are GOOD**: Don't filter, use all locations
5. **Let things fail**: Don't over-engineer error handling upfront
6. **No backward compatibility**: Break things cleanly, fix properly

### Common Pitfalls
- Forgetting to update all callers of `resolve_entities()`
- Not passing `selected_tools` parameter
- Trying to maintain backward compatibility (don't!)
- Over-caching (only cache rulebook entities)
- Not testing with real LLM calls
- Mixing sync and async code incorrectly

### Dependencies Between Phases
- **Phase 2** requires **Phase 1** (new entity format)
- **Phase 3** requires **Phase 1 & 2** (data models + prompts)
- **Phase 4** can happen in parallel with **Phase 3**
- **Phase 5** requires **Phase 3** (orchestrator must be ready)
- **Phase 6** requires **Phases 1-5** (everything must be integrated)
- **Phase 7** can happen anytime after **Phase 6**

---

## Success Criteria

### Definition of Done
- [ ] All 28 tasks completed (Phases 1-7)
- [ ] All tests passing (unit, integration, manual)
- [ ] Performance benchmark shows improvement over old system
- [ ] No errors in any files
- [ ] Documentation updated (design doc, README, copilot-instructions)
- [ ] Code reviewed and cleaned up
- [ ] Old router prompts deleted
- [ ] Multi-location entities working correctly
- [ ] 2 parallel LLM calls replacing 3 sequential calls

### Key Metrics (Targets)
- **LLM Calls**: 2 parallel (was 3 sequential) ✅ 33% reduction
- **Latency**: <50% of old system (40-60% faster)
- **Token Usage**: <70% of old system (30-50% savings)
- **Code Quality**: Cleaner, more maintainable, better separation of concerns
- **Test Coverage**: >80% for new components

---

## Timeline

### Estimated Schedule (20 hours over 2-3 days)
- **Day 1**: Phase 1 + Phase 2 (5 hours)
  - Morning: Update data models
  - Afternoon: Create new LLM prompts
- **Day 2**: Phase 3 + Phase 4 (6 hours)
  - Morning: Build Central Orchestrator
  - Afternoon: Finalize EntitySearchEngine
- **Day 3**: Phase 5 + Phase 6 + Phase 7 (9 hours)
  - Morning: Update Query Routers
  - Afternoon: Integration & Testing
  - Evening: Polish & Documentation

### Checkpoints
- **After Phase 1**: Data models updated, no syntax errors, all imports work
- **After Phase 2**: New prompts tested with real LLM, JSON output valid
- **After Phase 3**: Central orchestrator working with example query end-to-end
- **After Phase 4**: Entity search filtering verified with all tool combinations
- **After Phase 5**: All routers updated and tested individually
- **After Phase 6**: Full system tested, benchmarked, documented
- **After Phase 7**: All polish tasks complete, system production-ready

---

## Related Documents

- **Architecture Design**: [docs/DESIGN_RAG_ORCHESTRATION.md](DESIGN_RAG_ORCHESTRATION.md)
- **Legacy Entity Search**: [docs/TASKS_ENTITY_SEARCH_LEGACY.md](TASKS_ENTITY_SEARCH_LEGACY.md)
- **RAG Orchestration Tasks**: [docs/TASKS_RAG_ORCHESTRATION.md](TASKS_RAG_ORCHESTRATION.md)
- **Project Instructions**: [.github/copilot-instructions.md](../.github/copilot-instructions.md)

---

**Last Updated**: October 1, 2025  
**Next Review**: After Phase 3 completion  
**Status**: Ready to begin Phase 1
