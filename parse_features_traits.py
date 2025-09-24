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
import sys
import re
from typing import Dict, List, Optional, Union, Any
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Enhanced feature objects for D&D Beyond parsing

@dataclass
class ActivationDetails:
    """Activation information for features and actions."""
    activationTime: Optional[int] = None
    activationType: Optional[str] = None  # Converted to human-readable string

@dataclass 
class LimitedUse:
    """Limited use information for features."""
    maxUses: Optional[int] = None
    resetType: Optional[str] = None  # Converted to human-readable string

@dataclass
class RangeInfo:
    """Range information for actions."""
    range: Optional[int] = None
    longRange: Optional[int] = None
    aoeType: Optional[int] = None
    aoeSize: Optional[int] = None
    hasAoeSpecialDescription: Optional[bool] = None
    minimumRange: Optional[int] = None

@dataclass
class EnhancedRacialTrait:
    """Enhanced racial trait with all D&D Beyond fields."""
    name: str
    description: Optional[str] = None
    creatureRules: Optional[List[Dict[str, Any]]] = None
    featureType: Optional[str] = None  # Converted to human-readable string

@dataclass
class EnhancedClassFeature:
    """Enhanced class feature with all D&D Beyond fields.""" 
    name: str
    description: Optional[str] = None

@dataclass
class EnhancedFeat:
    """Enhanced feat with all D&D Beyond fields."""
    name: str
    description: Optional[str] = None
    activation: Optional[ActivationDetails] = None
    creatureRules: Optional[List[Dict[str, Any]]] = None
    isRepeatable: Optional[bool] = None

@dataclass
class EnhancedAction:
    """Enhanced action with all D&D Beyond fields."""
    limitedUse: Optional[LimitedUse] = None
    name: Optional[str] = None
    description: Optional[str] = None
    abilityModifierStatName: Optional[str] = None  # Human readable name
    onMissDescription: Optional[str] = None
    saveFailDescription: Optional[str] = None
    saveSuccessDescription: Optional[str] = None
    saveStatId: Optional[int] = None
    fixedSaveDc: Optional[int] = None
    attackTypeRange: Optional[int] = None
    actionType: Optional[str] = None  # Converted to human-readable string
    attackSubtype: Optional[int] = None
    dice: Optional[Dict[str, Any]] = None
    value: Optional[int] = None
    damageTypeId: Optional[int] = None
    isMartialArts: Optional[bool] = None
    isProficient: Optional[bool] = None
    spellRangeType: Optional[int] = None
    range: Optional[RangeInfo] = None
    activation: Optional[ActivationDetails] = None

@dataclass
class EnhancedModifier:
    """Enhanced modifier with selected D&D Beyond fields."""
    type: Optional[str] = None
    subType: Optional[str] = None
    dice: Optional[Dict[str, Any]] = None
    restriction: Optional[str] = None
    statId: Optional[int] = None
    requiresAttunement: Optional[bool] = None
    duration: Optional[Dict[str, Any]] = None
    friendlyTypeName: Optional[str] = None
    friendlySubtypeName: Optional[str] = None
    bonusTypes: Optional[List[str]] = None
    value: Optional[int] = None

