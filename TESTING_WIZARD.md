# Character Creation Wizard - Testing Guide

## Overview
This guide provides step-by-step instructions for testing the complete character creation wizard implementation.

## Prerequisites
✅ Docker containers running (MySQL, API, Frontend)
✅ Frontend accessible at http://localhost:3000
✅ API accessible at http://localhost:8000
✅ Database initialized with schema

## Test URL
Navigate to: **http://localhost:3000/test/character-creation**

---

## Test Checklist

### Step 1: URL Input ✓
**What to test:**
- [ ] Page loads with wizard UI
- [ ] Progress indicator shows "Step 1 of 4"
- [ ] URL input field is pre-filled with test URL
- [ ] Help section displays instructions
- [ ] "Fetch Character" button is clickable

**Test URL:** `https://www.dndbeyond.com/characters/152248393`

**Expected behavior:**
- Click "Fetch Character"
- Button shows "Fetching..." state
- API call to `/api/characters/fetch`
- Success: Auto-advance to Step 2
- Error: Display error message, stay on Step 1

**Validation:**
- Invalid URL format shows validation error
- Network errors display user-friendly message

---

### Step 2: Parsing Progress ✓
**What to test:**
- [ ] Auto-advances from Step 1 after successful fetch
- [ ] Progress indicator shows "Step 2 of 4"
- [ ] WebSocket connection established
- [ ] 6 parser progress bars displayed:
  - Core Stats & Abilities ⚡
  - Inventory & Equipment 🎒
  - Spells & Spellcasting ✨
  - Features & Traits 🎖️
  - Backstory & Personality 📜
  - Actions & Attacks ⚔️
- [ ] Real-time progress updates for each parser
- [ ] Execution times displayed when parsers complete
- [ ] Overall progress percentage increases
- [ ] Character summary card appears when complete
- [ ] "Continue to Review & Edit" button appears

**Expected behavior:**
- Each parser shows status: idle → started → in_progress → complete
- Progress bars animate smoothly
- Completion takes ~2.5-5.5 seconds
- Character summary shows: Name, Race, Class, Level, HP, AC
- Auto-advance to Step 3 after 1 second delay

**Validation:**
- Parser failures show specific error messages
- WebSocket disconnections handled gracefully
- Progress state persists during brief disconnections

---

### Step 3: Section Review & Edit ✓
**What to test:**
- [ ] Progress indicator shows "Step 3 of 4"
- [ ] 8 section accordions displayed
- [ ] Each section shows icon, label, description
- [ ] Sections marked as "Loaded" if data present
- [ ] Click to expand/collapse sections
- [ ] Only one section expanded at a time

**Sections to test:**

#### 3.1: Ability Scores Editor (💪)
- [ ] Grid of 6 ability scores displayed
- [ ] STR, DEX, CON, INT, WIS, CHA labels
- [ ] Score input fields (1-30 range)
- [ ] Modifiers calculated automatically
- [ ] Positive modifiers show green, negative show red
- [ ] Stats summary shows total, average, total modifiers
- [ ] Guidelines box explains score ranges
- [ ] "Save Ability Scores" button works

**Test actions:**
- Change STR from 10 to 18
- Verify modifier updates to +4
- Change INT from 10 to 8
- Verify modifier shows -1 in red
- Click Save button

#### 3.2: Combat Stats (⚔️)
- [ ] JSON preview displays (no editor yet)
- [ ] Shows HP, AC, initiative, speed
- [ ] "Save Section" button available

#### 3.3: Inventory Editor (🎒)
- [ ] Currency section with 5 coin types
- [ ] 13 equipment slots (head, eyes, neck, etc.)
- [ ] Add/remove buttons for equipped items
- [ ] Backpack section with item list
- [ ] Add Item button creates new entry
- [ ] Remove Item button deletes entry
- [ ] Item fields: name, quantity, weight, description
- [ ] Total carried weight calculated
- [ ] "Save Inventory" button works

**Test actions:**
- Add 100 gold pieces
- Add a sword to main_hand slot
- Add 5 items to backpack
- Verify weight calculation
- Remove an item
- Click Save button

#### 3.4: Spell List Editor (✨)
- [ ] Spellcasting stats section
- [ ] Ability dropdown (INT/WIS/CHA)
- [ ] Spell Save DC input
- [ ] Spell Attack Bonus input
- [ ] Spell levels 0-9 displayed
- [ ] Expandable level sections
- [ ] Add Spell button per level
- [ ] Spell fields: name, school, casting time, range, description
- [ ] School dropdown with 8 options
- [ ] Remove Spell button works
- [ ] Total spells counter
- [ ] "Save Spell List" button works

**Test actions:**
- Set spellcasting ability to WIS
- Expand "Cantrips" section
- Add a new cantrip
- Fill in spell details
- Expand "1st Level" section
- Add 3 spells
- Remove one spell
- Click Save button

#### 3.5: Actions Editor (🎯)
- [ ] Attacks per action setting
- [ ] Actions list (initially empty or from parsing)
- [ ] Add Action button
- [ ] Expandable action cards
- [ ] Action type icons (⚔️ ⚡ 🛡️ 💨)
- [ ] Action fields: name, action type, attack type, bonus, damage, range, description
- [ ] Limited uses section (optional)
- [ ] Remove Action button
- [ ] "Save Actions" button works

**Test actions:**
- Set attacks per action to 2
- Add a melee attack action
- Set name: "Longsword"
- Set attack bonus: +7
- Set damage: "1d8+3 slashing"
- Add limited uses: 3/day, short rest
- Add a bonus action
- Remove one action
- Click Save button

