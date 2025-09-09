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


# ===== USER INTENTIONS - CONSOLIDATED =====

class UserIntention(Enum):
    """Consolidated user intentions that map to broad character data sections."""
    
    # Core Character Information - everything about the base character
    CHARACTER_BASICS = "character_basics"  # character_base, characteristics, ability_scores
    
    # Combat & Defense - all combat-related data
    COMBAT_INFO = "combat_info"  # combat_stats, damage_modifiers, passive_scores, action_economy
    
    # Skills & Abilities - all proficiencies and abilities
    ABILITIES_INFO = "abilities_info"  # proficiencies, passive_scores, senses, features_and_traits
    
    # Equipment & Inventory - all items and equipment
    INVENTORY_INFO = "inventory_info"  # complete inventory with all nested data
    
    # Magic & Spellcasting - all spell-related information
    MAGIC_INFO = "magic_info"  # spell_list with all nested spellcasting data
    
    # Character Story - all narrative and background information
    STORY_INFO = "story_info"  # background_info, personality, backstory
    
    # Social & Relationships - all social connections
    SOCIAL_INFO = "social_info"  # organizations, allies, enemies
    
    # Progress & Objectives - all goals and advancement
    PROGRESS_INFO = "progress_info"  # objectives_and_contracts, notes, progression
    
    # Complete Character - everything
    FULL_CHARACTER = "full_character"  # All character data
    
    # Quick Summary - essential overview data only
    CHARACTER_SUMMARY = "character_summary"  # Key fields for quick overview


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
            # Core Character Information - basic character identity and stats
            UserIntention.CHARACTER_BASICS: IntentionMapping(
                intention=UserIntention.CHARACTER_BASICS,
                category=IntentionCategory.CHARACTER_SHEET,
                required_fields={'character_base', 'characteristics', 'ability_scores'},
                entity_types={EntityType.RACE, EntityType.CLASS, EntityType.BACKGROUND},
                calculation_required=True
            ),
            
            # Combat & Defense - everything needed for combat
            UserIntention.COMBAT_INFO: IntentionMapping(
                intention=UserIntention.COMBAT_INFO,
                category=IntentionCategory.COMBAT,
                required_fields={'combat_stats', 'damage_modifiers', 'passive_scores', 'action_economy'},
                optional_fields={'ability_scores', 'inventory', 'features_and_traits', 'proficiencies'},
                entity_types={EntityType.WEAPON, EntityType.ACTION, EntityType.ARMOR},
                calculation_required=True,
                aggregation_required=True
            ),
            
            # Skills & Abilities - all character capabilities and traits
            UserIntention.ABILITIES_INFO: IntentionMapping(
                intention=UserIntention.ABILITIES_INFO,
                category=IntentionCategory.ABILITIES,
                required_fields={'proficiencies', 'passive_scores', 'senses', 'features_and_traits'},
                optional_fields={'ability_scores', 'character_base', 'background_info'},
                entity_types={EntityType.SKILL, EntityType.FEATURE, EntityType.TRAIT, EntityType.ABILITY},
                aggregation_required=True
            ),
            
            # Equipment & Inventory - all items, weapons, armor, etc.
            UserIntention.INVENTORY_INFO: IntentionMapping(
                intention=UserIntention.INVENTORY_INFO,
                category=IntentionCategory.INVENTORY,
                required_fields={'inventory'},
                optional_fields={'ability_scores', 'proficiencies'},  # For carrying capacity and proficiency
                nested_requirements={
                    'inventory': ['equipped_items', 'backpack', 'carrying_capacity', 'currency']
                },
                entity_types={EntityType.ITEM, EntityType.WEAPON, EntityType.ARMOR},
                calculation_required=True,
                aggregation_required=True
            ),
            
            # Magic & Spellcasting - all spell-related data
            UserIntention.MAGIC_INFO: IntentionMapping(
                intention=UserIntention.MAGIC_INFO,
                category=IntentionCategory.MAGIC,
                required_fields={'spell_list'},
                optional_fields={'ability_scores', 'character_base', 'features_and_traits'},
                nested_requirements={
                    'spell_list': ['spells', 'spellcasting', 'spell_slots', 'cantrips']
                },
                entity_types={EntityType.SPELL},
                calculation_required=True,
                aggregation_required=True
            ),
            
            # Character Story - all narrative and background
            UserIntention.STORY_INFO: IntentionMapping(
                intention=UserIntention.STORY_INFO,
                category=IntentionCategory.BACKSTORY,
                required_fields={'background_info', 'personality', 'backstory'},
                entity_types={EntityType.BACKGROUND},
                aggregation_required=True
            ),
            
            # Social & Relationships - all connections and organizations
            UserIntention.SOCIAL_INFO: IntentionMapping(
                intention=UserIntention.SOCIAL_INFO,
                category=IntentionCategory.SOCIAL,
                required_fields={'organizations', 'allies', 'enemies'},
                optional_fields={'personality', 'background_info'},
                entity_types={EntityType.ALLY, EntityType.ENEMY, EntityType.ORGANIZATION},
                aggregation_required=True
            ),
            
            # Progress & Objectives - all goals, quests, and advancement
            UserIntention.PROGRESS_INFO: IntentionMapping(
                intention=UserIntention.PROGRESS_INFO,
                category=IntentionCategory.PROGRESSION,
                required_fields={'objectives_and_contracts'},
                optional_fields={'character_base', 'notes'},
                nested_requirements={
                    'objectives_and_contracts': ['current_objectives', 'active_contracts', 'completed_objectives']
                },
                entity_types={EntityType.QUEST, EntityType.CONTRACT},
                calculation_required=True,
                aggregation_required=True
            ),
            
            # Complete Character - absolutely everything
            UserIntention.FULL_CHARACTER: IntentionMapping(
                intention=UserIntention.FULL_CHARACTER,
                category=IntentionCategory.CHARACTER_SHEET,
                required_fields={
                    'character_base', 'characteristics', 'ability_scores', 'combat_stats',
                    'background_info', 'personality', 'backstory', 'organizations', 'allies',
                    'enemies', 'proficiencies', 'damage_modifiers', 'passive_scores', 'senses',
                    'action_economy', 'features_and_traits', 'inventory', 'spell_list',
                    'objectives_and_contracts', 'notes'
                },
                entity_types=set(EntityType),  # All entity types
                calculation_required=True,
                aggregation_required=True
            ),
            
            # Character Summary - essential overview only
            UserIntention.CHARACTER_SUMMARY: IntentionMapping(
                intention=UserIntention.CHARACTER_SUMMARY,
                category=IntentionCategory.CHARACTER_SHEET,
                required_fields={'character_base', 'ability_scores', 'combat_stats'},
                optional_fields={'background_info', 'personality'},
                calculation_required=True,
                aggregation_required=True
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
    
    @staticmethod
    def combine_mappings(mappings: List[IntentionMapping]) -> IntentionMapping:
        """Combine multiple IntentionMapping objects into a single mapping."""
        if not mappings:
            raise ValueError("Cannot combine empty list of mappings")
        
        if len(mappings) == 1:
            return mappings[0]
        
        # Merge all fields and properties
        combined_required_fields = set()
        combined_optional_fields = set()
        combined_nested_requirements = {}
        combined_entity_types = set()
        combined_calculation_required = False
        combined_aggregation_required = False
        
        # Use the first mapping's intention and category as base
        base_mapping = mappings[0]
        
        for mapping in mappings:
            combined_required_fields.update(mapping.required_fields)
            combined_optional_fields.update(mapping.optional_fields)
            combined_entity_types.update(mapping.entity_types)
            
            # Merge nested requirements
            for field, nested_list in mapping.nested_requirements.items():
                if field not in combined_nested_requirements:
                    combined_nested_requirements[field] = []
                combined_nested_requirements[field].extend(nested_list)
            
            # Set flags if any mapping requires them
            if mapping.calculation_required:
                combined_calculation_required = True
            if mapping.aggregation_required:
                combined_aggregation_required = True
        
        # Create combined mapping
        return IntentionMapping(
            intention=base_mapping.intention,  # Use first intention as primary
            category=base_mapping.category,    # Use first category as primary
            required_fields=combined_required_fields,
            optional_fields=combined_optional_fields,
            nested_requirements=combined_nested_requirements,
            entity_types=combined_entity_types,
            calculation_required=combined_calculation_required,
            aggregation_required=combined_aggregation_required
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
            "character_basics": "Core character identity and stats: name, race, class, level, alignment, physical characteristics, ability scores (STR, DEX, CON, INT, WIS, CHA), and basic derived stats",
            
            "combat_info": "All combat capabilities and defensive stats: hit points, armor class, initiative bonus, speed, saving throw bonuses, damage resistances/immunities, attack bonuses, weapon proficiencies, combat actions, and action economy options",
            
            "abilities_info": "Character capabilities and expertise: skill proficiencies, tool proficiencies, languages, special senses (darkvision, etc.), class features, racial traits, feats, and passive abilities that define what the character can do",
            
            "inventory_info": "Complete equipment and possessions: all equipped items (weapons, armor, accessories), backpack contents, carrying capacity calculations, encumbrance, currency (gold, silver, copper), and item descriptions/properties",
            
            "magic_info": "All spellcasting capabilities: known spells by class and level, spell slots available/used, spellcasting ability modifiers, spell attack bonuses, spell save DCs, cantrips, ritual spells, and magical item usage",
            
            "story_info": "Character narrative and personality: background details, personality traits, ideals, bonds, flaws, detailed backstory, personal history, motivations, and roleplay elements that define who the character is",
            
            "social_info": "Relationships and affiliations: allied NPCs, enemy relationships, organizational memberships, faction standings, contacts, social connections, reputation, and interpersonal dynamics",
            
            "progress_info": "Goals, objectives, and advancement: current active quests, completed objectives, ongoing contracts, character progression notes, future goals, quest rewards, experience tracking, and milestone achievements",
            
            "full_character": "Complete comprehensive character data: absolutely everything including all stats, equipment, spells, story elements, relationships, objectives, notes, and every piece of character information available",
            
            "character_summary": "Essential character overview: key identifying information, primary stats, main equipment, important abilities, and critical story elements for quick reference and character introduction"
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