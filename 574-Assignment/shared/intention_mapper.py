"""
Intention to Category Mapper
Maps query intentions to relevant D&D content categories
Extracted from src/rag/rulebook/rulebook_types.py
"""
from typing import List
from enum import Enum


class RulebookQueryIntent(Enum):
    """All supported D&D 5e rulebook query intentions"""
    DESCRIBE_ENTITY = "describe_entity"
    COMPARE_ENTITIES = "compare_entities"
    LEVEL_PROGRESSION = "level_progression"
    ACTION_OPTIONS = "action_options"
    RULE_MECHANICS = "rule_mechanics"
    CALCULATE_VALUES = "calculate_values"
    SPELL_DETAILS = "spell_details"
    CLASS_SPELL_ACCESS = "class_spell_access"
    MONSTER_STATS = "monster_stats"
    CONDITION_EFFECTS = "condition_effects"
    CHARACTER_CREATION = "character_creation"
    MULTICLASS_RULES = "multiclass_rules"
    EQUIPMENT_PROPERTIES = "equipment_properties"
    DAMAGE_TYPES = "damage_types"
    REST_MECHANICS = "rest_mechanics"
    SKILL_USAGE = "skill_usage"
    FIND_BY_CRITERIA = "find_by_criteria"
    PREREQUISITE_CHECK = "prerequisite_check"
    INTERACTION_RULES = "interaction_rules"
    TACTICAL_USAGE = "tactical_usage"
    ENVIRONMENTAL_RULES = "environmental_rules"
    CREATURE_ABILITIES = "creature_abilities"
    SAVING_THROWS = "saving_throws"
    MAGIC_ITEM_USAGE = "magic_item_usage"
    PLANAR_PROPERTIES = "planar_properties"
    DOWNTIME_ACTIVITIES = "downtime_activities"
    SUBCLASS_FEATURES = "subclass_features"
    COST_LOOKUP = "cost_lookup"
    LEGENDARY_MECHANICS = "legendary_mechanics"
    OPTIMIZATION_ADVICE = "optimization_advice"


class RulebookCategory(Enum):
    """The 10 main content categories"""
    CHARACTER_CREATION = 1
    CLASS_FEATURES = 2
    SPELLCASTING = 3
    COMBAT = 4
    CONDITIONS = 5
    EQUIPMENT = 6
    CORE_MECHANICS = 7
    EXPLORATION = 8
    CREATURES = 9
    WORLD_LORE = 10


