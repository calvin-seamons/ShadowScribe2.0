"""
Rulebook Query Templates

Templates for generating synthetic training data for the rulebook tool.
Each intent has 10-15 templates that can be filled with entity slots.

31 Intents:
- describe_entity
- compare_entities
- level_progression
- action_options
- rule_mechanics
- calculate_values
- spell_details
- class_spell_access
- monster_stats
- condition_effects
- character_creation
- multiclass_rules
- equipment_properties
- damage_types
- rest_mechanics
- skill_usage
- find_by_criteria
- prerequisite_check
- interaction_rules
- tactical_usage
- environmental_rules
- creature_abilities
- saving_throws
- magic_item_usage
- planar_properties
- downtime_activities
- subclass_features
- cost_lookup
- legendary_mechanics
- optimization_advice
"""

# =============================================================================
# DESCRIBE_ENTITY - Describe a single D&D entity (spell, creature, item, etc.)
# =============================================================================

DESCRIBE_ENTITY_TEMPLATES = [
    {"template": "What is {spell}?", "slots": {"spell": "spell"}},
    {"template": "Tell me about {creature}", "slots": {"creature": "creature"}},
    {"template": "Describe {item}", "slots": {"item": "item"}},
    {"template": "What does {spell} do?", "slots": {"spell": "spell"}},
    {"template": "Explain the {feature} feature", "slots": {"feature": "feature"}},
    {"template": "How does {spell} work?", "slots": {"spell": "spell"}},
    {"template": "What is {condition}?", "slots": {"condition": "condition"}},
    {"template": "Give me info on {creature}", "slots": {"creature": "creature"}},
    {"template": "What's the description of {spell}?", "slots": {"spell": "spell"}},
    {"template": "Tell me everything about {item}", "slots": {"item": "item"}},
    {"template": "Explain {feature} to me", "slots": {"feature": "feature"}},
    {"template": "What are the details of {spell}?", "slots": {"spell": "spell"}},
    {"template": "Describe the {creature} creature", "slots": {"creature": "creature"}},
]

# =============================================================================
# COMPARE_ENTITIES - Compare two or more D&D entities
# =============================================================================

COMPARE_ENTITIES_TEMPLATES = [
    {"template": "What's the difference between {spell1} and {spell2}?", "slots": {"spell1": "spell", "spell2": "spell"}},
    {"template": "Compare {weapon1} vs {weapon2}", "slots": {"weapon1": "weapon", "weapon2": "weapon"}},
    {"template": "Which is better, {class1} or {class2}?", "slots": {"class1": "class", "class2": "class"}},
    {"template": "How does {spell1} compare to {spell2}?", "slots": {"spell1": "spell", "spell2": "spell"}},
    {"template": "{creature1} vs {creature2}, who would win?", "slots": {"creature1": "creature", "creature2": "creature"}},
    {"template": "What are the differences between {race1} and {race2}?", "slots": {"race1": "race", "race2": "race"}},
    {"template": "Compare the {armor1} and {armor2}", "slots": {"armor1": "armor", "armor2": "armor"}},
    {"template": "Which is stronger, {creature1} or {creature2}?", "slots": {"creature1": "creature", "creature2": "creature"}},
    {"template": "Difference between {condition1} and {condition2}?", "slots": {"condition1": "condition", "condition2": "condition"}},
    {"template": "{class1} vs {class2} for damage?", "slots": {"class1": "class", "class2": "class"}},
    {"template": "Is {spell1} or {spell2} better for combat?", "slots": {"spell1": "spell", "spell2": "spell"}},
]

# =============================================================================
# LEVEL_PROGRESSION - Class progression, leveling, XP
# =============================================================================

LEVEL_PROGRESSION_TEMPLATES = [
    {"template": "What do {class_name}s get at level {level}?", "slots": {"class_name": "class", "level": "level"}},
    {"template": "How much XP do I need to reach level {level}?", "slots": {"level": "level"}},
    {"template": "What features does a {class_name} get when they level up?", "slots": {"class_name": "class"}},
    {"template": "When do {class_name}s get Extra Attack?", "slots": {"class_name": "class"}},
    {"template": "What's the proficiency bonus at level {level}?", "slots": {"level": "level"}},
    {"template": "What spell slots does a level {level} {class_name} have?", "slots": {"level": "level", "class_name": "class"}},
    {"template": "{class_name} progression table", "slots": {"class_name": "class"}},
    {"template": "When do {class_name}s get their subclass?", "slots": {"class_name": "class"}},
    {"template": "What level do {class_name}s get {feature}?", "slots": {"class_name": "class", "feature": "feature"}},
    {"template": "XP requirements for level {level}", "slots": {"level": "level"}},
    {"template": "What abilities does a {class_name} unlock at higher levels?", "slots": {"class_name": "class"}},
    {"template": "Spell slot progression for {class_name}", "slots": {"class_name": "class"}},
]

