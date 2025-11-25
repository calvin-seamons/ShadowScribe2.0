"""
Entity Gazetteers for D&D 5e Query Classification

This module contains comprehensive lists of D&D 5e SRD entities used for:
1. Template slot filling during synthetic data generation
2. NER training data annotation
3. Entity recognition in queries

IMPORTANT: These are GENERIC D&D 5e entities from the SRD.
Do NOT include campaign-specific entities (custom NPCs, locations, items).
"""

# =============================================================================
# SPELLS - From D&D 5e SRD Spell Descriptions
# =============================================================================

SPELL_NAMES = [
    # Cantrips
    "Acid Splash", "Chill Touch", "Dancing Lights", "Druidcraft", "Eldritch Blast",
    "Fire Bolt", "Guidance", "Light", "Mage Hand", "Mending", "Message",
    "Minor Illusion", "Poison Spray", "Prestidigitation", "Produce Flame",
    "Ray of Frost", "Resistance", "Sacred Flame", "Shillelagh", "Shocking Grasp",
    "Spare the Dying", "Thaumaturgy", "True Strike", "Vicious Mockery",

    # 1st Level
    "Alarm", "Animal Friendship", "Armor of Agathys", "Arms of Hadar", "Bane",
    "Bless", "Burning Hands", "Charm Person", "Color Spray", "Command",
    "Comprehend Languages", "Create or Destroy Water", "Cure Wounds",
    "Detect Evil and Good", "Detect Magic", "Detect Poison and Disease",
    "Disguise Self", "Divine Favor", "Entangle", "Expeditious Retreat",
    "Faerie Fire", "False Life", "Feather Fall", "Find Familiar", "Fog Cloud",
    "Goodberry", "Grease", "Guiding Bolt", "Healing Word", "Hellish Rebuke",
    "Heroism", "Hex", "Hunter's Mark", "Identify", "Illusory Script",
    "Inflict Wounds", "Jump", "Longstrider", "Mage Armor", "Magic Missile",
    "Protection from Evil and Good", "Purify Food and Drink", "Ray of Sickness",
    "Sanctuary", "Shield", "Shield of Faith", "Silent Image", "Sleep",
    "Speak with Animals", "Tasha's Hideous Laughter", "Thunderwave",
    "Unseen Servant", "Witch Bolt",

    # 2nd Level
    "Aid", "Alter Self", "Animal Messenger", "Arcane Lock", "Augury",
    "Barkskin", "Blindness/Deafness", "Blur", "Branding Smite",
    "Calm Emotions", "Cloud of Daggers", "Continual Flame", "Crown of Madness",
    "Darkness", "Darkvision", "Detect Thoughts", "Enhance Ability", "Enthrall",
    "Find Steed", "Find Traps", "Flame Blade", "Flaming Sphere", "Gentle Repose",
    "Gust of Wind", "Heat Metal", "Hold Person", "Invisibility", "Knock",
    "Lesser Restoration", "Levitate", "Locate Animals or Plants", "Locate Object",
    "Magic Mouth", "Magic Weapon", "Mirror Image", "Misty Step", "Moonbeam",
    "Pass without Trace", "Phantasmal Force", "Prayer of Healing",
    "Protection from Poison", "Ray of Enfeeblement", "Rope Trick", "Scorching Ray",
    "See Invisibility", "Shatter", "Silence", "Spider Climb", "Spike Growth",
    "Spiritual Weapon", "Suggestion", "Warding Bond", "Web", "Zone of Truth",

    # 3rd Level
    "Animate Dead", "Aura of Vitality", "Beacon of Hope", "Bestow Curse",
    "Blinding Smite", "Blink", "Call Lightning", "Clairvoyance",
    "Conjure Animals", "Conjure Barrage", "Counterspell", "Create Food and Water",
    "Crusader's Mantle", "Daylight", "Dispel Magic", "Elemental Weapon",
    "Fear", "Feign Death", "Fireball", "Fly", "Gaseous Form", "Glyph of Warding",
    "Haste", "Hunger of Hadar", "Hypnotic Pattern", "Lightning Arrow",
    "Lightning Bolt", "Magic Circle", "Major Image", "Mass Healing Word",
    "Meld into Stone", "Nondetection", "Phantom Steed", "Plant Growth",
    "Protection from Energy", "Remove Curse", "Revivify", "Sending",
    "Sleet Storm", "Slow", "Speak with Dead", "Speak with Plants",
    "Spirit Guardians", "Stinking Cloud", "Tongues", "Vampiric Touch",
    "Water Breathing", "Water Walk", "Wind Wall",

    # 4th Level
    "Arcane Eye", "Aura of Life", "Aura of Purity", "Banishment", "Blight",
    "Compulsion", "Confusion", "Conjure Minor Elementals", "Conjure Woodland Beings",
    "Control Water", "Death Ward", "Dimension Door", "Divination",
    "Dominate Beast", "Elemental Bane", "Evard's Black Tentacles",
    "Fabricate", "Fire Shield", "Freedom of Movement", "Giant Insect",
    "Grasping Vine", "Greater Invisibility", "Guardian of Faith",
    "Hallucinatory Terrain", "Ice Storm", "Locate Creature", "Phantasmal Killer",
    "Polymorph", "Staggering Smite", "Stone Shape", "Stoneskin", "Wall of Fire",

    # 5th Level
    "Animate Objects", "Antilife Shell", "Awaken", "Banishing Smite",
    "Bigby's Hand", "Circle of Power", "Cloudkill", "Commune",
    "Commune with Nature", "Cone of Cold", "Conjure Elemental", "Conjure Volley",
    "Contact Other Plane", "Contagion", "Creation", "Destructive Wave",
    "Dispel Evil and Good", "Dominate Person", "Dream", "Flame Strike",
    "Geas", "Greater Restoration", "Hallow", "Hold Monster", "Insect Plague",
    "Legend Lore", "Mass Cure Wounds", "Mislead", "Modify Memory",
    "Passwall", "Planar Binding", "Raise Dead", "Reincarnate", "Scrying",
    "Seeming", "Swift Quiver", "Telekinesis", "Telepathic Bond",
    "Teleportation Circle", "Tree Stride", "Wall of Force", "Wall of Stone",

    # 6th Level
    "Arcane Gate", "Blade Barrier", "Chain Lightning", "Circle of Death",
    "Conjure Fey", "Contingency", "Create Undead", "Disintegrate",
    "Eyebite", "Find the Path", "Flesh to Stone", "Forbiddance",
    "Globe of Invulnerability", "Guards and Wards", "Harm", "Heal",
    "Heroes' Feast", "Magic Jar", "Mass Suggestion", "Move Earth",
    "Otiluke's Freezing Sphere", "Otto's Irresistible Dance", "Planar Ally",
    "Programmed Illusion", "Sunbeam", "Transport via Plants",
    "True Seeing", "Wall of Ice", "Wall of Thorns", "Wind Walk", "Word of Recall",

    # 7th Level
    "Conjure Celestial", "Delayed Blast Fireball", "Divine Word", "Etherealness",
    "Finger of Death", "Fire Storm", "Forcecage", "Mirage Arcane",
    "Mordenkainen's Magnificent Mansion", "Mordenkainen's Sword", "Plane Shift",
    "Prismatic Spray", "Project Image", "Regenerate", "Resurrection",
    "Reverse Gravity", "Sequester", "Simulacrum", "Symbol", "Teleport",

    # 8th Level
    "Animal Shapes", "Antimagic Field", "Antipathy/Sympathy", "Clone",
    "Control Weather", "Demiplane", "Dominate Monster", "Earthquake",
    "Feeblemind", "Glibness", "Holy Aura", "Incendiary Cloud", "Maze",
    "Mind Blank", "Power Word Stun", "Sunburst", "Telepathy", "Tsunami",

    # 9th Level
    "Astral Projection", "Foresight", "Gate", "Imprisonment", "Mass Heal",
    "Meteor Swarm", "Power Word Kill", "Prismatic Wall", "Shapechange",
    "Storm of Vengeance", "Time Stop", "True Polymorph", "True Resurrection",
    "Weird", "Wish",
]

