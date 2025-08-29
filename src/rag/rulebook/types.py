"""
D&D 5e Rulebook Storage System - Rulebook-Specific Types
"""

from typing import List, Dict, Optional, Set, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from difflib import SequenceMatcher

if TYPE_CHECKING:
    from .storage import RulebookStorage


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


class DnDEntityType(Enum):
    """Types of D&D entities that can be extracted"""
    CLASS = "class"
    SUBCLASS = "subclass"  # Add this
    RACE = "race"
    SUBRACE = "subrace"
    SPELL = "spell"
    FEAT = "feat"
    ITEM = "item"
    MAGIC_ITEM = "magic_item"
    MONSTER = "monster"
    CONDITION = "condition"
    SKILL = "skill"
    RULE = "rule"
    EQUIPMENT = "equipment"
    PLANE = "plane"
    ACTIVITY = "activity"
    MECHANIC = "mechanic"
    LOCATION = "location"
    DEITY = "deity"
    BACKGROUND = "background"
    FEATURE = "feature"  # Add this for class features
    TABLE = "table"  # Add this for progression tables


@dataclass
class RulebookSection:
    """Represents a hierarchical section of the D&D 5e rulebook"""
    id: str
    title: str
    level: int  # 1 for chapter, 2 for section, etc.
    content: str
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    entity_names: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_content(self, include_children: bool = False, storage: Optional['RulebookStorage'] = None) -> str:
        """Get content including optional children sections"""
        if not include_children:
            return self.content
        
        # Recursively include children content
        if not storage:
            # If no storage provided, can't access children
            return self.content
        
        content_parts = [self.content]
        
        # Add all children sections recursively
        for child_id in self.children_ids:
            if child_id in storage.sections:
                child_section = storage.sections[child_id]
                child_content = child_section.get_full_content(include_children=True, storage=storage)
                content_parts.append(child_content)
        
        return '\n\n'.join(content_parts)


@dataclass
class DnDEntity:
    """Represents a D&D 5e game entity"""
    name: str
    entity_type: DnDEntityType
    aliases: List[str] = field(default_factory=list)
    section_ids: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    related_entities: List[str] = field(default_factory=list)
    
    def matches(self, term: str) -> float:
        """Calculate match score for a search term"""
        term_lower = term.lower()
        name_lower = self.name.lower()
        
        # Exact match
        if term_lower == name_lower:
            return 1.0
        
        # Alias match
        for alias in self.aliases:
            if term_lower == alias.lower():
                return 0.95
        
        # Partial match
        if term_lower in name_lower or name_lower in term_lower:
            return 0.7
        
        # Fuzzy match
        return SequenceMatcher(None, term_lower, name_lower).ratio()


@dataclass
class RulebookQueryResult:
    """Standardized D&D 5e rulebook query result"""
    content: str
    sections: List[RulebookSection] = field(default_factory=list)
    entities: List[DnDEntity] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    fallback_suggestions: List[str] = field(default_factory=list)
