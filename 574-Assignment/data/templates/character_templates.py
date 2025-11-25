"""
Character Data Query Templates

Templates for generating synthetic training data for the character_data tool.
Each intent has 15-20 templates that can be filled with entity slots.

10 Intents:
- character_basics
- combat_info
- abilities_info
- inventory_info
- magic_info
- story_info
- social_info
- progress_info
- full_character
- character_summary
"""

# =============================================================================
# CHARACTER_BASICS - Core character identity and stats
# =============================================================================

CHARACTER_BASICS_TEMPLATES = [
    # Simple queries
    {"template": "What is my character's race?", "slots": {}},
    {"template": "What class am I?", "slots": {}},
    {"template": "What level am I?", "slots": {}},
    {"template": "What is my alignment?", "slots": {}},
    {"template": "What are my ability scores?", "slots": {}},
    {"template": "What's my {ability} score?", "slots": {"ability": "ability"}},
    {"template": "Tell me about my character's physical appearance", "slots": {}},
    {"template": "How old is my character?", "slots": {}},
    {"template": "What's my character's name?", "slots": {}},
    {"template": "What race and class combination am I?", "slots": {}},
    {"template": "What's my proficiency bonus?", "slots": {}},
    {"template": "Am I a {class_name}?", "slots": {"class_name": "class"}},
    {"template": "What's my {ability} modifier?", "slots": {"ability": "ability"}},
    {"template": "How tall is my character?", "slots": {}},
    {"template": "What's my character's background?", "slots": {}},
    {"template": "What subclass am I?", "slots": {}},
    {"template": "What's my experience points total?", "slots": {}},
    {"template": "Tell me my base stats", "slots": {}},
]

# =============================================================================
# COMBAT_INFO - Combat capabilities and defensive stats
# =============================================================================

COMBAT_INFO_TEMPLATES = [
    # AC and HP
    {"template": "What is my AC?", "slots": {}},
    {"template": "What's my armor class?", "slots": {}},
    {"template": "How many hit points do I have?", "slots": {}},
    {"template": "What's my HP?", "slots": {}},
    {"template": "What's my max HP?", "slots": {}},
    {"template": "What's my current hit points?", "slots": {}},

    # Combat stats
    {"template": "What's my initiative bonus?", "slots": {}},
    {"template": "What is my speed?", "slots": {}},
    {"template": "What attacks can I make in combat?", "slots": {}},
    {"template": "What's my attack bonus?", "slots": {}},
    {"template": "What damage do I deal with my attacks?", "slots": {}},

    # Saves and resistances
    {"template": "What are my saving throw bonuses?", "slots": {}},
    {"template": "What's my {ability} saving throw?", "slots": {"ability": "ability"}},
    {"template": "What damage resistances do I have?", "slots": {}},
    {"template": "What immunities do I have?", "slots": {}},
    {"template": "Am I resistant to {damage_type} damage?", "slots": {"damage_type": "damage_type"}},

    # Actions
    {"template": "What actions can I take in combat?", "slots": {}},
    {"template": "What bonus actions do I have?", "slots": {}},
    {"template": "What reactions can I use?", "slots": {}},
    {"template": "How many attacks can I make per turn?", "slots": {}},
]

# =============================================================================
# ABILITIES_INFO - Skills, proficiencies, features
# =============================================================================

ABILITIES_INFO_TEMPLATES = [
    # Proficiencies
    {"template": "What skill proficiencies do I have?", "slots": {}},
    {"template": "What tools am I proficient with?", "slots": {}},
    {"template": "What weapons am I proficient with?", "slots": {}},
    {"template": "What armor am I proficient with?", "slots": {}},
    {"template": "Am I proficient in {skill}?", "slots": {"skill": "skill"}},
    {"template": "What's my {skill} bonus?", "slots": {"skill": "skill"}},

    # Languages and senses
    {"template": "What languages can I speak?", "slots": {}},
    {"template": "What special senses do I have?", "slots": {}},
    {"template": "Do I have darkvision?", "slots": {}},
    {"template": "What's my passive perception?", "slots": {}},
    {"template": "What's my passive insight?", "slots": {}},

    # Features and traits
    {"template": "What class features do I have?", "slots": {}},
    {"template": "What racial traits do I have?", "slots": {}},
    {"template": "Tell me about my {feature} ability", "slots": {"feature": "feature"}},
    {"template": "What feats do I have?", "slots": {}},
    {"template": "What special abilities do I have?", "slots": {}},
    {"template": "How does my {feature} work?", "slots": {"feature": "feature"}},
    {"template": "What abilities do I get from being a {class_name}?", "slots": {"class_name": "class"}},
]

# =============================================================================
# INVENTORY_INFO - Equipment and possessions
# =============================================================================

