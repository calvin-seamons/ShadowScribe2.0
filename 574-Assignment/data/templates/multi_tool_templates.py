"""
Multi-Tool Query Templates

Templates for generating synthetic training data that requires 2-3 tools.
These represent compound questions that users commonly ask.

Target: 70% of dataset should be multi-tool queries
- 50% 2-tool queries (5,000 samples)
- 20% 3-tool queries (2,000 samples)

Tool combinations:
- character_data + rulebook (most common - questions about character + rules)
- character_data + session_notes (character info + what happened)
- session_notes + rulebook (what happened + rules clarification)
- character_data + session_notes + rulebook (all three)
"""

# =============================================================================
# CHARACTER_DATA + RULEBOOK (2-tool)
# Most common: "What's my X and how does Y work?"
# =============================================================================

CHARACTER_RULEBOOK_TEMPLATES = [
    # Combat stats + spell/rule mechanics
    {
        "template": "What's my AC and how does {spell} affect it?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },
    {
        "template": "What's my attack bonus and how do critical hits work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "rule_mechanics"},
        "slots": {}
    },
    {
        "template": "What's my HP and how does {spell} heal?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },
    {
        "template": "What's my initiative and how does surprise work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "rule_mechanics"},
        "slots": {}
    },
    {
        "template": "What's my {ability} save and what triggers it?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "saving_throws"},
        "slots": {"ability": "ability"}
    },

    # Abilities + rule explanations
    {
        "template": "What's my {skill} bonus and when do I use it?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "skill_usage"},
        "slots": {"skill": "skill"}
    },
    {
        "template": "Am I proficient in {skill} and what can I do with it?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "skill_usage"},
        "slots": {"skill": "skill"}
    },
    {
        "template": "What languages do I know and how does language work in D&D?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "rule_mechanics"},
        "slots": {}
    },
    {
        "template": "Do I have darkvision and how does it work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "rule_mechanics"},
        "slots": {}
    },
    {
        "template": "What's my passive perception and how is it calculated?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "calculate_values"},
        "slots": {}
    },

    # Magic + spell rules
    {
        "template": "Can I cast {spell} and what does it do?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "magic_info", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },
    {
        "template": "What's my spell save DC and how is it calculated?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "magic_info", "rulebook": "calculate_values"},
        "slots": {}
    },
    {
        "template": "How many spell slots do I have and how do they recover?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "magic_info", "rulebook": "rest_mechanics"},
        "slots": {}
    },
    {
        "template": "What cantrips do I know and how does {spell} scale?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "magic_info", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },
    {
        "template": "Do I have {spell} prepared and what are its components?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "magic_info", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },

    # Inventory + equipment rules
    {
        "template": "What weapons do I have and what's the damage for {weapon}?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "inventory_info", "rulebook": "equipment_properties"},
        "slots": {"weapon": "weapon"}
    },
    {
        "template": "What armor am I wearing and how does AC calculation work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "inventory_info", "rulebook": "calculate_values"},
        "slots": {}
    },
    {
        "template": "Do I have a {item} and how does it work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "inventory_info", "rulebook": "magic_item_usage"},
        "slots": {"item": "magic_item"}
    },
    {
        "template": "What magic items do I have and how does attunement work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "inventory_info", "rulebook": "magic_item_usage"},
        "slots": {}
    },
    {
        "template": "How much gold do I have and what can I buy with it?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "inventory_info", "rulebook": "cost_lookup"},
        "slots": {}
    },

    # Character basics + class features
    {
        "template": "What class am I and what features do I get at level {level}?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "level_progression"},
        "slots": {"level": "level"}
    },
    {
        "template": "What level am I and when do I get Extra Attack?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "level_progression"},
        "slots": {}
    },
    {
        "template": "What race am I and what racial traits do I get?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "describe_entity"},
        "slots": {}
    },
    {
        "template": "What's my subclass and what features does it give?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "subclass_features"},
        "slots": {}
    },
    {
        "template": "What's my background and what feature does it provide?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "describe_entity"},
        "slots": {}
    },

    # Class features + how they work
    {
        "template": "Do I have {feature} and how does it work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "describe_entity"},
        "slots": {"feature": "feature"}
    },
    {
        "template": "What class features do I have and how does {feature} work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "describe_entity"},
        "slots": {"feature": "feature"}
    },
    {
        "template": "What feats do I have and what are the prerequisites for {feat}?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "prerequisite_check"},
        "slots": {"feat": "feat"}
    },

    # Character + monster comparison
    {
        "template": "What's my AC compared to a {creature}'s attack bonus?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "monster_stats"},
        "slots": {"creature": "creature"}
    },
    {
        "template": "Can I hit a {creature} with my attack bonus?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "monster_stats"},
        "slots": {"creature": "creature"}
    },
    {
        "template": "Am I resistant to {damage_type} and what creatures deal that damage?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "damage_types"},
        "slots": {"damage_type": "damage_type"}
    },

    # Character + condition effects
    {
        "template": "What actions can I take and what happens if I'm {condition}?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "condition_effects"},
        "slots": {"condition": "condition"}
    },
    {
        "template": "Can I still cast spells while {condition}?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "magic_info", "rulebook": "condition_effects"},
        "slots": {"condition": "condition"}
    },

    # Multiclass questions
    {
        "template": "What class am I and can I multiclass into {class_name}?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "multiclass_rules"},
        "slots": {"class_name": "class"}
    },
    {
        "template": "What are my ability scores and do I meet multiclass requirements?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "multiclass_rules"},
        "slots": {}
    },

    # Optimization questions
    {
        "template": "What's my class and what feats would be good for me?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_basics", "rulebook": "optimization_advice"},
        "slots": {}
    },
    {
        "template": "What's my build and how can I optimize my damage?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "character_summary", "rulebook": "optimization_advice"},
        "slots": {}
    },

    # Progress + leveling
    {
        "template": "How much XP do I have and when do I level up?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "progress_info", "rulebook": "level_progression"},
        "slots": {}
    },
    {
        "template": "What are my current goals and what rewards are typical?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "progress_info", "rulebook": "cost_lookup"},
        "slots": {}
    },

    # Story + planar
    {
        "template": "Where did my character come from and what's the {plane} like?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "story_info", "rulebook": "planar_properties"},
        "slots": {"plane": "plane"}
    },

    # Action economy questions
    {
        "template": "What bonus actions do I have and can I cast {spell} as a bonus action?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "action_options"},
        "slots": {"spell": "spell"}
    },
    {
        "template": "How many attacks can I make and how does two-weapon fighting work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "action_options"},
        "slots": {}
    },

    # Rest and recovery
    {
        "template": "What abilities do I recover on a short rest and how do hit dice work?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "abilities_info", "rulebook": "rest_mechanics"},
        "slots": {}
    },
    {
        "template": "How many hit dice do I have and how do I spend them?",
        "tools": ["character_data", "rulebook"],
        "intents": {"character_data": "combat_info", "rulebook": "rest_mechanics"},
        "slots": {}
    },
]

# =============================================================================
# CHARACTER_DATA + SESSION_NOTES (2-tool)
# "What's my X and what happened with it?"
# =============================================================================

CHARACTER_SESSION_TEMPLATES = [
    # Items + session history
    {
        "template": "What magic items do I have and how did I get them?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "inventory_info", "session_notes": "item_tracking"},
        "slots": {}
    },
    {
        "template": "What's in my inventory and what loot did we find last session?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "inventory_info", "session_notes": "loot_rewards"},
        "slots": {}
    },
    {
        "template": "What weapons do I have and when did I get my current weapon?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "inventory_info", "session_notes": "item_tracking"},
        "slots": {}
    },
    {
        "template": "How much gold do I have and what was our last big treasure haul?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "inventory_info", "session_notes": "loot_rewards"},
        "slots": {}
    },

    # Character stats + combat history
    {
        "template": "What's my current HP and what happened in our last fight?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap"},
        "slots": {}
    },
    {
        "template": "What's my AC and how did that help in recent combat?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap"},
        "slots": {}
    },
    {
        "template": "What attacks can I make and what did I fight last session?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap"},
        "slots": {}
    },

    # Spells + usage history
    {
        "template": "What spells do I have and which ones did I cast last session?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "magic_info", "session_notes": "spell_ability_usage"},
        "slots": {}
    },
    {
        "template": "How many spell slots do I have and how many did I use?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "magic_info", "session_notes": "spell_ability_usage"},
        "slots": {}
    },
    {
        "template": "What cantrips do I know and when did I use them effectively?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "magic_info", "session_notes": "spell_ability_usage"},
        "slots": {}
    },

    # Abilities + usage
    {
        "template": "What class features do I have and when did I use them?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "abilities_info", "session_notes": "spell_ability_usage"},
        "slots": {}
    },
    {
        "template": "What's my {skill} bonus and when did I roll it?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "abilities_info", "session_notes": "rules_mechanics"},
        "slots": {"skill": "skill"}
    },

    # Character identity + story
    {
        "template": "What's my backstory and how has it come up in the campaign?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "story_info", "session_notes": "character_decisions"},
        "slots": {}
    },
    {
        "template": "What are my character's goals and what progress have I made?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "story_info", "session_notes": "quest_tracking"},
        "slots": {}
    },
    {
        "template": "What motivates my character and what choices have I made?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "story_info", "session_notes": "character_decisions"},
        "slots": {}
    },

    # Social + NPC interactions
    {
        "template": "Who are my allies and who did we meet last session?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "social_info", "session_notes": "npc_info"},
        "slots": {}
    },
    {
        "template": "What factions am I part of and how is my standing with them?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "social_info", "session_notes": "npc_info"},
        "slots": {}
    },
    {
        "template": "Who are my contacts and what did they tell me?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "social_info", "session_notes": "npc_info"},
        "slots": {}
    },

    # Progress + quests
    {
        "template": "What are my current objectives and what quests have I completed?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "progress_info", "session_notes": "quest_tracking"},
        "slots": {}
    },
    {
        "template": "What quests am I on and what's the status of each?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "progress_info", "session_notes": "quest_tracking"},
        "slots": {}
    },
    {
        "template": "What long-term goals do I have and what mysteries remain unsolved?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "progress_info", "session_notes": "unresolved_mysteries"},
        "slots": {}
    },

    # Character status
    {
        "template": "What's my character's current status and condition?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "character_summary", "session_notes": "character_status"},
        "slots": {}
    },
    {
        "template": "Give me an overview of my character and recent events",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "character_summary", "session_notes": "event_sequence"},
        "slots": {}
    },

    # Death and revival
    {
        "template": "What's my HP and have I ever been knocked unconscious?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "combat_info", "session_notes": "death_revival"},
        "slots": {}
    },
    {
        "template": "What healing do I have access to and when have I needed it?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "magic_info", "session_notes": "death_revival"},
        "slots": {}
    },

    # Party dynamics
    {
        "template": "Who are my companions and how do we work together?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "social_info", "session_notes": "party_dynamics"},
        "slots": {}
    },
    {
        "template": "What role do I play in the party and how has that evolved?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "character_summary", "session_notes": "party_dynamics"},
        "slots": {}
    },

    # Location and exploration
    {
        "template": "What senses do I have and what locations have we explored?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "abilities_info", "session_notes": "location_details"},
        "slots": {}
    },

    # Divine/religious
    {
        "template": "What's my alignment and what divine encounters have we had?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "character_basics", "session_notes": "divine_religious"},
        "slots": {}
    },

    # Humor and moments
    {
        "template": "What's my personality and what funny moments have I had?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "story_info", "session_notes": "humor_moments"},
        "slots": {}
    },

    # Future implications
    {
        "template": "What are my goals and what consequences might come from recent actions?",
        "tools": ["character_data", "session_notes"],
        "intents": {"character_data": "progress_info", "session_notes": "future_implications"},
        "slots": {}
    },
]

