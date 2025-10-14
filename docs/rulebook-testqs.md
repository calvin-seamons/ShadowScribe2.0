# Rulebook Test Questions

This document provides comprehensive test questions for all D&D 5e rulebook query intentions. Use these with `demo_central_engine.py` to verify the RAG system correctly routes queries and retrieves appropriate rulebook context.

## Usage
```bash
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Test single question
python demo_central_engine.py -q "How does concentration work?"

# Test multiple questions in sequence (tests conversation history)
python demo_central_engine.py -q "What is a dwarf's speed?" -q "What about their darkvision?"

# Interactive mode for exploratory testing
python demo_central_engine.py
```

---

## 1. DESCRIBE_ENTITY
**Intent Definition**: Find exact section for single entity

### Test Questions
1. "What are the traits of a dwarf?"
2. "Describe the fireball spell"
3. "Tell me about the fighter class"
4. "What is the poisoned condition?"
5. "Explain what a longsword is"

---

## 2. COMPARE_ENTITIES
**Intent Definition**: Compare multiple entities

### Test Questions
1. "What's the difference between a wizard and a sorcerer?"
2. "Compare the dwarf and elf races"
3. "What's different between chain mail and plate armor?"
4. "Compare fireball and lightning bolt spells"
5. "How do the barbarian and fighter differ?"

---

## 3. LEVEL_PROGRESSION
**Intent Definition**: Class level features

### Test Questions
1. "What does a fighter get at level 5?"
2. "What abilities does a wizard gain at 3rd level?"
3. "Describe cleric level progression from 1 to 5"
4. "What features does a rogue unlock at level 2?"
5. "When does a barbarian get extra attack?"

---

## 4. ACTION_OPTIONS
**Intent Definition**: Combat actions available

### Test Questions
1. "What can I do on my turn in combat?"
2. "What actions are available in D&D 5e?"
3. "Can I use a bonus action and an action in the same turn?"
4. "What's the difference between an action and a reaction?"
5. "What combat actions can I take besides attacking?"

---

## 5. RULE_MECHANICS
**Intent Definition**: Specific rule explanations

### Test Questions
1. "How does concentration work?"
2. "Explain the advantage and disadvantage system"
3. "How do saving throws work?"
4. "What is proficiency bonus?"
5. "Explain how ability checks work"

---

## 6. CALCULATE_VALUES
**Intent Definition**: Math and calculations

### Test Questions
1. "What's my AC with chain mail and a shield?"
2. "How do I calculate my attack bonus?"
3. "What's the damage for a longsword with 16 Strength?"
4. "Calculate my spell save DC with 18 Intelligence"
5. "How much HP does a 5th level fighter with 14 Constitution have?"

---

## 7. SPELL_DETAILS
**Intent Definition**: Individual spell descriptions

### Test Questions
1. "What does fireball do?"
2. "Describe the cure wounds spell"
3. "What are the effects of counterspell?"
4. "How does healing word work?"
5. "Tell me about the shield spell"

---

## 8. CLASS_SPELL_ACCESS
**Intent Definition**: Class spell lists

### Test Questions
1. "What spells can a ranger learn?"
2. "What's on the wizard spell list?"
3. "Can a cleric cast fireball?"
4. "What healing spells does a paladin have access to?"
5. "List some 3rd level bard spells"

---

## 9. MONSTER_STATS
**Intent Definition**: Creature stat blocks

### Test Questions
1. "What are the stats for a red dragon?"
2. "Describe a goblin's abilities"
3. "What is the AC and HP of a lich?"
4. "Give me the stat block for an owlbear"
5. "What are a beholder's stats?"

---

## 10. CONDITION_EFFECTS
**Intent Definition**: Status effects

### Test Questions
1. "What does being poisoned do?"
2. "Explain the stunned condition"
3. "What are the effects of being charmed?"
4. "How does the paralyzed condition work?"
5. "What happens when you're frightened?"

---

