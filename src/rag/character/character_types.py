"""
Character Types Module

This module defines Python type definitions for creating and managing RPG characters.
These types are designed to be generalizable across different character concepts
while maintaining flexibility for various game systems and settings.

The types are organized by functional areas:
- Core character information
- Background and personality
- Combat and actions
- Abilities and features
- Inventory and equipment
- Spells and spellcasting
- Objectives and contracts
"""

from typing import Dict, List, Optional, Union, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime


# ===== CORE CHARACTER TYPES =====

@dataclass
class AbilityScores:
    """Represents the six core ability scores."""
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


@dataclass
class CombatStats:
    """Core combat statistics."""
    max_hp: int
    armor_class: int
    initiative_bonus: int
    speed: int
    hit_dice: Optional[Dict[str, str]] = None


@dataclass
class CharacterBase:
    """Basic character information."""
    name: str
    race: str
    character_class: str  # Primary class
    total_level: int
    alignment: str
    background: str
    subrace: Optional[str] = None
    multiclass_levels: Optional[Dict[str, int]] = None
    lifestyle: Optional[str] = None


@dataclass
class PhysicalCharacteristics:
    """Physical appearance and traits."""
    alignment: str
    gender: str
    eyes: str
    size: str
    height: str
    hair: str
    skin: str
    age: int
    weight: str  # Include unit (e.g., "180 lb")
    faith: Optional[str] = None


@dataclass
class Proficiency:
    """Represents a skill, tool, language, or armor proficiency."""
    type: Literal["armor", "weapon", "tool", "language", "skill", "saving_throw"]
    name: str


@dataclass
class DamageModifier:
    """Damage resistance, immunity, or vulnerability."""
    damage_type: str
    modifier_type: Literal["resistance", "immunity", "vulnerability"]


@dataclass
class PassiveScores:
    """Passive perception and other passive abilities."""
    perception: int
    investigation: Optional[int] = None
    insight: Optional[int] = None
    stealth: Optional[int] = None


@dataclass
class Senses:
    """
    Special senses in D&D 5e.

    A flexible dictionary to store any type of sense with its range or description.
    Common examples:
    - "darkvision": 60 (feet)
    - "blindsight": 30
    - "tremorsense": 20
    - "truesight": 120
    - "devils_sight": 120
    - "ethereal_sight": 60
    - "see_invisibility": 10
    - "superior_darkvision": 120

    Values can be integers (ranges in feet) or strings (descriptive values).
    """
    senses: Dict[str, Union[int, str]] = field(default_factory=dict)


# ===== BACKGROUND AND PERSONALITY TYPES =====

@dataclass
class BackgroundFeature:
    """A background feature with name and description."""
    name: str
    description: str


@dataclass
class BackgroundInfo:
    """Character background information."""
    name: str
    feature: BackgroundFeature
    skill_proficiencies: List[str] = field(default_factory=list)
    tool_proficiencies: List[str] = field(default_factory=list)
    language_proficiencies: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    feature_description: Optional[str] = None


@dataclass
class PersonalityTraits:
    """Personality traits, ideals, bonds, and flaws."""
    personality_traits: List[str] = field(default_factory=list)
    ideals: List[str] = field(default_factory=list)
    bonds: List[str] = field(default_factory=list)
    flaws: List[str] = field(default_factory=list)


@dataclass
class BackstorySection:
    """A section of the character's backstory."""
    heading: str
    content: str


@dataclass
class FamilyBackstory:
    """Family background information."""
    parents: str
    sections: List[BackstorySection] = field(default_factory=list)


@dataclass
class Backstory:
    """Complete character backstory."""
    title: str
    family_backstory: FamilyBackstory
    sections: List[BackstorySection] = field(default_factory=list)


@dataclass
class Organization:
    """An organization the character belongs to."""
    name: str
    role: str
    description: str


@dataclass
class Ally:
    """An ally or contact."""
    name: str
    description: str
    title: Optional[str] = None


