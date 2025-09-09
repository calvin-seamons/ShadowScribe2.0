# Goal: Convert character sheet markdown (e.g. `knowledge_base/ceej10_125292496.md`) into populated insta## Error Handling & Recovery
- **Network failures**: Exponential backoff (1s, 2s, 4s) with 3 retry attempts per task.
- **JSON validation fails**: Retry with enhanced prompt including the validation error message.
- **Partial results**: Accept partially populated dataclasses; missing fields trigger gap-fill prompts.
- **Conflicting extractions**: Log conflicts for manual review; use first successful extraction as default.
- **Timeout handling**: Individual task timeout of 30 seconds; overall pipeline timeout of 5 minutes. of the dataclasses in `src/rag/## OCR Handling Considerations
- **Inconsistent formatting**: Tables may have varying column alignments, missing borders, or merged cells.
- **Text recognition errors**: Expect OCR artifacts like "0" instead of "O", missing characters, extra spaces.
- **Layout variations**: Same information may appear in different locations across different character sheets.
- **Incomplete data**: Some fields may be genuinely missing or illegible - handle gracefully with null values.
- **Unit normalization**: Standardize weight units ("lb.", "lb", "pounds" → "lb") and other measurements.acter/character_types.py` by orchestrating multiple parallel LLM API calls, each focused on extracting a specific character type/component.

## Guiding Principles
1. **Parallel extraction**: Run multiple LLM calls concurrently, each targeting a specific dataclass or component (e.g. `CharacterBase`, `AbilityScores`, `Inventory`, etc.).
2. **OCR-tolerant prompts**: Design prompts that can handle OCR inconsistencies, formatting variations, and partial information.
3. **JSON schema enforcement**: Each LLM call outputs structured JSON matching the target dataclass schema with validation and retry logic.
4. **Aggregation layer**: Merge all parallel extraction results into a single `Character` instance with conflict resolution.
5. **Gap filling**: After initial parallel extraction, identify missing/incomplete fields and run targeted follow-up prompts.r Extraction Strategy (Markdo## OCR-Tolerant Prompt Design
- **Format flexibility**: Prompts handle tables with inconsistent delimiters (`|`, spaces, alignment issues).
- **Missing information**: Each prompt explicitly handles "not found" cases with null/default values.
- **Context clues**: Use surrounding text and page layout hints when direct values are unclear.
- **Fuzzy matching**: Look for approximate matches ("STR", "Strength", "STRENGTH") rather than exact strings.
- **Validation prompts**: Include examples of valid/invalid outputs in system messages.>## LLM Prompt Templates

### Template Structure (All Tasks)
```
System: You are extracting D&D character data from OCR'd markdown. Output ONLY valid JSON matching the schema. Use null for missing values.

Schema: [specific dataclass schema]

User: [entire markdown document]

Extract [specific component] information and return JSON only.
```

### Example Prompts
1. **CharacterBase Extraction**:
   - Find character name, race/species, class, level, background, alignment
   - Handle variations: "Mountain Dwarf", "Dwarf (Mountain)", "Species: Mountain Dwarf"

2. **Inventory Extraction**:
   - Extract all equipment, weapons, magical items with quantities and weights
   - Parse attuned items separately
   - Handle weight formats: "5 lb.", "5 lb", "5 pounds"

3. **Spell Extraction**:
   - Extract spell lists by level, including cantrips
   - Parse spell components (V/S/M), duration, range
   - Handle spell slot information

4. **Features Extraction**:
   - Parse all features, feats, racial traits, class abilities
   - Extract usage limitations (per long rest, per day, etc.)
   - Categorize by source (racial, class, feat)es via Incremental LLM Calls)

Goal: Convert character sheet markdown (e.g. `knowledge_base/ceej10_125292496.md`) into populated instances of the dataclasses in `src/rag/character/character_types.py` by orchestrating multiple small, reliable LLM + heuristic passes instead of one giant prompt.

## Guiding Principles
1. Deterministic first: prefer regex / structural parsing for obvious tables (spells, inventory) before invoking an LLM.
2. Narrow prompts: each LLM call extracts a single semantic slice (e.g. Core Identity, Passive Scores, One Inventory Row Batch, etc.).
3. JSON schema every time: enforce target fragment shape; reject / retry on validation failure.
4. Idempotent merges: each pass patches a partial `Character` object in storage (dict / pydantic model) with provenance metadata.
5. Diff + gap fill loop: after all passes, run a “missing fields auditor” prompt listing unset / suspicious values and request only those.

## Proposed Pipeline Phases
| Phase | Purpose | Inputs | Outputs |
| ----- | ------- | ------ | ------- |
| 0 Load & Segment | Split markdown by page & detect section headings | Raw MD | Page objects w/ tags |
| 1 Core Identity | Name, class, level, race/species, background, alignment | Pages 1–3 heuristics | `CharacterBase` |
| 2 Ability & Combat | Passive scores table, HP (if present), AC, initiative, speed | Page 1 + textual lines | `AbilityScores`, `CombatStats`, `PassiveScores` |
| 3 Features/Traits | Feats, racial traits, class features w/ recharge & action type | Feature sections | `FeaturesAndTraits` (populated lists) |
| 4 Inventory | Two-column equipment table; attuned items | Inventory table | `Inventory` (items w/ weights) |
| 5 Spells Overview | Spellcasting ability, DC, attack bonus | Early feature text | `SpellcastingInfo` base |
| 6 Spell Tables | Extract spells level-by-level (structured rows) | Spell tables | `SpellList.spells` |
| 7 Organizations & Notes | Narrative / “Organizations” page fragments | Page 4 etc. | `organizations`, `notes` |
| 8 QA & Gap Fill | Identify missing / inconsistent fields | Aggregated model | Patch list + final model |

