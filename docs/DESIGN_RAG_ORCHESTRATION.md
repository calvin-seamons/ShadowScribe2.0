# RAG Orchestration Architecture Design

**Document Version**: 1.0  
**Date**: October 1, 2025  
**Status**: Planning

---

## Overview

This document describes the new RAG orchestration architecture that replaces the old 3-sequential-router approach with a cleaner 2-parallel-call system. The new design separates concerns properly: tool selection, entity extraction, and entity resolution are now independent, composable operations.

---

## Problem Statement

### Current Architecture (BROKEN)

```
User Query
    ↓
3 Sequential LLM Calls (wasteful & confused):
    ├─ Character Router: "Do you need character data? What entities? What search_contexts?"
    ├─ Session Notes Router: "Do you need session notes? What entities? What search_contexts?"
    └─ Rulebook Router: "Do you need rulebook? What entities? What search_contexts?"
```

**Issues**:
1. **Redundancy**: Each router extracts entities independently → inconsistent results
2. **Wasteful**: 3 sequential calls when only 1-2 tools might be needed
3. **Confused Logic**: LLM guesses `search_contexts` instead of deriving from tool selection
4. **Poor Separation**: Tool selection mixed with entity extraction mixed with intention classification

---

## New Architecture (CLEAN)

```
User Query
    ↓
2 PARALLEL LLM Calls:
    ├─ Tool & Intention Selector
    │   Returns: [
    │     {"tool": "character_data", "intention": "combat_info", "confidence": 0.95},
    │     {"tool": "session_notes", "intention": "npc_history", "confidence": 0.85}
    │   ]
    │
    └─ Entity Extractor
        Returns: [
          {"name": "Eldaryth of Regret", "confidence": 1.0},
          {"name": "Elara", "confidence": 0.9}
        ]

    ↓ (Results combined in Central Orchestrator)
    
Selected Tools: ["character_data", "session_notes"]
Intentions: {
  "character_data": "combat_info",
  "session_notes": "npc_history"
}
Entities: ["Eldaryth of Regret", "Elara"]

    ↓
    
EntitySearchEngine.resolve_entities():
    For each entity:
        Search ONLY in selected tools (character_data + session_notes)
        Skip unselected tools (rulebook not searched)
    
    Returns: {
      "Eldaryth of Regret": [
        EntitySearchResult(found_in_sections=["inventory"], confidence=1.0)
      ],
      "Elara": [
        EntitySearchResult(found_in_sections=["session_notes.npc"], confidence=0.95)
      ]
    }

    ↓
    
Execute RAG Tool Queries (parallel):
    ├─ CharacterQueryRouter.query_character(
    │     intentions=["combat_info"],
    │     entities=["Eldaryth of Regret"],
    │     auto_include_sections=["inventory"]  # From entity resolution
    │  )
    │
    └─ SessionNotesQueryRouter.query_session_notes(
          intention="npc_history",
          entities=["Elara"],
          auto_include_sections=["session_notes.npc"]  # From entity resolution
       )

    ↓
    
Context Assembler combines results
    ↓
Final Response LLM call
```

---

## Key Components

### 1. Tool & Intention Selector (New LLM Call)

**Purpose**: Single call to determine which RAG tools are needed and how each will be used

**Input**:
- User query
- Character name (context)

**Output**:
```json
{
  "tools_needed": [
    {
      "tool": "character_data",
      "intention": "combat_info",
      "confidence": 0.95
    },
    {
      "tool": "session_notes",
      "intention": "npc_history", 
      "confidence": 0.85
    }
  ]
}
```

**Tool Options**:
- `character_data`: Character stats, inventory, spells, abilities, backstory
- `session_notes`: Campaign history, past events, NPCs, decisions
- `rulebook`: D&D 5e rules, mechanics, spell descriptions, monster stats

**Intentions by Tool**:
- **character_data**: `character_basics`, `combat_info`, `abilities_info`, `inventory_info`, `magic_info`, `story_info`, `social_info`, `progress_info`
- **session_notes**: `npc_history`, `location_history`, `event_recap`, `decision_history`, `quest_status`, `combat_recap`, `character_development`
- **rulebook**: `describe_entity`, `compare_entities`, `level_progression`, `rule_mechanics`, `spell_details`, `monster_stats`, `condition_effects`, etc. (30+ intentions)

