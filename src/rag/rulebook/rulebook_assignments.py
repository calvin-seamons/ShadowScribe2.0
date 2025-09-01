# Complete Category Mapping for D&D 5e Rulebook Sections
# Legend for Categories:
# CHARACTER_CREATION - Races, base classes, ability scores, backgrounds
# CLASS_FEATURES - All class abilities and specializations
# SPELLCASTING - Magic rules, spell lists, descriptions
# COMBAT - Combat mechanics and tactical rules
# CONDITIONS - All temporary effects and ailments
# EQUIPMENT - Gear, weapons, magical equipment
# CORE_MECHANICS - Fundamental rules like advantage, proficiency
# EXPLORATION - Non-combat adventuring and travel
# CREATURES - All creature stats and abilities
# WORLD_LORE - Planes, deities, campaign setting info


RULEBOOK_CATEGORY_ASSIGNMENTS = {
    # Legal Information
    "Legal Information": [],  # Skip - not game content
    
    # RACES CHAPTER
    "chapter-races": [1],  # CHARACTER_CREATION
    "section-racial-traits": [1],
    "section-dragonborn": [1],
    "section-dwarf": [1],
    "section-elf": [1],
    "section-gnome": [1],
    "section-half-elf": [1],
    "section-half-orc": [1],
    "section-halfling": [1],
    "section-human": [1],
    "section-tiefling": [1],
    
    # CLASSES CHAPTER - Most sections need dual categorization
    "chapter-classes": [1, 2],  # CHARACTER_CREATION, CLASS_FEATURES
    
    # Barbarian and features
    "section-barbarian": [1, 2],
    "section-barbarian-paths": [2],
    # All barbarian features (Rage, Unarmored Defense, etc.)
    "*barbarian*": [2],  # All barbarian-specific features
    
    # Bard and features
    "section-bard": [1, 2],
    "section-bard-colleges": [2],
    "*bard*": [2],  # All bard-specific features
    
    # Cleric and features
    "section-cleric": [1, 2],
    "section-domains": [2],
    "*cleric*": [2],
    
    # Druid and features
    "section-druid": [1, 2],
    "section-druid-circles": [2],
    "*druid*": [2],
    
    # Fighter and features
    "section-fighter": [1, 2],
    "section-martial-archetypes": [2],
    "*fighter*": [2],
    
    # Monk and features
    "section-monk": [1, 2],
    "section-monastic-traditions": [2],
    "*monk*": [2],
    
    # Paladin and features
    "section-paladin": [1, 2],
    "section-sacred-oaths": [2],
    "*paladin*": [2],
    
    # Ranger and features
    "section-ranger": [1, 2],
    "section-ranger-archetypes": [2],
    "*ranger*": [2],
    
    # Rogue and features
    "section-rogue": [1, 2],
    "section-roguish-archetypes": [2],
    "*rogue*": [2],
    
    # Sorcerer and features
    "section-sorcerer": [1, 2],
    "section-sorcerous-origins": [2],
    "*sorcerer*": [2],
    
    # Warlock and features
    "section-warlock": [1, 2],
    "section-eldritch-invocations": [2],
    "section-otherworldly-patrons": [2],
    "*warlock*": [2],
    
    # Wizard and features
    "section-wizard": [1, 2],
    "section-arcane-traditions": [2],
    "*wizard*": [2],
    
    # USING ABILITY SCORES CHAPTER
    "chapter-using-ability-scores": [7],  # CORE_MECHANICS
    "section-ability-scores-and-modifiers": [7],
    "section-advantage-and-disadvantage": [7],
    "section-proficiency-bonus": [7],
    "section-ability-checks": [7],
    "section-using-each-ability": [7],
    "section-saving-throws": [4, 7],  # COMBAT, CORE_MECHANICS
    
    # BEYOND 1ST LEVEL CHAPTER
    "chapter-beyond-1st-level": [1],  # CHARACTER_CREATION
    "section-character-advancement": [1, 7],  # CHARACTER_CREATION, CORE_MECHANICS
    "section-multiclassing": [1, 2],  # CHARACTER_CREATION, CLASS_FEATURES
    "section-alignment": [1],
    "section-languages": [1],
    "section-backgrounds": [1],
    
    # FEATS CHAPTER
    "chapter-feats": [1, 2],  # CHARACTER_CREATION, CLASS_FEATURES
    "section-grappler": [1, 2, 4],  # Also COMBAT for grappling
    "section-inspiration": [7],  # CORE_MECHANICS
    
    # THE PLANES OF EXISTENCE CHAPTER
    "chapter-the-planes-of-existence": [10],  # WORLD_LORE
    "section-the-material-plane": [10],
    "section-beyond-the-material": [10],
    
    # PANTHEONS CHAPTER
    "chapter-pantheons": [10],  # WORLD_LORE
    "section-the-celtic-pantheon": [10],
    "section-the-egyptian-pantheon": [10],
    "section-the-greek-pantheon": [10],
    "section-the-norse-pantheon": [10],
    
    # ADVENTURING CHAPTER
    "chapter-adventuring": [8],  # EXPLORATION
    "section-time": [8],
    "section-movement": [8],
    "section-environment": [8],
    "section-objects": [7, 8],  # CORE_MECHANICS, EXPLORATION
    "section-resting": [7, 8],  # CORE_MECHANICS, EXPLORATION
    "section-between-adventures": [8],
    "section-conditions": [5],  # CONDITIONS
    "section-poisons": [5],  # CONDITIONS
    "section-diseases": [5],  # CONDITIONS
    "section-madness": [5],  # CONDITIONS
    "section-traps": [8, 4],  # EXPLORATION, COMBAT
    
    # Individual conditions should only be CONDITIONS (override parent inheritance)
    "blinded": [5],  # CONDITIONS
    "charmed": [5],  # CONDITIONS
    "deafened": [5],  # CONDITIONS
    "exhaustion": [5],  # CONDITIONS
    "frightened": [5],  # CONDITIONS
    "grappled": [5],  # CONDITIONS
    "incapacitated": [5],  # CONDITIONS
    "invisible": [5],  # CONDITIONS
    "paralyzed": [5],  # CONDITIONS
    "petrified": [5],  # CONDITIONS
    "poisoned": [5],  # CONDITIONS
    "prone": [5],  # CONDITIONS
    "restrained": [5],  # CONDITIONS
    "stunned": [5],  # CONDITIONS
    "unconscious": [5],  # CONDITIONS
    
    # Restoration spells should only be SPELLCASTING (override parent inheritance)
    "greater-restoration": [3],  # SPELLCASTING
    "lesser-restoration": [3],  # SPELLCASTING
    
    # Restorative items should only be EQUIPMENT (override parent inheritance)
    "restorative-ointment": [6],  # EQUIPMENT
    
    # COMBAT CHAPTER
    "chapter-combat": [4],  # COMBAT
    "section-the-order-of-combat": [4],
    "section-movement-and-position": [4],
    "section-actions-in-combat": [4],
    "section-making-an-attack": [4],
    "section-cover": [4],
    "section-damage-and-healing": [4, 7],  # COMBAT, CORE_MECHANICS
    "section-mounted-combat": [4],
    "section-underwater-combat": [4, 8],  # COMBAT, EXPLORATION
    
    # SPELLCASTING CHAPTER
    "chapter-spellcasting": [3],  # SPELLCASTING
    "section-what-is-a-spell": [3],
    "section-casting-a-spell": [3],
    
    # SPELL LISTS CHAPTER
    "chapter-spell-lists": [3],  # SPELLCASTING
    "section-bard-spells": [2, 3],  # CLASS_FEATURES, SPELLCASTING
    "section-cleric-spells": [2, 3],
    "section-druid-spells": [2, 3],
    "section-paladin-spells": [2, 3],
    "section-ranger-spells": [2, 3],
    "section-sorcerer-spells": [2, 3],
    "section-warlock-spells": [2, 3],
    "section-wizard-spells": [2, 3],
    "section-spell-descriptions": [3],
    # All individual spells
    "*spell-*": [3],  # Pattern for all spell entries
    
    # EQUIPMENT CHAPTER
    "chapter-equipment": [6],  # EQUIPMENT
    "section-currency": [6],
    "section-selling-treasure": [6],
    "section-adventuring-gear": [6],
    "section-tools": [6],
    "section-mounts-and-vehicles": [6, 8],  # EQUIPMENT, EXPLORATION
    "section-trade-goods": [6],
    "section-expenses": [6, 8],  # EQUIPMENT, EXPLORATION
    "section-services": [6, 8],  # EQUIPMENT, EXPLORATION
    "section-armor": [6],
    "section-weapons": [6],
    
    # MAGIC ITEMS CHAPTER
    "chapter-magic-items": [6],  # EQUIPMENT
    "section-attunement": [6],
    "section-wearing-and-wielding-items": [6],
    "section-activating-an-item": [6],
    "section-magic-item-descriptions": [6],
    # All individual magic items
    "*magic-item-*": [6],  # Pattern for all magic item entries
    "section-sentient-magic-items": [6],
    "section-artifacts": [6],
    
    # MONSTERS CHAPTER
    "chapter-monsters": [9],  # CREATURES
    "section-monster-construction": [9],
    "section-legendary-creatures": [9],
    "section-monster-descriptions": [9],
    # All individual monsters/creature types
    "*monster-*": [9],  # Pattern for all monster entries
    
    # MISCELLANEOUS CREATURES CHAPTER
    "chapter-miscellaneous-creatures": [9],  # CREATURES
    "section-creature-descriptions": [9],
    # All miscellaneous creatures
    "*creature-*": [9],
    
    # NONPLAYER CHARACTERS CHAPTER
    "chapter-nonplayer-characters": [9],  # CREATURES (NPCs are statblocks)
    "section-customizing-npcs": [9],
    "section-nonplayer-character-descriptions": [9],
    # All NPC stat blocks
    "*npc-*": [9],
}