# =============================================================================
# CREATURES/MONSTERS - From D&D 5e SRD Monster Manual
# =============================================================================

CREATURE_NAMES = [
    # Aberrations
    "Aboleth", "Chuul", "Cloaker", "Gibbering Mouther", "Otyugh",

    # Beasts
    "Ape", "Bat", "Bear", "Boar", "Cat", "Crocodile", "Deer", "Eagle",
    "Elephant", "Frog", "Giant Ape", "Giant Bat", "Giant Boar", "Giant Crab",
    "Giant Crocodile", "Giant Eagle", "Giant Elk", "Giant Frog", "Giant Lizard",
    "Giant Owl", "Giant Rat", "Giant Scorpion", "Giant Spider", "Giant Toad",
    "Giant Vulture", "Giant Wasp", "Giant Wolf Spider", "Hawk", "Horse",
    "Hyena", "Lion", "Lizard", "Mammoth", "Mastiff", "Owl", "Panther",
    "Poisonous Snake", "Polar Bear", "Rat", "Raven", "Rhinoceros",
    "Saber-Toothed Tiger", "Scorpion", "Shark", "Spider", "Tiger", "Vulture",
    "Warhorse", "Wolf",

    # Celestials
    "Couatl", "Deva", "Pegasus", "Planetar", "Solar", "Unicorn",

    # Constructs
    "Animated Armor", "Clay Golem", "Flesh Golem", "Flying Sword",
    "Homunculus", "Iron Golem", "Rug of Smothering", "Shield Guardian",
    "Stone Golem",

    # Dragons
    "Adult Black Dragon", "Adult Blue Dragon", "Adult Brass Dragon",
    "Adult Bronze Dragon", "Adult Copper Dragon", "Adult Gold Dragon",
    "Adult Green Dragon", "Adult Red Dragon", "Adult Silver Dragon",
    "Adult White Dragon", "Ancient Black Dragon", "Ancient Blue Dragon",
    "Ancient Brass Dragon", "Ancient Bronze Dragon", "Ancient Copper Dragon",
    "Ancient Gold Dragon", "Ancient Green Dragon", "Ancient Red Dragon",
    "Ancient Silver Dragon", "Ancient White Dragon", "Black Dragon Wyrmling",
    "Blue Dragon Wyrmling", "Brass Dragon Wyrmling", "Bronze Dragon Wyrmling",
    "Copper Dragon Wyrmling", "Dragon Turtle", "Gold Dragon Wyrmling",
    "Green Dragon Wyrmling", "Pseudodragon", "Red Dragon Wyrmling",
    "Silver Dragon Wyrmling", "White Dragon Wyrmling", "Wyvern",
    "Young Black Dragon", "Young Blue Dragon", "Young Brass Dragon",
    "Young Bronze Dragon", "Young Copper Dragon", "Young Gold Dragon",
    "Young Green Dragon", "Young Red Dragon", "Young Silver Dragon",
    "Young White Dragon",

    # Elementals
    "Air Elemental", "Azer", "Dust Mephit", "Earth Elemental", "Fire Elemental",
    "Gargoyle", "Ice Mephit", "Invisible Stalker", "Magma Mephit", "Magmin",
    "Mud Mephit", "Salamander", "Smoke Mephit", "Steam Mephit", "Water Elemental",
    "Xorn",

    # Fey
    "Dryad", "Green Hag", "Night Hag", "Satyr", "Sea Hag", "Sprite",

    # Fiends
    "Balor", "Barbed Devil", "Bearded Devil", "Bone Devil", "Chain Devil",
    "Dretch", "Erinyes", "Glabrezu", "Hell Hound", "Hezrou", "Horned Devil",
    "Ice Devil", "Imp", "Lemure", "Manes", "Marilith", "Nalfeshnee", "Nightmare",
    "Pit Fiend", "Quasit", "Rakshasa", "Shadow Demon", "Succubus", "Incubus",
    "Vrock",

    # Giants
    "Cloud Giant", "Cyclops", "Ettin", "Fire Giant", "Frost Giant",
    "Hill Giant", "Ogre", "Oni", "Stone Giant", "Storm Giant", "Troll",

    # Humanoids
    "Acolyte", "Assassin", "Bandit", "Bandit Captain", "Berserker",
    "Bugbear", "Commoner", "Cultist", "Cult Fanatic", "Druid", "Drow",
    "Duergar", "Gladiator", "Gnoll", "Goblin", "Guard", "Hobgoblin",
    "Knight", "Kobold", "Lizardfolk", "Mage", "Merfolk", "Noble", "Orc",
    "Priest", "Scout", "Spy", "Thug", "Tribal Warrior", "Veteran",

    # Monstrosities
    "Ankheg", "Basilisk", "Behir", "Bulette", "Carrion Crawler", "Centaur",
    "Chimera", "Cockatrice", "Darkmantle", "Death Dog", "Displacer Beast",
    "Doppelganger", "Drider", "Ettercap", "Gorgon", "Grick", "Griffon",
    "Harpy", "Hippogriff", "Hook Horror", "Hydra", "Kraken", "Lamia",
    "Manticore", "Medusa", "Merrow", "Mimic", "Minotaur", "Owlbear",
    "Phase Spider", "Purple Worm", "Remorhaz", "Roc", "Roper", "Rust Monster",
    "Sahuagin", "Sphinx", "Stirge", "Tarrasque", "Umber Hulk", "Winter Wolf",
    "Worg", "Yeti",

    # Oozes
    "Black Pudding", "Gelatinous Cube", "Gray Ooze", "Ochre Jelly",

    # Plants
    "Awakened Shrub", "Awakened Tree", "Shambling Mound", "Treant",

    # Undead
    "Banshee", "Ghost", "Ghast", "Ghoul", "Lich", "Mummy", "Mummy Lord",
    "Shadow", "Skeleton", "Specter", "Vampire", "Vampire Spawn", "Wight",
    "Will-o'-Wisp", "Wraith", "Zombie",
]

