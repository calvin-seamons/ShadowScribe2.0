# Entity Resolution System Design

## Problem Statement

Currently, the LLM router classifies entities with a type (e.g., "Eldaryth of Regret" as `feature`), but this classification is often incorrect. When the LLM misclassifies an entity, the character query router fails to include the relevant data section, causing incomplete responses.

### Current Flow (Broken)
```
User Query: "What actions are tied to Eldaryth of Regret?"
    ↓
LLM Router: Classifies as 'feature' entity
    ↓
Character Router: Uses 'abilities_info' intention → only returns features_and_traits
    ↓
Problem: Eldaryth is a weapon in inventory, but inventory wasn't included!
```

### Core Issue
**We're asking the LLM to classify entities WITHOUT giving it access to the actual character data.** The LLM has no way to know if "Eldaryth of Regret" is a weapon, spell, feature, or something else.

---

## Proposed Solution: Context-Based Entity Search

Instead of relying on LLM entity type classification, we should:

1. **LLM identifies entity names and search contexts** (not types)
2. **Character router searches all relevant sections** based on context
3. **Fuzzy matching finds the actual entity** in character data
4. **Automatically include that section** in the response

### New Flow
```
User Query: "What actions are tied to Eldaryth of Regret?"
    ↓
LLM Router: 
  - Entity: "Eldaryth of Regret"
  - Search contexts: ['character_data', 'session_notes']  
  - Intention: 'abilities_info'
    ↓
Character Router (NEW BEHAVIOR):
  1. Search inventory for "Eldaryth of Regret" → FOUND (weapon)
  2. Search features_and_traits for "Eldaryth of Regret" → NOT FOUND
  3. Search spell_list for "Eldaryth of Regret" → NOT FOUND
  4. Auto-include inventory because entity was found there
  5. Also include abilities_info data per intention
    ↓
Response: Contains both inventory (weapon details) AND abilities (how to use it)
```

---

## Design Proposal: Search Context System

### 1. LLM Router Output Changes

**Current Schema:**
```json
{
  "entities": [
    {"name": "Eldaryth of Regret", "type": "feature"}  // ❌ Type is often wrong
  ]
}
```

**Proposed Schema:**
```json
{
  "entities": [
    {
      "name": "Eldaryth of Regret",
      "search_contexts": ["character_data"],  // Where to look
      "confidence": 0.9
    }
  ]
}
```

### 2. Search Context Types

The LLM would choose from these search contexts:

- **`character_data`** - Search all character sections (inventory, spells, features, etc.)
- **`session_notes`** - Search campaign history
- **`rulebook`** - Search D&D rules
- **`all`** - Search everywhere (default when uncertain)

### 3. Character Router Behavior

```python
# Pseudo-code for new behavior
def query_character(intentions, entities):
    # Step 1: Get data for intentions
    intention_data = extract_data_for_intentions(intentions)
    
    # Step 2: For each entity, search character data
    for entity in entities:
        if 'character_data' in entity.search_contexts:
            # Search ALL character sections with fuzzy matching
            found_in_sections = search_all_character_sections(entity.name)
            
            # Step 3: Auto-include sections where entity was found
            for section in found_in_sections:
                if section not in intention_data:
                    intention_data[section] = get_section_data(section)
                    
    return intention_data
```

### 4. Entity Search Algorithm

```python
def search_all_character_sections(entity_name, fuzzy_threshold=0.75):
    """Search all character sections for an entity by name."""
    found_in = []
    
    # Define searchable sections and their data structures
    search_map = {
        'inventory': lambda: search_inventory(entity_name),
        'spell_list': lambda: search_spells(entity_name),
        'features_and_traits': lambda: search_features(entity_name),
        'proficiencies': lambda: search_proficiencies(entity_name),
        'allies': lambda: search_allies(entity_name),
        'enemies': lambda: search_enemies(entity_name),
        'organizations': lambda: search_organizations(entity_name),
        'objectives_and_contracts': lambda: search_objectives(entity_name)
    }
    
    for section_name, search_func in search_map.items():
        if search_func():  # Found match
            found_in.append(section_name)
    
    return found_in
```

---

## Clarifying Questions

### Architecture Questions

**Q1: Should entity resolution happen BEFORE or AFTER intention mapping?**

