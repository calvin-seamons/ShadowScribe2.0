"""
Character Query System Types

This module defines types for handling user queries about character information.
It maps user intentions to required character data and provides a structured
way to return relevant information.
"""

from typing import Dict, List, Optional, Union, Any, Literal, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ===== ENTITY TYPES =====

class EntityType(Enum):
    """Types of entities that can be referenced in queries."""
    SPELL = "spell"
    ITEM = "item"
    WEAPON = "weapon"
    ARMOR = "armor"
    FEATURE = "feature"
    TRAIT = "trait"
    QUEST = "quest"
    CONTRACT = "contract"
    ALLY = "ally"
    ENEMY = "enemy"
    ORGANIZATION = "organization"
    ABILITY = "ability"
    SKILL = "skill"
    ACTION = "action"
    CLASS = "class"
    RACE = "race"
    BACKGROUND = "background"
    CONDITION = "condition"
    RESOURCE = "resource"


@dataclass
class QueryEntity:
    """An entity referenced in a user query."""
    name: str
    type: EntityType
    raw_text: str  # Original text from user
    confidence: float = 1.0  # Confidence in entity recognition
    attributes: Dict[str, Any] = field(default_factory=dict)


# ===== INTENTION CATEGORIES =====

class IntentionCategory(Enum):
    """High-level categories of user intentions."""
    COMBAT = "combat"
    INVENTORY = "inventory"
    MAGIC = "magic"
    CHARACTER_SHEET = "character_sheet"
    BACKSTORY = "backstory"
    ABILITIES = "abilities"
    PROGRESSION = "progression"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    RESOURCES = "resources"
    RULES = "rules"
    OPTIMIZATION = "optimization"


# ===== USER INTENTIONS =====

class UserIntention(Enum):
    """Streamlined list of user intentions that map directly to character data structure."""
    
    # Core Character Information (maps to character_base, characteristics, ability_scores)
    CHARACTER_BASICS = "character_basics"  # Name, race, class, level, alignment, physical traits
    ABILITY_SCORES = "ability_scores"      # Strength, dex, con, int, wis, cha + modifiers
    
    # Combat & Defense (maps to combat_stats, damage_modifiers, passive_scores)
    COMBAT_INFO = "combat_info"            # HP, AC, initiative, speed, saving throws, resistances
    ACTION_ECONOMY = "action_economy"      # Available actions, attacks, reactions, bonus actions
    
    # Skills & Proficiencies (maps to proficiencies, passive_scores)
    PROFICIENCIES = "proficiencies"        # All proficiencies: skills, tools, languages, armor, weapons
    PASSIVE_ABILITIES = "passive_abilities" # Passive perception, investigation, insight, etc.
    
    # Movement & Senses (maps to senses, combat_stats.speed)
    MOVEMENT_SENSES = "movement_senses"    # Movement speed, special movement, senses, vision
    
    # Features & Abilities (maps to features_and_traits)
    CLASS_FEATURES = "class_features"      # Class features and abilities
    RACIAL_TRAITS = "racial_traits"       # Racial traits and abilities  
    BACKGROUND_FEATURES = "background_features" # Background features
    FEATS = "feats"                       # Feats and their effects
    ALL_FEATURES = "all_features"         # All features and traits combined
    
    # Inventory & Equipment (maps to inventory)
    INVENTORY = "inventory"               # Full inventory, equipped items, carrying capacity
    WEAPONS = "weapons"                   # Weapon details and attack options
    ARMOR_EQUIPMENT = "armor_equipment"   # Armor and protective equipment
    MAGICAL_ITEMS = "magical_items"       # Magic items and their properties
    
    # Spellcasting (maps to spell_list)
    SPELLCASTING = "spellcasting"         # Spell save DC, attack bonus, spellcasting ability
    SPELL_LIST = "spell_list"             # Known/prepared spells by level
    SPELL_DETAILS = "spell_details"       # Specific spell information
    SPELL_SLOTS = "spell_slots"           # Available spell slots by level
    
    # Background & Story (maps to background_info, personality, backstory)
    BACKGROUND_INFO = "background_info"   # Background, lifestyle, languages
    PERSONALITY = "personality"           # Personality traits, ideals, bonds, flaws
    BACKSTORY = "backstory"              # Character backstory and history
    
    # Relationships (maps to organizations, allies, enemies)
    RELATIONSHIPS = "relationships"       # Organizations, allies, enemies, contacts
    
    # Objectives & Progress (maps to objectives_and_contracts)
    OBJECTIVES = "objectives"             # Active quests, contracts, goals
    COMPLETED_OBJECTIVES = "completed_objectives" # Completed quests and contracts
    
    # Character Development (maps to character_base levels, notes)
    PROGRESSION = "progression"           # Level, XP, advancement options
    
    # Full Character Data
    FULL_CHARACTER_SHEET = "full_character_sheet" # Complete character information
    CHARACTER_SUMMARY = "character_summary"       # High-level character overview
    
    # Calculations & Analysis (computed from multiple data sources)
    CALCULATIONS = "calculations"         # Damage calculations, optimization analysis
    
    # Session & Roleplay (maps to notes, personality)
    ROLEPLAY_INFO = "roleplay_info"      # Character voice, motivations, session prep


