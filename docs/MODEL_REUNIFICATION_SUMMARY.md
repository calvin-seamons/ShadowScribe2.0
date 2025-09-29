# Model Reunification Summary

**Date:** September 29, 2025  
**Task:** Reunify action models between `parse_actions.py` and `character_types.py`

## Problem

The codebase had duplicate action model definitions:
- `parse_actions.py` defined its own action models (ActionActivation, ActionUsage, etc.)
- `character_types.py` had different action models (DamageInfo, AttackAction, SpecialAction)
- This created inconsistency and duplication

## Solution

Used `parse_actions.py` models as the **single source of truth** since they were optimized for D&D Beyond JSON structure.

## Changes Made

### 1. Updated `src/rag/character/character_types.py`

**Removed old models:**
- `DamageInfo` - replaced by `ActionDamage`
- `AttackAction` - replaced by `CharacterAction`
- `SpecialAction` - replaced by `CharacterAction`

**Added new models from parse_actions.py:**
- `ActionActivation` - How an action is activated
- `ActionUsage` - Usage limitations (charges, resets)
- `ActionRange` - Range and area of effect information
- `ActionDamage` - Damage dice, type, and bonuses
- `ActionSave` - Saving throw DC and effects
- `CharacterAction` - Unified action model for all action types

**Updated existing models:**
- `ActionEconomy` - Changed from using `SpecialAction` to using `CharacterAction`

### 2. Updated `parse_actions.py`

**Removed:**
- All local dataclass definitions (ActionActivation, ActionUsage, etc.)

**Added:**
- Import statement for all action models from `character_types.py`:
  ```python
  from rag.character.character_types import (
      ActionActivation,
      ActionUsage,
      ActionRange,
      ActionDamage,
      ActionSave,
      CharacterAction
  )
  ```

### 3. Updated Documentation

**Updated `docs/CHARACTER_EXTRACTION_API_SCHEMAS.md`:**
- Replaced old action model documentation with new unified models
- Added extraction paths and mappings for D&D Beyond JSON

## Benefits

1. **Single Source of Truth:** All action models now live in `character_types.py`
2. **No Duplication:** Eliminated redundant model definitions
3. **Consistency:** All parts of the codebase use the same models
4. **Better Structure:** Models are optimized for D&D Beyond JSON format
5. **Easier Maintenance:** Changes only need to be made in one place

## Model Hierarchy

```
CharacterAction (unified action model)
├── activation: ActionActivation
├── usage: ActionUsage  
├── actionRange: ActionRange
├── damage: ActionDamage
└── save: ActionSave
```

## Action Categories

The `CharacterAction` model supports all action types through the `actionCategory` field:
- `"attack"` - Weapon attacks
- `"feature"` - Class/racial features  
- `"spell"` - Spell actions
- `"item"` - Item-granted actions
- `"unequipped_weapon"` - Weapons not currently equipped

## Migration Notes

Any code that previously used:
- `AttackAction` → should now use `CharacterAction` with `actionCategory="attack"`
- `SpecialAction` → should now use `CharacterAction` with `actionCategory="feature"`
- `DamageInfo` → should now use `ActionDamage`

## Files Modified

1. `/src/rag/character/character_types.py` - Added action models, removed old ones
2. `/parse_actions.py` - Removed duplicate models, added imports
3. `/docs/CHARACTER_EXTRACTION_API_SCHEMAS.md` - Updated documentation

## Verification

All action parsing functionality remains intact:
- ✓ Parser still creates CharacterAction objects correctly
- ✓ All action attributes preserved
- ✓ JSON serialization still works
- ✓ No breaking changes to external APIs