## 11. CHARACTER_CREATION
**Intent Definition**: Character building overview

### Test Questions
1. "How do I create a character?"
2. "What steps are involved in character creation?"
3. "Explain the character creation process"
4. "What do I need to know to build a new character?"
5. "Walk me through making a D&D character"

---

## 12. MULTICLASS_RULES
**Intent Definition**: Multi-classing requirements

### Test Questions
1. "Can I multiclass barbarian and wizard?"
2. "What are the requirements for multiclassing?"
3. "How does multiclassing work in 5e?"
4. "Can I be a fighter/rogue multiclass?"
5. "What do I need to multiclass into cleric?"

---

## 13. EQUIPMENT_PROPERTIES
**Intent Definition**: Item properties

### Test Questions
1. "What does the finesse property mean?"
2. "Explain the versatile weapon property"
3. "What is the heavy property on weapons?"
4. "How does the reach property work?"
5. "What does the two-handed property do?"

---

## 14. DAMAGE_TYPES
**Intent Definition**: Damage mechanics

### Test Questions
1. "How does fire damage work?"
2. "What's the difference between slashing and piercing damage?"
3. "Explain radiant damage"
4. "What damage types are there in 5e?"
5. "How does resistance to damage work?"

---

## 15. REST_MECHANICS
**Intent Definition**: Rest rules

### Test Questions
1. "What happens during a long rest?"
2. "How does a short rest work?"
3. "What's the difference between short and long rests?"
4. "What do I recover during a rest?"
5. "How long is a long rest?"

---

## 16. SKILL_USAGE
**Intent Definition**: Skill applications

### Test Questions
1. "When do I use Investigation vs Perception?"
2. "How does the Stealth skill work?"
3. "What situations call for an Athletics check?"
4. "Explain when to use Insight"
5. "When should I roll Persuasion vs Deception?"

---

## 17. FIND_BY_CRITERIA
**Intent Definition**: Search by properties

### Test Questions
1. "What spells deal thunder damage?"
2. "List all races with darkvision"
3. "What weapons have the finesse property?"
4. "What classes can cast healing spells?"
5. "Which spells require concentration?"

---

## 18. PREREQUISITE_CHECK
**Intent Definition**: Requirements

### Test Questions
1. "What do I need to take the Grappler feat?"
2. "What are the prerequisites for War Caster?"
3. "Can I wear heavy armor as a wizard?"
4. "What ability score do I need to multiclass into paladin?"
5. "What are the requirements for the Alert feat?"

---

## 19. INTERACTION_RULES
**Intent Definition**: Rule interactions

### Test Questions
1. "How does invisibility interact with opportunity attacks?"
2. "Can I cast a spell while grappled?"
3. "What happens when concentration is broken during a spell?"
4. "How do cover and advantage interact?"
5. "Can I rage while wearing armor?"

---

## 20. TACTICAL_USAGE
**Intent Definition**: Combat tactics

### Test Questions
1. "How do I effectively use grappling?"
2. "What's the best way to use cover in combat?"
3. "How should I use the Ready action tactically?"
4. "What are good tactics for using my bonus action?"
5. "How can I maximize opportunity attacks?"

---

## 21. ENVIRONMENTAL_RULES
**Intent Definition**: Environment effects

### Test Questions
1. "How does underwater combat work?"
2. "What are the rules for difficult terrain?"
3. "How does fall damage work?"
4. "What happens in extreme cold or heat?"
5. "Explain the rules for darkness and dim light"

---

## 22. CREATURE_ABILITIES
**Intent Definition**: Monster special abilities

### Test Questions
1. "What special abilities does a lich have?"
2. "Describe a dragon's breath weapon"
3. "What abilities do vampires have?"
4. "What special traits does a beholder possess?"
5. "Explain a mind flayer's powers"

---

## 23. SAVING_THROWS
**Intent Definition**: Save mechanics