# ===== QUERY INPUT/OUTPUT TYPES =====


@dataclass
class DataRequirement:
    """Specifies what character data is needed."""
    primary_fields: Set[str]  # Top-level Character fields needed
    nested_objects: Dict[str, List[str]] = field(default_factory=dict)  # Specific nested data
    filters: Dict[str, Any] = field(default_factory=dict)  # Filtering criteria
    include_relationships: bool = True  # Include related objects
    depth_limit: Optional[int] = None  # How deep to traverse nested objects


@dataclass
class CharacterInformationResult:
    """Output structure containing requested character information."""
    query: str # Original user query
    data_retrieved: Dict[str, Any]  # Actual character data


# ===== INTENTION MAPPING =====

@dataclass
class IntentionMapping:
    """Maps user intentions to required character data."""
    intention: UserIntention
    category: IntentionCategory
    required_fields: Set[str]
    optional_fields: Set[str] = field(default_factory=set)
    nested_requirements: Dict[str, List[str]] = field(default_factory=dict)
    entity_types: Set[EntityType] = field(default_factory=set)
    calculation_required: bool = False
    aggregation_required: bool = False


# ===== INTENTION TO DATA MAPPINGS =====

class IntentionDataMapper:
    """Maps all user intentions to their data requirements."""
    
    @staticmethod
    def get_mappings() -> Dict[UserIntention, IntentionMapping]:
        """Returns comprehensive mapping of intentions to data requirements."""
        return {
            # Core Character Information
            UserIntention.CHARACTER_BASICS: IntentionMapping(
                intention=UserIntention.CHARACTER_BASICS,
                category=IntentionCategory.CHARACTER_SHEET,
                required_fields={'character_base', 'characteristics'},
                entity_types={EntityType.RACE, EntityType.CLASS, EntityType.BACKGROUND}
            ),
            
            UserIntention.ABILITY_SCORES: IntentionMapping(
                intention=UserIntention.ABILITY_SCORES,
                category=IntentionCategory.CHARACTER_SHEET,
                required_fields={'ability_scores'},
                optional_fields={'character_base'},  # For proficiency bonus
                calculation_required=True
            ),
            
            # Combat & Defense
            UserIntention.COMBAT_INFO: IntentionMapping(
                intention=UserIntention.COMBAT_INFO,
                category=IntentionCategory.COMBAT,
                required_fields={'combat_stats', 'ability_scores', 'damage_modifiers'},
                optional_fields={'inventory', 'features_and_traits', 'proficiencies'},
                calculation_required=True
            ),
            
            UserIntention.ACTION_ECONOMY: IntentionMapping(
                intention=UserIntention.ACTION_ECONOMY,
                category=IntentionCategory.COMBAT,
                required_fields={'action_economy'},
                optional_fields={'inventory', 'features_and_traits', 'spell_list'},
                entity_types={EntityType.WEAPON, EntityType.ACTION, EntityType.SPELL},
                aggregation_required=True
            ),
            
            # Skills & Proficiencies
            UserIntention.PROFICIENCIES: IntentionMapping(
                intention=UserIntention.PROFICIENCIES,
                category=IntentionCategory.ABILITIES,
                required_fields={'proficiencies'},
                optional_fields={'background_info', 'character_base'},
                entity_types={EntityType.SKILL},
                aggregation_required=True
            ),
            
            UserIntention.PASSIVE_ABILITIES: IntentionMapping(
                intention=UserIntention.PASSIVE_ABILITIES,
                category=IntentionCategory.ABILITIES,
                required_fields={'passive_scores'},
                optional_fields={'ability_scores', 'proficiencies', 'features_and_traits'},
                calculation_required=True
            ),
            
            # Movement & Senses
            UserIntention.MOVEMENT_SENSES: IntentionMapping(
                intention=UserIntention.MOVEMENT_SENSES,
                category=IntentionCategory.EXPLORATION,
                required_fields={'senses', 'combat_stats'},
                optional_fields={'features_and_traits', 'inventory'},
                calculation_required=True
            ),
            
            # Features & Abilities
            UserIntention.CLASS_FEATURES: IntentionMapping(
                intention=UserIntention.CLASS_FEATURES,
                category=IntentionCategory.ABILITIES,
                required_fields={'features_and_traits', 'character_base'},
                nested_requirements={'features_and_traits': ['class_features']},
                entity_types={EntityType.FEATURE, EntityType.CLASS}
            ),
            
            UserIntention.RACIAL_TRAITS: IntentionMapping(
                intention=UserIntention.RACIAL_TRAITS,
                category=IntentionCategory.ABILITIES,
                required_fields={'features_and_traits', 'character_base'},
                nested_requirements={'features_and_traits': ['racial_traits']},
                entity_types={EntityType.TRAIT, EntityType.RACE}
            ),
            
            UserIntention.BACKGROUND_FEATURES: IntentionMapping(
                intention=UserIntention.BACKGROUND_FEATURES,
                category=IntentionCategory.ABILITIES,
                required_fields={'background_info'},
                nested_requirements={'background_info': ['feature']},
                entity_types={EntityType.FEATURE, EntityType.BACKGROUND}
            ),
            
            UserIntention.FEATS: IntentionMapping(
                intention=UserIntention.FEATS,
                category=IntentionCategory.ABILITIES,
                required_fields={'features_and_traits'},
                nested_requirements={'features_and_traits': ['feats']},
                entity_types={EntityType.FEATURE}
            ),
            
            UserIntention.ALL_FEATURES: IntentionMapping(
                intention=UserIntention.ALL_FEATURES,
                category=IntentionCategory.ABILITIES,
                required_fields={'features_and_traits', 'background_info'},
                aggregation_required=True
            ),
            
            # Inventory & Equipment
            UserIntention.INVENTORY: IntentionMapping(
                intention=UserIntention.INVENTORY,
                category=IntentionCategory.INVENTORY,
                required_fields={'inventory'},
                optional_fields={'ability_scores'},  # For carrying capacity
                entity_types={EntityType.ITEM, EntityType.WEAPON, EntityType.ARMOR},
                aggregation_required=True,
                calculation_required=True
            ),
            
            UserIntention.WEAPONS: IntentionMapping(
                intention=UserIntention.WEAPONS,
                category=IntentionCategory.INVENTORY,
                required_fields={'inventory'},
                optional_fields={'ability_scores', 'proficiencies'},
                nested_requirements={'inventory': ['equipped_items', 'backpack']},
                entity_types={EntityType.WEAPON},
                aggregation_required=True
            ),
            
            UserIntention.ARMOR_EQUIPMENT: IntentionMapping(
                intention=UserIntention.ARMOR_EQUIPMENT,
                category=IntentionCategory.INVENTORY,
                required_fields={'inventory'},
                nested_requirements={'inventory': ['equipped_items']},
                entity_types={EntityType.ARMOR},
                aggregation_required=True
            ),
            
            UserIntention.MAGICAL_ITEMS: IntentionMapping(
                intention=UserIntention.MAGICAL_ITEMS,
                category=IntentionCategory.INVENTORY,
                required_fields={'inventory'},
                nested_requirements={'inventory': ['equipped_items', 'backpack']},
                entity_types={EntityType.ITEM},
                aggregation_required=True
            ),
            
            # Spellcasting
            UserIntention.SPELLCASTING: IntentionMapping(
                intention=UserIntention.SPELLCASTING,
                category=IntentionCategory.MAGIC,
                required_fields={'spell_list', 'ability_scores', 'character_base'},
                nested_requirements={'spell_list': ['spellcasting']},
                calculation_required=True
            ),
            
            UserIntention.SPELL_LIST: IntentionMapping(
                intention=UserIntention.SPELL_LIST,
                category=IntentionCategory.MAGIC,
                required_fields={'spell_list'},
                nested_requirements={'spell_list': ['spells', 'spellcasting']},
                entity_types={EntityType.SPELL},
                aggregation_required=True
            ),
            
            UserIntention.SPELL_DETAILS: IntentionMapping(
                intention=UserIntention.SPELL_DETAILS,
                category=IntentionCategory.MAGIC,
                required_fields={'spell_list'},
                nested_requirements={'spell_list': ['spells']},
                entity_types={EntityType.SPELL}
            ),
            
            UserIntention.SPELL_SLOTS: IntentionMapping(
                intention=UserIntention.SPELL_SLOTS,
                category=IntentionCategory.MAGIC,
                required_fields={'spell_list'},
                nested_requirements={'spell_list': ['spellcasting']},
                calculation_required=True
            ),
            
            # Background & Story
            UserIntention.BACKGROUND_INFO: IntentionMapping(
                intention=UserIntention.BACKGROUND_INFO,
                category=IntentionCategory.BACKSTORY,
                required_fields={'background_info'},
                entity_types={EntityType.BACKGROUND}
            ),
            
            UserIntention.PERSONALITY: IntentionMapping(
                intention=UserIntention.PERSONALITY,
                category=IntentionCategory.BACKSTORY,
                required_fields={'personality'}
            ),
            
            UserIntention.BACKSTORY: IntentionMapping(
                intention=UserIntention.BACKSTORY,
                category=IntentionCategory.BACKSTORY,
                required_fields={'backstory'},
                optional_fields={'background_info', 'personality'}
            ),
            
            # Relationships
            UserIntention.RELATIONSHIPS: IntentionMapping(
                intention=UserIntention.RELATIONSHIPS,
                category=IntentionCategory.SOCIAL,
                required_fields={'organizations', 'allies', 'enemies'},
                entity_types={EntityType.ALLY, EntityType.ENEMY, EntityType.ORGANIZATION},
                aggregation_required=True
            ),
            
            # Objectives & Progress
            UserIntention.OBJECTIVES: IntentionMapping(
                intention=UserIntention.OBJECTIVES,
                category=IntentionCategory.PROGRESSION,
                required_fields={'objectives_and_contracts'},
                nested_requirements={'objectives_and_contracts': ['current_objectives', 'active_contracts']},
                entity_types={EntityType.QUEST, EntityType.CONTRACT},
                aggregation_required=True
            ),
            
            UserIntention.COMPLETED_OBJECTIVES: IntentionMapping(
                intention=UserIntention.COMPLETED_OBJECTIVES,
                category=IntentionCategory.PROGRESSION,
                required_fields={'objectives_and_contracts'},
                nested_requirements={'objectives_and_contracts': ['completed_objectives']},
                entity_types={EntityType.QUEST, EntityType.CONTRACT},
                aggregation_required=True
            ),
            
            # Character Development
            UserIntention.PROGRESSION: IntentionMapping(
                intention=UserIntention.PROGRESSION,
                category=IntentionCategory.PROGRESSION,
                required_fields={'character_base'},
                optional_fields={'notes'},
                calculation_required=True
            ),
            
            # Full Character Data
            UserIntention.FULL_CHARACTER_SHEET: IntentionMapping(
                intention=UserIntention.FULL_CHARACTER_SHEET,
                category=IntentionCategory.CHARACTER_SHEET,
                required_fields={
                    'character_base', 'characteristics', 'ability_scores', 'combat_stats',
                    'background_info', 'personality', 'backstory', 'organizations', 'allies',
                    'enemies', 'proficiencies', 'damage_modifiers', 'passive_scores', 'senses',
                    'action_economy', 'features_and_traits', 'inventory', 'spell_list',
                    'objectives_and_contracts', 'notes'
                }
            ),
            
            UserIntention.CHARACTER_SUMMARY: IntentionMapping(
                intention=UserIntention.CHARACTER_SUMMARY,
                category=IntentionCategory.CHARACTER_SHEET,
                required_fields={'character_base', 'ability_scores', 'combat_stats'},
                optional_fields={'background_info', 'personality'},
                aggregation_required=True
            ),
            
            # Calculations & Analysis
            UserIntention.CALCULATIONS: IntentionMapping(
                intention=UserIntention.CALCULATIONS,
                category=IntentionCategory.OPTIMIZATION,
                required_fields={'ability_scores', 'inventory', 'features_and_traits'},
                optional_fields={'spell_list', 'proficiencies'},
                calculation_required=True,
                aggregation_required=True
            ),
            
            # Session & Roleplay
            UserIntention.ROLEPLAY_INFO: IntentionMapping(
                intention=UserIntention.ROLEPLAY_INFO,
                category=IntentionCategory.SOCIAL,
                required_fields={'personality', 'backstory'},
                optional_fields={'notes', 'relationships'}
            )
        }
    
    @staticmethod
    def get_data_requirements(intentions: List[UserIntention]) -> DataRequirement:
        """Combine data requirements for multiple intentions."""
        all_mappings = IntentionDataMapper.get_mappings()
        
        primary_fields = set()
        nested_objects = {}
        entity_types = set()
        
        for intention in intentions:
            if intention in all_mappings:
                mapping = all_mappings[intention]
                primary_fields.update(mapping.required_fields)
                primary_fields.update(mapping.optional_fields)
                
                for field, nested in mapping.nested_requirements.items():
                    if field not in nested_objects:
                        nested_objects[field] = []
                    nested_objects[field].extend(nested)
                
                entity_types.update(mapping.entity_types)
        
        return DataRequirement(
            primary_fields=primary_fields,
            nested_objects=nested_objects,
            include_relationships=True
        )