@dataclass
class Enemy:
    """An enemy or rival."""
    name: str
    description: str


# ===== COMBAT AND ACTION TYPES =====

@dataclass
class DamageInfo:
    """Damage information for attacks."""
    one_handed: Optional[str] = None
    two_handed: Optional[str] = None
    base: Optional[str] = None
    type: str = "slashing"


@dataclass
class AttackAction:
    """An attack action or weapon attack."""
    name: str
    type: Literal["weapon_attack", "melee_attack", "ranged_attack", "spell_attack"]
    damage: Optional[DamageInfo] = None
    properties: List[str] = field(default_factory=list)
    range: Optional[str] = None
    reach: bool = False
    attack_bonus: int = 0
    damage_type: Optional[str] = None
    charges: Optional[Dict[str, Union[int, str]]] = None
    weapon_properties: List[str] = field(default_factory=list)
    special_options: Optional[List[Dict[str, str]]] = None
    required_items: Optional[List['InventoryItem']] = None


@dataclass
class SpecialAction:
    """A special action like Channel Divinity."""
    name: str
    type: Literal["action", "bonus_action", "reaction", "no_action", "feature"]
    description: Optional[str] = None
    uses: Optional[Dict[str, Union[int, str]]] = None
    save_dc: Optional[int] = None
    range: Optional[str] = None
    effect: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    trigger: Optional[str] = None
    sub_actions: Optional[List[AttackAction]] = None
    required_items: Optional[List['InventoryItem']] = None


@dataclass
class ActionEconomy:
    """Character's action economy information."""
    attacks_per_action: int = 1
    actions: List[SpecialAction] = field(default_factory=list)


# ===== FEATURES AND TRAITS TYPES =====

@dataclass
class Feature:
    """A class feature, racial trait, or feat."""
    name: str
    description: Optional[str] = None
    action_type: Optional[Literal["action", "bonus_action", "reaction", "no_action"]] = None
    passive: bool = False
    uses: Optional[Dict[str, Union[int, str]]] = None
    effect: Optional[str] = None
    cost: Optional[str] = None
    damage: Optional[Dict[str, Any]] = None
    trigger: Optional[str] = None
    subclass: bool = False
    channel_divinity: Optional[Dict[str, Any]] = None
    duration: Optional[str] = None
    range: Optional[str] = None
    save_dc: Optional[int] = None
    focus: Optional[str] = None
    preparation: Optional[str] = None


@dataclass
class ClassFeatures:
    """Features for a specific class."""
    level: int
    features: List[Feature] = field(default_factory=list)


@dataclass
class FeaturesAndTraits:
    """All character features and traits organized by class."""
    class_features: Dict[str, ClassFeatures] = field(default_factory=dict)
    racial_traits: List[Feature] = field(default_factory=list)
    feats: List[Feature] = field(default_factory=list)


# ===== INVENTORY TYPES =====

@dataclass
class ItemProperty:
    """A magical property of an item."""
    name: str
    description: Optional[str] = None
    effect: Optional[str] = None


@dataclass
class SpellCharges:
    """Spell charges for magical items."""
    save_dc: int
    recharge: str
    spells: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SpecialFeatures:
    """Special features of magical items."""
    critical_range: Optional[str] = None
    extra_damage: Optional[str] = None
    curse: Optional[Dict[str, Any]] = None
    random_properties: Optional[List[str]] = None
    spell_charges: Optional[SpellCharges] = None
    lore: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class InventoryItem:
    """An item in the character's inventory."""
    name: str
    type: str
    rarity: str = "Common"
    requires_attunement: bool = False
    attunement_process: Optional[str] = None
    proficient: bool = True
    attack_type: Optional[Literal["Melee", "Ranged"]] = None
    reach: Optional[str] = None
    damage: Optional[DamageInfo] = None
    damage_type: Optional[str] = None
    weight: Optional[Union[int, float]] = None
    cost: Optional[str] = None
    properties: List[str] = field(default_factory=list)
    version: Optional[int] = None
    magical_bonus: Optional[str] = None
    special_features: Optional[SpecialFeatures] = None
    equipped: bool = False
    armor_class: Optional[int] = None
    quantity: int = 1