# =============================================================================
# ACTION_OPTIONS - Actions, bonus actions, reactions in combat
# =============================================================================

ACTION_OPTIONS_TEMPLATES = [
    {"template": "What actions can I take in combat?", "slots": {}},
    {"template": "What bonus actions are available?", "slots": {}},
    {"template": "What can I do with my reaction?", "slots": {}},
    {"template": "Can I attack and cast a spell in the same turn?", "slots": {}},
    {"template": "What is the Dodge action?", "slots": {}},
    {"template": "How does the Ready action work?", "slots": {}},
    {"template": "Can I move between attacks?", "slots": {}},
    {"template": "What's the difference between an action and a bonus action?", "slots": {}},
    {"template": "How many actions do I get per turn?", "slots": {}},
    {"template": "What is the Help action?", "slots": {}},
    {"template": "Can I use a bonus action spell and a regular spell?", "slots": {}},
    {"template": "What triggers an opportunity attack?", "slots": {}},
    {"template": "What free actions can I take?", "slots": {}},
    {"template": "How does the Dash action work?", "slots": {}},
]

# =============================================================================
# RULE_MECHANICS - General rules and mechanics
# =============================================================================

RULE_MECHANICS_TEMPLATES = [
    {"template": "How does {mechanic} work?", "slots": {"mechanic": "mechanic"}},
    {"template": "What are the rules for {mechanic}?", "slots": {"mechanic": "mechanic"}},
    {"template": "Explain {mechanic}", "slots": {"mechanic": "mechanic"}},
    {"template": "How do you calculate {mechanic}?", "slots": {"mechanic": "mechanic"}},
    {"template": "What's the rule for {mechanic}?", "slots": {"mechanic": "mechanic"}},
    {"template": "How does advantage work?", "slots": {}},
    {"template": "What is disadvantage?", "slots": {}},
    {"template": "How do critical hits work?", "slots": {}},
    {"template": "What happens on a natural 20?", "slots": {}},
    {"template": "How does cover work?", "slots": {}},
    {"template": "What are the flanking rules?", "slots": {}},
    {"template": "How does concentration work?", "slots": {}},
    {"template": "What breaks concentration?", "slots": {}},
]

# =============================================================================
# CALCULATE_VALUES - Numerical calculations
# =============================================================================

CALCULATE_VALUES_TEMPLATES = [
    {"template": "How do I calculate my AC?", "slots": {}},
    {"template": "How is spell save DC calculated?", "slots": {}},
    {"template": "What's the formula for attack bonus?", "slots": {}},
    {"template": "How do I calculate damage for {spell}?", "slots": {"spell": "spell"}},
    {"template": "How much damage does {weapon} do?", "slots": {"weapon": "weapon"}},
    {"template": "How do I figure out my hit points?", "slots": {}},
    {"template": "What's my carry capacity based on?", "slots": {}},
    {"template": "How do I calculate initiative?", "slots": {}},
    {"template": "What modifies my saving throws?", "slots": {}},
    {"template": "How is passive perception calculated?", "slots": {}},
    {"template": "What's the damage formula for {spell}?", "slots": {"spell": "spell"}},
    {"template": "How much healing does {spell} do?", "slots": {"spell": "spell"}},
]

# =============================================================================
# SPELL_DETAILS - Specific spell information
# =============================================================================

SPELL_DETAILS_TEMPLATES = [
    {"template": "What are the components for {spell}?", "slots": {"spell": "spell"}},
    {"template": "What's the range of {spell}?", "slots": {"spell": "spell"}},
    {"template": "What level is {spell}?", "slots": {"spell": "spell"}},
    {"template": "Is {spell} concentration?", "slots": {"spell": "spell"}},
    {"template": "What's the duration of {spell}?", "slots": {"spell": "spell"}},
    {"template": "What's the casting time for {spell}?", "slots": {"spell": "spell"}},
    {"template": "Can {spell} be upcast?", "slots": {"spell": "spell"}},
    {"template": "What school of magic is {spell}?", "slots": {"spell": "spell"}},
    {"template": "Does {spell} require a saving throw?", "slots": {"spell": "spell"}},
    {"template": "What does {spell} do at higher levels?", "slots": {"spell": "spell"}},
    {"template": "Is {spell} a ritual?", "slots": {"spell": "spell"}},
    {"template": "What's the area of effect for {spell}?", "slots": {"spell": "spell"}},
    {"template": "Does {spell} have verbal components?", "slots": {"spell": "spell"}},
]

# =============================================================================
# CLASS_SPELL_ACCESS - Which classes can cast which spells
# =============================================================================