# =============================================================================
# ITEMS - Weapons, Armor, Equipment, Magic Items from D&D 5e SRD
# =============================================================================

WEAPON_NAMES = [
    # Simple Melee
    "Club", "Dagger", "Greatclub", "Handaxe", "Javelin", "Light Hammer",
    "Mace", "Quarterstaff", "Sickle", "Spear",

    # Simple Ranged
    "Crossbow, Light", "Dart", "Shortbow", "Sling",

    # Martial Melee
    "Battleaxe", "Flail", "Glaive", "Greataxe", "Greatsword", "Halberd",
    "Lance", "Longsword", "Maul", "Morningstar", "Pike", "Rapier",
    "Scimitar", "Shortsword", "Trident", "War Pick", "Warhammer", "Whip",

    # Martial Ranged
    "Blowgun", "Crossbow, Hand", "Crossbow, Heavy", "Longbow", "Net",
]

ARMOR_NAMES = [
    # Light Armor
    "Padded Armor", "Leather Armor", "Studded Leather Armor",

    # Medium Armor
    "Hide Armor", "Chain Shirt", "Scale Mail", "Breastplate", "Half Plate",

    # Heavy Armor
    "Ring Mail", "Chain Mail", "Splint Armor", "Plate Armor",

    # Shields
    "Shield",
]