**Prompt Template**: See `CentralPromptManager.get_tool_and_intention_selector_prompt()`

---

### 2. Entity Extractor (New LLM Call)

**Purpose**: Extract all entity names mentioned in query

**Input**:
- User query

**Output**:
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

**Note**: NO `search_contexts` field! This is derived from tool selection.

**Prompt Template**: See `CentralPromptManager.get_entity_extraction_prompt()`

---

### 3. Central Orchestrator (Updated)

**Location**: `src/rag/central_engine.py` (to be created/refactored)

**Responsibilities**:
1. Make 2 parallel LLM calls (tool selector + entity extractor)
2. Combine results:
   - Map selected tools → search contexts for entities
   - Pass to EntitySearchEngine
3. Execute RAG tool queries with intentions and auto-include sections
4. Assemble final context
5. Generate final response

**Key Method**:
```python
async def process_query(
    self,
    user_query: str,
    character_name: str
) -> str:
    # 1. Parallel LLM calls
    tool_selection, entities = await asyncio.gather(
        self.llm_client.call_tool_selector(user_query, character_name),
        self.llm_client.call_entity_extractor(user_query)
    )
    
    # 2. Derive search contexts from selected tools
    selected_tools = [t["tool"] for t in tool_selection["tools_needed"]]
    
    # 3. Resolve entities ONLY in selected tools
    entity_results = self.entity_search_engine.resolve_entities(
        entities=entities["entities"],
        selected_tools=selected_tools,
        character=self.character,
        session_notes_storage=self.session_notes_storage,
        rulebook_storage=self.rulebook_storage
    )
    
    # 4. Execute RAG queries with auto-include sections
    rag_results = await self._execute_rag_queries(
        tool_selection, entity_results
    )
    
    # 5. Assemble and generate final response
    context = self.context_assembler.assemble(rag_results)
    return await self.llm_client.generate_final_response(context, user_query)
```

---

### 4. EntitySearchEngine (Updated)

**Location**: `src/rag/entity_search_engine.py`

**Changes**:
- Update `resolve_entities()` signature to accept `selected_tools` list
- Only search in tools specified in `selected_tools`
- Remove `search_contexts` parameter from entities (derived from selected_tools)

**Updated Method Signature**:
```python
def resolve_entities(
    self,
    entities: List[Dict[str, Any]],  # Just {"name": "X", "confidence": 0.95}
    selected_tools: List[str],        # ["character_data", "session_notes"]
    character: Character,
    session_notes_storage: Optional[CampaignSessionNotesStorage] = None,
    rulebook_storage: Optional[RulebookStorage] = None
) -> Dict[str, List[EntitySearchResult]]:
    """
    Resolve entities by searching ONLY in selected tools.
    
    Args:
        entities: List of entity dicts with 'name' and 'confidence'
        selected_tools: Which tools to search ('character_data', 'session_notes', 'rulebook')
        character: Character object
        session_notes_storage: Optional session notes storage
        rulebook_storage: Optional rulebook storage
    
    Returns:
        Dict mapping entity names to lists of EntitySearchResult
    """
    entity_resolution_results = {}
    
    for entity_dict in entities:
        entity_name = entity_dict.get('name', '')
        if not entity_name:
            continue
        
        all_results = []
        
        # Search character data if selected
        if 'character_data' in selected_tools:
            char_results = self.search_all_character_sections(character, entity_name)
            all_results.extend(char_results)
        
        # Search session notes if selected
        if 'session_notes' in selected_tools and session_notes_storage:
            session_result = self.search_session_notes(session_notes_storage, entity_name)
            if session_result:
                all_results.append(session_result)
        
        # Search rulebook if selected (with caching)
        if 'rulebook' in selected_tools and rulebook_storage:
            if entity_name in self._rulebook_cache:
                rulebook_results = self._rulebook_cache[entity_name]
            else:
                rulebook_results = self.search_rulebook(
                    rulebook_storage, entity_name, max_results=5
                )
                self._rulebook_cache[entity_name] = rulebook_results
            all_results.extend(rulebook_results)
        
        entity_resolution_results[entity_name] = all_results
    
    return entity_resolution_results
```

---

### 5. QueryEntity Dataclass (Updated)

**Location**: `src/rag/character/character_query_types.py`

