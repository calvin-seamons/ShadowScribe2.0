# Session Notes Test Questions

This document provides comprehensive test questions for all session notes user intentions. Use these with `demo_central_engine.py` to verify the RAG system correctly routes queries and retrieves appropriate session note context.

## Usage
```bash
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Test single question
python demo_central_engine.py -q "What happened in the last session?"

# Test multiple questions in sequence (tests conversation history)
python demo_central_engine.py -q "Who did we meet in Session 40?" -q "What about the session after that?"

# Interactive mode for exploratory testing
python demo_central_engine.py
```

---

## 1. CHARACTER_STATUS
**Intent Definition**: Current character status and conditions

### Test Questions
1. "What is Duskryn's current HP and condition?"
2. "Is Duskryn alive or dead right now?"
3. "Where is my character located currently?"
4. "What conditions is my character suffering from?"
5. "How did Duskryn's physical state change in Session 40?"

---

## 2. EVENT_SEQUENCE
**Intent Definition**: What happened when - chronological events

### Test Questions
1. "What happened in Session 41?"
2. "Walk me through the events of the last session in order"
3. "What were the key events that occurred in Session 40?"
4. "Give me a chronological summary of Session 41"
5. "What happened first, second, and third in the most recent session?"

---

## 3. NPC_INFO
**Intent Definition**: NPC interactions, relationships, and information

### Test Questions
1. "Tell me about Ghul'vor the Undying"
2. "Who is High Acolyte Aldric and what did he do?"
3. "What NPCs did we encounter in Session 41?"
4. "What is Ethernea's relationship with Duskryn?"
5. "Describe the Soul Harvester we fought"

---

## 4. LOCATION_DETAILS
**Intent Definition**: Information about places visited and explored

### Test Questions
1. "What is the Soul Cairn?"
2. "Describe the Theater of Blood where the ritual happened"
3. "What locations have we visited recently?"
4. "What are the notable features of the Soul Cairn?"
5. "Where did the Black Benediction ritual take place?"

---

## 5. ITEM_TRACKING
**Intent Definition**: Items found, lost, used, or traded

### Test Questions
1. "What items did we obtain in Session 41?"
2. "What happened to Duskryn's Eldarith?"
3. "Did we find any loot in the last session?"
4. "What magical items were used during the rescue mission?"
5. "Track the Eldarith of Chaos - who has it and what was it used for?"

---

## 6. COMBAT_RECAP
**Intent Definition**: Details of past combat encounters

### Test Questions
1. "Tell me about the combat in Session 41"
2. "Who did we fight in the Soul Cairn?"
3. "How much damage did the Soul Harvester deal?"
4. "What was the outcome of the combat in the last session?"
5. "Describe the tactics used against the Soul Harvester"

---

## 7. SPELL_ABILITY_USAGE
**Intent Definition**: Spells and abilities used during sessions

### Test Questions
1. "What spells did Willow cast in Session 41?"
2. "Tell me about the Eldarith of Chaos ability that was used"
3. "What spells were used in Session 40 to try to stop Duskryn?"
4. "Did anyone cast Calm Emotions? What was the effect?"
5. "What magical abilities did Duskryn use during the ritual?"

---

## 8. CHARACTER_DECISIONS
**Intent Definition**: Important character choices and their outcomes

### Test Questions
1. "Why did Duskryn give up his Eldarith to Ghul'vor?"
2. "What was Zivu's decision about helping with the rescue?"
3. "Why did the party choose to enter the Soul Cairn?"
4. "What was Pork's motivation for jumping through the rift?"
5. "What decision did Duskryn make despite divine warnings?"

---

## 9. PARTY_DYNAMICS
**Intent Definition**: Group interactions and relationships

### Test Questions
1. "How does the party feel about Duskryn after his choices?"
2. "What conflict occurred between Zivu and the rescue mission?"
3. "Describe the party's relationship dynamics in Session 41"
4. "What did Willow say about Duskryn while helping him?"
5. "How did the party work together during the rescue?"

---