EQUIPMENT_NAMES = [
    # Adventuring Gear
    "Backpack", "Bedroll", "Bell", "Blanket", "Block and Tackle", "Book",
    "Bottle", "Bucket", "Caltrops", "Candle", "Chain", "Chalk", "Chest",
    "Climber's Kit", "Clothes", "Component Pouch", "Crowbar", "Fishing Tackle",
    "Flask", "Grappling Hook", "Hammer", "Healer's Kit", "Holy Symbol",
    "Holy Water", "Hourglass", "Hunting Trap", "Ink", "Ink Pen", "Jug",
    "Ladder", "Lamp", "Lantern", "Lock", "Magnifying Glass", "Manacles",
    "Mess Kit", "Mirror", "Oil", "Paper", "Parchment", "Perfume",
    "Pick", "Piton", "Poison", "Pole", "Pot", "Potion", "Pouch",
    "Quiver", "Ram", "Rations", "Robes", "Rope", "Sack", "Scale",
    "Sealing Wax", "Shovel", "Signal Whistle", "Signet Ring", "Soap",
    "Spellbook", "Spikes", "Spyglass", "Tent", "Tinderbox", "Torch",
    "Vial", "Waterskin", "Whetstone",

    # Tools
    "Alchemist's Supplies", "Brewer's Supplies", "Calligrapher's Supplies",
    "Carpenter's Tools", "Cartographer's Tools", "Cobbler's Tools",
    "Cook's Utensils", "Disguise Kit", "Forgery Kit", "Gaming Set",
    "Glassblower's Tools", "Herbalism Kit", "Jeweler's Tools",
    "Leatherworker's Tools", "Mason's Tools", "Navigator's Tools",
    "Painter's Supplies", "Poisoner's Kit", "Potter's Tools",
    "Smith's Tools", "Thieves' Tools", "Tinker's Tools",
    "Weaver's Tools", "Woodcarver's Tools",

    # Musical Instruments
    "Bagpipes", "Drum", "Dulcimer", "Flute", "Horn", "Lute", "Lyre",
    "Pan Flute", "Shawm", "Viol",
]

