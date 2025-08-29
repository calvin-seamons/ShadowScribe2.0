# Rulebook Query Intentions - Retrieval Strategies

## 1. **describe_entity**
- **Genres**: Races, Classes, Spells, Magic Items, Monsters, Equipment, Feats
- **Example**: "What are the traits of a dwarf?"
- **Entities needed**: Single entity required
- **Retrieval strategy**: Direct section grab - find the exact header/subsection for the entity

## 2. **compare_entities**
- **Genres**: Races, Classes, Spells, Equipment, Feats
- **Example**: "What's the difference between a wizard and a sorcerer?"
- **Entities needed**: Multiple entities required (usually 2-3)
- **Retrieval strategy**: Grab full subsections for each entity, then semantic search for comparison keywords

## 3. **level_progression**
- **Genres**: Classes, Beyond 1st Level
- **Example**: "What does a fighter get at level 5?"
- **Entities needed**: Class name required, level number required
- **Retrieval strategy**: Grab entire class section, focus on level-specific features

## 4. **action_options**
- **Genres**: Combat, Spellcasting
- **Example**: "What can I do on my turn in combat?"
- **Entities needed**: Optional (specific action names)
- **Retrieval strategy**: Grab "Actions in Combat" section entirely

## 5. **rule_mechanics**
- **Genres**: Using Ability Scores, Combat, Spellcasting, Adventuring
- **Example**: "How does concentration work?"
- **Entities needed**: Single rule/mechanic name required
- **Retrieval strategy**: Semantic search for the specific mechanic across relevant chapters

## 6. **calculate_values**
- **Genres**: Using Ability Scores, Combat, Equipment
- **Example**: "What's my AC with chain mail and a shield?"
- **Entities needed**: Multiple entities (equipment pieces, stats)
- **Retrieval strategy**: Grab armor section + semantic search for AC calculation rules

## 7. **spell_details**
- **Genres**: Spell Lists, Spellcasting
- **Example**: "What does fireball do?"
- **Entities needed**: Single spell name required
- **Retrieval strategy**: Direct lookup in spell descriptions section

## 8. **class_spell_access**
- **Genres**: Spell Lists, Classes
- **Example**: "What spells can a ranger learn?"
- **Entities needed**: Single class name required
- **Retrieval strategy**: Grab entire class spell list subsection

## 9. **monster_stats**
- **Genres**: Monsters, Miscellaneous Creatures
- **Example**: "What are the stats for a red dragon?"
- **Entities needed**: Single monster name required
- **Retrieval strategy**: Direct section grab for specific monster entry

## 10. **condition_effects**
- **Genres**: Adventuring, Combat
- **Example**: "What does being poisoned do?"
- **Entities needed**: Single condition name required
- **Retrieval strategy**: Grab conditions section, find specific condition

## 11. **character_creation**
- **Genres**: Races, Classes, Equipment, Beyond 1st Level
- **Example**: "How do I create a character?"
- **Entities needed**: None required
- **Retrieval strategy**: Semantic search across character creation topics + grab overview sections

## 12. **multiclass_rules**
- **Genres**: Beyond 1st Level, Classes
- **Example**: "Can I multiclass barbarian and wizard?"
- **Entities needed**: Multiple class names required
- **Retrieval strategy**: Grab multiclassing section + specific class requirements

## 13. **equipment_properties**
- **Genres**: Equipment, Magic Items
- **Example**: "What does the finesse property mean?"
- **Entities needed**: Single property name required
- **Retrieval strategy**: Grab weapon properties subsection

## 14. **damage_types**
- **Genres**: Combat, Spells, Monsters
- **Example**: "How does fire damage work?"
- **Entities needed**: Single damage type required
- **Retrieval strategy**: Semantic search for damage type across combat and resistance rules

## 15. **rest_mechanics**
- **Genres**: Adventuring, Classes
- **Example**: "What happens during a long rest?"
- **Entities needed**: Rest type required (short/long)
- **Retrieval strategy**: Grab resting section from Adventuring

## 16. **skill_usage**
- **Genres**: Using Ability Scores
- **Example**: "When do I use Investigation vs Perception?"
- **Entities needed**: Multiple skill names required
- **Retrieval strategy**: Grab skills section + semantic search for specific skill uses

## 17. **find_by_criteria**
- **Genres**: Spells, Monsters, Equipment, Magic Items
- **Example**: "What spells deal thunder damage?"
- **Entities needed**: Criteria/property required, no specific entity
- **Retrieval strategy**: Semantic search across relevant list with filtering

## 18. **prerequisite_check**
- **Genres**: Feats, Classes, Beyond 1st Level
- **Example**: "What do I need to take the Grappler feat?"
- **Entities needed**: Single entity required
- **Retrieval strategy**: Direct lookup for entity + prerequisites section

## 19. **interaction_rules**
- **Genres**: Any (context-dependent)
- **Example**: "How does invisibility interact with opportunity attacks?"
- **Entities needed**: Multiple entities/concepts required
- **Retrieval strategy**: Semantic search for both concepts + intersection points

## 20. **tactical_usage**
- **Genres**: Combat, Spells, Monsters
- **Example**: "How do I effectively use grappling?"
- **Entities needed**: Single tactic/ability required
- **Retrieval strategy**: Grab relevant mechanic + semantic search for tactical advice

## 21. **environmental_rules**
- **Genres**: Adventuring, Combat
- **Example**: "How does underwater combat work?"
- **Entities needed**: Environment type required
- **Retrieval strategy**: Grab specific environment section

## 22. **creature_abilities**
- **Genres**: Monsters, Miscellaneous Creatures
- **Example**: "What special abilities does a lich have?"
- **Entities needed**: Single creature required
- **Retrieval strategy**: Grab full monster entry including abilities

## 23. **saving_throws**
- **Genres**: Using Ability Scores, Combat, Spells
- **Example**: "When do I make a Wisdom saving throw?"
- **Entities needed**: Save type optional
- **Retrieval strategy**: Semantic search for saving throw situations

## 24. **magic_item_usage**
- **Genres**: Magic Items
- **Example**: "How does a Bag of Holding work?"
- **Entities needed**: Single item required
- **Retrieval strategy**: Direct lookup in magic items section

## 25. **planar_properties**
- **Genres**: The Planes of Existence
- **Example**: "What are the properties of the Feywild?"
- **Entities needed**: Single plane name required
- **Retrieval strategy**: Grab specific plane subsection

## 26. **downtime_activities**
- **Genres**: Adventuring, Beyond 1st Level
- **Example**: "What can I do during downtime?"
- **Entities needed**: Optional activity name
- **Retrieval strategy**: Grab downtime activities section

## 27. **subclass_features**
- **Genres**: Classes
- **Example**: "What does a Circle of the Moon druid get?"
- **Entities needed**: Class and subclass names required
- **Retrieval strategy**: Grab specific subclass section

## 28. **cost_lookup**
- **Genres**: Equipment, Services
- **Example**: "How much does plate armor cost?"
- **Entities needed**: Single item/service required
- **Retrieval strategy**: Direct lookup in equipment tables

## 29. **legendary_mechanics**
- **Genres**: Monsters, Magic Items
- **Example**: "How do legendary actions work?"
- **Entities needed**: None or specific creature
- **Retrieval strategy**: Grab legendary creatures section + specific examples

## 30. **optimization_advice**
- **Genres**: Classes, Races, Feats, Equipment (multiple)
- **Example**: "What's the best build for a tank?"
- **Entities needed**: Concept/role required
- **Retrieval strategy**: Semantic search across character options for synergies