## 10. QUEST_TRACKING
**Intent Definition**: Quest progress, objectives, and completion status

### Test Questions
1. "What is the current objective of our rescue mission?"
2. "What quests are we currently pursuing?"
3. "What was the goal of entering the Soul Cairn?"
4. "Have we completed any major objectives recently?"
5. "What do we need to do to save Duskryn?"

---

## 11. PUZZLE_SOLUTIONS
**Intent Definition**: Puzzles encountered and how they were solved

### Test Questions
1. "Tell me about the lantern puzzle in the Soul Cairn"
2. "What is the color sequence for the lanterns?"
3. "How did we discover the puzzle mechanism?"
4. "What do the different lantern colors represent?"
5. "What puzzles are we currently trying to solve?"

---

## 12. LOOT_REWARDS
**Intent Definition**: Treasure, rewards, and items obtained

### Test Questions
1. "What loot did we get in Session 41?"
2. "Have we received any rewards recently?"
3. "What treasure did we obtain in the last few sessions?"
4. "Did anyone get any new equipment?"
5. "What items were acquired during the rescue mission?"

---

## 13. DEATH_REVIVAL
**Intent Definition**: Character deaths, revivals, and soul-related events

### Test Questions
1. "How did Duskryn die?"
2. "Tell me about character deaths in recent sessions"
3. "What happened to Duskryn's soul?"
4. "Has anyone been revived recently?"
5. "Describe the soul separation that occurred"

---

## 14. DIVINE_RELIGIOUS
**Intent Definition**: Interactions with deities and religious events

### Test Questions
1. "What divine interventions have occurred recently?"
2. "Tell me about Ethernea's appearance in Session 41"
3. "What religious significance does Duskryn's knighting ceremony have?"
4. "What did the divine figure offer the party?"
5. "Describe the Black Benediction ritual and its religious implications"

---

## 15. MEMORY_VISION
**Intent Definition**: Memories recovered, visions seen, dreams experienced

### Test Questions
1. "What memories did Duskryn experience in the Soul Cairn?"
2. "Tell me about Duskryn's knighting ceremony memory"
3. "What visions has my character had recently?"
4. "Describe the memory of Duskryn joining the Priory"
5. "What do Duskryn's memories reveal about his past?"

---

## 16. RULES_MECHANICS
**Intent Definition**: Rule interpretations and mechanical decisions made

### Test Questions
1. "What were the mechanics of the soul draining in Session 41?"
2. "How does the Soul Harvester's beam attack work?"
3. "What was the DC for the saving throw against the reality rift?"
4. "Explain the soul HP mechanic for Duskryn"
5. "What were the combat mechanics of the Soul Cairn encounter?"

---

## 17. HUMOR_MOMENTS
**Intent Definition**: Funny moments and memorable jokes

### Test Questions
1. "What funny moments happened in Session 41?"
2. "Tell me some memorable jokes from recent sessions"
3. "What did Pork say that was funny?"
4. "What humorous comparisons were made during Session 40?"
5. "Describe any comedic moments during the rescue mission"

---

## 18. UNRESOLVED_MYSTERIES
**Intent Definition**: Ongoing mysteries and unanswered questions

### Test Questions
1. "What mysteries remain unresolved in the campaign?"
2. "What questions do we still have about the Soul Cairn?"
3. "What is still unknown about Ghul'vor's plans?"
4. "What unanswered questions came up in Session 41?"
5. "What mysteries were left at the end of the last session?"

---

## 19. FUTURE_IMPLICATIONS
**Intent Definition**: Events that might affect future sessions

### Test Questions
1. "What cliffhanger did Session 41 end on?"
2. "What future implications does Duskryn's ritual have?"
3. "What might happen in the next session?"
4. "What consequences might we face from recent events?"
5. "What are the next session hooks from Session 41?"

---

## 20. CROSS_SESSION
**Intent Definition**: Connections and patterns across multiple sessions

### Test Questions
1. "How do Sessions 40 and 41 connect to each other?"
2. "What is the story arc across the last two sessions?"
3. "Compare Duskryn's state in Session 40 versus Session 41"
4. "What patterns emerged across multiple sessions?"
5. "How has the party's situation evolved from Session 40 to 41?"