CLASS_SPELL_ACCESS_TEMPLATES = [
    {"template": "Can {class_name}s cast {spell}?", "slots": {"class_name": "class", "spell": "spell"}},
    {"template": "What classes have access to {spell}?", "slots": {"spell": "spell"}},
    {"template": "Is {spell} on the {class_name} spell list?", "slots": {"spell": "spell", "class_name": "class"}},
    {"template": "What spells can a {class_name} learn?", "slots": {"class_name": "class"}},
    {"template": "What healing spells can a {class_name} cast?", "slots": {"class_name": "class"}},
    {"template": "Does a {class_name} get {spell}?", "slots": {"class_name": "class", "spell": "spell"}},
    {"template": "What level {level} spells do {class_name}s get?", "slots": {"level": "spell_level", "class_name": "class"}},
    {"template": "Can a {class_name} learn {spell} from a scroll?", "slots": {"class_name": "class", "spell": "spell"}},
    {"template": "What's on the {class_name} spell list?", "slots": {"class_name": "class"}},
    {"template": "Best {class_name} spells at level {level}?", "slots": {"class_name": "class", "level": "level"}},
    {"template": "What damage spells can {class_name}s use?", "slots": {"class_name": "class"}},
]

# =============================================================================
# MONSTER_STATS - Monster/creature statistics
# =============================================================================

MONSTER_STATS_TEMPLATES = [
    {"template": "What's the CR of a {creature}?", "slots": {"creature": "creature"}},
    {"template": "How many hit points does a {creature} have?", "slots": {"creature": "creature"}},
    {"template": "What's the AC of a {creature}?", "slots": {"creature": "creature"}},
    {"template": "What attacks does a {creature} have?", "slots": {"creature": "creature"}},
    {"template": "What are the {creature}'s stats?", "slots": {"creature": "creature"}},
    {"template": "What resistances does a {creature} have?", "slots": {"creature": "creature"}},
    {"template": "What immunities does a {creature} have?", "slots": {"creature": "creature"}},
    {"template": "What's a {creature}'s speed?", "slots": {"creature": "creature"}},
    {"template": "Does a {creature} have legendary actions?", "slots": {"creature": "creature"}},
    {"template": "What abilities does a {creature} have?", "slots": {"creature": "creature"}},
    {"template": "What's the {creature}'s challenge rating?", "slots": {"creature": "creature"}},
    {"template": "How much damage does a {creature} deal?", "slots": {"creature": "creature"}},
]

# =============================================================================
# CONDITION_EFFECTS - Status conditions and their effects
# =============================================================================

CONDITION_EFFECTS_TEMPLATES = [
    {"template": "What does {condition} do?", "slots": {"condition": "condition"}},
    {"template": "What are the effects of being {condition}?", "slots": {"condition": "condition"}},
    {"template": "How do I remove {condition}?", "slots": {"condition": "condition"}},
    {"template": "What causes the {condition} condition?", "slots": {"condition": "condition"}},
    {"template": "Can I attack while {condition}?", "slots": {"condition": "condition"}},
    {"template": "What spells cause {condition}?", "slots": {"condition": "condition"}},
    {"template": "What can I do while {condition}?", "slots": {"condition": "condition"}},
    {"template": "Does {condition} give advantage or disadvantage?", "slots": {"condition": "condition"}},
    {"template": "How long does {condition} last?", "slots": {"condition": "condition"}},
    {"template": "What's the difference between {condition1} and {condition2}?", "slots": {"condition1": "condition", "condition2": "condition"}},
    {"template": "List all conditions", "slots": {}},
]

# =============================================================================
# CHARACTER_CREATION - Character creation rules
# =============================================================================

