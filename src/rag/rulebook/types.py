"""
D&D 5e Rulebook Storage System - Core Data Models
"""

from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import hashlib


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


@dataclass
class RulebookSection:
    """Represents a hierarchical section of the D&D 5e rulebook"""
    id: str
    title: str
    level: int  # 1 for chapter (#), 2 for section (##), etc.
    content: str  # Content until next header (any level)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    categories: List[RulebookCategory] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    vector: Optional[List[float]] = None  # Embedding vector
    
    def get_full_content(self, include_children: bool = False, storage: Optional['RulebookStorage'] = None) -> str:
        """Get content including optional children sections"""
        if not include_children:
            return self.content
        
        # Recursively include children content
        if not storage:
            return self.content
        
        content_parts = [self.content]
        
        # Add all children sections recursively
        for child_id in self.children_ids:
            if child_id in storage.sections:
                child_section = storage.sections[child_id]
                child_content = child_section.get_full_content(include_children=True, storage=storage)
                content_parts.append(child_content)
        
        return '\n\n'.join(content_parts)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'level': self.level,
            'content': self.content,
            'parent_id': self.parent_id,
            'children_ids': self.children_ids,
            'categories': [cat.value for cat in self.categories],
            'metadata': self.metadata,
            'vector': self.vector
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RulebookSection':
        """Create from dictionary for deserialization"""
        return cls(
            id=data['id'],
            title=data['title'],
            level=data['level'],
            content=data['content'],
            parent_id=data.get('parent_id'),
            children_ids=data.get('children_ids', []),
            categories=[RulebookCategory(cat) for cat in data.get('categories', [])],
            metadata=data.get('metadata', {}),
            vector=data.get('vector')
        )
    
    def generate_id(self) -> str:
        """Generate a unique ID based on title and parent"""
        text = f"{self.parent_id or 'root'}_{self.title}"
        return hashlib.md5(text.encode()).hexdigest()[:12]


@dataclass
class SearchResult:
    """Represents a search result with relevance scoring"""
    section: RulebookSection
    score: float
    matched_entities: List[str] = field(default_factory=list)
    matched_context: List[str] = field(default_factory=list)
    includes_children: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            'id': self.section.id,
            'title': self.section.title,
            'level': self.section.level,
            'content': self.section.content,
            'score': self.score,
            'matched_entities': self.matched_entities,
            'matched_context': self.matched_context,
            'includes_children': self.includes_children,
            'categories': [cat.name for cat in self.section.categories]
        }


@dataclass 
class QueryRequest:
    """Request structure for querying the rulebook"""
    intention: RulebookQueryIntent
    entities: List[str]  # Already normalized
    context_hints: Optional[List[str]] = None
    max_tokens: int = 8000
    include_children_for_top: bool = True
    
    def validate(self) -> bool:
        """Validate the query request"""
        if not self.intention:
            return False
        if not isinstance(self.entities, list):
            return False
        if self.max_tokens < 100 or self.max_tokens > 50000:
            return False
        return True


@dataclass
class QueryResponse:
    """Response structure from rulebook queries"""
    request: QueryRequest
    results: List[SearchResult]
    total_tokens: int
    categories_searched: List[RulebookCategory]
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            'intention': self.request.intention.value,
            'entities': self.request.entities,
            'context_hints': self.request.context_hints,
            'results': [r.to_dict() for r in self.results],
            'total_tokens': self.total_tokens,
            'categories_searched': [cat.name for cat in self.categories_searched],
            'processing_time_ms': self.processing_time_ms
        }


# Intention to Category Mapping
INTENTION_CATEGORY_MAP: Dict[RulebookQueryIntent, List[RulebookCategory]] = {
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