# =============================================================================
# SESSION_NOTES + RULEBOOK (2-tool)
# "What happened and how does that rule work?"
# =============================================================================

SESSION_RULEBOOK_TEMPLATES = [
    # Combat events + rules
    {
        "template": "What happened in our last fight and how does {mechanic} work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "combat_recap", "rulebook": "rule_mechanics"},
        "slots": {"mechanic": "mechanic"}
    },
    {
        "template": "Who did we fight and what's a {creature}'s stat block?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "combat_recap", "rulebook": "monster_stats"},
        "slots": {"creature": "creature"}
    },
    {
        "template": "What enemies did we face and what resistances do {creature}s have?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "combat_recap", "rulebook": "monster_stats"},
        "slots": {"creature": "creature"}
    },

    # Spells used + spell details
    {
        "template": "What spells were cast and how does {spell} work exactly?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "spell_ability_usage", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },
    {
        "template": "When did we use {spell} and what are its full details?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "spell_ability_usage", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },

    # Items found + item rules
    {
        "template": "What magic items did we find and how does {magic_item} work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "item_tracking", "rulebook": "magic_item_usage"},
        "slots": {"magic_item": "magic_item"}
    },
    {
        "template": "What loot did we get and what's the value of {item}?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "loot_rewards", "rulebook": "cost_lookup"},
        "slots": {"item": "item"}
    },
    {
        "template": "What weapons did we find and what are the properties of {weapon}?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "loot_rewards", "rulebook": "equipment_properties"},
        "slots": {"weapon": "weapon"}
    },

    # Conditions encountered + condition rules
    {
        "template": "What conditions affected us and how does {condition} work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "combat_recap", "rulebook": "condition_effects"},
        "slots": {"condition": "condition"}
    },
    {
        "template": "Who got {condition} and what are the effects?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "character_status", "rulebook": "condition_effects"},
        "slots": {"condition": "condition"}
    },

    # Locations + planar rules
    {
        "template": "Where did we go and what are the rules for the {plane}?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "location_details", "rulebook": "planar_properties"},
        "slots": {"plane": "plane"}
    },
    {
        "template": "What location did we explore and how does {mechanic} work there?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "location_details", "rulebook": "environmental_rules"},
        "slots": {"mechanic": "mechanic"}
    },

    # NPCs + creature abilities
    {
        "template": "Who did we meet and what abilities do {creature}s have?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "npc_info", "rulebook": "creature_abilities"},
        "slots": {"creature": "creature"}
    },
    {
        "template": "What monster did we encounter and what's its challenge rating?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "combat_recap", "rulebook": "monster_stats"},
        "slots": {}
    },

    # Rules clarifications from play
    {
        "template": "What rule question came up and how does {mechanic} actually work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "rules_mechanics", "rulebook": "rule_mechanics"},
        "slots": {"mechanic": "mechanic"}
    },
    {
        "template": "What happened when we tried {mechanic} and is that how it works?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "rules_mechanics", "rulebook": "rule_mechanics"},
        "slots": {"mechanic": "mechanic"}
    },

    # Puzzles + skill checks
    {
        "template": "What puzzle did we solve and how do {skill} checks work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "puzzle_solutions", "rulebook": "skill_usage"},
        "slots": {"skill": "skill"}
    },

    # Death/revival + rules
    {
        "template": "Who went down in combat and how do death saves work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "death_revival", "rulebook": "saving_throws"},
        "slots": {}
    },
    {
        "template": "What resurrection happened and what are the rules for it?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "death_revival", "rulebook": "spell_details"},
        "slots": {}
    },

    # Divine encounters + rules
    {
        "template": "What divine event occurred and how do divine interventions work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "divine_religious", "rulebook": "rule_mechanics"},
        "slots": {}
    },

    # Quest rewards + values
    {
        "template": "What quest rewards did we get and how much are they worth?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "loot_rewards", "rulebook": "cost_lookup"},
        "slots": {}
    },

    # Downtime between sessions
    {
        "template": "What downtime did we have and what activities are available?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "cross_session", "rulebook": "downtime_activities"},
        "slots": {}
    },

    # Legendary creatures
    {
        "template": "What boss did we fight and how do legendary actions work?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "combat_recap", "rulebook": "legendary_mechanics"},
        "slots": {}
    },
    {
        "template": "What legendary creature did we encounter and what can it do?",
        "tools": ["session_notes", "rulebook"],
        "intents": {"session_notes": "combat_recap", "rulebook": "legendary_mechanics"},
        "slots": {}
    },
]

# =============================================================================
# ALL THREE TOOLS (3-tool)
# Complex compound questions
# =============================================================================

THREE_TOOL_TEMPLATES = [
    # Character + session + spell rules
    {
        "template": "What spells do I know, when did I cast {spell}, and what are its full rules?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "magic_info", "session_notes": "spell_ability_usage", "rulebook": "spell_details"},
        "slots": {"spell": "spell"}
    },
    {
        "template": "What's my spell save DC, what spells did I cast last session, and how does upcasting work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "magic_info", "session_notes": "spell_ability_usage", "rulebook": "spell_details"},
        "slots": {}
    },

    # Character + session + combat rules
    {
        "template": "What's my AC, what did we fight, and how does cover affect AC?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap", "rulebook": "rule_mechanics"},
        "slots": {}
    },
    {
        "template": "What attacks can I make, what combat happened, and how do opportunity attacks work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap", "rulebook": "action_options"},
        "slots": {}
    },
    {
        "template": "What's my HP, what damage did I take last session, and how does resistance work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap", "rulebook": "damage_types"},
        "slots": {}
    },

    # Character + session + item rules
    {
        "template": "What magic items do I have, when did I get them, and how does {magic_item} work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "inventory_info", "session_notes": "item_tracking", "rulebook": "magic_item_usage"},
        "slots": {"magic_item": "magic_item"}
    },
    {
        "template": "What's in my inventory, what did we loot, and what are these items worth?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "inventory_info", "session_notes": "loot_rewards", "rulebook": "cost_lookup"},
        "slots": {}
    },
    {
        "template": "What weapons do I have, what fights used them, and what's the damage for {weapon}?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "inventory_info", "session_notes": "combat_recap", "rulebook": "equipment_properties"},
        "slots": {"weapon": "weapon"}
    },

    # Character + session + creature rules
    {
        "template": "What's my attack bonus, what monsters did we fight, and what's a {creature}'s AC?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap", "rulebook": "monster_stats"},
        "slots": {"creature": "creature"}
    },
    {
        "template": "What resistances do I have, what hit us, and what damage types do {creature}s deal?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "combat_recap", "rulebook": "monster_stats"},
        "slots": {"creature": "creature"}
    },

    # Character + session + condition rules
    {
        "template": "What's my current status, what conditions affected us, and how does {condition} work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "character_summary", "session_notes": "character_status", "rulebook": "condition_effects"},
        "slots": {"condition": "condition"}
    },
    {
        "template": "What saves do I have, what saves did I roll, and how do saving throws work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "rules_mechanics", "rulebook": "saving_throws"},
        "slots": {}
    },

    # Character + session + skill rules
    {
        "template": "What's my {skill} bonus, when did I use it, and what are typical DCs?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "abilities_info", "session_notes": "rules_mechanics", "rulebook": "skill_usage"},
        "slots": {"skill": "skill"}
    },
    {
        "template": "What skills am I proficient in, what checks did I make, and how does advantage work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "abilities_info", "session_notes": "rules_mechanics", "rulebook": "rule_mechanics"},
        "slots": {}
    },

    # Character + session + class progression
    {
        "template": "What level am I, what progress have I made, and when do I get my next feature?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "character_basics", "session_notes": "quest_tracking", "rulebook": "level_progression"},
        "slots": {}
    },
    {
        "template": "What class features do I have, when did I use them, and how does {feature} work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "abilities_info", "session_notes": "spell_ability_usage", "rulebook": "describe_entity"},
        "slots": {"feature": "feature"}
    },

    # Character + session + NPC/social rules
    {
        "template": "Who are my allies, who did we meet, and how do social encounters work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "social_info", "session_notes": "npc_info", "rulebook": "skill_usage"},
        "slots": {}
    },

    # Character + session + location rules
    {
        "template": "What senses do I have, where did we explore, and how does darkness affect perception?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "abilities_info", "session_notes": "location_details", "rulebook": "environmental_rules"},
        "slots": {}
    },

    # Character + session + rest rules
    {
        "template": "How many hit dice do I have, what rest did we take, and what recovers on a short rest?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "character_status", "rulebook": "rest_mechanics"},
        "slots": {}
    },
    {
        "template": "What spell slots do I have left, how many did I use, and how do they recover?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "magic_info", "session_notes": "spell_ability_usage", "rulebook": "rest_mechanics"},
        "slots": {}
    },

    # Character + session + death rules
    {
        "template": "What's my max HP, have I gone down before, and how do death saves work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "combat_info", "session_notes": "death_revival", "rulebook": "saving_throws"},
        "slots": {}
    },

    # Character + session + divine rules
    {
        "template": "What's my alignment, what divine encounters have we had, and how does divine magic work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "character_basics", "session_notes": "divine_religious", "rulebook": "rule_mechanics"},
        "slots": {}
    },

    # Character + session + planar rules
    {
        "template": "What's my backstory, what planes have we visited, and what are the rules for the {plane}?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "story_info", "session_notes": "location_details", "rulebook": "planar_properties"},
        "slots": {"plane": "plane"}
    },

    # Quest + progress + rules
    {
        "template": "What are my goals, what quests have we done, and what are typical quest rewards?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "progress_info", "session_notes": "quest_tracking", "rulebook": "cost_lookup"},
        "slots": {}
    },

    # Character + puzzle + skill rules
    {
        "template": "What's my Intelligence, what puzzles have we solved, and how do Investigation checks work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "character_basics", "session_notes": "puzzle_solutions", "rulebook": "skill_usage"},
        "slots": {}
    },

    # Full character breakdown
    {
        "template": "Give me my character summary, recent events, and rules for my key abilities",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "character_summary", "session_notes": "event_sequence", "rulebook": "describe_entity"},
        "slots": {}
    },
    {
        "template": "What's my full character sheet, what happened recently, and how do my abilities work?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "full_character", "session_notes": "character_status", "rulebook": "describe_entity"},
        "slots": {}
    },

    # Future planning
    {
        "template": "What are my long-term goals, what mysteries remain, and what's the best way to advance?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "progress_info", "session_notes": "unresolved_mysteries", "rulebook": "optimization_advice"},
        "slots": {}
    },

    # Party coordination
    {
        "template": "What role do I play, how does our party work, and how can we optimize our tactics?",
        "tools": ["character_data", "session_notes", "rulebook"],
        "intents": {"character_data": "character_summary", "session_notes": "party_dynamics", "rulebook": "tactical_usage"},
        "slots": {}
    },
]

