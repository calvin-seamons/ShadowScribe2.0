# Character Data Test Questions

This document provides example queries for testing each character data intention in the RAG system. Use these with `demo_central_engine.py` to verify routing and data retrieval works correctly.

## Usage
```bash
# Test a single question
python demo_central_engine.py -q "What is my character's race?"

# Test multiple questions in conversation
python demo_central_engine.py -q "What's my AC?" -q "And my HP?" -q "What about my speed?"

# Run interactively and paste questions
python demo_central_engine.py
```

---

## CHARACTER_BASICS
**Intent**: Core character identity and stats (name, race, class, level, ability scores, physical characteristics)

1. What is my character's race and class?
2. What level am I?
3. What are my ability scores?
4. Tell me about my character's physical appearance
5. What's my alignment and background?

---

## COMBAT_INFO
**Intent**: All combat capabilities and defensive stats (HP, AC, initiative, speed, saves, resistances, attacks, action economy)

1. What is my AC?
2. How many hit points do I have?
3. What attacks can I make in combat?
4. What damage resistances or immunities do I have?
5. What's my initiative bonus and speed?

---

## ABILITIES_INFO
**Intent**: Character capabilities and expertise (skills, proficiencies, languages, senses, features, traits, feats)

1. What skill proficiencies do I have?
2. What languages can I speak?
3. What special senses do I have like darkvision?
4. What class features do I have at my current level?
5. Tell me about my racial traits

---

## INVENTORY_INFO
**Intent**: Complete equipment and possessions (equipped items, backpack, carrying capacity, currency)

1. What weapons am I carrying?
2. What's in my backpack?
3. What armor am I wearing?
4. How much gold do I have?
5. What's my current carrying capacity and total weight?

---

## MAGIC_INFO
**Intent**: All spellcasting capabilities (known spells, spell slots, spellcasting modifiers, cantrips)

1. What spells can I cast?
2. How many spell slots do I have remaining?
3. What cantrips do I know?
4. What's my spell save DC and spell attack bonus?
5. What level 3 spells do I have prepared?

---

## STORY_INFO
**Intent**: Character narrative and personality (background, personality traits, ideals, bonds, flaws, backstory)

1. What's my character's backstory?
2. What are my personality traits and ideals?
3. Tell me about my character's bonds and flaws
4. What's my character's background feature?
5. What motivates my character?

---

## SOCIAL_INFO
**Intent**: Relationships and affiliations (NPCs, organizations, faction standings, allies, enemies)

1. Who are my allies?
2. What organizations am I part of?
3. Do I have any enemies?
4. Tell me about my mentor
5. What's my relationship with the Holy Knights of Kluntul?

---

## PROGRESS_INFO
**Intent**: Goals, objectives, and advancement (active quests, completed objectives, contracts, character progression)

1. What are my current objectives?
2. What quests have I completed?
3. What active contracts do I have?
4. What are my character's long-term goals?
5. Show me my character progression notes

---

## FULL_CHARACTER
**Intent**: Complete comprehensive character data (absolutely everything)

1. Give me a complete character sheet
2. Tell me everything about my character
3. Export all my character data
4. Show me my full character information
5. What's all the information you have about my character?

---

## CHARACTER_SUMMARY
**Intent**: Essential character overview (key stats, main equipment, important abilities)

1. Give me a quick summary of my character
2. What are the most important things to know about my character?
3. Summarize my character's key stats
4. Quick overview of my character
5. What's the elevator pitch for my character?

---

## Combined Intent Testing

These questions test multiple intentions at once:

1. **COMBAT_INFO + INVENTORY_INFO**: "What weapons do I have and what's my attack bonus with each?"
2. **MAGIC_INFO + ABILITIES_INFO**: "What spellcasting abilities do I have as a Warlock/Paladin?"
3. **STORY_INFO + SOCIAL_INFO**: "Tell me about my backstory and how it connects to my allies"
4. **CHARACTER_BASICS + COMBAT_INFO**: "Give me my character's core stats for combat"
5. **INVENTORY_INFO + MAGIC_INFO**: "What magical items and spells do I have?"

---

## Entity-Specific Testing

These questions test entity recognition and resolution:

1. "Tell me about Eldaryth of Regret" (weapon in inventory)
2. "What does my Hexblade's Curse ability do?" (class feature)
3. "Who is High Acolyte Aldric?" (NPC ally)
4. "Tell me about the Holy Knights of Kluntul" (organization)
5. "What can I do with Eldritch Blast?" (spell)

---

## Conversation History Testing

These sequences test conversation context maintenance:

### Sequence 1: Session Notes
```
Q1: "Describe the last session"
Q2: "What about the session before that?"
Q3: "What happened in the session where I fought Xurmurrin?"
```

### Sequence 2: Combat Stats
```
Q1: "What is my AC?"
Q2: "What about my HP?"
Q3: "And my initiative bonus?"
```

### Sequence 3: Equipment
```
Q1: "What weapon am I using?"
Q2: "What abilities does it have?"
Q3: "Can I use it to cast spells?"
```

### Sequence 4: Character Building
```
Q1: "What's my character's background?"
Q2: "How does that relate to my personality?"
Q3: "What organizations am I part of because of it?"
```

---

## Edge Cases & Complex Queries

1. "What combat abilities do I have tied to Eldaryth of Regret?" (cross-tool query)
2. "How does my Aura of the Guardian feature work and what does it cost me?" (feature + rules)
3. "What persuasion abilities do I have and how do they relate to my background?" (abilities + story)
4. "Can I cast Call Lightning with my current spell slots?" (magic + resource tracking)
5. "What's my total bonus when making a Religion check?" (abilities + proficiencies + stats)

---

## Negative/Missing Data Testing

These test graceful handling of missing information:

1. "What magic items do I have attuned?" (if none listed)
2. "What are my current quest objectives?" (empty objectives)
3. "Tell me about my familiar" (if none exists)
4. "What legendary actions can I take?" (character doesn't have any)
5. "What spells did I cast yesterday?" (temporal data not tracked)

---

## Notes for Testing

- **Conversation history**: The demo maintains context across multiple queries in the same session
- **Entity resolution**: System should find entities in character data, session notes, or rulebook automatically
- **Tool selection**: Router should intelligently select minimal tools needed for each query
- **Performance**: Track execution time for different query types
- **Accuracy**: Verify returned data matches the character's actual stats/info

Use `--quiet` flag for automated testing, omit it for detailed debugging output.