@dataclass
class CharacterQueryPerformanceMetrics:
    """Detailed timing performance information for character query operations"""
    total_time_ms: float = 0.0
    character_loading_ms: float = 0.0
    intention_mapping_ms: float = 0.0
    data_extraction_ms: float = 0.0
    entity_filtering_ms: float = 0.0
    serialization_ms: float = 0.0
    
    # Entity processing metrics
    entities_processed: int = 0
    entity_matches_found: int = 0
    
    # Data scope metrics
    total_character_fields: int = 0
    fields_extracted: int = 0
    objects_serialized: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for analysis"""
        return {
            'total_time_ms': self.total_time_ms,
            'timing_breakdown': {
                'character_loading_ms': self.character_loading_ms,
                'intention_mapping_ms': self.intention_mapping_ms,
                'data_extraction_ms': self.data_extraction_ms,
                'entity_filtering_ms': self.entity_filtering_ms,
                'serialization_ms': self.serialization_ms
            },
            'entity_processing': {
                'entities_processed': self.entities_processed,
                'entity_matches_found': self.entity_matches_found
            },
            'data_scope': {
                'total_character_fields': self.total_character_fields,
                'fields_extracted': self.fields_extracted,
                'objects_serialized': self.objects_serialized
            }
        }


# ===== PROMPT GENERATION HELPERS =====

class CharacterPromptHelper:
    """Provides prompt-ready information for character intents and entity types."""
    
    @staticmethod
    def get_intent_definitions() -> Dict[str, str]:
        """Returns all character intentions with their definitions for prompts."""
        return {
            "character_basics": "Name, race, class, level, alignment, physical traits",
            "ability_scores": "STR, DEX, CON, INT, WIS, CHA scores and modifiers",
            "combat_info": "HP, AC, initiative, speed, saving throws, resistances", 
            "action_economy": "Available actions, attacks, reactions, bonus actions",
            "proficiencies": "All proficiencies: skills, tools, languages, armor, weapons",
            "passive_abilities": "Passive perception, investigation, insight, etc.",
            "movement_senses": "Movement speed, special movement, senses, vision",
            "class_features": "Class features and abilities",
            "racial_traits": "Racial traits and abilities",
            "background_features": "Background features",
            "feats": "Feats and their effects",
            "all_features": "All features and traits combined",
            "inventory": "Full inventory, equipped items, carrying capacity",
            "weapons": "Weapon details and attack options",
            "armor_equipment": "Armor and protective equipment",
            "magical_items": "Magic items and their properties",
            "spellcasting": "Spell save DC, attack bonus, spellcasting ability",
            "spell_list": "Known/prepared spells by level",
            "spell_details": "Specific spell information",
            "spell_slots": "Available spell slots by level",
            "background_info": "Background, lifestyle, languages",
            "personality": "Personality traits, ideals, bonds, flaws",
            "backstory": "Character backstory and history",
            "relationships": "Organizations, allies, enemies, contacts",
            "objectives": "Active quests, contracts, goals",
            "completed_objectives": "Completed quests and contracts",
            "progression": "Level, XP, advancement options",
            "full_character_sheet": "Complete character information",
            "character_summary": "High-level character overview",
            "calculations": "Damage calculations, optimization analysis",
            "roleplay_info": "Character voice, motivations, session prep"
        }
    
    @staticmethod
    def get_entity_type_definitions() -> Dict[str, str]:
        """Returns all character entity types with examples for prompts."""
        return {
            "spell": "Magic spells (e.g., 'fireball', 'cure wounds')",
            "item": "General items (e.g., 'rope', 'torch', 'healing potion')",
            "weapon": "Weapons (e.g., 'longsword', 'shortbow', 'dagger')",
            "armor": "Armor and shields (e.g., 'chainmail', 'leather armor', 'shield')",
            "feature": "Class features (e.g., 'rage', 'sneak attack', 'action surge')",
            "trait": "Racial traits (e.g., 'darkvision', 'lucky', 'stone cunning')",
            "quest": "Quests and missions (e.g., 'rescue the princess', 'find the artifact')",
            "contract": "Formal contracts (e.g., 'assassination contract', 'escort mission')",
            "ally": "Allies and friends (e.g., 'tavern keeper', 'guild contact')",
            "enemy": "Enemies and foes (e.g., 'red dragon', 'orc chieftain')",
            "organization": "Groups and organizations (e.g., 'thieves guild', 'royal guard')",
            "ability": "Abilities and skills (e.g., 'athletics', 'perception', 'insight')",
            "skill": "Skill proficiencies (e.g., 'stealth', 'investigation', 'persuasion')",
            "action": "Combat actions (e.g., 'attack', 'dash', 'dodge', 'help')",
            "class": "Character classes (e.g., 'fighter', 'wizard', 'rogue')",
            "race": "Character races (e.g., 'elf', 'dwarf', 'human')",
            "background": "Character backgrounds (e.g., 'criminal', 'soldier', 'noble')",
            "condition": "Status conditions (e.g., 'poisoned', 'stunned', 'charmed')",
            "resource": "Resources and currencies (e.g., 'gold', 'spell slots', 'hit dice')"
        }
    
    @staticmethod
    def get_all_intents() -> List[str]:
        """Returns list of all character intention names."""
        return [intent.value for intent in UserIntention]
    
    @staticmethod
    def get_all_entity_types() -> List[str]:
        """Returns list of all character entity type names."""
        return [entity.value for entity in EntityType]