CHARACTER_CREATION_TEMPLATES = [
    {"template": "How do I create a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "What are the steps for character creation?", "slots": {}},
    {"template": "How do I determine ability scores?", "slots": {}},
    {"template": "What's point buy?", "slots": {}},
    {"template": "How do I roll for stats?", "slots": {}},
    {"template": "What equipment does a {class_name} start with?", "slots": {"class_name": "class"}},
    {"template": "What backgrounds are available?", "slots": {}},
    {"template": "How do I pick a race?", "slots": {}},
    {"template": "What are the {race} racial traits?", "slots": {"race": "race"}},
    {"template": "Starting gold for a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "How do I choose skills?", "slots": {}},
    {"template": "What's the standard array?", "slots": {}},
]

# =============================================================================
# MULTICLASS_RULES - Multiclassing rules
# =============================================================================

MULTICLASS_RULES_TEMPLATES = [
    {"template": "How does multiclassing work?", "slots": {}},
    {"template": "What are the requirements to multiclass into {class_name}?", "slots": {"class_name": "class"}},
    {"template": "How do spell slots work when multiclassing?", "slots": {}},
    {"template": "Can I multiclass {class1} and {class2}?", "slots": {"class1": "class", "class2": "class"}},
    {"template": "What proficiencies do I get from multiclassing?", "slots": {}},
    {"template": "Does multiclassing affect my proficiency bonus?", "slots": {}},
    {"template": "When should I take a level in {class_name}?", "slots": {"class_name": "class"}},
    {"template": "What's the minimum stats for multiclassing?", "slots": {}},
    {"template": "How do extra attacks work with multiclass?", "slots": {}},
    {"template": "Can I multiclass as a {race}?", "slots": {"race": "race"}},
    {"template": "Multiclass spell slot table", "slots": {}},
]

# =============================================================================
# EQUIPMENT_PROPERTIES - Weapon and armor properties
# =============================================================================

EQUIPMENT_PROPERTIES_TEMPLATES = [
    {"template": "What does {property} mean on a weapon?", "slots": {"property": "weapon_property"}},
    {"template": "What's the damage of a {weapon}?", "slots": {"weapon": "weapon"}},
    {"template": "Is {weapon} finesse?", "slots": {"weapon": "weapon"}},
    {"template": "What weapons have the {property} property?", "slots": {"property": "weapon_property"}},
    {"template": "What's the range of a {weapon}?", "slots": {"weapon": "weapon"}},
    {"template": "What armor gives the best AC?", "slots": {}},
    {"template": "Does {armor} have a stealth disadvantage?", "slots": {"armor": "armor"}},
    {"template": "What's the AC of {armor}?", "slots": {"armor": "armor"}},
    {"template": "Is {weapon} a martial or simple weapon?", "slots": {"weapon": "weapon"}},
    {"template": "What properties does {weapon} have?", "slots": {"weapon": "weapon"}},
    {"template": "What's the difference between light and heavy armor?", "slots": {}},
    {"template": "Can I dual wield {weapon}?", "slots": {"weapon": "weapon"}},
]

# =============================================================================
# DAMAGE_TYPES - Types of damage
# =============================================================================

DAMAGE_TYPES_TEMPLATES = [
    {"template": "What creatures are resistant to {damage_type} damage?", "slots": {"damage_type": "damage_type"}},
    {"template": "What spells deal {damage_type} damage?", "slots": {"damage_type": "damage_type"}},
    {"template": "What's the difference between {damage_type1} and {damage_type2}?", "slots": {"damage_type1": "damage_type", "damage_type2": "damage_type"}},
    {"template": "Is {damage_type} a common resistance?", "slots": {"damage_type": "damage_type"}},
    {"template": "What weapons deal {damage_type} damage?", "slots": {"damage_type": "damage_type"}},
    {"template": "List all damage types", "slots": {}},
    {"template": "What's the best damage type to use?", "slots": {}},
    {"template": "What creatures are immune to {damage_type}?", "slots": {"damage_type": "damage_type"}},
    {"template": "Does {spell} deal {damage_type} damage?", "slots": {"spell": "spell", "damage_type": "damage_type"}},
    {"template": "How does {damage_type} resistance work?", "slots": {"damage_type": "damage_type"}},
]

# =============================================================================
# REST_MECHANICS - Short rest, long rest, recovery
# =============================================================================

REST_MECHANICS_TEMPLATES = [
    {"template": "What do I recover on a short rest?", "slots": {}},
    {"template": "What do I recover on a long rest?", "slots": {}},
    {"template": "How long is a short rest?", "slots": {}},
    {"template": "How long is a long rest?", "slots": {}},
    {"template": "Do I recover spell slots on a short rest?", "slots": {}},
    {"template": "How do hit dice work?", "slots": {}},
    {"template": "Can I take a short rest during combat?", "slots": {}},
    {"template": "Does {class_name} recover abilities on short rest?", "slots": {"class_name": "class"}},
    {"template": "What interrupts a long rest?", "slots": {}},
    {"template": "How many hit dice do I recover?", "slots": {}},
    {"template": "What features reset on a short rest?", "slots": {}},
]

# =============================================================================
# SKILL_USAGE - Skills and ability checks
# =============================================================================

SKILL_USAGE_TEMPLATES = [
    {"template": "What can I use {skill} for?", "slots": {"skill": "skill"}},
    {"template": "When do I roll {skill}?", "slots": {"skill": "skill"}},
    {"template": "What ability is {skill} based on?", "slots": {"skill": "skill"}},
    {"template": "What's the difference between {skill1} and {skill2}?", "slots": {"skill1": "skill", "skill2": "skill"}},
    {"template": "Can I use {skill} in combat?", "slots": {"skill": "skill"}},
    {"template": "How does contested {skill} work?", "slots": {"skill": "skill"}},
    {"template": "What's a typical DC for {skill}?", "slots": {"skill": "skill"}},
    {"template": "List all skills", "slots": {}},
    {"template": "What skills does a {class_name} get?", "slots": {"class_name": "class"}},
    {"template": "Can I help with a {skill} check?", "slots": {"skill": "skill"}},
    {"template": "When would I roll {ability} instead of a skill?", "slots": {"ability": "ability"}},
]

# =============================================================================
# FIND_BY_CRITERIA - Search for entities matching criteria
# =============================================================================

FIND_BY_CRITERIA_TEMPLATES = [
    {"template": "What spells deal fire damage?", "slots": {}},
    {"template": "List all healing spells", "slots": {}},
    {"template": "What level {level} spells are there?", "slots": {"level": "spell_level"}},
    {"template": "What concentration spells are available?", "slots": {}},
    {"template": "What creatures have a CR of 5?", "slots": {}},
    {"template": "What spells don't require concentration?", "slots": {}},
    {"template": "What finesse weapons are there?", "slots": {}},
    {"template": "List all cantrips", "slots": {}},
    {"template": "What spells have a range of touch?", "slots": {}},
    {"template": "What ritual spells are there?", "slots": {}},
    {"template": "What bonus action spells exist?", "slots": {}},
    {"template": "What creatures are undead?", "slots": {}},
]

# =============================================================================
# PREREQUISITE_CHECK - Check if something meets requirements
# =============================================================================

PREREQUISITE_CHECK_TEMPLATES = [
    {"template": "What are the prerequisites for {feat}?", "slots": {"feat": "feat"}},
    {"template": "Do I need anything to cast {spell}?", "slots": {"spell": "spell"}},
    {"template": "What level do I need to be for {spell}?", "slots": {"spell": "spell"}},
    {"template": "Can a level {level} {class_name} cast {spell}?", "slots": {"level": "level", "class_name": "class", "spell": "spell"}},
    {"template": "What are the requirements for {feat}?", "slots": {"feat": "feat"}},
    {"template": "Do I need {ability} to multiclass into {class_name}?", "slots": {"ability": "ability", "class_name": "class"}},
    {"template": "What do I need to use {item}?", "slots": {"item": "item"}},
    {"template": "Prerequisites for {feature}?", "slots": {"feature": "feature"}},
    {"template": "Can I take {feat} at level {level}?", "slots": {"feat": "feat", "level": "level"}},
    {"template": "What's required to attune to {item}?", "slots": {"item": "item"}},
]

# =============================================================================
# INTERACTION_RULES - How different rules interact
# =============================================================================

INTERACTION_RULES_TEMPLATES = [
    {"template": "Can I cast {spell} while concentrating on another spell?", "slots": {"spell": "spell"}},
    {"template": "Does {spell} stack with {spell2}?", "slots": {"spell": "spell", "spell2": "spell"}},
    {"template": "Can I use {feature} and {feature2} together?", "slots": {"feature": "feature", "feature2": "feature"}},
    {"template": "How does {spell} interact with {condition}?", "slots": {"spell": "spell", "condition": "condition"}},
    {"template": "Does advantage cancel out disadvantage?", "slots": {}},
    {"template": "Can I use {feature} while {condition}?", "slots": {"feature": "feature", "condition": "condition"}},
    {"template": "Do multiple sources of {damage_type} resistance stack?", "slots": {"damage_type": "damage_type"}},
    {"template": "Can I benefit from multiple {item} items?", "slots": {"item": "item"}},
    {"template": "How does {spell} work with {feature}?", "slots": {"spell": "spell", "feature": "feature"}},
    {"template": "Does {condition} affect {spell}?", "slots": {"condition": "condition", "spell": "spell"}},
]

# =============================================================================
# TACTICAL_USAGE - How to use abilities tactically
# =============================================================================

TACTICAL_USAGE_TEMPLATES = [
    {"template": "When should I use {spell}?", "slots": {"spell": "spell"}},
    {"template": "What's the best way to use {feature}?", "slots": {"feature": "feature"}},
    {"template": "How do I use {spell} effectively?", "slots": {"spell": "spell"}},
    {"template": "Best tactics for a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "When is {spell} most useful?", "slots": {"spell": "spell"}},
    {"template": "How should I position as a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "What's the best use of {feature}?", "slots": {"feature": "feature"}},
    {"template": "Tips for using {spell} in combat?", "slots": {"spell": "spell"}},
    {"template": "How do I maximize damage as a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "Best {class_name} combat strategies?", "slots": {"class_name": "class"}},
]

# =============================================================================
# ENVIRONMENTAL_RULES - Environmental hazards and terrain
# =============================================================================

ENVIRONMENTAL_RULES_TEMPLATES = [
    {"template": "How does difficult terrain work?", "slots": {}},
    {"template": "What are the rules for swimming?", "slots": {}},
    {"template": "How does underwater combat work?", "slots": {}},
    {"template": "What happens in extreme cold?", "slots": {}},
    {"template": "How does falling damage work?", "slots": {}},
    {"template": "What are the rules for climbing?", "slots": {}},
    {"template": "How does lava damage work?", "slots": {}},
    {"template": "What are the rules for suffocation?", "slots": {}},
    {"template": "How does darkness affect combat?", "slots": {}},
    {"template": "What's the effect of being in water?", "slots": {}},
    {"template": "How does fog work?", "slots": {}},
]

# =============================================================================
# CREATURE_ABILITIES - Special creature abilities
# =============================================================================

CREATURE_ABILITIES_TEMPLATES = [
    {"template": "What is {creature_ability}?", "slots": {"creature_ability": "creature_ability"}},
    {"template": "How does {creature_ability} work?", "slots": {"creature_ability": "creature_ability"}},
    {"template": "What creatures have {creature_ability}?", "slots": {"creature_ability": "creature_ability"}},
    {"template": "How do I counter {creature_ability}?", "slots": {"creature_ability": "creature_ability"}},
    {"template": "What does a {creature}'s {creature_ability} do?", "slots": {"creature": "creature", "creature_ability": "creature_ability"}},
    {"template": "How does breath weapon work?", "slots": {}},
    {"template": "What is magic resistance?", "slots": {}},
    {"template": "How does pack tactics work?", "slots": {}},
    {"template": "What is regeneration?", "slots": {}},
    {"template": "How does frightful presence work?", "slots": {}},
    {"template": "What's the difference between fly and hover?", "slots": {}},
]

# =============================================================================
# SAVING_THROWS - Saving throw mechanics
# =============================================================================

SAVING_THROWS_TEMPLATES = [
    {"template": "How do saving throws work?", "slots": {}},
    {"template": "What's a {ability} saving throw used for?", "slots": {"ability": "ability"}},
    {"template": "Which classes get {ability} save proficiency?", "slots": {"ability": "ability"}},
    {"template": "What happens if I fail a save against {spell}?", "slots": {"spell": "spell"}},
    {"template": "What's the DC for {spell}?", "slots": {"spell": "spell"}},
    {"template": "Can I choose to fail a saving throw?", "slots": {}},
    {"template": "What modifies saving throws?", "slots": {}},
    {"template": "How do death saving throws work?", "slots": {}},
    {"template": "What triggers a concentration save?", "slots": {}},
    {"template": "What's the save DC for {creature}'s abilities?", "slots": {"creature": "creature"}},
    {"template": "Do I add proficiency to saving throws?", "slots": {}},
]

# =============================================================================
# MAGIC_ITEM_USAGE - Magic item rules
# =============================================================================

MAGIC_ITEM_USAGE_TEMPLATES = [
    {"template": "How does {magic_item} work?", "slots": {"magic_item": "magic_item"}},
    {"template": "Does {magic_item} require attunement?", "slots": {"magic_item": "magic_item"}},
    {"template": "How many items can I attune to?", "slots": {}},
    {"template": "What's the rarity of {magic_item}?", "slots": {"magic_item": "magic_item"}},
    {"template": "How do I identify a magic item?", "slots": {}},
    {"template": "Can I use {magic_item} as a {class_name}?", "slots": {"magic_item": "magic_item", "class_name": "class"}},
    {"template": "How long does attunement take?", "slots": {}},
    {"template": "What are the charges on {magic_item}?", "slots": {"magic_item": "magic_item"}},
    {"template": "Can {magic_item} be used by anyone?", "slots": {"magic_item": "magic_item"}},
    {"template": "What happens when {magic_item} runs out of charges?", "slots": {"magic_item": "magic_item"}},
]

# =============================================================================
# PLANAR_PROPERTIES - Planes and their effects
# =============================================================================

PLANAR_PROPERTIES_TEMPLATES = [
    {"template": "What are the properties of the {plane}?", "slots": {"plane": "plane"}},
    {"template": "What creatures live in the {plane}?", "slots": {"plane": "plane"}},
    {"template": "How does magic work in the {plane}?", "slots": {"plane": "plane"}},
    {"template": "What's the {plane} like?", "slots": {"plane": "plane"}},
    {"template": "How do I travel to the {plane}?", "slots": {"plane": "plane"}},
    {"template": "What dangers are in the {plane}?", "slots": {"plane": "plane"}},
    {"template": "What spells let me go to other planes?", "slots": {}},
    {"template": "Describe the {plane}", "slots": {"plane": "plane"}},
    {"template": "What's the difference between the {plane1} and {plane2}?", "slots": {"plane1": "plane", "plane2": "plane"}},
    {"template": "What gods are associated with the {plane}?", "slots": {"plane": "plane"}},
]

# =============================================================================
# DOWNTIME_ACTIVITIES - Downtime activities
# =============================================================================

DOWNTIME_ACTIVITIES_TEMPLATES = [
    {"template": "What downtime activities are there?", "slots": {}},
    {"template": "How does crafting work?", "slots": {}},
    {"template": "How do I craft a magic item?", "slots": {}},
    {"template": "What can I do during downtime?", "slots": {}},
    {"template": "How does training work?", "slots": {}},
    {"template": "Can I learn a new language during downtime?", "slots": {}},
    {"template": "How long does it take to craft {item}?", "slots": {"item": "item"}},
    {"template": "What's the cost to craft {item}?", "slots": {"item": "item"}},
    {"template": "How do I run a business during downtime?", "slots": {}},
    {"template": "Can I research during downtime?", "slots": {}},
    {"template": "How do I find work during downtime?", "slots": {}},
]

# =============================================================================
# SUBCLASS_FEATURES - Subclass-specific features
# =============================================================================

SUBCLASS_FEATURES_TEMPLATES = [
    {"template": "What are the {subclass} features?", "slots": {"subclass": "subclass"}},
    {"template": "What does a {subclass} get?", "slots": {"subclass": "subclass"}},
    {"template": "How does {subclass} play?", "slots": {"subclass": "subclass"}},
    {"template": "What's unique about the {subclass}?", "slots": {"subclass": "subclass"}},
    {"template": "What subclasses does {class_name} have?", "slots": {"class_name": "class"}},
    {"template": "When does {subclass} get its features?", "slots": {"subclass": "subclass"}},
    {"template": "Compare {subclass1} vs {subclass2}", "slots": {"subclass1": "subclass", "subclass2": "subclass"}},
    {"template": "What's the best {class_name} subclass?", "slots": {"class_name": "class"}},
    {"template": "What spells does {subclass} get?", "slots": {"subclass": "subclass"}},
    {"template": "How does {subclass} change the {class_name}?", "slots": {"subclass": "subclass", "class_name": "class"}},
]

# =============================================================================
# COST_LOOKUP - Prices and costs
# =============================================================================

COST_LOOKUP_TEMPLATES = [
    {"template": "How much does {item} cost?", "slots": {"item": "item"}},
    {"template": "What's the price of {weapon}?", "slots": {"weapon": "weapon"}},
    {"template": "How much is {armor}?", "slots": {"armor": "armor"}},
    {"template": "What's the cost of {spell} components?", "slots": {"spell": "spell"}},
    {"template": "How much gold for a {item}?", "slots": {"item": "item"}},
    {"template": "What's the value of {magic_item}?", "slots": {"magic_item": "magic_item"}},
    {"template": "How expensive is {item}?", "slots": {"item": "item"}},
    {"template": "Cost of living expenses?", "slots": {}},
    {"template": "How much does it cost to hire a {creature}?", "slots": {"creature": "creature"}},
    {"template": "What's the price of a {spell} scroll?", "slots": {"spell": "spell"}},
]

# =============================================================================
# LEGENDARY_MECHANICS - Legendary creatures and actions
# =============================================================================

LEGENDARY_MECHANICS_TEMPLATES = [
    {"template": "What are legendary actions?", "slots": {}},
    {"template": "How do legendary resistances work?", "slots": {}},
    {"template": "How many legendary actions does a {creature} have?", "slots": {"creature": "creature"}},
    {"template": "What legendary actions can a {creature} take?", "slots": {"creature": "creature"}},
    {"template": "When can a creature use legendary actions?", "slots": {}},
    {"template": "What's a lair action?", "slots": {}},
    {"template": "Does a {creature} have lair actions?", "slots": {"creature": "creature"}},
    {"template": "How do I deal with legendary resistance?", "slots": {}},
    {"template": "What's a mythic creature?", "slots": {}},
    {"template": "How many legendary resistances does a {creature} have?", "slots": {"creature": "creature"}},
]

# =============================================================================
# OPTIMIZATION_ADVICE - Build and optimization advice
# =============================================================================

OPTIMIZATION_ADVICE_TEMPLATES = [
    {"template": "What's the best race for a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "How do I optimize a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "Best feats for a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "What stats should I prioritize for {class_name}?", "slots": {"class_name": "class"}},
    {"template": "Best multiclass for {class_name}?", "slots": {"class_name": "class"}},
    {"template": "How do I build a tank?", "slots": {}},
    {"template": "Best damage dealing build?", "slots": {}},
    {"template": "How do I maximize spell damage?", "slots": {}},
    {"template": "What's a good support build?", "slots": {}},
    {"template": "Best {race} class combinations?", "slots": {"race": "race"}},
    {"template": "How do I build for AC?", "slots": {}},
]

# =============================================================================
# CONSOLIDATED TEMPLATES
# =============================================================================

RULEBOOK_TEMPLATES = {
    "describe_entity": DESCRIBE_ENTITY_TEMPLATES,
    "compare_entities": COMPARE_ENTITIES_TEMPLATES,
    "level_progression": LEVEL_PROGRESSION_TEMPLATES,
    "action_options": ACTION_OPTIONS_TEMPLATES,
    "rule_mechanics": RULE_MECHANICS_TEMPLATES,
    "calculate_values": CALCULATE_VALUES_TEMPLATES,
    "spell_details": SPELL_DETAILS_TEMPLATES,
    "class_spell_access": CLASS_SPELL_ACCESS_TEMPLATES,
    "monster_stats": MONSTER_STATS_TEMPLATES,
    "condition_effects": CONDITION_EFFECTS_TEMPLATES,
    "character_creation": CHARACTER_CREATION_TEMPLATES,
    "multiclass_rules": MULTICLASS_RULES_TEMPLATES,
    "equipment_properties": EQUIPMENT_PROPERTIES_TEMPLATES,
    "damage_types": DAMAGE_TYPES_TEMPLATES,
    "rest_mechanics": REST_MECHANICS_TEMPLATES,
    "skill_usage": SKILL_USAGE_TEMPLATES,
    "find_by_criteria": FIND_BY_CRITERIA_TEMPLATES,
    "prerequisite_check": PREREQUISITE_CHECK_TEMPLATES,
    "interaction_rules": INTERACTION_RULES_TEMPLATES,
    "tactical_usage": TACTICAL_USAGE_TEMPLATES,
    "environmental_rules": ENVIRONMENTAL_RULES_TEMPLATES,
    "creature_abilities": CREATURE_ABILITIES_TEMPLATES,
    "saving_throws": SAVING_THROWS_TEMPLATES,
    "magic_item_usage": MAGIC_ITEM_USAGE_TEMPLATES,
    "planar_properties": PLANAR_PROPERTIES_TEMPLATES,
    "downtime_activities": DOWNTIME_ACTIVITIES_TEMPLATES,
    "subclass_features": SUBCLASS_FEATURES_TEMPLATES,
    "cost_lookup": COST_LOOKUP_TEMPLATES,
    "legendary_mechanics": LEGENDARY_MECHANICS_TEMPLATES,
    "optimization_advice": OPTIMIZATION_ADVICE_TEMPLATES,
}

# Intent descriptions for reference
RULEBOOK_INTENT_DESCRIPTIONS = {
    "describe_entity": "Describe a single D&D entity (spell, creature, item, class, etc.)",
    "compare_entities": "Compare two or more D&D entities",
    "level_progression": "Class progression, leveling up, XP requirements",
    "action_options": "Actions, bonus actions, reactions available in combat",
    "rule_mechanics": "General rules and mechanics explanations",
    "calculate_values": "Numerical calculations (AC, damage, HP, etc.)",
    "spell_details": "Specific spell information (components, range, duration)",
    "class_spell_access": "Which classes can cast which spells",
    "monster_stats": "Monster/creature statistics and abilities",
    "condition_effects": "Status conditions and their effects",
    "character_creation": "Character creation rules and steps",
    "multiclass_rules": "Multiclassing rules and requirements",
    "equipment_properties": "Weapon and armor properties",
    "damage_types": "Types of damage and resistances",
    "rest_mechanics": "Short rest, long rest, recovery rules",
    "skill_usage": "Skills and ability checks",
    "find_by_criteria": "Search for entities matching criteria",
    "prerequisite_check": "Check if something meets requirements",
    "interaction_rules": "How different rules interact with each other",
    "tactical_usage": "How to use abilities tactically",
    "environmental_rules": "Environmental hazards and terrain effects",
    "creature_abilities": "Special creature abilities",
    "saving_throws": "Saving throw mechanics",
    "magic_item_usage": "Magic item rules and usage",
    "planar_properties": "Planes and their properties",
    "downtime_activities": "Downtime activities and rules",
    "subclass_features": "Subclass-specific features",
    "cost_lookup": "Prices and costs of items/services",
    "legendary_mechanics": "Legendary creatures, actions, and resistances",
    "optimization_advice": "Build and character optimization advice",
}

# Slot type to gazetteer mapping
SLOT_MAPPINGS = {
    "spell": "spell",
    "spell1": "spell",
    "spell2": "spell",
    "creature": "creature",
    "creature1": "creature",
    "creature2": "creature",
    "item": "item",
    "feature": "feature",
    "feature2": "feature",
    "condition": "condition",
    "condition1": "condition",
    "condition2": "condition",
    "class_name": "class",
    "class": "class",
    "class1": "class",
    "class2": "class",
    "race": "race",
    "race1": "race",
    "race2": "race",
    "weapon": "weapon",
    "weapon1": "weapon",
    "weapon2": "weapon",
    "armor": "armor",
    "armor1": "armor",
    "armor2": "armor",
    "level": "level",
    "spell_level": "spell_level",
    "mechanic": "mechanic",
    "skill": "skill",
    "skill1": "skill",
    "skill2": "skill",
    "ability": "ability",
    "damage_type": "damage_type",
    "damage_type1": "damage_type",
    "damage_type2": "damage_type",
    "property": "weapon_property",
    "creature_ability": "creature_ability",
    "magic_item": "magic_item",
    "plane": "plane",
    "plane1": "plane",
    "plane2": "plane",
    "subclass": "subclass",
    "subclass1": "subclass",
    "subclass2": "subclass",
    "feat": "feat",
    "weapon_property": "weapon_property",
}


def get_all_rulebook_templates():
    """Return all rulebook templates as a flat list with intent labels."""
    all_templates = []
    for intent, templates in RULEBOOK_TEMPLATES.items():
        for template in templates:
            all_templates.append({
                "template": template["template"],
                "slots": template["slots"],
                "tool": "rulebook",
                "intent": intent,
            })
    return all_templates


def get_intent_templates(intent: str):
    """Get all templates for a specific intent."""
    return RULEBOOK_TEMPLATES.get(intent, [])