### Test Questions
1. "When do I make a Wisdom saving throw?"
2. "How do saving throws work?"
3. "What's the DC for a saving throw?"
4. "Explain Dexterity saving throws"
5. "What determines saving throw modifiers?"

---

## 24. MAGIC_ITEM_USAGE
**Intent Definition**: Magic item mechanics

### Test Questions
1. "How does a Bag of Holding work?"
2. "What does attunement mean for magic items?"
3. "Explain how to use a Ring of Protection"
4. "How many magic items can I attune to?"
5. "What does a Cloak of Invisibility do?"

---

## 25. PLANAR_PROPERTIES
**Intent Definition**: Plane characteristics

### Test Questions
1. "What are the properties of the Feywild?"
2. "Describe the Nine Hells"
3. "What is the Shadowfell like?"
4. "Explain the Astral Plane"
5. "What are the characteristics of the Elemental Plane of Fire?"

---

## 26. DOWNTIME_ACTIVITIES
**Intent Definition**: Non-adventure activities

### Test Questions
1. "What can I do during downtime?"
2. "How does crafting work in downtime?"
3. "What downtime activities are available?"
4. "Can I research things during downtime?"
5. "How do I train for tool proficiency during downtime?"

---

## 27. SUBCLASS_FEATURES
**Intent Definition**: Subclass abilities

### Test Questions
1. "What does a Circle of the Moon druid get?"
2. "Describe the Battle Master fighter abilities"
3. "What features does an Evocation wizard have?"
4. "Explain the Assassin rogue subclass"
5. "What abilities does a Life Domain cleric get?"

---

## 28. COST_LOOKUP
**Intent Definition**: Item pricing

### Test Questions
1. "How much does plate armor cost?"
2. "What's the price of a longsword?"
3. "How much gold does a healing potion cost?"
4. "What's the cost of a horse?"
5. "How expensive is chain mail?"

---

## 29. LEGENDARY_MECHANICS
**Intent Definition**: Legendary creature rules

### Test Questions
1. "How do legendary actions work?"
2. "What are legendary resistances?"
3. "Explain lair actions"
4. "How many legendary actions can a creature take?"
5. "When do legendary actions reset?"

---

## 30. OPTIMIZATION_ADVICE
**Intent Definition**: Character build advice

### Test Questions
1. "What's the best build for a tank?"
2. "How should I optimize a wizard for damage?"
3. "What's a good fighter build for beginners?"
4. "What feats should a rogue take?"
5. "How do I build an effective healer?"

---

## Additional Test Scenarios

### Combined Intent Testing
Test questions that require multiple intent types:

1. "Compare the fighter and barbarian at level 5, including their features and combat tactics" (COMPARE_ENTITIES + LEVEL_PROGRESSION + TACTICAL_USAGE)
2. "What spells can a wizard cast at 3rd level that deal fire damage?" (CLASS_SPELL_ACCESS + LEVEL_PROGRESSION + FIND_BY_CRITERIA)
3. "How does the poisoned condition affect my attack rolls and saving throws?" (CONDITION_EFFECTS + RULE_MECHANICS + SAVING_THROWS)
4. "What's my AC with plate armor and a shield, and how does cover affect it?" (CALCULATE_VALUES + EQUIPMENT_PROPERTIES + INTERACTION_RULES)

### Entity-Specific Deep Dives
Test comprehensive entity queries:

1. "Tell me everything about the wizard class - creation, features, spell list, and optimization"
2. "Give me complete information on fireball - spell details, who can cast it, and tactical usage"
3. "Explain dwarves comprehensively - traits, darkvision, combat training, and optimization"
4. "Complete guide to grappling - rules, tactics, conditions involved, and feat interactions"

### Conversation History Tests
Test the conversation context tracking:

1. First: "What are the traits of a dwarf?" → Then: "How do they compare to elves?"
2. First: "Tell me about the fighter class" → Then: "What do they get at level 5?"
3. First: "Describe the fireball spell" → Then: "What classes can cast it?"
4. First: "How does concentration work?" → Then: "What breaks it?"
5. First: "What does the poisoned condition do?" → Then: "How do I cure it?"