INVENTORY_INFO_TEMPLATES = [
    # General inventory
    {"template": "What's in my inventory?", "slots": {}},
    {"template": "What equipment do I have?", "slots": {}},
    {"template": "What's in my backpack?", "slots": {}},
    {"template": "What am I carrying?", "slots": {}},
    {"template": "List my possessions", "slots": {}},

    # Weapons and armor
    {"template": "What weapons am I carrying?", "slots": {}},
    {"template": "What armor am I wearing?", "slots": {}},
    {"template": "What's my main weapon?", "slots": {}},
    {"template": "Do I have a {weapon}?", "slots": {"weapon": "weapon"}},
    {"template": "Tell me about my {item}?", "slots": {"item": "item"}},

    # Magic items
    {"template": "What magic items do I have?", "slots": {}},
    {"template": "What magical equipment do I own?", "slots": {}},
    {"template": "Do I have any {magic_item}?", "slots": {"magic_item": "magic_item"}},

    # Currency and capacity
    {"template": "How much gold do I have?", "slots": {}},
    {"template": "What's my total currency?", "slots": {}},
    {"template": "What's my carrying capacity?", "slots": {}},
    {"template": "How much weight am I carrying?", "slots": {}},
    {"template": "Am I encumbered?", "slots": {}},
]

# =============================================================================
# MAGIC_INFO - Spellcasting capabilities
# =============================================================================

MAGIC_INFO_TEMPLATES = [
    # Spell lists
    {"template": "What spells can I cast?", "slots": {}},
    {"template": "What spells do I know?", "slots": {}},
    {"template": "What spells do I have prepared?", "slots": {}},
    {"template": "List my spells", "slots": {}},
    {"template": "What {class_name} spells do I have?", "slots": {"class_name": "class"}},

    # Spell slots
    {"template": "How many spell slots do I have?", "slots": {}},
    {"template": "What spell slots do I have remaining?", "slots": {}},
    {"template": "How many level {level} spell slots do I have?", "slots": {"level": "spell_level"}},

    # Cantrips
    {"template": "What cantrips do I know?", "slots": {}},
    {"template": "Do I know {spell}?", "slots": {"spell": "spell"}},

    # Spellcasting stats
    {"template": "What's my spell save DC?", "slots": {}},
    {"template": "What's my spell attack bonus?", "slots": {}},
    {"template": "What's my spellcasting ability?", "slots": {}},
    {"template": "What's my spellcasting modifier?", "slots": {}},

    # Specific spell queries
    {"template": "Can I cast {spell}?", "slots": {"spell": "spell"}},
    {"template": "What level is {spell}?", "slots": {"spell": "spell"}},
    {"template": "How does my {spell} work?", "slots": {"spell": "spell"}},
    {"template": "What ritual spells do I have?", "slots": {}},
]

# =============================================================================
# STORY_INFO - Background, personality, backstory
# =============================================================================

STORY_INFO_TEMPLATES = [
    # Background
    {"template": "What's my character's backstory?", "slots": {}},
    {"template": "Tell me about my background", "slots": {}},
    {"template": "What's my character's history?", "slots": {}},
    {"template": "Where did my character come from?", "slots": {}},
    {"template": "What happened in my character's past?", "slots": {}},

    # Personality
    {"template": "What are my personality traits?", "slots": {}},
    {"template": "What are my character's ideals?", "slots": {}},
    {"template": "What are my bonds?", "slots": {}},
    {"template": "What are my flaws?", "slots": {}},
    {"template": "Describe my character's personality", "slots": {}},

    # Motivations
    {"template": "What motivates my character?", "slots": {}},
    {"template": "What are my character's goals?", "slots": {}},
    {"template": "What does my character want?", "slots": {}},
    {"template": "Why is my character adventuring?", "slots": {}},

    # Roleplay elements
    {"template": "How would my character react to this?", "slots": {}},
    {"template": "What would my character say?", "slots": {}},
    {"template": "What's my character's background feature?", "slots": {}},
]

# =============================================================================
# SOCIAL_INFO - Relationships and affiliations
# =============================================================================

SOCIAL_INFO_TEMPLATES = [
    # Allies
    {"template": "Who are my allies?", "slots": {}},
    {"template": "Who are my friends?", "slots": {}},
    {"template": "Tell me about my companions", "slots": {}},
    {"template": "Who do I trust?", "slots": {}},

    # Enemies
    {"template": "Who are my enemies?", "slots": {}},
    {"template": "Do I have any rivals?", "slots": {}},
    {"template": "Who wants to harm my character?", "slots": {}},

    # Organizations
    {"template": "What organizations am I part of?", "slots": {}},
    {"template": "What factions am I affiliated with?", "slots": {}},
    {"template": "What guilds do I belong to?", "slots": {}},
    {"template": "What's my standing with various factions?", "slots": {}},

    # Specific relationships
    {"template": "Tell me about my mentor", "slots": {}},
    {"template": "Who trained my character?", "slots": {}},
    {"template": "Do I have any family?", "slots": {}},
    {"template": "What contacts do I have?", "slots": {}},
    {"template": "Who owes me a favor?", "slots": {}},
]

# =============================================================================
# PROGRESS_INFO - Goals, quests, advancement
# =============================================================================