# Special handling patterns for subsections
PATTERN_RULES = {
    # Any section with "spell" in the ID that's not already categorized
    "contains:spell": [3],  # SPELLCASTING
    
    # Any section with class names should be in CLASS_FEATURES
    "contains:barbarian|bard|cleric|druid|fighter|monk|paladin|ranger|rogue|sorcerer|warlock|wizard": [2],
    
    # Specific condition names
    "contains:blinded|charmed|deafened|exhaustion|frightened|grappled|incapacitated|invisible|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious": [5],
    
    # Combat-related keywords
    "contains:attack|damage|initiative|reaction|bonus-action": [4],
    
    # Exploration keywords
    "contains:travel|rest|downtime|lifestyle": [8],
}

# Sections that need MULTIPLE categories (duplicates)
MULTI_CATEGORY_SECTIONS = {
    # Class spell lists appear in both categories
    "section-bard-spells": [2, 3],
    "section-cleric-spells": [2, 3],
    "section-druid-spells": [2, 3],
    "section-paladin-spells": [2, 3],
    "section-ranger-spells": [2, 3],
    "section-sorcerer-spells": [2, 3],
    "section-warlock-spells": [2, 3],
    "section-wizard-spells": [2, 3],
    
    # Multiclassing is both character creation and class features
    "section-multiclassing": [1, 2],
    
    # Saving throws are both combat and core mechanics
    "section-saving-throws": [4, 7],
    
    # Damage and healing span combat and core mechanics
    "section-damage-and-healing": [4, 7],
    
    # Underwater combat is both combat and exploration
    "section-underwater-combat": [4, 8],
    
    # Traps can be combat encounters or exploration hazards
    "section-traps": [4, 8],
    
    # Mounts are both equipment and exploration
    "section-mounts-and-vehicles": [6, 8],
}