MAGIC_ITEM_NAMES = [
    # Armor
    "Adamantine Armor", "Armor of Invulnerability", "Armor of Resistance",
    "Armor of Vulnerability", "Arrow-Catching Shield", "Demon Armor",
    "Dragon Scale Mail", "Dwarven Plate", "Efreeti Chain", "Elven Chain",
    "Glamoured Studded Leather", "Mithral Armor", "Plate Armor of Etherealness",
    "Shield of Missile Attraction", "Spellguard Shield",

    # Potions
    "Potion of Healing", "Potion of Greater Healing", "Potion of Superior Healing",
    "Potion of Supreme Healing", "Potion of Animal Friendship", "Potion of Clairvoyance",
    "Potion of Climbing", "Potion of Diminution", "Potion of Fire Breath",
    "Potion of Flying", "Potion of Gaseous Form", "Potion of Giant Strength",
    "Potion of Growth", "Potion of Heroism", "Potion of Invisibility",
    "Potion of Invulnerability", "Potion of Longevity", "Potion of Mind Reading",
    "Potion of Poison", "Potion of Resistance", "Potion of Speed",
    "Potion of Vitality", "Potion of Water Breathing",

    # Rings
    "Ring of Animal Influence", "Ring of Djinni Summoning", "Ring of Elemental Command",
    "Ring of Evasion", "Ring of Feather Falling", "Ring of Free Action",
    "Ring of Invisibility", "Ring of Jumping", "Ring of Mind Shielding",
    "Ring of Protection", "Ring of Regeneration", "Ring of Resistance",
    "Ring of Shooting Stars", "Ring of Spell Storing", "Ring of Spell Turning",
    "Ring of Swimming", "Ring of Telekinesis", "Ring of the Ram",
    "Ring of Three Wishes", "Ring of Warmth", "Ring of Water Walking",
    "Ring of X-ray Vision",

    # Rods
    "Immovable Rod", "Rod of Absorption", "Rod of Alertness",
    "Rod of Lordly Might", "Rod of Rulership", "Rod of Security",

    # Scrolls
    "Spell Scroll",

    # Staffs
    "Staff of Charming", "Staff of Fire", "Staff of Frost", "Staff of Healing",
    "Staff of Power", "Staff of Striking", "Staff of Swarming Insects",
    "Staff of the Magi", "Staff of the Python", "Staff of the Woodlands",
    "Staff of Thunder and Lightning", "Staff of Withering",

    # Wands
    "Wand of Binding", "Wand of Enemy Detection", "Wand of Fear",
    "Wand of Fireballs", "Wand of Lightning Bolts", "Wand of Magic Detection",
    "Wand of Magic Missiles", "Wand of Paralysis", "Wand of Polymorph",
    "Wand of Secrets", "Wand of the War Mage", "Wand of Web", "Wand of Wonder",

    # Weapons
    "Berserker Axe", "Dancing Sword", "Defender", "Dragon Slayer",
    "Dwarven Thrower", "Flame Tongue", "Frost Brand", "Giant Slayer",
    "Holy Avenger", "Javelin of Lightning", "Luck Blade", "Mace of Disruption",
    "Mace of Smiting", "Mace of Terror", "Nine Lives Stealer", "Oathbow",
    "Scimitar of Speed", "Sun Blade", "Sword of Life Stealing",
    "Sword of Sharpness", "Sword of Wounding", "Trident of Fish Command",
    "Vicious Weapon", "Vorpal Sword", "Weapon of Warning",

    # Wondrous Items
    "Amulet of Health", "Amulet of Proof against Detection and Location",
    "Amulet of the Planes", "Bag of Beans", "Bag of Devouring", "Bag of Holding",
    "Bag of Tricks", "Bead of Force", "Belt of Dwarvenkind",
    "Belt of Giant Strength", "Boots of Elvenkind", "Boots of Levitation",
    "Boots of Speed", "Boots of Striding and Springing", "Boots of the Winterlands",
    "Bowl of Commanding Water Elementals", "Bracers of Archery",
    "Bracers of Defense", "Brazier of Commanding Fire Elementals",
    "Brooch of Shielding", "Broom of Flying", "Candle of Invocation",
    "Cape of the Mountebank", "Carpet of Flying", "Censer of Controlling Air Elementals",
    "Chime of Opening", "Circlet of Blasting", "Cloak of Arachnida",
    "Cloak of Displacement", "Cloak of Elvenkind", "Cloak of Many Fashions",
    "Cloak of Protection", "Cloak of the Bat", "Cloak of the Manta Ray",
    "Crystal Ball", "Cube of Force", "Cubic Gate", "Daern's Instant Fortress",
    "Decanter of Endless Water", "Deck of Illusions", "Deck of Many Things",
    "Dimensional Shackles", "Dust of Disappearance", "Dust of Dryness",
    "Dust of Sneezing and Choking", "Efreeti Bottle", "Elemental Gem",
    "Eyes of Charming", "Eyes of Minute Seeing", "Eyes of the Eagle",
    "Figurine of Wondrous Power", "Folding Boat", "Gauntlets of Ogre Power",
    "Gem of Brightness", "Gem of Seeing", "Gloves of Missile Snaring",
    "Gloves of Swimming and Climbing", "Gloves of Thievery",
    "Goggles of Night", "Handy Haversack", "Hat of Disguise",
    "Headband of Intellect", "Helm of Brilliance", "Helm of Comprehending Languages",
    "Helm of Telepathy", "Helm of Teleportation", "Horn of Blasting",
    "Horn of Valhalla", "Horseshoes of a Zephyr", "Horseshoes of Speed",
    "Instant Fortress", "Ioun Stone", "Iron Bands of Binding",
    "Iron Flask", "Lantern of Revealing", "Mantle of Spell Resistance",
    "Manual of Bodily Health", "Manual of Gainful Exercise", "Manual of Golems",
    "Manual of Quickness of Action", "Marvelous Pigments", "Medallion of Thoughts",
    "Mirror of Life Trapping", "Necklace of Adaptation", "Necklace of Fireballs",
    "Necklace of Prayer Beads", "Orb of Dragonkind", "Periapt of Health",
    "Periapt of Proof against Poison", "Periapt of Wound Closure",
    "Pipes of Haunting", "Pipes of the Sewers", "Portable Hole",
    "Robe of Eyes", "Robe of Scintillating Colors", "Robe of Stars",
    "Robe of the Archmagi", "Robe of Useful Items", "Rope of Climbing",
    "Rope of Entanglement", "Scarab of Protection", "Sending Stones",
    "Slippers of Spider Climbing", "Sovereign Glue", "Sphere of Annihilation",
    "Stone of Controlling Earth Elementals", "Stone of Good Luck",
    "Talisman of Pure Good", "Talisman of the Sphere", "Talisman of Ultimate Evil",
    "Tome of Clear Thought", "Tome of Leadership and Influence",
    "Tome of Understanding", "Universal Solvent", "Well of Many Worlds",
    "Wind Fan", "Winged Boots", "Wings of Flying",
]

