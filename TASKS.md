# Multi-Intention Character Router Support - Task Breakdown

## Overview
Add support for multiple intentions in character queries to handle complex two-part questions like "What are my spells and inventory?" while maintaining strict LLM prompt control to prevent overuse.

## Current State Analysis
- Character router currently accepts single `user_intention: str`
- LLM Router Output uses `user_intention: Optional[str]` (singular)
- Character Query Router processes one intention at a time
- All related types and processing logic assume single intention

## Task Breakdown

### Task 1: Update Core Type Definitions (5 minutes)
**File**: `src/rag/central_engine.py`
- [ ] Modify `CharacterLLMRouterOutput` dataclass:
  - Change `user_intention: Optional[str]` to `user_intentions: List[str]`
  - Add validation property to ensure max 2 intentions
- [ ] Add type validation method `validate_intentions_count()`

### Task 2: Update Character Query Router Interface (15 minutes)
**File**: `src/rag/character/character_query_router.py`
- [ ] Modify `query_character()` method signature:
  - Change `user_intention: str` to `user_intentions: List[str]`
  - Add validation for max 2 intentions (raise ValueError if more)
- [ ] Update method docstring with new parameter description
- [ ] Update `CharacterQueryResult.metadata` to store `intentions` (plural)
- [ ] Modify the main method logic to handle intention list:
  - Loop through intentions for enum conversion and validation
  - Collect all mappings for the provided intentions
  - Merge required_fields and optional_fields from all mappings
  - Update performance metrics to track multiple intentions

### Task 3: Update Character Query Types for Multi-Intention Support (5 minutes)
**File**: `src/rag/character/character_query_types.py`
- [ ] Add helper method to `IntentionDataMapper` class:
  - `combine_mappings()` to merge multiple `IntentionMapping` objects
  - Merge required_fields, optional_fields, entity_types from all mappings
  - Set `calculation_required` or `aggregation_required` if any mapping has them
  - Return combined `IntentionMapping` with merged data requirements

### Task 4: Update LLM Prompt for Strict Multi-Intention Control (10 minutes)
**File**: `src/rag/central_prompt_manager.py`
- [ ] Modify `get_character_router_prompt()` method:
  - Update JSON schema to use `user_intentions: string[]`
  - Add strict validation rules in prompt:
    - "CRITICAL: Only return multiple intentions for two-part questions"
    - "Single concepts should use ONE intention only"
    - "Maximum 2 intentions allowed - never return more"
    - "Examples of valid multi-intention: 'show my spells and inventory', 'what are my combat stats and abilities'"
- [ ] Add examples section with single vs multi-intention cases

### Task 5: Update Central Engine Execution Logic (10 minutes)
**File**: `src/rag/central_engine.py`
- [ ] Modify `_execute_character_router()` method:
  - Change parameter access from `output.user_intention` to `output.user_intentions`
  - Add validation that intentions list isn't empty when `is_needed=true`
  - Update debug logging to show intention count
- [ ] Modify `_make_character_router_llm_call()` method:
  - Update JSON parsing to expect `user_intentions` array
  - Add validation for max 2 intentions in parsed response
  - Update `CharacterLLMRouterOutput` creation to use intentions list

### Task 6: Update JSON Repair Schema (5 minutes)
**File**: `src/rag/json_repair.py`
- [ ] Update character router JSON schema:
  - Change `"user_intention": string or null,` to `"user_intentions": array of strings,`
  - Add validation for array length <= 2

### Task 7: Create Test Script for Multi-Intention (10 minutes)
**File**: `scripts/test_multi_intention_character_router.py`
- [ ] Create test script with examples:
  - Single intention tests (ensure no regression)
  - Valid two-part questions: "spells and inventory", "combat stats and abilities"
  - Edge cases: empty intentions, too many intentions
  - Validation error testing
- [ ] Include performance comparison vs single intention queries

### Task 8: Update Existing Test Scripts (5 minutes)
**File**: `scripts/test_character_query_router.py`
- [ ] Update all `query_character()` calls:
  - Change `user_intention="intention"` to `user_intentions=["intention"]`
- [ ] Add backward compatibility note in comments

### Task 9: Integration Testing (10 minutes)
**File**: `demo_central_engine.py` (if exists)
- [ ] Test full pipeline with multi-intention queries
- [ ] Verify LLM prompt generates appropriate single vs multiple intentions
- [ ] Test that final response properly synthesizes multiple data sections
- [ ] Validate strict controls prevent excessive multi-intention usage

## Success Criteria

### Functional Requirements
- [ ] Support maximum 2 intentions per character query
- [ ] Maintain full backward compatibility with single intention queries
- [ ] Strict LLM prompt prevents overuse of multi-intention feature
- [ ] Combined data extraction works correctly for multiple intentions
- [ ] Performance impact is minimal (< 20% overhead for multi-intention)

### Quality Requirements
- [ ] All existing tests pass with single intention format
- [ ] New multi-intention tests demonstrate correct functionality
- [ ] Error handling for invalid intention counts
- [ ] Comprehensive logging for debugging multi-intention queries
- [ ] Code maintains current architectural patterns

## Risk Mitigation
- **Risk**: LLM generates too many intentions despite prompt restrictions
  - **Mitigation**: Hard validation limits in code (max 2 intentions)
- **Risk**: Performance degradation from processing multiple mappings
  - **Mitigation**: Combine mappings efficiently, benchmark performance
- **Risk**: Breaking changes affect existing functionality
  - **Mitigation**: Maintain backward compatibility, comprehensive testing

## Dependencies
- No external dependencies
- All changes are internal to existing modules
- Virtual environment activation required before testing

## Estimated Total Time: 85 minutes (~1.4 hours)

## Notes
- Start with virtual environment activation: `.\.venv\Scripts\Activate.ps1`
- Test each component individually before integration
- Use existing `Duskryn Nightwarden` character for testing
- Focus on quality over speed - ensure no regression in current functionality