Option A: Search first, then map intentions
```python
# Resolve entities first
resolved_entities = resolve_all_entities(entities)
# Then map intentions
intention_data = map_intentions(intentions)
# Merge them
return merge(intention_data, resolved_entities)
```

Option B: Map intentions first, then search and expand
```python
# Get intention data first
intention_data = map_intentions(intentions)
# Search for entities and auto-expand
expanded_data = search_and_expand(intention_data, entities)
return expanded_data
```

**Recommendation: Option B** - It's more efficient and maintains backward compatibility.

---

**Q2: Should we search ALL sections or only "likely" sections based on intention?**

Option A: Always search all sections (comprehensive but slower)
```python
search_sections = ['inventory', 'spell_list', 'features_and_traits', ...]  # All sections
```

Option B: Search only sections related to the intention (faster but might miss things)
```python
if intention == 'magic_info':
    search_sections = ['spell_list', 'features_and_traits']  # Magic-related only
elif intention == 'combat_info':
    search_sections = ['inventory', 'features_and_traits', 'spell_list']  # Combat-related
```

Option C: Hybrid - Search intention-related sections first, then all sections if not found
```python
# Try targeted search first
results = search_targeted_sections(entity, intention)
if not results:
    # Fallback to comprehensive search
    results = search_all_sections(entity)
```

**Question: Which approach fits our use case better?**

---

**Q3: How aggressive should fuzzy matching be?**

Current threshold: `0.6` (60% similarity)

Scenarios:
- "Eldaryth of Regret" vs "Eldaryth of Regrett" → 0.98 similarity ✅
- "Eldaryth" vs "Eldaryth of Regret" → 0.65 similarity ⚠️
- "longsword" vs "Eldaryth of Regret (Longsword)" → 0.35 similarity ❌

**Options:**
- **High threshold (0.8+)**: Fewer false positives, might miss partial matches
- **Medium threshold (0.6-0.8)**: Balanced, current setting
- **Low threshold (0.4-0.6)**: More matches, more false positives
- **Dynamic threshold**: Adjust based on entity name length or context

**Question: What's the acceptable false positive vs false negative trade-off?**

---

**Q4: Should we search by partial name matches?**

Example: User asks about "Eldaryth" (short form)

Option A: Only fuzzy match on full name
```python
# "Eldaryth" vs "Eldaryth of Regret" → No exact match
# Check fuzzy → 0.65 similarity → Maybe match?
```

Option B: Support partial name matching explicitly
```python
# Check if "Eldaryth" appears in "Eldaryth of Regret" → YES, match!
```

Option C: Use both approaches with priority
```python
# 1. Try exact match
# 2. Try partial substring match
# 3. Try fuzzy match
# Return first match found
```

**Recommendation: Option C** - Provides best user experience.

---

### Implementation Questions

**Q5: Where should entity resolution logic live?**

Option A: In `CharacterQueryRouter` (current location)
- ✅ Centralized with other query logic
- ❌ Mixes routing with entity resolution concerns

Option B: In `EntityMatcher` class (expand its role)
- ✅ Single responsibility - all entity logic in one place
- ✅ Easier to test and reuse
- ❌ EntityMatcher becomes more complex

Option C: New `EntityResolver` class
- ✅ Clean separation of concerns
- ✅ Can be used by multiple routers
- ❌ Another class to maintain

**Question: What's the best separation of concerns?**

---

**Q6: Should entity resolution cache results?**

Within a single query, we might search for the same entity multiple times:
- Once in character router
- Once in session notes router
- Once for validation

Option A: Cache entity resolutions per query
```python
self.entity_cache = {}  # Reset per query
result = self.entity_cache.get(entity_name) or resolve_entity(entity_name)
```

Option B: Don't cache - re-search each time
- Simpler, no cache invalidation issues
- Slower for repeated searches

**Question: Is the performance gain worth the complexity?**

---

**Q7: What should happen when an entity is found in multiple sections?**

Example: "Hexblade's Curse" might appear in:
- `features_and_traits` (class feature)
- `spell_list` (if it has spell-like properties)
- `action_economy` (action type)

Option A: Include ALL sections where found
```python
return ['features_and_traits', 'spell_list', 'action_economy']
```

Option B: Include only the "primary" section (first match)
```python
return ['features_and_traits']  # First match wins
```