# Combine all items
ITEM_NAMES = WEAPON_NAMES + ARMOR_NAMES + EQUIPMENT_NAMES + MAGIC_ITEM_NAMES

# =============================================================================
# CLASS FEATURES - From D&D 5e SRD Class Descriptions
# =============================================================================

CLASS_FEATURE_NAMES = [
    # Barbarian
    "Rage", "Unarmored Defense", "Reckless Attack", "Danger Sense",
    "Primal Path", "Extra Attack", "Fast Movement", "Feral Instinct",
    "Brutal Critical", "Relentless Rage", "Persistent Rage", "Indomitable Might",
    "Primal Champion", "Frenzy", "Mindless Rage", "Intimidating Presence",
    "Retaliation",

    # Bard
    "Bardic Inspiration", "Jack of All Trades", "Song of Rest", "Bard College",
    "Expertise", "Font of Inspiration", "Countercharm", "Magical Secrets",
    "Superior Inspiration", "Cutting Words", "Additional Magical Secrets",
    "Peerless Skill",

    # Cleric
    "Spellcasting", "Divine Domain", "Channel Divinity", "Turn Undead",
    "Destroy Undead", "Divine Intervention", "Disciple of Life",
    "Preserve Life", "Blessed Healer", "Divine Strike", "Supreme Healing",

    # Druid
    "Druidic", "Wild Shape", "Druid Circle", "Timeless Body", "Beast Spells",
    "Archdruid", "Natural Recovery", "Circle Spells", "Land's Stride",
    "Nature's Ward", "Nature's Sanctuary",

    # Fighter
    "Fighting Style", "Second Wind", "Action Surge", "Martial Archetype",
    "Indomitable", "Improved Critical", "Remarkable Athlete",
    "Additional Fighting Style", "Superior Critical", "Survivor",

    # Monk
    "Martial Arts", "Ki", "Unarmored Movement", "Monastic Tradition",
    "Deflect Missiles", "Slow Fall", "Stunning Strike", "Ki-Empowered Strikes",
    "Evasion", "Stillness of Mind", "Purity of Body", "Tongue of the Sun and Moon",
    "Diamond Soul", "Timeless Body", "Empty Body", "Perfect Self",
    "Flurry of Blows", "Patient Defense", "Step of the Wind",
    "Open Hand Technique", "Wholeness of Body", "Tranquility", "Quivering Palm",

    # Paladin
    "Divine Sense", "Lay on Hands", "Divine Smite", "Divine Health",
    "Sacred Oath", "Aura of Protection", "Aura of Courage", "Improved Divine Smite",
    "Cleansing Touch", "Channel Divinity", "Aura of Devotion", "Purity of Spirit",
    "Holy Nimbus",

    # Ranger
    "Favored Enemy", "Natural Explorer", "Primeval Awareness", "Ranger Archetype",
    "Land's Stride", "Hide in Plain Sight", "Vanish", "Feral Senses",
    "Foe Slayer", "Hunter's Prey", "Defensive Tactics", "Multiattack",
    "Superior Hunter's Defense", "Colossus Slayer", "Giant Killer", "Horde Breaker",

    # Rogue
    "Sneak Attack", "Thieves' Cant", "Cunning Action", "Roguish Archetype",
    "Uncanny Dodge", "Reliable Talent", "Blindsense", "Slippery Mind",
    "Elusive", "Stroke of Luck", "Fast Hands", "Second-Story Work",
    "Supreme Sneak", "Use Magic Device", "Thief's Reflexes",

    # Sorcerer
    "Sorcerous Origin", "Font of Magic", "Sorcery Points", "Metamagic",
    "Sorcerous Restoration", "Draconic Resilience", "Elemental Affinity",
    "Dragon Wings", "Draconic Presence", "Careful Spell", "Distant Spell",
    "Empowered Spell", "Extended Spell", "Heightened Spell", "Quickened Spell",
    "Subtle Spell", "Twinned Spell",

    # Warlock
    "Otherworldly Patron", "Pact Magic", "Eldritch Invocations", "Pact Boon",
    "Mystic Arcanum", "Eldritch Master", "Pact of the Chain", "Pact of the Blade",
    "Pact of the Tome", "Dark One's Blessing", "Dark One's Own Luck",
    "Fiendish Resilience", "Hurl Through Hell", "Agonizing Blast",
    "Armor of Shadows", "Devil's Sight", "Eldritch Sight", "Mask of Many Faces",
    "Repelling Blast", "Thirsting Blade",

    # Wizard
    "Arcane Recovery", "Arcane Tradition", "Spell Mastery", "Signature Spells",
    "Evocation Savant", "Sculpt Spells", "Potent Cantrip", "Empowered Evocation",
    "Overchannel",
]