#### 3.6: Features & Traits (🎖️)
- [ ] JSON preview displays (no editor yet)
- [ ] Shows class features, racial traits
- [ ] "Save Section" button available

#### 3.7: Backstory Editor (📜)
- [ ] Title input field
- [ ] 6 textarea fields with labels
- [ ] Character counters for each field
- [ ] "Save Backstory" button works

**Test actions:**
- Fill in title
- Add family history (100+ words)
- Verify character count updates
- Click Save button

#### 3.8: Personality Editor (🎭)
- [ ] 4 textarea fields: Traits, Ideals, Bonds, Flaws
- [ ] Character counters for each
- [ ] Help tips for each section
- [ ] Info box with D&D 5e guidance
- [ ] "Save Personality" button works

**Test actions:**
- Fill in all 4 fields
- Verify character counts
- Click Save button

**General Section Testing:**
- [ ] "Continue to Preview & Save" button at bottom
- [ ] Button navigates to Step 4
- [ ] Info box explains section editing

---

### Step 4: Preview & Save ✓
**What to test:**
- [ ] Progress indicator shows "Step 4 of 4"
- [ ] Character summary card displayed
- [ ] Name, race, class shown prominently
- [ ] Core stats grid: Level, HP, AC, Initiative
- [ ] Ability scores grid (6 abilities)
- [ ] Section summaries for inventory, spells, backstory, personality
- [ ] "Save Character to Database" button
- [ ] Info box explains what happens on save

**Expected behavior:**
- Click "Save Character to Database"
- Button shows "Saving Character..." state
- API call to `POST /api/characters`
- Success shows:
  - 🎉 success animation
  - Character ID displayed
  - "View Character Details" link
  - "Import Another Character" button

**Test actions:**
- Review all displayed data
- Click Save button
- Wait for success message
- Verify character ID shown
- Click "View Character Details" (should navigate to character page)

**After Save Testing:**
- [ ] Character appears in database
- [ ] All sections saved correctly
- [ ] Character accessible via API
- [ ] Character data matches wizard input

---

## Integration Tests

### WebSocket Connection
- [ ] WebSocket connects on Step 2
- [ ] Progress events received in real-time
- [ ] Connection survives brief network interruptions
- [ ] Error handling for WebSocket failures

### API Endpoints
- [ ] `POST /api/characters/fetch` - Fetch from D&D Beyond
- [ ] `POST /api/characters` - Create new character
- [ ] `PATCH /api/characters/{id}/{section}` - Update section

### Database Verification
```bash
# Connect to MySQL
docker exec -it shadowscribe_mysql mysql -u root -prootpassword shadowscribe

# Check characters table
SELECT id, name, race, character_class, level FROM characters;

# View character data
SELECT JSON_PRETTY(data) FROM characters WHERE name = 'Test Character' LIMIT 1;
```

---

## Performance Benchmarks

### Target Metrics (from plan)
- [ ] Character fetch from D&D Beyond: < 2 seconds
- [ ] Total parsing time: < 6 seconds
- [ ] WebSocket progress updates: every ~500ms
- [ ] Section save (PATCH): < 500ms
- [ ] Full character save (POST): < 1 second

### Actual Metrics
Record actual times during testing:
- Fetch time: _____ seconds
- Parsing time: _____ seconds
- Section save: _____ ms
- Full save: _____ ms

---

## Error Handling Tests

### Invalid Inputs
- [ ] Invalid D&D Beyond URL format
- [ ] Non-existent character ID
- [ ] Network timeout during fetch
- [ ] WebSocket disconnect during parsing
- [ ] Invalid ability score (< 1 or > 30)
- [ ] Empty required fields
- [ ] Malformed JSON data

### Expected Behaviors
- Clear error messages displayed to user
- Errors don't crash the wizard
- User can retry failed operations
- Progress preserved where possible

---

## Browser Compatibility
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers (responsive design)

---

## Debug Panel (Development)

The wizard includes a debug panel in development mode. Verify it shows:
- [ ] Current Step number
- [ ] Character ID
- [ ] Saved ID
- [ ] Is Creating status
- [ ] Completed/Total parser count
- [ ] Data availability flags
- [ ] Progress events count

---

## Known Issues / Limitations

### Current Implementation
- Combat Stats editor: Shows JSON preview only
- Features & Traits editor: Shows JSON preview only
- Section PATCH endpoints: May need backend implementation
- Character images: Not supported in MVP

### Future Enhancements
- Full combat stats editor
- Features & traits CRUD editor
- Drag-and-drop item reordering
- Spell slot tracking
- Character image upload
- Export to PDF

---

## Success Criteria

All tests passing means:
✅ User can paste D&D Beyond URL and fetch character
✅ All 6 parsers run in parallel with real-time progress
✅ User can edit all character sections with full CRUD
✅ Character saves to database with complete data
✅ Multi-step wizard navigation works flawlessly
✅ Error handling provides clear feedback
✅ Performance meets target benchmarks

---

## Reporting Issues

When reporting bugs, include:
1. Test step where issue occurred
2. Expected vs actual behavior
3. Browser and version
4. Console error messages
5. Network tab (for API issues)
6. Screenshots/video if applicable

---

## Next Steps After Testing

1. Fix any bugs discovered
2. Implement missing section editors (combat stats, features)
3. Add PATCH endpoint support
4. Performance optimization if needed
5. Add unit tests for critical components
6. Deploy to staging environment
7. User acceptance testing

---

**Testing completed by:** __________  
**Date:** __________  
**Result:** ☐ All tests passed ☐ Issues found (see notes)  
**Notes:**