class IntentionMapper:
    """Maps user intentions to D&D content categories for filtering"""
    
    # Mapping from RulebookQueryIntent to list of RulebookCategory
    INTENTION_CATEGORY_MAP = {
        RulebookQueryIntent.DESCRIBE_ENTITY: [
            RulebookCategory.CHARACTER_CREATION,
            RulebookCategory.CLASS_FEATURES,
            RulebookCategory.SPELLCASTING,
            RulebookCategory.EQUIPMENT,
            RulebookCategory.CREATURES
        ],
        RulebookQueryIntent.COMPARE_ENTITIES: [
            RulebookCategory.CHARACTER_CREATION,
            RulebookCategory.CLASS_FEATURES,
            RulebookCategory.SPELLCASTING,
            RulebookCategory.EQUIPMENT,
            RulebookCategory.CREATURES
        ],
        RulebookQueryIntent.LEVEL_PROGRESSION: [
            RulebookCategory.CLASS_FEATURES
        ],
        RulebookQueryIntent.ACTION_OPTIONS: [
            RulebookCategory.COMBAT,
            RulebookCategory.CORE_MECHANICS
        ],
        RulebookQueryIntent.RULE_MECHANICS: [
            RulebookCategory.CORE_MECHANICS
        ],
        RulebookQueryIntent.CALCULATE_VALUES: [
            RulebookCategory.CHARACTER_CREATION,
            RulebookCategory.CLASS_FEATURES,
            RulebookCategory.CORE_MECHANICS
        ],
        RulebookQueryIntent.SPELL_DETAILS: [
            RulebookCategory.SPELLCASTING
        ],
        RulebookQueryIntent.CLASS_SPELL_ACCESS: [
            RulebookCategory.CLASS_FEATURES,
            RulebookCategory.SPELLCASTING
        ],
        RulebookQueryIntent.MONSTER_STATS: [
            RulebookCategory.CREATURES
        ],
        RulebookQueryIntent.CONDITION_EFFECTS: [
            RulebookCategory.CONDITIONS
        ],
        RulebookQueryIntent.CHARACTER_CREATION: [
            RulebookCategory.CHARACTER_CREATION
        ],
        RulebookQueryIntent.MULTICLASS_RULES: [
            RulebookCategory.CHARACTER_CREATION,
            RulebookCategory.CLASS_FEATURES
        ],
        RulebookQueryIntent.EQUIPMENT_PROPERTIES: [
            RulebookCategory.EQUIPMENT
        ],
        RulebookQueryIntent.DAMAGE_TYPES: [
            RulebookCategory.COMBAT,
            RulebookCategory.CORE_MECHANICS
        ],
        RulebookQueryIntent.REST_MECHANICS: [
            RulebookCategory.CORE_MECHANICS,
            RulebookCategory.EXPLORATION
        ],
        RulebookQueryIntent.SKILL_USAGE: [
            RulebookCategory.CORE_MECHANICS
        ],
        RulebookQueryIntent.FIND_BY_CRITERIA: [
            RulebookCategory.CHARACTER_CREATION,
            RulebookCategory.CLASS_FEATURES,
            RulebookCategory.SPELLCASTING,
            RulebookCategory.EQUIPMENT,
            RulebookCategory.CREATURES
        ],
        RulebookQueryIntent.PREREQUISITE_CHECK: [
            RulebookCategory.CHARACTER_CREATION,
            RulebookCategory.CLASS_FEATURES,
            RulebookCategory.EQUIPMENT
        ],
        RulebookQueryIntent.INTERACTION_RULES: [
            RulebookCategory.CORE_MECHANICS,
            RulebookCategory.EXPLORATION
        ],
        RulebookQueryIntent.TACTICAL_USAGE: [
            RulebookCategory.COMBAT
        ],
        RulebookQueryIntent.ENVIRONMENTAL_RULES: [
            RulebookCategory.EXPLORATION
        ],
        RulebookQueryIntent.CREATURE_ABILITIES: [
            RulebookCategory.CREATURES
        ],
        RulebookQueryIntent.SAVING_THROWS: [
            RulebookCategory.COMBAT,
            RulebookCategory.CORE_MECHANICS
        ],
        RulebookQueryIntent.MAGIC_ITEM_USAGE: [
            RulebookCategory.EQUIPMENT
        ],
        RulebookQueryIntent.PLANAR_PROPERTIES: [
            RulebookCategory.WORLD_LORE
        ],
        RulebookQueryIntent.DOWNTIME_ACTIVITIES: [
            RulebookCategory.EXPLORATION
        ],
        RulebookQueryIntent.SUBCLASS_FEATURES: [
            RulebookCategory.CLASS_FEATURES
        ],
        RulebookQueryIntent.COST_LOOKUP: [
            RulebookCategory.EQUIPMENT,
            RulebookCategory.EXPLORATION
        ],
        RulebookQueryIntent.LEGENDARY_MECHANICS: [
            RulebookCategory.CREATURES
        ],
        RulebookQueryIntent.OPTIMIZATION_ADVICE: [
            RulebookCategory.CHARACTER_CREATION,
            RulebookCategory.CLASS_FEATURES
        ]
    }
    
    @staticmethod
    def get_categories(intention: str) -> List[str]:
        """
        Returns list of relevant category names for filtering
        
        Args:
            intention: Intention name (string value from RulebookQueryIntent)
            
        Returns:
            List of category names as strings
        """
        # Convert string to enum
        try:
            intent_enum = RulebookQueryIntent(intention)
        except ValueError:
            # If invalid intention, return all categories
            return [cat.name for cat in RulebookCategory]
        
        # Get categories for this intention
        categories = IntentionMapper.INTENTION_CATEGORY_MAP.get(intent_enum, [])
        
        # Return category names
        return [cat.name for cat in categories]
    
    @staticmethod
    def get_category_values(intention: str) -> List[int]:
        """
        Returns list of category enum values for filtering
        
        Args:
            intention: Intention name (string value from RulebookQueryIntent)
            
        Returns:
            List of category values as integers
        """
        try:
            intent_enum = RulebookQueryIntent(intention)
        except ValueError:
            return [cat.value for cat in RulebookCategory]
        
        categories = IntentionMapper.INTENTION_CATEGORY_MAP.get(intent_enum, [])
        return [cat.value for cat in categories]