# =============================================================================
# RACES AND CLASSES
# =============================================================================

RACE_NAMES = [
    "Dragonborn", "Dwarf", "Hill Dwarf", "Mountain Dwarf", "Elf", "High Elf",
    "Wood Elf", "Dark Elf", "Drow", "Gnome", "Rock Gnome", "Forest Gnome",
    "Half-Elf", "Half-Orc", "Halfling", "Lightfoot Halfling", "Stout Halfling",
    "Human", "Tiefling", "Aasimar", "Genasi", "Goliath", "Tabaxi", "Tortle",
    "Kenku", "Lizardfolk", "Triton", "Firbolg", "Bugbear", "Goblin", "Hobgoblin",
    "Kobold", "Orc", "Yuan-ti",
]

CLASS_NAMES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
    "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard",
    "Artificer", "Blood Hunter",
]

SUBCLASS_NAMES = [
    # Barbarian
    "Path of the Berserker", "Path of the Totem Warrior", "Path of the Ancestral Guardian",
    "Path of the Storm Herald", "Path of the Zealot",

    # Bard
    "College of Lore", "College of Valor", "College of Glamour",
    "College of Swords", "College of Whispers",

    # Cleric
    "Life Domain", "Light Domain", "Nature Domain", "Tempest Domain",
    "Trickery Domain", "War Domain", "Knowledge Domain", "Death Domain",
    "Forge Domain", "Grave Domain", "Order Domain", "Peace Domain", "Twilight Domain",

    # Druid
    "Circle of the Land", "Circle of the Moon", "Circle of Dreams",
    "Circle of the Shepherd", "Circle of Spores", "Circle of Stars", "Circle of Wildfire",

    # Fighter
    "Champion", "Battle Master", "Eldritch Knight", "Arcane Archer",
    "Cavalier", "Samurai", "Echo Knight", "Psi Warrior", "Rune Knight",

    # Monk
    "Way of the Open Hand", "Way of Shadow", "Way of the Four Elements",
    "Way of the Drunken Master", "Way of the Kensei", "Way of the Sun Soul",
    "Way of the Long Death", "Way of Mercy", "Way of the Astral Self",

    # Paladin
    "Oath of Devotion", "Oath of the Ancients", "Oath of Vengeance",
    "Oath of Conquest", "Oath of Redemption", "Oath of Glory",
    "Oath of the Crown", "Oath of the Watchers", "Oathbreaker",

    # Ranger
    "Hunter", "Beast Master", "Gloom Stalker", "Horizon Walker",
    "Monster Slayer", "Fey Wanderer", "Swarmkeeper", "Drakewarden",

    # Rogue
    "Thief", "Assassin", "Arcane Trickster", "Inquisitive", "Mastermind",
    "Scout", "Swashbuckler", "Phantom", "Soulknife",

    # Sorcerer
    "Draconic Bloodline", "Wild Magic", "Divine Soul", "Shadow Magic",
    "Storm Sorcery", "Aberrant Mind", "Clockwork Soul",

    # Warlock
    "The Archfey", "The Fiend", "The Great Old One", "The Celestial",
    "The Hexblade", "The Fathomless", "The Genie", "The Undead",

    # Wizard
    "School of Abjuration", "School of Conjuration", "School of Divination",
    "School of Enchantment", "School of Evocation", "School of Illusion",
    "School of Necromancy", "School of Transmutation", "Bladesinging",
    "War Magic", "Order of Scribes", "Chronurgy Magic", "Graviturgy Magic",
]

# =============================================================================
# CONDITIONS
# =============================================================================

CONDITION_NAMES = [
    "Blinded", "Charmed", "Deafened", "Exhaustion", "Frightened",
    "Grappled", "Incapacitated", "Invisible", "Paralyzed", "Petrified",
    "Poisoned", "Prone", "Restrained", "Stunned", "Unconscious",
]

# =============================================================================
# LOCATIONS / PLANES
# =============================================================================