## Parallel Execution Strategy
- **Concurrent calls**: Launch all 12 extraction tasks simultaneously using async/threading.
- **Full context**: Each LLM call receives the entire markdown document to handle OCR inconsistencies.
- **Token management**: Cap each call at ~2000 input tokens, ~500 output tokens.
- **Task independence**: Each extraction task operates independently - no dependencies between tasks.
- **Retry logic**: Failed tasks retry up to 3 times with exponential backoff.

## Data Structures (Working Layer)
```python
ExtractionResult = {
  "task_id": str,
  "target_type": str,  # e.g. "CharacterBase", "Inventory"
  "status": "pending|running|completed|failed",
  "result": dict,  # JSON matching target dataclass schema
  "confidence": float,
  "retry_count": int,
  "errors": List[str]
}

CharacterAggregate = {
  "extraction_results": Dict[str, ExtractionResult],
  "merged_character": Character,  # Final merged result
  "conflicts": List[Dict],  # Field conflicts to resolve
  "missing_fields": List[str]  # Fields needing gap-fill prompts
}
```

## Heuristic Extraction Targets
- Tables delimited by `|` — parse via splitting; map header variants (e.g. `HIT`, `DAMAGE/TYPE`).
- Feat / trait bullets: lines starting with `* ` up to blank line → classify (feat vs racial vs class) by keyword presence (e.g. “PHB”, “TCoE”, “EGIW”, known race feature names).
- Spell slot summary lines like `=== 3rd LEVEL === | 3 Slots OOO` → slot count.

## LLM Prompt Patterns (Sketch)
1. Core Identity Prompt:
   - System: “Extract ONLY the JSON matching schema ...”
   - User: Provide relevant page snippet.
   - Schema: `{ "name": str, "race": str, "character_class": str, "total_level": int, "background": str, "alignment": str }`.
2. Feature Normalization Prompt:
   - Input: Bullet lines chunk.
   - Output schema: list of `{ name, description, action_type, uses, recharge, source, category }`.
3. Spell Row Clarifier (fallback): For ambiguous parsed row, send original line + header mapping, ask LLM to return normalized `{ level, name, school?, casting_time, range, components:{v,s,m}, duration, tags:[...] }`.
4. Gap Auditor Prompt: Provide serialized partial character + list of unset critical fields; ask for JSON list of suggestions or “[]”.

## Validation & Merging
1. Parse LLM JSON → pydantic (or dataclass constructor) → on failure: one retry with stricter instructions.
2. For conflicting fields (e.g. `alignment` differing): keep first, append conflict record to `errors` for manual review.
3. Normalize enumerations (e.g. action types) via lookup table before assignment.

## Error Handling & Recovery
- Timeout / network: exponential backoff (3 tries) then log task as Stalled.
- Validation fail: Retry with appended “Previous output invalid because: ... produce corrected JSON only.”
- Hallucination guard: If value not present in snippet (simple substring scan ignoring case) and not in an allowlist (derived stats), drop it.

## Performance / Cost Controls
- Cache hash(page_fragment_text + prompt_type) → response.
- Prefer heuristic extraction for tables; only ambiguous cells go to LLM.
- Consolidate minor features into single prompt when under token limit.

## Suggested Module Layout
```
src/rag/character/extraction/
  prompts.py          # LLM prompt templates for each dataclass
  extractors.py       # Individual extraction functions (T1-T12)
  parallel_runner.py  # Async execution of all extraction tasks
  merger.py           # Combine extraction results into Character
  validator.py        # JSON schema validation & retry logic
  orchestrator.py     # Main pipeline coordinator
  schemas.py          # Pydantic schemas mirroring character_types.py
  gap_filler.py       # Follow-up prompts for missing fields
```

## Incremental Development Order
1. **Setup schemas**: Create Pydantic schemas mirroring all character_types.py dataclasses.
2. **Core extractors**: Implement T1-T4 (CharacterBase, PhysicalCharacteristics, AbilityScores, CombatStats).
3. **Parallel runner**: Build async execution framework for running multiple LLM calls concurrently.
4. **Merger logic**: Implement aggregation of extraction results into final Character object.
5. **Advanced extractors**: Add T5-T12 (remaining dataclass extractors).
6. **Gap filler**: Implement follow-up prompts for missing/incomplete fields.
7. **End-to-end testing**: Test with sample markdown files and validate complete Character objects.

## Testing Strategy
- Unit: Each heuristic parser with controlled markdown snippets.
- Contract: Round-trip extraction → serialized JSON must instantiate `Character` without exception.
- Regression: Snapshot of final JSON for sample file; diff tolerance only allows additive feature lists.

## Open Questions / Assumptions
- No raw numeric ability scores appear in sample; may require additional OCR sources later.
- Some feature descriptions truncated by layout; plan for later “detail enrichment” pass querying rulebook RAG.
- Weight units are consistently `lb .` (normalize to `lb`).

## Next Action Recommendation
Start by implementing the parallel extraction framework (schemas, extractors T1-T4, parallel runner) to prove the concurrent approach works, then scale to remaining extractors.