# =============================================================================
# CONSOLIDATED TEMPLATES
# =============================================================================

MULTI_TOOL_TEMPLATES = {
    "character_rulebook": CHARACTER_RULEBOOK_TEMPLATES,
    "character_session": CHARACTER_SESSION_TEMPLATES,
    "session_rulebook": SESSION_RULEBOOK_TEMPLATES,
    "three_tool": THREE_TOOL_TEMPLATES,
}

# Template counts for dataset generation
TEMPLATE_COUNTS = {
    "character_rulebook": len(CHARACTER_RULEBOOK_TEMPLATES),
    "character_session": len(CHARACTER_SESSION_TEMPLATES),
    "session_rulebook": len(SESSION_RULEBOOK_TEMPLATES),
    "three_tool": len(THREE_TOOL_TEMPLATES),
}


def get_all_multi_tool_templates():
    """Return all multi-tool templates as a flat list."""
    all_templates = []
    for category, templates in MULTI_TOOL_TEMPLATES.items():
        for template in templates:
            all_templates.append({
                **template,
                "category": category,
            })
    return all_templates


def get_two_tool_templates():
    """Get all 2-tool templates."""
    templates = []
    templates.extend(CHARACTER_RULEBOOK_TEMPLATES)
    templates.extend(CHARACTER_SESSION_TEMPLATES)
    templates.extend(SESSION_RULEBOOK_TEMPLATES)
    return templates


def get_three_tool_templates():
    """Get all 3-tool templates."""
    return THREE_TOOL_TEMPLATES.copy()


def get_templates_by_tools(tools: list):
    """Get templates that use exactly the specified tools."""
    all_templates = get_all_multi_tool_templates()
    return [t for t in all_templates if set(t["tools"]) == set(tools)]