LOCATION_NAMES = [
    # Planes of Existence
    "Material Plane", "Feywild", "Shadowfell", "Ethereal Plane", "Astral Plane",
    "Elemental Plane of Air", "Elemental Plane of Earth", "Elemental Plane of Fire",
    "Elemental Plane of Water", "Elemental Chaos", "Para-Elemental Planes",

    # Outer Planes
    "Mount Celestia", "Bytopia", "Elysium", "The Beastlands", "Arborea",
    "Ysgard", "Limbo", "Pandemonium", "The Abyss", "Carceri", "Hades",
    "Gehenna", "Nine Hells", "Acheron", "Mechanus", "Arcadia", "Outlands",
    "Sigil",

    # Generic Fantasy Locations
    "Underdark", "Dungeon", "Cave", "Castle", "Tower", "Temple", "Shrine",
    "Tomb", "Crypt", "Forest", "Swamp", "Mountain", "Desert", "Tundra",
    "Ocean", "Island", "City", "Village", "Town", "Fortress", "Ruins",
    "Tavern", "Inn", "Guild Hall", "Arena", "Marketplace", "Harbor",
    "Library", "Academy", "Monastery", "Cathedral", "Graveyard", "Prison",
]

# =============================================================================
# DAMAGE TYPES
# =============================================================================

DAMAGE_TYPES = [
    "Acid", "Bludgeoning", "Cold", "Fire", "Force", "Lightning",
    "Necrotic", "Piercing", "Poison", "Psychic", "Radiant", "Slashing", "Thunder",
]

# =============================================================================
# SKILLS
# =============================================================================

SKILL_NAMES = [
    "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
    "History", "Insight", "Intimidation", "Investigation", "Medicine",
    "Nature", "Perception", "Performance", "Persuasion", "Religion",
    "Sleight of Hand", "Stealth", "Survival",
]

# =============================================================================
# ABILITY SCORES
# =============================================================================

ABILITY_NAMES = [
    "Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma",
    "STR", "DEX", "CON", "INT", "WIS", "CHA",
]

# =============================================================================
# COMBAT STATS
# =============================================================================

COMBAT_STAT_NAMES = [
    "AC", "Armor Class", "HP", "Hit Points", "Hit Dice",
    "Initiative", "Speed", "Walking Speed", "Flying Speed", "Swimming Speed",
    "Climbing Speed", "Proficiency Bonus", "Spell Save DC", "Spell Attack Bonus",
    "Attack Bonus", "Damage Bonus",
]

# =============================================================================
# SLOT MAPPINGS FOR TEMPLATE FILLING
# =============================================================================

SLOT_FILLERS = {
    "spell": SPELL_NAMES,
    "spell_name": SPELL_NAMES,
    "creature": CREATURE_NAMES,
    "monster": CREATURE_NAMES,
    "npc_type": CREATURE_NAMES[:50],  # Use first 50 as generic NPC types
    "item": ITEM_NAMES,
    "item_name": ITEM_NAMES,
    "weapon": WEAPON_NAMES,
    "armor": ARMOR_NAMES,
    "magic_item": MAGIC_ITEM_NAMES,
    "equipment": EQUIPMENT_NAMES,
    "feature": CLASS_FEATURE_NAMES,
    "class_feature": CLASS_FEATURE_NAMES,
    "race": RACE_NAMES,
    "class": CLASS_NAMES,
    "class_name": CLASS_NAMES,
    "subclass": SUBCLASS_NAMES,
    "condition": CONDITION_NAMES,
    "location": LOCATION_NAMES,
    "plane": LOCATION_NAMES[:20],  # Planes only
    "damage_type": DAMAGE_TYPES,
    "skill": SKILL_NAMES,
    "ability": ABILITY_NAMES,
    "stat": COMBAT_STAT_NAMES + ABILITY_NAMES,
    "combat_stat": COMBAT_STAT_NAMES,
}

# =============================================================================
# NER ENTITY TYPE MAPPING
# =============================================================================

# Maps entity type to the lists that contain entities of that type
NER_ENTITY_MAPPING = {
    "SPELL": SPELL_NAMES,
    "ITEM": ITEM_NAMES,
    "CREATURE": CREATURE_NAMES,
    "LOCATION": LOCATION_NAMES,
    "FEATURE": CLASS_FEATURE_NAMES,
    "CLASS": CLASS_NAMES + SUBCLASS_NAMES,
    "RACE": RACE_NAMES,
    "CONDITION": CONDITION_NAMES,
}

# All entities combined for gazetteer lookup
ALL_ENTITIES = (
    SPELL_NAMES + CREATURE_NAMES + ITEM_NAMES + CLASS_FEATURE_NAMES +
    RACE_NAMES + CLASS_NAMES + SUBCLASS_NAMES + CONDITION_NAMES + LOCATION_NAMES
)


def get_entity_type(entity_name: str) -> str | None:
    """
    Determine the entity type for a given entity name.
    Returns the NER tag (SPELL, ITEM, etc.) or None if not found.
    """
    entity_lower = entity_name.lower()

    for entity_type, entity_list in NER_ENTITY_MAPPING.items():
        if any(e.lower() == entity_lower for e in entity_list):
            return entity_type

    return None


def get_slot_values(slot_name: str) -> list[str]:
    """
    Get the list of possible values for a template slot.
    """
    return SLOT_FILLERS.get(slot_name, [])