Option C: Include sections based on intention priority
```python
if intention == 'magic_info':
    prefer 'spell_list' over 'features_and_traits'
elif intention == 'abilities_info':
    prefer 'features_and_traits' over 'spell_list'
```

**Question: Should we prioritize breadth (all sections) or precision (best section)?**

---

### User Experience Questions

**Q8: Should we show debug info about entity resolution to users?**

Option A: Detailed debug output
```
🔍 Entity Resolution:
   • "Eldaryth of Regret" found in inventory (0.98 match)
   • Auto-included inventory section
```

Option B: Only show when entities aren't found
```
⚠️ Could not find "Eldarth of Regert" in character data
   Did you mean "Eldaryth of Regret"?
```

Option C: No debug output - silent resolution

**Question: How much transparency do users want/need?**

---

**Q9: How should we handle misspellings and typos?**

Example: User types "Eldarth of Regert"

Option A: Best-effort fuzzy match with no feedback
```python
# Silently match to "Eldaryth of Regret" if similarity > threshold
```

Option B: Match and inform user
```python
# Match and show: "Found 'Eldaryth of Regret' (did you mean this?)"
```

Option C: Ask for confirmation on low-confidence matches
```python
# If similarity < 0.8, show options:
# "Did you mean: Eldaryth of Regret, or Moonblade?"
```

**Question: Should fuzzy matching be silent or interactive?**

---

**Q10: Should the LLM be allowed to override search contexts?**

Scenario: User asks "What spells does Duskryn know?"
- LLM might only set `search_contexts: ['character_data']`
- But we know the intention is `magic_info`, so we should search `spell_list`

Option A: LLM search contexts are advisory only
```python
# Always search based on intention first
# Use LLM search contexts as expansion hints
```

Option B: LLM search contexts are mandatory
```python
# Only search where LLM tells us to
# Might miss data if LLM is wrong
```

Option C: Hybrid - combine both signals
```python
search_locations = set(intention_sections + llm_search_contexts)
```

**Question: How much should we trust the LLM's search context suggestions?**

---

## Implementation Phases

### Phase 1: Update LLM Router Prompts ⚡ QUICK WIN
- Change prompt to return `search_contexts` instead of `type`
- Support both old and new schemas during transition
- **Effort:** 1-2 hours

### Phase 2: Enhance Entity Search in Character Router 🔧 CORE CHANGE
- Implement comprehensive search across all character sections
- Add fuzzy matching with configurable threshold
- Auto-include sections where entities are found
- **Effort:** 4-6 hours

### Phase 3: Add Entity Resolution Caching (Optional) 🚀 OPTIMIZATION
- Cache entity lookups within a query
- Add performance metrics
- **Effort:** 2-3 hours

### Phase 4: User Feedback & Iteration 🔍 POLISH
- Add debug output for entity resolution
- Handle misspellings gracefully
- Provide "did you mean?" suggestions
- **Effort:** 3-4 hours

---

## Success Metrics

How do we know if this design is working?

1. **Accuracy**: Entities are found in correct sections 95%+ of the time
2. **Completeness**: All relevant sections included when entity is found
3. **Performance**: Entity resolution adds <50ms to query time
4. **User Satisfaction**: Users get complete answers without needing to rephrase

---

## Open Questions for Discussion

1. Should entity resolution be synchronous or async?
2. Should we pre-build an entity index on character load?
3. How do we handle entities that exist in session notes but not character data?
4. Should character data take priority over session notes when both match?
5. Do we need different fuzzy thresholds for different entity types?

---

## Next Steps

1. **Answer clarifying questions** (see above)
2. **Choose implementation approach** based on answers
3. **Create test cases** for entity resolution
4. **Implement Phase 1** (LLM prompt changes)
5. **Implement Phase 2** (entity search enhancement)
6. **Test with real queries** (like "Eldaryth of Regret")
7. **Iterate based on results**

---

## Related Files

- `/src/rag/character/character_query_router.py` - Main router logic
- `/src/rag/character/entity_matcher.py` - Existing entity matching utilities
- `/src/rag/central_prompt_manager.py` - LLM prompt generation
- `/src/rag/character/character_query_types.py` - Type definitions

---

**Document Status:** Draft for Review
**Created:** October 2025
**Last Updated:** October 2025
