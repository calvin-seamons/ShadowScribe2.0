"""
Character Management System

Core types and utilities for D&D character management.
"""

from .character_types import (
    # Core character types
    Character, CharacterBase, AbilityScores, CombatStats, PhysicalCharacteristics,
    
    # Background and personality
    BackgroundInfo, BackgroundFeature, PersonalityTraits, Backstory, BackstorySection,
    FamilyBackstory,
    
    # Inventory and items
    Inventory, InventoryItem, InventoryItemDefinition, ItemModifier,
    
    # Spells
    SpellList, Spell, SpellComponents, SpellcastingInfo, SpellRite,
    
    # Actions
    ActionEconomy, CharacterAction, ActionActivation, ActionUsage, ActionRange,
    ActionDamage, ActionSave,
    
    # Features and traits
    FeaturesAndTraits, ClassFeature, RacialTrait, Feat, FeatureAction, 
    FeatureActivation, FeatureModifier, FeatureRange, LimitedUse,
    
    # Relationships
    Organization, Ally, Enemy,
    
    # Objectives and contracts
    ObjectivesAndContracts, BaseObjective, Quest, Contract, ContractTemplate,
    
    # Modifiers and proficiencies
    Proficiency, DamageModifier, PassiveScores, Senses
)
from .character_manager import CharacterManager
from .character_query_router import CharacterQueryRouter
from .character_query_types import (
    UserIntention, IntentionCategory, QueryEntity, SearchContext,
    CharacterInformationResult, CharacterPromptHelper
)

__all__ = [
    # Core character types
    'Character', 'CharacterBase', 'AbilityScores', 'CombatStats', 'PhysicalCharacteristics',
    
    # Background and personality
    'BackgroundInfo', 'BackgroundFeature', 'PersonalityTraits', 'Backstory', 'BackstorySection',
    'FamilyBackstory',
    
    # Inventory and items
    'Inventory', 'InventoryItem', 'InventoryItemDefinition', 'ItemModifier',
    
    # Spells
    'SpellList', 'Spell', 'SpellComponents', 'SpellcastingInfo', 'SpellRite',
    
    # Actions
    'ActionEconomy', 'CharacterAction', 'ActionActivation', 'ActionUsage', 'ActionRange',
    'ActionDamage', 'ActionSave',
    
    # Features and traits
    'FeaturesAndTraits', 'ClassFeature', 'RacialTrait', 'Feat', 'FeatureAction',
    'FeatureActivation', 'FeatureModifier', 'FeatureRange', 'LimitedUse',
    
    # Relationships
    'Organization', 'Ally', 'Enemy',
    
    # Objectives and contracts
    'ObjectivesAndContracts', 'BaseObjective', 'Quest', 'Contract', 'ContractTemplate',
    
    # Modifiers and proficiencies
    'Proficiency', 'DamageModifier', 'PassiveScores', 'Senses',
    
    # Character management
    'CharacterManager',
    
    # Query system
    'CharacterQueryRouter', 'UserIntention', 'IntentionCategory', 'QueryEntity', 
    'SearchContext', 'CharacterInformationResult', 'CharacterPromptHelper'
]