@dataclass
class Inventory:
    """Character's complete inventory."""
    total_weight: float
    weight_unit: str = "lb"
    equipped_items: Dict[str, List[InventoryItem]] = field(default_factory=dict)
    backpack: List[InventoryItem] = field(default_factory=list)
    valuables: List[Dict[str, Any]] = field(default_factory=list)


# ===== SPELL TYPES =====

@dataclass
class SpellComponents:
    """Components required for spellcasting."""
    verbal: bool = False
    somatic: bool = False
    material: Union[bool, str] = False


@dataclass
class SpellRite:
    """A rite option for certain spells."""
    name: str
    effect: str


@dataclass
class Spell:
    """A spell definition."""
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: SpellComponents
    duration: str
    description: str
    concentration: bool = False
    ritual: bool = False
    tags: List[str] = field(default_factory=list)
    area: Optional[str] = None
    rites: Optional[List[SpellRite]] = None
    charges: Optional[int] = None


@dataclass
class SpellcastingInfo:
    """Spellcasting ability information."""
    ability: str
    spell_save_dc: int
    spell_attack_bonus: int
    cantrips_known: List[str] = field(default_factory=list)
    spells_known: List[str] = field(default_factory=list)
    spell_slots: Dict[int, int] = field(default_factory=dict)


@dataclass
class SpellList:
    """Complete spell list organized by class."""
    spellcasting: Dict[str, SpellcastingInfo] = field(default_factory=dict)
    spells: Dict[str, Dict[str, List[Spell]]] = field(default_factory=dict)


# ===== OBJECTIVES AND CONTRACTS TYPES =====

@dataclass
class BaseObjective:
    """Base for all objectives"""
    id: str
    name: str
    type: str
    status: Literal["Active", "In Progress", "Completed", "Failed", "Suspended", "Abandoned"]
    description: str
    priority: Optional[Literal["Absolute", "Critical", "High", "Medium", "Low"]] = None
    objectives: List[str] = field(default_factory=list)
    rewards: List[str] = field(default_factory=list)
    deadline: Optional[str] = None
    notes: Optional[str] = None
    completion_date: Optional[str] = None
    parties: Optional[str] = None
    outcome: Optional[str] = None
    obligations_accepted: List[str] = field(default_factory=list)
    lasting_effects: List[str] = field(default_factory=list)


@dataclass
class Quest(BaseObjective):
    """Quest-specific fields"""
    quest_giver: Optional[str] = None
    location: Optional[str] = None
    deity: Optional[str] = None
    purpose: Optional[str] = None
    signs_received: List[str] = field(default_factory=list)
    divine_favor: Optional[str] = None
    consequences_of_failure: List[str] = field(default_factory=list)
    motivation: Optional[str] = None
    steps: List[str] = field(default_factory=list)
    obstacles: List[str] = field(default_factory=list)
    importance: Optional[str] = None


@dataclass
class Contract(BaseObjective):
    """Contract-specific fields"""
    client: Optional[str] = None
    contractor: Optional[str] = None
    terms: Optional[str] = None
    payment: Optional[str] = None
    penalties: Optional[str] = None
    special_conditions: List[str] = field(default_factory=list)
    parties: Optional[str] = None
    outcome: Optional[str] = None
    obligations_accepted: List[str] = field(default_factory=list)
    lasting_effects: List[str] = field(default_factory=list)


@dataclass
class ContractTemplate:
    """Template for creating new contracts."""
    id: str = ""
    name: str = ""
    type: str = ""
    status: str = ""
    priority: str = ""
    quest_giver: str = ""
    location: str = ""
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    rewards: List[str] = field(default_factory=list)
    deadline: str = ""
    notes: str = ""