**Changes**:
- Remove `search_contexts` field (no longer needed)
- Remove `raw_text` field (already removed, unused)
- Keep only essential fields

**Updated Definition**:
```python
@dataclass
class QueryEntity:
    """An entity referenced in a user query.
    
    Entities are resolved by searching across selected RAG tools.
    The search scope is determined by the tool selector, not the entity itself.
    """
    name: str                           # Entity name from query
    confidence: float = 1.0            # Confidence in entity recognition
    attributes: Dict[str, Any] = field(default_factory=dict)  # Optional metadata
```

---

## Data Flow Examples

### Example 1: Combat Query with Item Reference

**Query**: "What combat abilities do I have tied to Eldaryth of Regret?"

**Step 1 - Tool & Intention Selector**:
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

**Step 2 - Entity Extractor**:
```json
{
  "entities": [
    {"name": "Eldaryth of Regret", "confidence": 1.0}
  ]
}
```

**Step 3 - Entity Resolution** (search ONLY in character_data):
```python
{
  "Eldaryth of Regret": [
    EntitySearchResult(
      found_in_sections=["inventory"],
      match_confidence=1.0,
      matched_text="Eldaryth of Regret"
    )
  ]
}
```

**Step 4 - Execute RAG Query**:
```python
CharacterQueryRouter.query_character(
    intentions=["combat_info"],
    entities=["Eldaryth of Regret"],
    auto_include=["inventory"]  # Auto-included because entity found here
)
# Returns: combat_stats + action_economy + inventory (with Eldaryth)
```

---

### Example 2: Multi-Tool Query

**Query**: "Remind me who Elara is and what persuasion abilities I have"

**Step 1 - Tool & Intention Selector**:
```json
{
  "tools_needed": [
    {
      "tool": "session_notes",
      "intention": "npc_history",
      "confidence": 0.9
    },
    {
      "tool": "character_data",
      "intention": "abilities_info",
      "confidence": 0.95
    }
  ]
}
```

**Step 2 - Entity Extractor**:
```json
{
  "entities": [
    {"name": "Elara", "confidence": 1.0},
    {"name": "persuasion", "confidence": 0.8}
  ]
}
```

**Step 3 - Entity Resolution** (search in session_notes + character_data):
```python
{
  "Elara": [
    EntitySearchResult(
      found_in_sections=["session_notes.npc"],
      match_confidence=0.95,
      matched_text="Elara (NPC)"
    )
  ],
  "persuasion": [
    EntitySearchResult(
      found_in_sections=["proficiencies"],
      match_confidence=0.85,
      matched_text="Persuasion (skill)"
    )
  ]
}
```

**Step 4 - Execute RAG Queries** (parallel):
```python
# Query 1: Session Notes
SessionNotesQueryRouter.query_session_notes(
    intention="npc_history",
    entities=["Elara"],
    auto_include=["session_notes.npc"]
)

# Query 2: Character Data
CharacterQueryRouter.query_character(
    intentions=["abilities_info"],
    entities=["persuasion"],
    auto_include=["proficiencies"]
)
```

---

### Example 3: Rules + Character Query

**Query**: "How does grappling work and what's my athletics bonus?"

**Step 1 - Tool & Intention Selector**:
```json
{
  "tools_needed": [
    {
      "tool": "rulebook",
      "intention": "rule_mechanics",
      "confidence": 1.0
    },
    {
      "tool": "character_data",
      "intention": "abilities_info",
      "confidence": 1.0
    }
  ]
}
```

**Step 2 - Entity Extractor**:
```json
{
  "entities": [
    {"name": "grappling", "confidence": 1.0},
    {"name": "athletics", "confidence": 1.0}
  ]
}
```

**Step 3 - Entity Resolution** (search in rulebook + character_data):
```python
{
  "grappling": [
    EntitySearchResult(
      found_in_sections=["rulebook.combat.grappling_rules"],
      match_confidence=1.0,
      matched_text="Grappling"
    ),
    EntitySearchResult(
      found_in_sections=["proficiencies"],
      match_confidence=0.7,
      matched_text="Athletics (used for grappling)"
    )
  ],
  "athletics": [
    EntitySearchResult(
      found_in_sections=["proficiencies"],
      match_confidence=1.0,
      matched_text="Athletics"
    )
  ]
}
```