PROGRESS_INFO_TEMPLATES = [
    # Current objectives
    {"template": "What are my current objectives?", "slots": {}},
    {"template": "What quests am I on?", "slots": {}},
    {"template": "What should I be doing?", "slots": {}},
    {"template": "What's my current mission?", "slots": {}},

    # Completed objectives
    {"template": "What quests have I completed?", "slots": {}},
    {"template": "What have I accomplished?", "slots": {}},
    {"template": "What objectives have I finished?", "slots": {}},

    # Contracts and tasks
    {"template": "What active contracts do I have?", "slots": {}},
    {"template": "What tasks am I working on?", "slots": {}},
    {"template": "What jobs have I taken?", "slots": {}},

    # Long-term goals
    {"template": "What are my long-term goals?", "slots": {}},
    {"template": "What is my character's ultimate objective?", "slots": {}},
    {"template": "What am I working towards?", "slots": {}},

    # Progression
    {"template": "Show me my character progression", "slots": {}},
    {"template": "How has my character grown?", "slots": {}},
    {"template": "What milestones have I achieved?", "slots": {}},
]

# =============================================================================
# FULL_CHARACTER - Complete character data
# =============================================================================

FULL_CHARACTER_TEMPLATES = [
    {"template": "Give me a complete character sheet", "slots": {}},
    {"template": "Tell me everything about my character", "slots": {}},
    {"template": "Export all my character data", "slots": {}},
    {"template": "Show me my full character information", "slots": {}},
    {"template": "What's all the information you have about my character?", "slots": {}},
    {"template": "Give me a full breakdown of my character", "slots": {}},
    {"template": "I need all my character details", "slots": {}},
    {"template": "Print my entire character sheet", "slots": {}},
    {"template": "Show me everything", "slots": {}},
    {"template": "Complete character dump", "slots": {}},
]

# =============================================================================
# CHARACTER_SUMMARY - Quick overview
# =============================================================================

CHARACTER_SUMMARY_TEMPLATES = [
    {"template": "Give me a quick summary of my character", "slots": {}},
    {"template": "What are the most important things about my character?", "slots": {}},
    {"template": "Summarize my character's key stats", "slots": {}},
    {"template": "Quick overview of my character", "slots": {}},
    {"template": "What's the elevator pitch for my character?", "slots": {}},
    {"template": "Brief description of my character", "slots": {}},
    {"template": "Give me the highlights of my character", "slots": {}},
    {"template": "TL;DR my character", "slots": {}},
    {"template": "What's essential to know about my character?", "slots": {}},
    {"template": "Quick character rundown", "slots": {}},
]

# =============================================================================
# CONSOLIDATED TEMPLATES
# =============================================================================

CHARACTER_TEMPLATES = {
    "character_basics": CHARACTER_BASICS_TEMPLATES,
    "combat_info": COMBAT_INFO_TEMPLATES,
    "abilities_info": ABILITIES_INFO_TEMPLATES,
    "inventory_info": INVENTORY_INFO_TEMPLATES,
    "magic_info": MAGIC_INFO_TEMPLATES,
    "story_info": STORY_INFO_TEMPLATES,
    "social_info": SOCIAL_INFO_TEMPLATES,
    "progress_info": PROGRESS_INFO_TEMPLATES,
    "full_character": FULL_CHARACTER_TEMPLATES,
    "character_summary": CHARACTER_SUMMARY_TEMPLATES,
}

# Intent descriptions for reference
CHARACTER_INTENT_DESCRIPTIONS = {
    "character_basics": "Core character identity and stats: name, race, class, level, alignment, physical characteristics, ability scores",
    "combat_info": "Combat capabilities and defensive stats: HP, AC, initiative, speed, saves, resistances, attacks, action economy",
    "abilities_info": "Character capabilities: skill proficiencies, tool proficiencies, languages, senses, class features, racial traits, feats",
    "inventory_info": "Equipment and possessions: weapons, armor, backpack contents, magic items, currency, carrying capacity",
    "magic_info": "Spellcasting: known spells, prepared spells, spell slots, cantrips, spell save DC, spell attack bonus",
    "story_info": "Narrative elements: background, personality traits, ideals, bonds, flaws, backstory, motivations",
    "social_info": "Relationships: allies, enemies, organizational memberships, faction standings, contacts",
    "progress_info": "Goals and advancement: current quests, completed objectives, contracts, long-term goals, progression",
    "full_character": "Complete character data: absolutely everything about the character",
    "character_summary": "Essential overview: key stats, main equipment, important abilities for quick reference",
}

# Slot type to gazetteer mapping (used by data generator)
SLOT_MAPPINGS = {
    "ability": "ability",
    "class_name": "class",
    "class": "class",
    "damage_type": "damage_type",
    "skill": "skill",
    "feature": "feature",
    "weapon": "weapon",
    "item": "item",
    "magic_item": "magic_item",
    "spell": "spell",
    "spell_level": ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"],
    "level": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
}


def get_all_character_templates():
    """Return all character templates as a flat list with intent labels."""
    all_templates = []
    for intent, templates in CHARACTER_TEMPLATES.items():
        for template in templates:
            all_templates.append({
                "template": template["template"],
                "slots": template["slots"],
                "tool": "character_data",
                "intent": intent,
            })
    return all_templates


def get_intent_templates(intent: str):
    """Get all templates for a specific intent."""
    return CHARACTER_TEMPLATES.get(intent, [])