@dataclass
class ObjectivesAndContracts:
    """All character objectives and contracts."""
    active_contracts: List[Contract] = field(default_factory=list)
    current_objectives: List[Quest] = field(default_factory=list)
    completed_objectives: List[Union[Quest, Contract]] = field(default_factory=list)
    contract_templates: Dict[str, ContractTemplate] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ===== MAIN CHARACTER CLASS =====

@dataclass
class Character:
    """Complete character definition combining all aspects."""
    # Core information (required fields first)
    character_base: CharacterBase
    characteristics: PhysicalCharacteristics
    ability_scores: AbilityScores
    combat_stats: CombatStats
    background_info: BackgroundInfo
    personality: PersonalityTraits
    backstory: Backstory

    # Optional fields
    organizations: List[Organization] = field(default_factory=list)
    allies: List[Ally] = field(default_factory=list)
    enemies: List[Enemy] = field(default_factory=list)
    proficiencies: List[Proficiency] = field(default_factory=list)
    damage_modifiers: List[DamageModifier] = field(default_factory=list)
    passive_scores: Optional[PassiveScores] = None
    senses: Optional[Senses] = None
    action_economy: Optional[ActionEconomy] = None
    features_and_traits: Optional[FeaturesAndTraits] = None
    inventory: Optional[Inventory] = None
    spell_list: Optional[SpellList] = None
    objectives_and_contracts: Optional[ObjectivesAndContracts] = None
    notes: Dict[str, Any] = field(default_factory=dict)
    created_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None


# ===== UTILITY FUNCTIONS =====

def create_empty_character(name: str, race: str, character_class: str) -> Character:
    """Create a minimal character with default empty values."""
    return Character(
        character_base=CharacterBase(
            name=name,
            race=race,
            character_class=character_class,
            total_level=1,
            alignment="Neutral",
            background="Unknown"
        ),
        characteristics=PhysicalCharacteristics(
            alignment="Neutral",
            gender="Unknown",
            eyes="Unknown",
            size="Medium",
            height="5'0\"",
            hair="Unknown",
            skin="Unknown",
            age=18,
            weight="150 lb"
        ),
        ability_scores=AbilityScores(
            strength=10, dexterity=10, constitution=10,
            intelligence=10, wisdom=10, charisma=10
        ),
        combat_stats=CombatStats(
            max_hp=10, armor_class=10, initiative_bonus=0, speed=30
        ),
        background_info=BackgroundInfo(
            name="Unknown",
            feature=BackgroundFeature(name="Unknown", description="")
        ),
        personality=PersonalityTraits(),
        backstory=Backstory(
            title="Unknown",
            family_backstory=FamilyBackstory(parents="Unknown")
        ),
        passive_scores=PassiveScores(perception=10),
        senses=Senses(
            senses={"darkvision": 60}  # Common for many races
        ),
        action_economy=ActionEconomy(),
        features_and_traits=FeaturesAndTraits(),
        inventory=Inventory(total_weight=0.0),
        spell_list=SpellList(),
        objectives_and_contracts=ObjectivesAndContracts()
    )


# ===== TYPE ALIASES =====

CharacterDict = Dict[str, Any]
SpellLevel = Literal["cantrip", "1st_level", "2nd_level", "3rd_level", "4th_level",
                     "5th_level", "6th_level", "7th_level", "8th_level", "9th_level"]
ActionType = Literal["action", "bonus_action", "reaction", "no_action", "feature"]
ProficiencyType = Literal["armor", "weapon", "tool", "language", "skill", "saving_throw"]
DamageModifierType = Literal["resistance", "immunity", "vulnerability"]
ObjectiveStatus = Literal["Active", "In Progress", "Completed", "Failed", "Suspended", "Abandoned"]
ObjectivePriority = Literal["Absolute", "Critical", "High", "Medium", "Low"]