**Step 4 - Execute RAG Queries** (parallel):
```python
# Query 1: Rulebook
RulebookQueryRouter.query_rulebook(
    intention="rule_mechanics",
    entities=["grappling"],
    auto_include=["rulebook.combat.grappling_rules"]
)

# Query 2: Character Data
CharacterQueryRouter.query_character(
    intentions=["abilities_info"],
    entities=["athletics"],
    auto_include=["proficiencies"]
)
```

---

## Implementation Plan

### Phase 1: Update Data Models (2 hours)
1. Remove `search_contexts` field from `QueryEntity`
2. Update `EntitySearchEngine.resolve_entities()` signature
3. Update tests for new entity structure

### Phase 2: Create New LLM Prompts (3 hours)
1. Create `get_tool_and_intention_selector_prompt()`
2. Create `get_entity_extraction_prompt()`
3. Remove old router prompts (character, session_notes, rulebook)
4. Test prompts with GPT-4 to validate outputs

### Phase 3: Refactor Central Orchestrator (4 hours)
1. Create/refactor `CentralEngine` class
2. Implement parallel LLM calls (asyncio.gather)
3. Implement tool selection → search context derivation
4. Update entity resolution flow
5. Update RAG query execution with auto-include

### Phase 4: Update EntitySearchEngine (2 hours)
1. Modify `resolve_entities()` to accept `selected_tools`
2. Add tool filtering logic (skip unselected tools)
3. Update tests for new behavior

### Phase 5: Update Query Routers (3 hours)
1. Update `CharacterQueryRouter` to use new entity format
2. Update `SessionNotesQueryRouter` (if exists)
3. Update `RulebookQueryRouter` (if exists)
4. Remove old router prompt handling

### Phase 6: Integration & Testing (4 hours)
1. End-to-end integration test
2. Test all example queries from this doc
3. Performance benchmarking (should be faster!)
4. Update documentation

**Total Estimated Time**: 18 hours (~2-3 days)

---

## Benefits Summary

### Performance
✅ **50% fewer LLM calls** (2 parallel instead of 3 sequential)  
✅ **Faster response time** (parallel execution)  
✅ **Reduced token usage** (no redundant entity extraction)

### Code Quality
✅ **Proper separation of concerns** (tool selection ≠ entity extraction)  
✅ **Simpler logic** (no search_contexts guessing)  
✅ **Easier to test** (each component independent)  
✅ **More maintainable** (clear data flow)

### Functionality
✅ **Contextual intention selection** (LLM knows why each tool is needed)  
✅ **Efficient entity resolution** (only search selected tools)  
✅ **Consistent entity extraction** (single source of truth)  
✅ **Better auto-include logic** (entity resolution tied to tool selection)

---

## Migration Strategy

### Backward Compatibility
**Breaking Changes Accepted**: This is a major refactor with no backward compatibility.

### Migration Steps
1. Create new prompt templates
2. Update entity dataclass (remove fields)
3. Refactor `EntitySearchEngine.resolve_entities()`
4. Create new `CentralEngine` orchestrator
5. Delete old router prompt methods
6. Update all integration points
7. **Let things fail!** Fix issues as they arise

### Testing Strategy
1. Unit tests for each component
2. Integration tests for full flow
3. Example query validation (from this doc)
4. Performance benchmarking vs old system

---

## Open Questions

1. **Async vs Sync**: Should we use asyncio for parallel calls or threading?
   - Recommendation: asyncio (better for I/O-bound LLM calls)

2. **Error Handling**: What if tool selector fails but entity extractor succeeds?
   - Recommendation: Fail fast, require both calls to succeed

3. **Caching Strategy**: Should we cache tool selection results?
   - Recommendation: No, queries are unique. Keep rulebook entity cache only.

4. **Confidence Thresholds**: Minimum confidence for tool selection?
   - Recommendation: 0.7 for tools, 0.6 for entities (configurable)

5. **Partial Results**: What if entity found in unselected tool?
   - Recommendation: Ignore it. Only search selected tools (by design).

6. **Multi-Location Entities**: What if entity found in multiple tools/sections?
   - Recommendation: **Use all of them!** Pass entity to every RAG tool where it was found.
   - Example: "grappling" found in both `rulebook.combat` and `proficiencies` → include in both RAG queries
   - This provides richer context and better answers

---

## Entity Resolution: Multi-Location Handling

