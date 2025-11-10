# Character Creation Hook - Testing Guide

## Overview
This guide explains how to test the `useCharacterCreation` React hook implementation.

## What Was Implemented

### 1. **useCharacterCreation Hook** (`frontend/lib/hooks/useCharacterCreation.ts`)
A comprehensive React hook that manages the entire character creation flow with WebSocket progress tracking.

**Features:**
- ✅ Real-time progress tracking for all 6 parsers (core, inventory, spells, features, background, actions)
- ✅ Parser status states: idle → started → in_progress → complete/error
- ✅ Execution time tracking per parser
- ✅ Character ID generation from name (kebab-case)
- ✅ Error handling and loading states
- ✅ Progress event history for debugging
- ✅ Reset functionality to clear all state

**API:**
```typescript
const {
  createCharacter,      // (urlOrJsonData: string | any) => Promise<string>
  parsers,              // Record<ParserName, ParserProgress>
  isCreating,           // boolean
  error,                // string | null
  characterId,          // string | null
  characterSummary,     // CharacterSummary | null
  progressEvents,       // CharacterCreationEvent[]
  resetProgress,        // () => void
  completedCount,       // number (0-6)
  totalCount            // number (always 6)
} = useCharacterCreation()
```

### 2. **Demo Component** (`frontend/components/character/CharacterCreationDemo.tsx`)
A fully functional demo component showcasing all hook features.

**Features:**
- URL input for D&D Beyond characters
- Real-time progress bars with status icons
- Parser-specific progress display with execution times
- Overall progress percentage
- Character summary display on completion
- Error handling UI
- Event log for debugging
- Reset functionality

### 3. **Test Page** (`frontend/app/test/character-creation/page.tsx`)
A Next.js page that renders the demo component.

### 4. **Type Exports** (`frontend/lib/hooks/index.ts`)
Convenient index file for importing hook and types.

## Testing Instructions

### Method 1: Using the Test Page (Recommended)

1. **Start the frontend dev server:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate to the test page:**
   ```
   http://localhost:3000/test/character-creation
   ```

3. **Test the flow:**
   - The page loads with a default D&D Beyond URL
   - Click "Create Character" to start the process
   - Watch the real-time progress bars update
   - Verify all 6 parsers complete successfully
   - Check the character summary displays correctly
   - Click "Reset" to clear and try again

### Method 2: Integration in Your Own Component

```tsx
'use client'

import { useCharacterCreation } from '@/lib/hooks/useCharacterCreation'

export function MyComponent() {
  const { 
    createCharacter, 
    parsers, 
    isCreating, 
    characterSummary 
  } = useCharacterCreation()
  
  const handleCreate = async () => {
    try {
      const id = await createCharacter('https://dndbeyond.com/characters/152248393')
      console.log('Character created with ID:', id)
    } catch (err) {
      console.error('Failed:', err)
    }
  }
  
  return (
    <div>
      <button onClick={handleCreate} disabled={isCreating}>
        {isCreating ? 'Creating...' : 'Create Character'}
      </button>
      
      {Object.values(parsers).map(parser => (
        <div key={parser.parser}>
          {parser.parser}: {parser.status}
          {parser.execution_time_ms && ` (${parser.execution_time_ms}ms)`}
        </div>
      ))}
      
      {characterSummary && (
        <div>
          <h2>{characterSummary.name}</h2>
          <p>Level {characterSummary.level} {characterSummary.race} {characterSummary.character_class}</p>
          <p>HP: {characterSummary.hp} | AC: {characterSummary.ac}</p>
        </div>
      )}
    </div>
  )
}
```

### Method 3: Programmatic Testing

```typescript
import { renderHook, act, waitFor } from '@testing-library/react'
import { useCharacterCreation } from '@/lib/hooks/useCharacterCreation'

test('creates character successfully', async () => {
  const { result } = renderHook(() => useCharacterCreation())
  
  // Initially idle
  expect(result.current.isCreating).toBe(false)
  expect(result.current.completedCount).toBe(0)
  
  // Start creation
  let characterId: string | undefined
  await act(async () => {
    characterId = await result.current.createCharacter(
      'https://dndbeyond.com/characters/152248393'
    )
  })
  
  // Verify completion
  await waitFor(() => {
    expect(result.current.isCreating).toBe(false)
    expect(result.current.completedCount).toBe(6)
    expect(result.current.characterSummary).toBeTruthy()
    expect(characterId).toBeTruthy()
  })
})
```

## Expected Behavior

### Success Flow:
1. **URL Input** → User provides D&D Beyond URL
2. **Fetch Started** → WebSocket connection established
3. **Fetch Complete** → Character JSON retrieved (name displayed)
4. **Parsers Started** → All 6 parsers start simultaneously
5. **Parser Progress** → Status updates in real-time:
   - Core, Inventory, Spells, Features: Complete in ~20-50ms
   - Actions: Complete in ~1-2 seconds (LLM-based)
   - Background: Complete in ~3-5 seconds (LLM-based)
6. **Assembly Started** → Character object being assembled
7. **Creation Complete** → Character summary displayed

### Parser Timing (Expected):
- **Fast parsers** (20-50ms): core, inventory, spells, features
- **Medium parser** (1-2s): actions
- **Slow parser** (3-5s): background
- **Total time**: ~4-6 seconds

### Character Summary Contains:
- Name (e.g., "Nikolai Dragovich")
- Race (e.g., "Centaur")
- Class (e.g., "Artificer")
- Level (e.g., 4)
- HP (e.g., 26)
- AC (e.g., 16)

## Troubleshooting

### Hook doesn't update progress:
- Ensure WebSocket connection is established
- Check browser console for WebSocket errors
- Verify API server is running on port 8000

### Progress bars don't animate:
- Check if CSS classes are loaded (Tailwind required)
- Verify status transitions are occurring

### Character summary doesn't display:
- Check `characterSummary` state in React DevTools
- Verify WebSocket receives `creation_complete` event
- Check for errors in `error` state

### Parsers stuck in "started" status:
- Check API server logs for parser errors
- Verify all parsers are completing successfully
- Look for timeout or network issues

## Files Created/Modified

```
frontend/
├── lib/
│   ├── hooks/
│   │   ├── useCharacterCreation.ts  ✨ NEW - Main hook implementation
│   │   └── index.ts                 ✨ NEW - Exports for easy import
│   ├── services/
│   │   └── websocket.ts             ✓ Modified - Added createCharacter()
│   └── types/
│       └── character.ts             ✓ Modified - Added progress types
├── components/
│   └── character/
│       └── CharacterCreationDemo.tsx ✨ NEW - Full-featured demo component
└── app/
    └── test/
        └── character-creation/
            └── page.tsx              ✨ NEW - Test page
```

## Next Steps

After verifying the hook works correctly:

1. **Step 7**: Implement the multi-step wizard UI
2. **Step 8**: Create section editor components
3. **Integration**: Wire everything together in the full wizard

## API Reference

See inline documentation in:
- `frontend/lib/hooks/useCharacterCreation.ts` - Full hook API
- `frontend/lib/types/character.ts` - All type definitions
- `frontend/lib/services/websocket.ts` - WebSocket service methods