---

## Additional Test Scenarios

### Combined Intent Testing
Test questions that require multiple intent types:

1. "Tell me about Duskryn's journey from Session 40 to now, including his death, current status, and the memories he experienced" (CHARACTER_STATUS + EVENT_SEQUENCE + MEMORY_VISION + DEATH_REVIVAL)
2. "Describe the complete rescue mission including who we fought, what spells were used, and what puzzle we're solving" (COMBAT_RECAP + SPELL_ABILITY_USAGE + PUZZLE_SOLUTIONS + EVENT_SEQUENCE)
3. "What NPCs have appeared recently, where did we encounter them, and what religious significance do they have?" (NPC_INFO + LOCATION_DETAILS + DIVINE_RELIGIOUS)

### Entity-Specific Cross-Session Tests
Test entity tracking across multiple sessions:

1. "Tell me everything about Ghul'vor across all sessions"
2. "What is High Acolyte Aldric's full story from all mentions?"
3. "Track Ethernea's involvement throughout the recent sessions"
4. "What happened with the Soul Cairn from first mention to now?"

### Conversation History Tests
Test the conversation context tracking:

1. First: "What happened in Session 40?" → Then: "What about the session after that?"
2. First: "Tell me about Ghul'vor" → Then: "What did he do in the ritual?"
3. First: "Describe the lantern puzzle" → Then: "What colors are involved?"
4. First: "Who is Ethernea?" → Then: "When did she appear to help us?"

### Temporal Query Tests
Test time-based queries:

1. "What happened in the most recent session?"
2. "What occurred in the session before the current one?"
3. "Tell me about Session 40 and Session 41"
4. "What events happened in the last two sessions?"
5. "Compare what happened in Session 40 versus Session 41"

### Edge Cases and Negative Tests

1. "What happened in Session 99?" (non-existent session)
2. "Tell me about Bob the Barbarian" (non-existent character)
3. "What loot did we get in Session 41?" (session with no loot)
4. "What spells did Pork cast?" (character who didn't cast spells)
5. "Describe the combat in Session 39" (session not in knowledge base)

### Ambiguous Entity Tests
Test entity resolution:

1. "Tell me about Dusk" (nickname for Duskryn)
2. "What happened with the cleric?" (referring to Duskryn)
3. "Describe the dwarf spirit" (referring to High Acolyte Aldric)
4. "Tell me about the ex-god" (referring to Ghul'vor)
5. "What did the divine figure say?" (referring to Ethernea)

---

## Testing Methodology

### Systematic Testing Approach
1. Test each intent category with all 5 questions
2. Verify correct intent classification in debug output
3. Confirm relevant session context is retrieved
4. Check that conversation history maintains context
5. Validate entity extraction and resolution

### Performance Benchmarks
- Intent classification should complete in <500ms
- Entity extraction should identify 80%+ of relevant entities
- Context retrieval should find correct sessions 95%+ of time
- Final response should reference appropriate session details

### Common Issues to Watch For
- Intent misclassification (e.g., COMBAT_RECAP routed to EVENT_SEQUENCE)
- Entity resolution failures (e.g., "Dusk" not resolving to "Duskryn")
- Missing context from relevant sessions
- Cross-session queries missing connections
- Conversation history not preserving entity references

---

## Debug Mode Usage

For detailed routing and context information:
```python
# In demo_central_engine.py, enable debug output
engine = CentralEngine(character, campaign_storage, rulebook_storage)

# Then run queries and examine:
# - Detected intentions
# - Extracted entities
# - Selected sessions
# - Context assembly
# - Final prompt construction
```

---

## Notes on Session Notes Coverage

The current knowledge base includes:
- **Session 40** (06-30-25.md): Black Benediction ritual, Duskryn's death
- **Session 41** (08-06-2025.md): Soul Cairn rescue mission

Test questions are designed to work with these sessions but can be adapted as more session notes are added to the knowledge base.