### Philosophy
**Entities found in multiple locations are GOOD, not a problem.** Each location provides different context that enriches the final response.

### Examples

#### Example 1: "Grappling" in Multiple Places
```python
entity_results = {
  "grappling": [
    EntitySearchResult(found_in_sections=["rulebook.combat.grappling_rules"], confidence=1.0),
    EntitySearchResult(found_in_sections=["proficiencies"], confidence=0.7)
  ]
}

# Result: Pass "grappling" to BOTH RAG queries
RulebookQueryRouter.query_rulebook(
    intention="rule_mechanics",
    entities=["grappling"],
    auto_include=["rulebook.combat.grappling_rules"]
)

CharacterQueryRouter.query_character(
    intentions=["abilities_info"],
    entities=["grappling"],
    auto_include=["proficiencies"]
)

# Final context includes:
# - Rulebook: How grappling works mechanically
# - Character: Character's athletics bonus and grappling proficiency
# = Complete answer!
```

#### Example 2: "Eldritch Blast" in Multiple Places
```python
entity_results = {
  "Eldritch Blast": [
    EntitySearchResult(found_in_sections=["spell_list"], confidence=1.0),
    EntitySearchResult(found_in_sections=["features_and_traits"], confidence=0.85),  # Agonizing Blast
    EntitySearchResult(found_in_sections=["rulebook.spellcasting"], confidence=0.9)
  ]
}

# Result: Pass to ALL three
CharacterQueryRouter.query_character(
    intentions=["magic_info"],
    entities=["Eldritch Blast"],
    auto_include=["spell_list", "features_and_traits"]  # Both character sections
)

RulebookQueryRouter.query_rulebook(
    intention="spell_details",
    entities=["Eldritch Blast"],
    auto_include=["rulebook.spellcasting"]
)

# Final context includes:
# - Character spell list: Character knows this spell
# - Character features: Agonizing Blast invocation adds CHA to damage
# - Rulebook: Full spell description and mechanics
# = Complete picture of character's Eldritch Blast capability
```

### Implementation Pattern

```python
def _distribute_entities_to_rag_queries(
    self,
    entity_results: Dict[str, List[EntitySearchResult]],
    tool_selection: List[Dict]
) -> Dict[str, List[str]]:
    """
    Distribute entities to RAG queries based on where they were found.
    
    An entity can appear in multiple RAG query inputs if found in multiple tools.
    
    Returns:
        Dict mapping tool names to lists of entity names for that tool
        Example: {
            "character_data": ["Eldritch Blast", "grappling"],
            "rulebook": ["Eldritch Blast", "grappling"]
        }
    """
    tool_entities = {}
    
    for entity_name, results in entity_results.items():
        for result in results:
            # Determine which tool this section belongs to
            tool = self._section_to_tool(result.get_primary_section())
            
            if tool not in tool_entities:
                tool_entities[tool] = []
            
            # Add entity to this tool's entity list (duplicates are fine)
            if entity_name not in tool_entities[tool]:
                tool_entities[tool].append(entity_name)
    
    return tool_entities
```

### Benefits of Multi-Location Entities

1. **Richer Context**: Each location provides different perspective on the entity
2. **Better Answers**: LLM has complete information from all relevant sources
3. **Natural Synthesis**: Final LLM naturally combines information from multiple sources
4. **No Information Loss**: Don't discard valuable matches due to arbitrary priority rules

### Anti-Pattern: Don't Filter!

❌ **Bad**: Choose one location and discard others
```python
# DON'T DO THIS
if len(results) > 1:
    # Pick highest confidence and discard rest
    best_result = max(results, key=lambda r: r.match_confidence)
    return [best_result]
```

✅ **Good**: Use all locations
```python
# DO THIS
# Return all results and let RAG queries use what's relevant
return results  # All of them!
```

---

## Success Criteria

- [ ] 2 parallel LLM calls replace 3 sequential calls
- [ ] Entity extraction happens once (not 3x)
- [ ] Entity resolution only searches selected tools
- [ ] All example queries work correctly
- [ ] Performance improved (lower latency, fewer tokens)
- [ ] Code is cleaner and more maintainable
- [ ] Tests pass for all components

---

## Document Changelog

- **v1.0** (2025-10-01): Initial design document created

---

**Next Steps**: Review this design with team, get approval, begin Phase 1 implementation.