@dataclass
class EnhancedFeaturesAndTraits:
    """Container for all enhanced features and traits."""
    racial_traits: List[EnhancedRacialTrait] = field(default_factory=list)
    class_features: Dict[str, Dict[int, List[EnhancedClassFeature]]] = field(default_factory=dict)
    feats: List[EnhancedFeat] = field(default_factory=list)
    actions: Dict[str, List[EnhancedAction]] = field(default_factory=dict)
    modifiers: Dict[str, List[EnhancedModifier]] = field(default_factory=dict)


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
        self.actions_data = self.data.get("actions", {})
        
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
    
    def find_action_for_feature(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Find corresponding action data for a feature by name."""
        # Search in all action categories
        for category in ["race", "class", "background", "item", "feat"]:
            actions = self.actions_data.get(category, [])
            if actions:
                for action in actions:
                    if action.get("name", "").lower() == feature_name.lower():
                        return action
        return None
    
    def extract_uses_from_action(self, action_data: Dict[str, Any]) -> Optional[Dict[str, Union[int, str]]]:
        """Extract usage information from action's limitedUse structure."""
        limited_use = action_data.get("limitedUse")
        if not limited_use:
            return None
            
        uses = {}
        
        # Map reset types
        reset_type_map = {
            1: "short_rest",
            2: "long_rest", 
            3: "dawn",
            4: "dusk",
            5: "recharge",
            6: "turn"
        }
        
        max_uses = limited_use.get("maxUses")
        number_used = limited_use.get("numberUsed", 0)
        reset_type = limited_use.get("resetType")
        
        if max_uses is not None:
            uses["max_uses"] = max_uses
            uses["current_uses"] = max_uses - number_used
            
        if reset_type in reset_type_map:
            uses["reset_type"] = reset_type_map[reset_type]
            
        return uses if uses else None
    
    def parse_racial_traits(self) -> List[EnhancedRacialTrait]:
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
            
            trait = EnhancedRacialTrait(
                name=name,
                description=description if description else None,
                creatureRules=creature_rules if creature_rules else None,
                featureType=feature_type_str
            )
            
            racial_traits.append(trait)
            
        return racial_traits
    
    def parse_feats(self) -> List[EnhancedFeat]:
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
                    activation = ActivationDetails(
                        activationTime=activation_time,
                        activationType=activation_type_str
                    )
            
            feat = EnhancedFeat(
                name=name,
                description=description if description else None,
                activation=activation,
                creatureRules=creature_rules if creature_rules else None,
                isRepeatable=is_repeatable
            )
            
            feats.append(feat)
            
        return feats
    
    def parse_class_features(self) -> Dict[str, Dict[int, List[EnhancedClassFeature]]]:
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
        features_by_level: Dict[int, List[EnhancedClassFeature]], 
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
            
            feature = EnhancedClassFeature(
                name=name,
                description=description if description else None
            )
            
            # Add to appropriate level
            if required_level not in features_by_level:
                features_by_level[required_level] = []
            features_by_level[required_level].append(feature)
    
    def parse_actions(self) -> Dict[str, List[EnhancedAction]]:
        """Parse actions from actions data."""
        parsed_actions = {}
        
        actions_data = self.actions_data
        
        for category in ["race", "class", "background", "item", "feat"]:
            actions_list = actions_data.get(category, [])
            if not actions_list:  # Skip if None or empty
                continue
            category_actions = []
            
            for action_data in actions_list:
                # Parse limited use
                limited_use = None
                limited_use_data = action_data.get("limitedUse")
                if limited_use_data and limited_use_data.get("maxUses"):
                    reset_type_int = limited_use_data.get("resetType")
                    reset_type_str = None
                    if reset_type_int in self.RESET_TYPE_MAP:
                        reset_type_str = self.RESET_TYPE_MAP[reset_type_int]
                        
                    limited_use = LimitedUse(
                        maxUses=limited_use_data.get("maxUses"),
                        resetType=reset_type_str
                    )
                
                # Parse range info
                range_info = None
                range_data = action_data.get("range")
                if range_data:
                    range_info = RangeInfo(
                        range=range_data.get("range"),
                        longRange=range_data.get("longRange"),
                        aoeType=range_data.get("aoeType"),
                        aoeSize=range_data.get("aoeSize"),
                        hasAoeSpecialDescription=range_data.get("hasAoeSpecialDescription"),
                        minimumRange=range_data.get("minimumRange")
                    )
                
                # Parse activation
                activation = None
                activation_data = action_data.get("activation")
                if activation_data:
                    activation_time = activation_data.get("activationTime")
                    activation_type_int = activation_data.get("activationType")
                    activation_type_str = None
                    if activation_type_int in self.ACTIVATION_TYPE_MAP:
                        activation_type_str = self.ACTIVATION_TYPE_MAP[activation_type_int]
                        
                    if activation_time is not None or activation_type_str is not None:
                        activation = ActivationDetails(
                            activationTime=activation_time,
                            activationType=activation_type_str
                        )
                
                # Get ability modifier stat name
                ability_stat_name = None
                ability_stat_id = action_data.get("abilityModifierStatId")
                if ability_stat_id and ability_stat_id in self.ABILITY_STAT_MAP:
                    ability_stat_name = self.ABILITY_STAT_MAP[ability_stat_id]
                
                # Convert action type to string
                action_type_int = action_data.get("actionType")
                action_type_str = None
                if action_type_int in self.ACTION_TYPE_MAP:
                    action_type_str = self.ACTION_TYPE_MAP[action_type_int]
                
                # Clean descriptions
                description = self.clean_html_description(action_data.get("description"))
                on_miss = self.clean_html_description(action_data.get("onMissDescription"))
                save_fail = self.clean_html_description(action_data.get("saveFailDescription"))
                save_success = self.clean_html_description(action_data.get("saveSuccessDescription"))
                
                action = EnhancedAction(
                    limitedUse=limited_use,
                    name=action_data.get("name"),
                    description=description if description else None,
                    abilityModifierStatName=ability_stat_name,
                    onMissDescription=on_miss if on_miss else None,
                    saveFailDescription=save_fail if save_fail else None,
                    saveSuccessDescription=save_success if save_success else None,
                    saveStatId=action_data.get("saveStatId"),
                    fixedSaveDc=action_data.get("fixedSaveDc"),
                    attackTypeRange=action_data.get("attackTypeRange"),
                    actionType=action_type_str,
                    attackSubtype=action_data.get("attackSubtype"),
                    dice=action_data.get("dice"),
                    value=action_data.get("value"),
                    damageTypeId=action_data.get("damageTypeId"),
                    isMartialArts=action_data.get("isMartialArts"),
                    isProficient=action_data.get("isProficient"),
                    spellRangeType=action_data.get("spellRangeType"),
                    range=range_info,
                    activation=activation
                )
                
                category_actions.append(action)
            
            if category_actions:  # Only add if there are actions
                parsed_actions[category] = category_actions
        
        return parsed_actions
    
    def parse_modifiers(self) -> Dict[str, List[EnhancedModifier]]:
        """Parse modifiers from modifiers data."""
        parsed_modifiers = {}
        
        modifiers_data = self.data.get("modifiers", {})
        
        for category in ["race", "class", "background", "item", "feat", "condition"]:
            modifiers_list = modifiers_data.get(category, [])
            if not modifiers_list:  # Skip if None or empty
                continue
            category_modifiers = []
            
            for mod_data in modifiers_list:
                modifier = EnhancedModifier(
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
    
    def parse_all_features(self) -> EnhancedFeaturesAndTraits:
        """Parse all features and traits into an EnhancedFeaturesAndTraits object."""
        racial_traits = self.parse_racial_traits()
        feats = self.parse_feats()
        class_features = self.parse_class_features()
        actions = self.parse_actions()
        modifiers = self.parse_modifiers()
        
        return EnhancedFeaturesAndTraits(
            racial_traits=racial_traits,
            class_features=class_features,
            feats=feats,
            actions=actions,
            modifiers=modifiers
        )
    
    def print_features_summary(self, features_and_traits: EnhancedFeaturesAndTraits):
        """Print a summary of parsed features."""
        print("\n" + "="*60)
        print("D&D BEYOND ENHANCED FEATURES EXTRACTION SUMMARY")
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
        
        # Actions Summary
        print(f"\nACTIONS:")
        print("-" * 40)
        for category, actions in features_and_traits.actions.items():
            print(f"\n{category.title()} Actions ({len(actions)}):")
            for action in actions:
                action_type = f" [{action.actionType}]" if action.actionType else ""
                uses_info = ""
                if action.limitedUse and action.limitedUse.maxUses:
                    reset_info = f" per {action.limitedUse.resetType}" if action.limitedUse.resetType else ""
                    uses_info = f" ({action.limitedUse.maxUses} uses{reset_info})"
                print(f"  • {action.name}{action_type}{uses_info}")
        
        # Modifiers Summary
        print(f"\nMODIFIERS:")
        print("-" * 40)
        for category, modifiers in features_and_traits.modifiers.items():
            print(f"\n{category.title()} Modifiers ({len(modifiers)}):")
            for modifier in modifiers:
                restriction = f" [{modifier.restriction}]" if modifier.restriction else ""
                print(f"  • {modifier.friendlyTypeName}: {modifier.friendlySubtypeName}{restriction}")


def clean_dict_for_json(obj):
    """Remove None values and empty collections from dictionary for cleaner JSON output."""
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            cleaned_value = clean_dict_for_json(value)
            # Only include if value is not None and not empty
            if cleaned_value is not None and cleaned_value != [] and cleaned_value != {}:
                cleaned[key] = cleaned_value
        return cleaned if cleaned else None
    elif isinstance(obj, list):
        cleaned = [clean_dict_for_json(item) for item in obj]
        # Filter out None values from list
        cleaned = [item for item in cleaned if item is not None]
        return cleaned if cleaned else None
    else:
        return obj

def main():
    """Main function to parse D&D Beyond JSON and extract features."""
    if len(sys.argv) != 2:
        print("Usage: python parse_dndbeyond_features.py <path_to_json_file>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    try:
        # Load JSON data
        print(f"Loading D&D Beyond character data from: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Parse features
        parser = DNDBeyondFeaturesParser(json_data)
        features_and_traits = parser.parse_all_features()
        
        # Print summary
        parser.print_features_summary(features_and_traits)
        
        # Save to output file
        output_file = json_file_path.replace('.json', '_clean_features_parsed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert to dict for JSON serialization and clean empty values
            features_dict = asdict(features_and_traits)
            cleaned_dict = clean_dict_for_json(features_dict)
            json.dump(cleaned_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\n" + "="*60)
        print(f"Features data saved to: {output_file}")
        print("="*60)
        
        return features_and_traits
        
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{json_file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()