### Cross-Category Queries
Test queries spanning multiple rulebook categories:

1. "How does a Battle Master fighter use superiority dice in underwater combat?" (CLASS_FEATURES + COMBAT + ENVIRONMENTAL_RULES)
2. "What happens when a wizard casts fireball while on the Elemental Plane of Fire?" (SPELLCASTING + WORLD_LORE + RULE_MECHANICS)
3. "Can a rogue with the Assassin subclass get advantage using cunning action and stealth?" (CLASS_FEATURES + COMBAT + CORE_MECHANICS)

### Edge Cases and Negative Tests

1. "What are the stats for Tiamat?" (legendary/unique creature - may not be in SRD)
2. "How much does a +3 longsword cost?" (magic items don't have standard prices)
3. "What spells can a blood hunter cast?" (non-SRD class)
4. "Describe the Hexblade patron" (Xanathar's content, not in SRD)
5. "What are the rules for firearms?" (optional rules, may not be in SRD)

### Ambiguous Entity Tests
Test entity resolution:

1. "Tell me about rage" (barbarian feature vs general concept)
2. "How does shield work?" (spell vs equipment)
3. "What does invisibility do?" (spell vs condition)
4. "Explain action surge" (specific fighter feature)
5. "Describe wild shape" (specific druid feature)

### Calculation and Math Tests
Test numerical reasoning:

1. "If I'm a level 5 fighter with 18 Strength using a greatsword, what's my attack bonus and damage?"
2. "Calculate spell save DC for a wizard with 20 Intelligence and proficiency +4"
3. "What's the AC of a fighter wearing plate armor with a shield and the Defense fighting style?"
4. "How much damage does a level 11 rogue's sneak attack do?"
5. "What's the average damage of fireball at 5th level?"

---

## Testing Methodology

### Systematic Testing Approach
1. Test each intent category with all 5 questions
2. Verify correct intent classification in debug output
3. Confirm relevant rulebook sections are retrieved
4. Check that conversation history maintains context
5. Validate entity extraction and normalization

### Performance Benchmarks
- Intent classification should complete in <500ms
- Entity extraction should identify 90%+ of relevant entities
- Section retrieval should find correct content 95%+ of time
- Semantic search should rank most relevant section first 80%+ of time

### Common Issues to Watch For
- Intent misclassification (e.g., SPELL_DETAILS routed to DESCRIBE_ENTITY)
- Entity normalization failures (e.g., "dwarves" not resolving to "dwarf")
- Missing relevant sections due to poor semantic matching
- Category filtering too aggressive (excluding relevant content)
- Conversation history not preserving entity references

---

## Debug Mode Usage

For detailed routing and context information:
```python
# Examine the central engine's decision-making
# Run queries and check:
# - Detected intentions
# - Extracted and normalized entities
# - Category filtering applied
# - Semantic search scores
# - Section selection logic
# - Final context assembly
```

---

## Notes on Rulebook Coverage

The current knowledge base includes:
- **Full D&D 5e SRD**: All core rules, spells, classes, races, monsters from the System Reference Document

Test questions are designed to work with SRD content. Questions about non-SRD content (e.g., Xanathar's Guide, Tasha's Cauldron) will not find results unless those sources are added to the knowledge base.

### Content Limitations
- No campaign-specific content (e.g., Forgotten Realms specific lore)
- No non-SRD subclasses (e.g., Hexblade, Gloomstalker)
- No optional rules from DMG (e.g., firearms, crafting magic items)
- Limited world lore (only core pantheons and planes)

### Best Practices for Testing
1. Start with core entity queries (races, classes, spells)
2. Test rule mechanics with common questions
3. Use conversation history to test follow-ups
4. Try edge cases to understand system limitations
5. Compare results across similar queries for consistency
