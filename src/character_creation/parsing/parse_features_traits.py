#!/usr/bin/env python3
"""
D&D Beyond Features Parser

This script parses a D&D Beyond character JSON export and extracts feature information
into the structured Feature, ClassFeatures, and FeaturesAndTraits objects as defined
in character_types.py.

Usage:
    python parse_dndbeyond_features.py <path_to_json_file>
"""

import json
import re
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path

from src.rag.character.character_types import (
    FeatureActivation,
    LimitedUse,
    FeatureRange,
    RacialTrait,
    ClassFeature,
    Feat,
    FeatureModifier,
    FeaturesAndTraits
)


class DNDBeyondFeaturesParser:
    """Parser for extracting D&D Beyond features into structured objects."""
    
    # Action type mapping from D&D Beyond integers to our literals
    ACTION_TYPE_MAP = {
        1: "action",
        2: "no_action",  # passive
        3: "bonus_action",
        4: "reaction",
        6: "reaction",  # opportunity attack
        8: "no_action",  # other
    }
    
    # Ability score ID to name mapping
    ABILITY_STAT_MAP = {
        1: "Strength",
        2: "Dexterity", 
        3: "Constitution",
        4: "Intelligence",
        5: "Wisdom",
        6: "Charisma"
    }
    
    # Reset type mapping
    RESET_TYPE_MAP = {
        1: "short_rest",
        2: "long_rest",
        3: "dawn",
        4: "dusk", 
        5: "recharge",
        6: "turn"
    }
    
    # Activation type mapping
    ACTIVATION_TYPE_MAP = {
        1: "action",
        2: "no_action",
        3: "bonus_action",
        4: "reaction",
        5: "minute",
        6: "hour",
        7: "special",
        8: "other"
    }
    
    # Feature type mapping
    FEATURE_TYPE_MAP = {
        1: "trait",
        2: "action", 
        3: "bonus_action",
        4: "reaction",
        5: "legendary_action",
        6: "mythic_action",
        7: "lair_action",
        8: "regional_effect",
        9: "other"
    }
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize parser with D&D Beyond JSON data."""
        self.data = json_data.get("data", {})
        
    def clean_html_description(self, description: str) -> str:
        """Clean HTML tags and format text for readable description."""
        if not description:
            return ""
            
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', description)
        
        # Replace HTML entities
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&rsquo;', "'")
        clean_text = clean_text.replace('&ldquo;', '"')
        clean_text = clean_text.replace('&rdquo;', '"')
        
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = clean_text.strip()
        
        return clean_text
    
    def parse_racial_traits(self) -> List[RacialTrait]:
        """Parse racial traits from race.racialTraits[]."""
        racial_traits = []
        
        race_data = self.data.get("race", {})
        racial_trait_list = race_data.get("racialTraits", [])
        
        for trait_data in racial_trait_list:
            definition = trait_data.get("definition", {})
            
            name = definition.get("name", "Unknown Trait")
            
            # Skip ability score improvements as they're not informative
            if "ability score increase" in name.lower():
                continue
                
            description = self.clean_html_description(definition.get("description"))
            creature_rules = definition.get("creatureRules")
            feature_type_int = definition.get("featureType")
            
            # Convert feature type to string
            feature_type_str = None
            if feature_type_int in self.FEATURE_TYPE_MAP:
                feature_type_str = self.FEATURE_TYPE_MAP[feature_type_int]
            
            trait = RacialTrait(
                name=name,
                description=description if description else None,
                creatureRules=creature_rules if creature_rules else None,
                featureType=feature_type_str
            )
            
            racial_traits.append(trait)
            
        return racial_traits
    
    def parse_feats(self) -> List[Feat]:
        """Parse feats from feats[]."""
        feats = []
        
        feat_list = self.data.get("feats", [])
        
        for feat_data in feat_list:
            definition = feat_data.get("definition", {})
            
            name = definition.get("name", "Unknown Feat")
            description = self.clean_html_description(definition.get("description"))
            creature_rules = definition.get("creatureRules")
            is_repeatable = definition.get("isRepeatable")
            
            # Parse activation details
            activation_data = definition.get("activation")
            activation = None
            if activation_data:
                activation_time = activation_data.get("activationTime")
                activation_type_int = activation_data.get("activationType")
                activation_type_str = None
                if activation_type_int in self.ACTIVATION_TYPE_MAP:
                    activation_type_str = self.ACTIVATION_TYPE_MAP[activation_type_int]
                    
                if activation_time is not None or activation_type_str is not None:
                    activation = FeatureActivation(
                        activationTime=activation_time,
                        activationType=activation_type_str
                    )
            
            feat = Feat(
                name=name,
                description=description if description else None,
                activation=activation,
                creatureRules=creature_rules if creature_rules else None,
                isRepeatable=is_repeatable
            )
            
            feats.append(feat)
            
        return feats
    
    def parse_class_features(self) -> Dict[str, Dict[int, List[ClassFeature]]]:
        """Parse class features from classes[] data."""
        class_features_dict = {}
        
        classes = self.data.get("classes", [])
        
        for class_data in classes:
            class_def = class_data.get("definition", {})
            subclass_def = class_data.get("subclassDefinition")
            
            class_name = class_def.get("name", "Unknown Class")
            class_level = class_data.get("level", 1)
            
            # Organize features by level they're gained
            features_by_level = {}
            
            # Parse base class features
            class_feature_list = class_def.get("classFeatures", [])
            self._process_class_feature_list(
                class_feature_list, features_by_level, class_level
            )
            
            # Parse subclass features if they exist
            if subclass_def:
                subclass_feature_list = subclass_def.get("classFeatures", [])
                self._process_class_feature_list(
                    subclass_feature_list, features_by_level, class_level
                )
            
            class_features_dict[class_name] = features_by_level
            
        return class_features_dict
    
    def _process_class_feature_list(
        self, 
        feature_list: List[Dict[str, Any]], 
        features_by_level: Dict[int, List[ClassFeature]], 
        max_level: int
    ):
        """Process a list of class features and organize by level."""
        for feature_data in feature_list:
            # Class features may have definition nested or be direct
            if "definition" in feature_data:
                definition = feature_data["definition"]
            else:
                definition = feature_data
            
            required_level = definition.get("requiredLevel", 1)
            
            # Only include features the character has access to
            if required_level > max_level:
                continue
                
            name = definition.get("name", "Unknown Feature")
            
            # Skip ability score improvements as they're not informative
            if "ability score improvement" in name.lower():
                continue
                
            description = self.clean_html_description(definition.get("description"))
            
            # Check if we already have this feature at this level to avoid duplicates
            if required_level in features_by_level:
                existing_names = [f.name for f in features_by_level[required_level]]
                if name in existing_names:
                    continue
            
            feature = ClassFeature(
                name=name,
                description=description if description else None
            )
            
            # Add to appropriate level
            if required_level not in features_by_level:
                features_by_level[required_level] = []
            features_by_level[required_level].append(feature)
    
    def parse_modifiers(self) -> Dict[str, List[FeatureModifier]]:
        """Parse modifiers from modifiers data."""
        parsed_modifiers = {}
        
        modifiers_data = self.data.get("modifiers", {})
        
        for category in ["race", "class", "background", "item", "feat", "condition"]:
            modifiers_list = modifiers_data.get(category, [])
            if not modifiers_list:  # Skip if None or empty
                continue
            category_modifiers = []
            
            for mod_data in modifiers_list:
                modifier = FeatureModifier(
                    type=mod_data.get("type"),
                    subType=mod_data.get("subType"),
                    dice=mod_data.get("dice"),
                    restriction=mod_data.get("restriction") if mod_data.get("restriction") else None,
                    statId=mod_data.get("statId"),
                    requiresAttunement=mod_data.get("requiresAttunement"),
                    duration=mod_data.get("duration"),
                    friendlyTypeName=mod_data.get("friendlyTypeName"),
                    friendlySubtypeName=mod_data.get("friendlySubtypeName"),
                    bonusTypes=mod_data.get("bonusTypes") if mod_data.get("bonusTypes") else None,
                    value=mod_data.get("value")
                )
                
                category_modifiers.append(modifier)
            
            if category_modifiers:  # Only add if there are modifiers
                parsed_modifiers[category] = category_modifiers
        
        return parsed_modifiers
    
    def parse_all_features(self) -> FeaturesAndTraits:
        """Parse all features and traits into a FeaturesAndTraits object.
        
        Note: Actions are no longer included here. Use parse_actions.py instead,
        which provides more complete action data including weapons and item spells.
        """
        racial_traits = self.parse_racial_traits()
        feats = self.parse_feats()
        class_features = self.parse_class_features()
        modifiers = self.parse_modifiers()
        
        return FeaturesAndTraits(
            racial_traits=racial_traits,
            class_features=class_features,
            feats=feats,
            modifiers=modifiers
        )
    
    def print_features_summary(self, features_and_traits: FeaturesAndTraits):
        """Print a summary of parsed features."""
        print("\n" + "="*60)
        print("D&D BEYOND FEATURES EXTRACTION SUMMARY")
        print("="*60)
        
        # Racial Traits Summary
        print(f"\nRACIAL TRAITS ({len(features_and_traits.racial_traits)}):")
        print("-" * 40)
        for trait in features_and_traits.racial_traits:
            print(f"  • {trait.name}")
        
        # Feats Summary  
        print(f"\nFEATS ({len(features_and_traits.feats)}):")
        print("-" * 40)
        for feat in features_and_traits.feats:
            repeatable = " [repeatable]" if feat.isRepeatable else ""
            print(f"  • {feat.name}{repeatable}")
        
        # Class Features Summary
        print(f"\nCLASS FEATURES:")
        print("-" * 40)
        for class_name, levels in features_and_traits.class_features.items():
            print(f"\n{class_name}:")
            for level, features in levels.items():
                print(f"  Level {level} ({len(features)} features):")
                for feature in features:
                    print(f"    • {feature.name}")
        
        # Modifiers Summary
        print(f"\nMODIFIERS:")
        print("-" * 40)
        for category, modifiers in features_and_traits.modifiers.items():
            print(f"\n{category.title()} Modifiers ({len(modifiers)}):")
            for modifier in modifiers:
                restriction = f" [{modifier.restriction}]" if modifier.restriction else ""
                print(f"  • {modifier.friendlyTypeName}: {modifier.friendlySubtypeName}{restriction}")

