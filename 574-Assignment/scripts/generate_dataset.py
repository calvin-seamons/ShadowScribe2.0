"""
Dataset Generation Script for 574 Assignment

Generates synthetic training data for the joint DeBERTa model.
Outputs train.json, val.json, test.json to 574-assignment/data/generated/

Features:
- K-expansion: Each template generates K samples with different entity fills
- API-based gazetteers: Uses cached D&D 5e SRD data (run fetch_srd_data.py first)
- Deduplication: Avoids identical samples

Run from project root:
    cd 574-assignment
    uv run python -m scripts.generate_dataset

Output structure:
{
    "query": "What's my AC and how does Shield work?",
    "tools": ["character_data", "rulebook"],
    "intents": {"character_data": "combat_info", "rulebook": "spell_details"},
    "bio_tags": ["O", "O", "O", "O", "O", "O", "B-SPELL", "O"],
    "entities": [{"text": "Shield", "type": "SPELL", "start": 6, "end": 7}]
}
"""

import json
import random
import re
import os
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any, Optional, Set

# Import templates and gazetteers
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATASET_CONFIG

from data.templates.entity_gazetteers import (
    SPELL_NAMES, CLASS_NAMES, RACE_NAMES, CREATURE_NAMES, WEAPON_NAMES,
    ARMOR_NAMES, EQUIPMENT_NAMES, MAGIC_ITEM_NAMES, SKILL_NAMES,
    CONDITION_NAMES, DAMAGE_TYPES, LOCATION_NAMES, CLASS_FEATURE_NAMES,
    ABILITY_NAMES_EXTENDED, FEAT_NAMES, BACKGROUND_NAMES, SUBCLASS_NAMES,
    MECHANIC_NAMES, CREATURE_ABILITY_NAMES, WEAPON_PROPERTIES, LANGUAGE_NAMES,
    LEVEL_NAMES, SPELL_LEVEL_NAMES
)
from data.templates.character_templates import (
    CHARACTER_BASICS_TEMPLATES, COMBAT_INFO_TEMPLATES, ABILITIES_INFO_TEMPLATES,
    INVENTORY_INFO_TEMPLATES, MAGIC_INFO_TEMPLATES, STORY_INFO_TEMPLATES,
    SOCIAL_INFO_TEMPLATES, PROGRESS_INFO_TEMPLATES, FULL_CHARACTER_TEMPLATES,
    CHARACTER_SUMMARY_TEMPLATES
)
from data.templates.session_templates import (
    CHARACTER_STATUS_TEMPLATES, EVENT_SEQUENCE_TEMPLATES, NPC_INFO_TEMPLATES,
    LOCATION_DETAILS_TEMPLATES, ITEM_TRACKING_TEMPLATES, COMBAT_RECAP_TEMPLATES,
    SPELL_ABILITY_USAGE_TEMPLATES, CHARACTER_DECISIONS_TEMPLATES, PARTY_DYNAMICS_TEMPLATES,
    QUEST_TRACKING_TEMPLATES, PUZZLE_SOLUTIONS_TEMPLATES, LOOT_REWARDS_TEMPLATES,
    DEATH_REVIVAL_TEMPLATES, DIVINE_RELIGIOUS_TEMPLATES, MEMORY_VISION_TEMPLATES,
    RULES_MECHANICS_TEMPLATES, HUMOR_MOMENTS_TEMPLATES, UNRESOLVED_MYSTERIES_TEMPLATES,
    FUTURE_IMPLICATIONS_TEMPLATES, CROSS_SESSION_TEMPLATES
)
from data.templates.rulebook_templates import (
    DESCRIBE_ENTITY_TEMPLATES, COMPARE_ENTITIES_TEMPLATES, LEVEL_PROGRESSION_TEMPLATES,
    ACTION_OPTIONS_TEMPLATES, RULE_MECHANICS_TEMPLATES, CALCULATE_VALUES_TEMPLATES,
    SPELL_DETAILS_TEMPLATES, CLASS_SPELL_ACCESS_TEMPLATES, MONSTER_STATS_TEMPLATES,
    CONDITION_EFFECTS_TEMPLATES, CHARACTER_CREATION_TEMPLATES, MULTICLASS_RULES_TEMPLATES,
    EQUIPMENT_PROPERTIES_TEMPLATES, DAMAGE_TYPES_TEMPLATES, REST_MECHANICS_TEMPLATES,
    SKILL_USAGE_TEMPLATES, FIND_BY_CRITERIA_TEMPLATES, PREREQUISITE_CHECK_TEMPLATES,
    INTERACTION_RULES_TEMPLATES, TACTICAL_USAGE_TEMPLATES, ENVIRONMENTAL_RULES_TEMPLATES,
    CREATURE_ABILITIES_TEMPLATES, SAVING_THROWS_TEMPLATES, MAGIC_ITEM_USAGE_TEMPLATES,
    PLANAR_PROPERTIES_TEMPLATES, DOWNTIME_ACTIVITIES_TEMPLATES, SUBCLASS_FEATURES_TEMPLATES,
    COST_LOOKUP_TEMPLATES, LEGENDARY_MECHANICS_TEMPLATES, OPTIMIZATION_ADVICE_TEMPLATES
)
from data.templates.multi_tool_templates import (
    CHARACTER_RULEBOOK_TEMPLATES, CHARACTER_SESSION_TEMPLATES, SESSION_RULEBOOK_TEMPLATES,
    THREE_TOOL_TEMPLATES
)

# =============================================================================
# Configuration (loaded from config.py)
# =============================================================================

RANDOM_SEED = DATASET_CONFIG.get('random_seed', 42)
EXPANSIONS_PER_TEMPLATE = DATASET_CONFIG.get('expansions_per_template', 10)
DEDUPLICATE = DATASET_CONFIG.get('deduplicate', True)

TRAIN_RATIO = DATASET_CONFIG.get('train_split', 0.8)
VAL_RATIO = DATASET_CONFIG.get('val_split', 0.1)
TEST_RATIO = DATASET_CONFIG.get('test_split', 0.1)

# Distribution of tool combinations
SINGLE_TOOL_RATIO = DATASET_CONFIG.get('one_tool_pct', 0.30)
TWO_TOOL_RATIO = DATASET_CONFIG.get('two_tool_pct', 0.50)
THREE_TOOL_RATIO = DATASET_CONFIG.get('three_tool_pct', 0.20)

# =============================================================================
# Entity Gazetteers Mapping (now loaded from API cache)
# =============================================================================

ENTITY_GAZETTEERS = {
    # Core entity types
    "spell": SPELL_NAMES,
    "spell1": SPELL_NAMES,
    "spell2": SPELL_NAMES,
    "class": CLASS_NAMES,
    "class1": CLASS_NAMES,
    "class2": CLASS_NAMES,
    "class_name": CLASS_NAMES,
    "race": RACE_NAMES,
    "race1": RACE_NAMES,
    "race2": RACE_NAMES,
    "creature": CREATURE_NAMES,
    "creature1": CREATURE_NAMES,
    "creature2": CREATURE_NAMES,
    "monster": CREATURE_NAMES,
    
    # Items
    "weapon": WEAPON_NAMES if WEAPON_NAMES else EQUIPMENT_NAMES[:50],
    "weapon1": WEAPON_NAMES if WEAPON_NAMES else EQUIPMENT_NAMES[:50],
    "weapon2": WEAPON_NAMES if WEAPON_NAMES else EQUIPMENT_NAMES[:50],
    "armor": ARMOR_NAMES if ARMOR_NAMES else EQUIPMENT_NAMES[:20],
    "armor1": ARMOR_NAMES if ARMOR_NAMES else EQUIPMENT_NAMES[:20],
    "armor2": ARMOR_NAMES if ARMOR_NAMES else EQUIPMENT_NAMES[:20],
    "item": EQUIPMENT_NAMES + MAGIC_ITEM_NAMES,
    "item1": EQUIPMENT_NAMES + MAGIC_ITEM_NAMES,
    "item2": EQUIPMENT_NAMES + MAGIC_ITEM_NAMES,
    "magic_item": MAGIC_ITEM_NAMES,
    "equipment": EQUIPMENT_NAMES,
    
    # Character building
    "ability": ABILITY_NAMES_EXTENDED,
    "ability1": ABILITY_NAMES_EXTENDED,
    "ability2": ABILITY_NAMES_EXTENDED,
    "skill": SKILL_NAMES,
    "skill1": SKILL_NAMES,
    "skill2": SKILL_NAMES,
    "condition": CONDITION_NAMES,
    "condition1": CONDITION_NAMES,
    "condition2": CONDITION_NAMES,
    "damage_type": DAMAGE_TYPES,
    "damage_type1": DAMAGE_TYPES,
    "damage_type2": DAMAGE_TYPES,
    "feat": FEAT_NAMES,
    "background": BACKGROUND_NAMES,
    "location": LOCATION_NAMES,
    "feature": CLASS_FEATURE_NAMES,
    "feature1": CLASS_FEATURE_NAMES,
    "feature2": CLASS_FEATURE_NAMES,
    "subclass": SUBCLASS_NAMES,
    
    # Misc
    "level": LEVEL_NAMES,
    "spell_level": SPELL_LEVEL_NAMES,
    "plane": LOCATION_NAMES[:20],
    "mechanic": MECHANIC_NAMES,
    "creature_ability": CREATURE_ABILITY_NAMES,
    "weapon_property": WEAPON_PROPERTIES,
    "language": LANGUAGE_NAMES,
}

# Slot type to NER tag mapping
SLOT_TO_NER_TAG = {
    "spell": "SPELL",
    "spell1": "SPELL",
    "spell2": "SPELL",
    "class": "CLASS",
    "class1": "CLASS",
    "class2": "CLASS",
    "class_name": "CLASS",
    "race": "RACE",
    "race1": "RACE",
    "race2": "RACE",
    "creature": "CREATURE",
    "creature1": "CREATURE",
    "creature2": "CREATURE",
    "weapon": "ITEM",
    "weapon1": "ITEM",
    "weapon2": "ITEM",
    "armor": "ITEM",
    "armor1": "ITEM",
    "armor2": "ITEM",
    "item": "ITEM",
    "magic_item": "ITEM",
    "ability": "ABILITY",
    "skill": "SKILL",
    "condition": "CONDITION",
    "condition1": "CONDITION",
    "condition2": "CONDITION",
    "damage_type": "DAMAGE_TYPE",
    "feat": "FEAT",
    "background": "BACKGROUND",
    "location": "LOCATION",
    "feature": "CLASS",  # Class features tagged as CLASS
    "level": "O",  # Levels are not entities
}

# =============================================================================
# Single-Tool Template Mappings
# =============================================================================

CHARACTER_TEMPLATES = {
    "character_basics": CHARACTER_BASICS_TEMPLATES,
    "combat_info": COMBAT_INFO_TEMPLATES,
    "abilities_info": ABILITIES_INFO_TEMPLATES,
    "inventory_info": INVENTORY_INFO_TEMPLATES,
    "magic_info": MAGIC_INFO_TEMPLATES,
    "story_info": STORY_INFO_TEMPLATES,
    "social_info": SOCIAL_INFO_TEMPLATES,
    "progress_info": PROGRESS_INFO_TEMPLATES,
    "full_character": FULL_CHARACTER_TEMPLATES,
    "character_summary": CHARACTER_SUMMARY_TEMPLATES,
}

SESSION_TEMPLATES = {
    "character_status": CHARACTER_STATUS_TEMPLATES,
    "event_sequence": EVENT_SEQUENCE_TEMPLATES,
    "npc_info": NPC_INFO_TEMPLATES,
    "location_details": LOCATION_DETAILS_TEMPLATES,
    "item_tracking": ITEM_TRACKING_TEMPLATES,
    "combat_recap": COMBAT_RECAP_TEMPLATES,
    "spell_ability_usage": SPELL_ABILITY_USAGE_TEMPLATES,
    "character_decisions": CHARACTER_DECISIONS_TEMPLATES,
    "party_dynamics": PARTY_DYNAMICS_TEMPLATES,
    "quest_tracking": QUEST_TRACKING_TEMPLATES,
    "puzzle_solutions": PUZZLE_SOLUTIONS_TEMPLATES,
    "loot_rewards": LOOT_REWARDS_TEMPLATES,
    "death_revival": DEATH_REVIVAL_TEMPLATES,
    "divine_religious": DIVINE_RELIGIOUS_TEMPLATES,
    "memory_vision": MEMORY_VISION_TEMPLATES,
    "rules_mechanics": RULES_MECHANICS_TEMPLATES,
    "humor_moments": HUMOR_MOMENTS_TEMPLATES,
    "unresolved_mysteries": UNRESOLVED_MYSTERIES_TEMPLATES,
    "future_implications": FUTURE_IMPLICATIONS_TEMPLATES,
    "cross_session": CROSS_SESSION_TEMPLATES,
}

RULEBOOK_TEMPLATES = {
    "describe_entity": DESCRIBE_ENTITY_TEMPLATES,
    "compare_entities": COMPARE_ENTITIES_TEMPLATES,
    "level_progression": LEVEL_PROGRESSION_TEMPLATES,
    "action_options": ACTION_OPTIONS_TEMPLATES,
    "rule_mechanics": RULE_MECHANICS_TEMPLATES,
    "calculate_values": CALCULATE_VALUES_TEMPLATES,
    "spell_details": SPELL_DETAILS_TEMPLATES,
    "class_spell_access": CLASS_SPELL_ACCESS_TEMPLATES,
    "monster_stats": MONSTER_STATS_TEMPLATES,
    "condition_effects": CONDITION_EFFECTS_TEMPLATES,
    "character_creation": CHARACTER_CREATION_TEMPLATES,
    "multiclass_rules": MULTICLASS_RULES_TEMPLATES,
    "equipment_properties": EQUIPMENT_PROPERTIES_TEMPLATES,
    "damage_types": DAMAGE_TYPES_TEMPLATES,
    "rest_mechanics": REST_MECHANICS_TEMPLATES,
    "skill_usage": SKILL_USAGE_TEMPLATES,
    "find_by_criteria": FIND_BY_CRITERIA_TEMPLATES,
    "prerequisite_check": PREREQUISITE_CHECK_TEMPLATES,
    "interaction_rules": INTERACTION_RULES_TEMPLATES,
    "tactical_usage": TACTICAL_USAGE_TEMPLATES,
    "environmental_rules": ENVIRONMENTAL_RULES_TEMPLATES,
    "creature_abilities": CREATURE_ABILITIES_TEMPLATES,
    "saving_throws": SAVING_THROWS_TEMPLATES,
    "magic_item_usage": MAGIC_ITEM_USAGE_TEMPLATES,
    "planar_properties": PLANAR_PROPERTIES_TEMPLATES,
    "downtime_activities": DOWNTIME_ACTIVITIES_TEMPLATES,
    "subclass_features": SUBCLASS_FEATURES_TEMPLATES,
    "cost_lookup": COST_LOOKUP_TEMPLATES,
    "legendary_mechanics": LEGENDARY_MECHANICS_TEMPLATES,
    "optimization_advice": OPTIMIZATION_ADVICE_TEMPLATES,
}

# =============================================================================
# Slot Filling Functions
# =============================================================================

def get_slot_value(slot_type: str) -> str:
    """Get a random value for a slot type."""
    # Handle numbered slots (e.g., spell1, spell2)
    base_type = re.sub(r'\d+$', '', slot_type)

    if base_type in ENTITY_GAZETTEERS:
        return random.choice(ENTITY_GAZETTEERS[base_type])
    elif slot_type == "class_name":
        return random.choice(ENTITY_GAZETTEERS["class"])
    else:
        print(f"Warning: Unknown slot type '{slot_type}'")
        return f"[{slot_type}]"


def fill_template(template: str, slots: Dict[str, str]) -> Tuple[str, List[Dict]]:
    """
    Fill a template with random entity values.
    Returns the filled query and list of entity spans.
    """
    filled = template
    entities = []

    # Sort slots by position in template (reverse) to maintain positions
    slot_positions = []
    for slot_name, slot_type in slots.items():
        pattern = "{" + slot_name + "}"
        match = re.search(re.escape(pattern), filled)
        if match:
            slot_positions.append((match.start(), slot_name, slot_type))

    # Sort by position (descending) to fill from end to start
    slot_positions.sort(key=lambda x: x[0], reverse=True)

    for pos, slot_name, slot_type in slot_positions:
        value = get_slot_value(slot_type)
        pattern = "{" + slot_name + "}"

        # Find position before replacement
        match = re.search(re.escape(pattern), filled)
        if match:
            start_char = match.start()
            filled = filled[:start_char] + value + filled[match.end():]

            # Get NER tag for this entity
            ner_tag = SLOT_TO_NER_TAG.get(slot_type, SLOT_TO_NER_TAG.get(slot_name, "O"))

            if ner_tag != "O":
                entities.append({
                    "text": value,
                    "type": ner_tag,
                    "start_char": start_char,
                })

    # Calculate word-level positions for entities
    words = filled.split()
    
    for entity in entities:
        entity_text = entity["text"]
        entity_start_char = entity["start_char"]
        
        # Find word positions by character offset
        char_pos = 0
        entity["start"] = -1
        entity["end"] = -1
        
        for i, word in enumerate(words):
            word_start = char_pos
            word_end = char_pos + len(word)
            
            # Check if this word is at or after the entity start position
            if entity["start"] == -1 and word_start <= entity_start_char < word_end + 1:
                entity["start"] = i
            
            char_pos = word_end + 1  # +1 for space
        
        # If we found the start, calculate end based on entity word count
        if entity["start"] != -1:
            entity_words = entity_text.split()
            entity["end"] = min(entity["start"] + len(entity_words), len(words))
        else:
            # Fallback: search for the entity text directly in words
            entity_words = entity_text.split()
            for i in range(len(words) - len(entity_words) + 1):
                # Check if consecutive words match the entity
                potential_match = " ".join(words[i:i + len(entity_words)])
                if potential_match.lower() == entity_text.lower() or potential_match == entity_text:
                    entity["start"] = i
                    entity["end"] = i + len(entity_words)
                    break
        
        del entity["start_char"]
    
    # Filter out entities with invalid spans
    valid_entities = [e for e in entities if e["start"] >= 0 and e["end"] > e["start"]]
    
    return filled, valid_entities


def generate_bio_tags(query: str, entities: List[Dict]) -> List[str]:
    """Generate BIO tags for a query given entity spans."""
    words = query.split()
    tags = ["O"] * len(words)

    for entity in entities:
        if entity["start"] >= 0 and entity["end"] > entity["start"]:
            for i in range(entity["start"], min(entity["end"], len(words))):
                if i == entity["start"]:
                    tags[i] = f"B-{entity['type']}"
                else:
                    tags[i] = f"I-{entity['type']}"

    return tags


# =============================================================================
# Sample Generation Functions
# =============================================================================

def generate_single_tool_sample(tool: str) -> Dict:
    """Generate a single-tool query sample."""
    if tool == "character_data":
        templates = CHARACTER_TEMPLATES
    elif tool == "session_notes":
        templates = SESSION_TEMPLATES
    elif tool == "rulebook":
        templates = RULEBOOK_TEMPLATES
    else:
        raise ValueError(f"Unknown tool: {tool}")

    # Pick random intent and template
    intent = random.choice(list(templates.keys()))
    template_list = templates[intent]
    template_data = random.choice(template_list)

    # Fill template
    query, entities = fill_template(template_data["template"], template_data.get("slots", {}))
    bio_tags = generate_bio_tags(query, entities)

    return {
        "query": query,
        "tools": [tool],
        "intents": {tool: intent},
        "bio_tags": bio_tags,
        "entities": entities
    }


def generate_two_tool_sample() -> Dict:
    """Generate a 2-tool query sample from multi-tool templates."""
    # Randomly pick a 2-tool template type
    template_type = random.choice([
        CHARACTER_RULEBOOK_TEMPLATES,
        CHARACTER_SESSION_TEMPLATES,
        SESSION_RULEBOOK_TEMPLATES
    ])

    template_data = random.choice(template_type)

    # Fill template
    query, entities = fill_template(template_data["template"], template_data.get("slots", {}))
    bio_tags = generate_bio_tags(query, entities)

    return {
        "query": query,
        "tools": template_data["tools"],
        "intents": template_data["intents"],
        "bio_tags": bio_tags,
        "entities": entities
    }


def generate_three_tool_sample() -> Dict:
    """Generate a 3-tool query sample."""
    template_data = random.choice(THREE_TOOL_TEMPLATES)

    # Fill template
    query, entities = fill_template(template_data["template"], template_data.get("slots", {}))
    bio_tags = generate_bio_tags(query, entities)

    return {
        "query": query,
        "tools": template_data["tools"],
        "intents": template_data["intents"],
        "bio_tags": bio_tags,
        "entities": entities
    }


def expand_template(template_data: Dict, tool: str = None, intent: str = None, k: int = 10) -> List[Dict]:
    """
    Generate K samples from a single template with different entity fills.
    
    Args:
        template_data: Template dict with 'template', 'slots', optionally 'tools', 'intents'
        tool: For single-tool templates, the tool name
        intent: For single-tool templates, the intent name
        k: Number of variations to generate
        
    Returns:
        List of K sample dictionaries
    """
    samples = []
    seen_queries: Set[str] = set()
    
    # Determine if this is single-tool or multi-tool template
    if tool and intent:
        # Single-tool template
        tools = [tool]
        intents = {tool: intent}
    else:
        # Multi-tool template (has tools/intents in template_data)
        tools = template_data["tools"]
        intents = template_data["intents"]
    
    slots = template_data.get("slots", {})
    
    # If no slots, only generate 1 sample (no variation possible)
    if not slots:
        query, entities = fill_template(template_data["template"], slots)
        bio_tags = generate_bio_tags(query, entities)
        return [{
            "query": query,
            "tools": tools,
            "intents": intents,
            "bio_tags": bio_tags,
            "entities": entities
        }]
    
    # Generate K variations
    attempts = 0
    max_attempts = k * 3  # Allow extra attempts for deduplication
    
    while len(samples) < k and attempts < max_attempts:
        attempts += 1
        
        query, entities = fill_template(template_data["template"], slots)
        
        # Deduplicate
        if DEDUPLICATE and query in seen_queries:
            continue
        seen_queries.add(query)
        
        bio_tags = generate_bio_tags(query, entities)
        
        samples.append({
            "query": query,
            "tools": tools,
            "intents": intents,
            "bio_tags": bio_tags,
            "entities": entities
        })
    
    return samples


def generate_dataset_with_expansion(seed: int = 42) -> List[Dict]:
    """
    Generate dataset using K-expansion per template.
    
    Each template generates K samples with different entity substitutions.
    Final dataset is split according to tool distribution ratios.
    """
    random.seed(seed)
    
    all_samples = []
    seen_queries: Set[str] = set()
    
    print(f"Generating dataset with K={EXPANSIONS_PER_TEMPLATE} expansions per template...")
    
    # Count templates
    single_tool_templates = 0
    two_tool_templates = 0
    three_tool_templates = 0
    
    # Generate from single-tool templates
    print("\n  Single-tool templates:")
    for tool_name, templates_dict in [
        ("character_data", CHARACTER_TEMPLATES),
        ("session_notes", SESSION_TEMPLATES),
        ("rulebook", RULEBOOK_TEMPLATES)
    ]:
        tool_samples = []
        for intent_name, template_list in templates_dict.items():
            for template_data in template_list:
                single_tool_templates += 1
                samples = expand_template(
                    template_data, 
                    tool=tool_name, 
                    intent=intent_name,
                    k=EXPANSIONS_PER_TEMPLATE
                )
                # Deduplicate across all samples
                for s in samples:
                    if not DEDUPLICATE or s["query"] not in seen_queries:
                        seen_queries.add(s["query"])
                        tool_samples.append(s)
        
        print(f"    {tool_name}: {len(tool_samples)} samples from templates")
        all_samples.extend(tool_samples)
    
    single_total = len(all_samples)
    print(f"  → Total single-tool: {single_total} samples")
    
    # Generate from two-tool templates
    print("\n  Two-tool templates:")
    two_tool_samples = []
    for template_type_name, template_list in [
        ("character+rulebook", CHARACTER_RULEBOOK_TEMPLATES),
        ("character+session", CHARACTER_SESSION_TEMPLATES),
        ("session+rulebook", SESSION_RULEBOOK_TEMPLATES)
    ]:
        type_samples = []
        for template_data in template_list:
            two_tool_templates += 1
            samples = expand_template(template_data, k=EXPANSIONS_PER_TEMPLATE)
            for s in samples:
                if not DEDUPLICATE or s["query"] not in seen_queries:
                    seen_queries.add(s["query"])
                    type_samples.append(s)
        print(f"    {template_type_name}: {len(type_samples)} samples")
        two_tool_samples.extend(type_samples)
    
    print(f"  → Total two-tool: {len(two_tool_samples)} samples")
    all_samples.extend(two_tool_samples)
    
    # Generate from three-tool templates
    print("\n  Three-tool templates:")
    three_tool_samples = []
    for template_data in THREE_TOOL_TEMPLATES:
        three_tool_templates += 1
        samples = expand_template(template_data, k=EXPANSIONS_PER_TEMPLATE)
        for s in samples:
            if not DEDUPLICATE or s["query"] not in seen_queries:
                seen_queries.add(s["query"])
                three_tool_samples.append(s)
    
    print(f"    three-tool: {len(three_tool_samples)} samples")
    print(f"  → Total three-tool: {len(three_tool_samples)} samples")
    all_samples.extend(three_tool_samples)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Template counts:")
    print(f"  Single-tool: {single_tool_templates}")
    print(f"  Two-tool: {two_tool_templates}")
    print(f"  Three-tool: {three_tool_templates}")
    print(f"  TOTAL templates: {single_tool_templates + two_tool_templates + three_tool_templates}")
    print(f"\nGenerated samples: {len(all_samples)}")
    print(f"{'='*60}")
    
    # Shuffle
    random.shuffle(all_samples)
    
    return all_samples


def split_dataset(samples: List[Dict], train_ratio: float, val_ratio: float) -> Tuple[List, List, List]:
    """Split dataset into train/val/test."""
    n = len(samples)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    return samples[:train_end], samples[train_end:val_end], samples[val_end:]


def analyze_dataset(samples: List[Dict], name: str) -> Dict[str, Any]:
    """Print dataset statistics and return them for class weight calculation."""
    print(f"\n{name} Statistics:")
    print(f"  Total samples: {len(samples)}")

    # Tool distribution
    tool_counts = defaultdict(int)
    num_tools = defaultdict(int)
    intent_counts = defaultdict(lambda: defaultdict(int))  # per-tool intent counts
    entity_type_counts = defaultdict(int)
    bio_tag_counts = defaultdict(int)

    for s in samples:
        for tool in s["tools"]:
            tool_counts[tool] += 1
        num_tools[len(s["tools"])] += 1
        
        # Track intents per tool
        for tool, intent in s["intents"].items():
            intent_counts[tool][intent] += 1
            
        for entity in s["entities"]:
            entity_type_counts[entity["type"]] += 1
            
        for tag in s["bio_tags"]:
            bio_tag_counts[tag] += 1

    print(f"  Tools: {dict(tool_counts)}")
    print(f"  Num tools per query: {dict(num_tools)}")
    
    # Print per-tool intent distribution
    print(f"  Intent distribution by tool:")
    for tool in ["character_data", "session_notes", "rulebook"]:
        if intent_counts[tool]:
            top_intents = sorted(intent_counts[tool].items(), key=lambda x: -x[1])[:3]
            print(f"    {tool}: {dict(top_intents)} ...")
    
    print(f"  Entity types: {dict(entity_type_counts)}")
    print(f"  BIO tag distribution (top 5): {dict(sorted(bio_tag_counts.items(), key=lambda x: -x[1])[:5])}")
    
    return {
        "tool_counts": dict(tool_counts),
        "intent_counts": {k: dict(v) for k, v in intent_counts.items()},
        "entity_type_counts": dict(entity_type_counts),
        "bio_tag_counts": dict(bio_tag_counts)
    }


def main():
    """Main entry point."""
    # Setup paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    output_dir = project_dir / "data" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Dataset Generation for 574 Assignment")
    print(f"K-expansion: {EXPANSIONS_PER_TEMPLATE} samples per template")
    print(f"Deduplication: {DEDUPLICATE}")
    print("=" * 60)

    # Generate dataset using K-expansion
    samples = generate_dataset_with_expansion(RANDOM_SEED)

    # Split
    train, val, test = split_dataset(samples, TRAIN_RATIO, VAL_RATIO)

    # Analyze and get statistics for class weights
    train_stats = analyze_dataset(train, "Train")
    val_stats = analyze_dataset(val, "Validation")
    test_stats = analyze_dataset(test, "Test")

    # Save datasets
    print("\nSaving datasets...")

    with open(output_dir / "train.json", "w") as f:
        json.dump(train, f, indent=2)
    print(f"  Saved {len(train)} samples to {output_dir / 'train.json'}")

    with open(output_dir / "val.json", "w") as f:
        json.dump(val, f, indent=2)
    print(f"  Saved {len(val)} samples to {output_dir / 'val.json'}")

    with open(output_dir / "test.json", "w") as f:
        json.dump(test, f, indent=2)
    print(f"  Saved {len(test)} samples to {output_dir / 'test.json'}")

    # Build comprehensive label mappings
    label_mappings = build_label_mappings(train_stats)

    with open(output_dir / "label_mappings.json", "w") as f:
        json.dump(label_mappings, f, indent=2)
    print(f"  Saved label mappings to {output_dir / 'label_mappings.json'}")

    # Validate dataset
    print("\nValidating dataset...")
    validate_dataset(train + val + test, label_mappings)

    print("\n" + "=" * 60)
    print("Dataset generation complete!")
    print(f"Total samples: {len(samples)}")
    print(f"  Train: {len(train)} ({100*len(train)/len(samples):.1f}%)")
    print(f"  Val: {len(val)} ({100*len(val)/len(samples):.1f}%)")
    print(f"  Test: {len(test)} ({100*len(test)/len(samples):.1f}%)")
    print(f"Output directory: {output_dir}")
    print("=" * 60)


def build_label_mappings(train_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Build comprehensive label mappings including per-tool intent indices and class weights."""
    
    # Tool mappings
    tool_to_idx = {"character_data": 0, "session_notes": 1, "rulebook": 2}
    idx_to_tool = {v: k for k, v in tool_to_idx.items()}
    
    # BIO tag mappings
    tag_to_idx = {
        "O": 0,
        "B-SPELL": 1, "I-SPELL": 2,
        "B-CLASS": 3, "I-CLASS": 4,
        "B-RACE": 5, "I-RACE": 6,
        "B-CREATURE": 7, "I-CREATURE": 8,
        "B-ITEM": 9, "I-ITEM": 10,
        "B-LOCATION": 11, "I-LOCATION": 12,
        "B-ABILITY": 13, "I-ABILITY": 14,
        "B-SKILL": 15, "I-SKILL": 16,
        "B-CONDITION": 17, "I-CONDITION": 18,
        "B-DAMAGE_TYPE": 19, "I-DAMAGE_TYPE": 20,
        "B-FEAT": 21, "I-FEAT": 22,
        "B-BACKGROUND": 23, "I-BACKGROUND": 24,
    }
    idx_to_tag = {v: k for k, v in tag_to_idx.items()}
    
    # Per-tool intent mappings (THIS IS THE KEY CHANGE)
    # Each tool has its own intent indices starting from 0
    character_intents = list(CHARACTER_TEMPLATES.keys())
    session_intents = list(SESSION_TEMPLATES.keys())
    rulebook_intents = list(RULEBOOK_TEMPLATES.keys())
    
    intent_to_idx_per_tool = {
        "character_data": {intent: i for i, intent in enumerate(character_intents)},
        "session_notes": {intent: i for i, intent in enumerate(session_intents)},
        "rulebook": {intent: i for i, intent in enumerate(rulebook_intents)},
    }
    
    idx_to_intent_per_tool = {
        "character_data": {i: intent for i, intent in enumerate(character_intents)},
        "session_notes": {i: intent for i, intent in enumerate(session_intents)},
        "rulebook": {i: intent for i, intent in enumerate(rulebook_intents)},
    }
    
    # Global intent mapping (for backward compatibility)
    all_intents = []
    intent_to_tool = {}
    for intent in character_intents:
        all_intents.append(intent)
        intent_to_tool[intent] = "character_data"
    for intent in session_intents:
        all_intents.append(intent)
        intent_to_tool[intent] = "session_notes"
    for intent in rulebook_intents:
        all_intents.append(intent)
        intent_to_tool[intent] = "rulebook"
    
    global_intent_to_idx = {intent: i for i, intent in enumerate(all_intents)}
    
    # Calculate class weights for imbalanced intents
    intent_weights = calculate_intent_weights(train_stats["intent_counts"])
    
    # Calculate NER tag weights
    ner_weights = calculate_ner_weights(train_stats["bio_tag_counts"], tag_to_idx)
    
    return {
        # Core mappings
        "tool_to_idx": tool_to_idx,
        "idx_to_tool": idx_to_tool,
        "tag_to_idx": tag_to_idx,
        "idx_to_tag": idx_to_tag,
        
        # Per-tool intent mappings (for Stage 2 gated prediction)
        "intent_to_idx_per_tool": intent_to_idx_per_tool,
        "idx_to_intent_per_tool": idx_to_intent_per_tool,
        
        # Intent counts per tool (for model architecture)
        "num_intents_per_tool": {
            "character_data": len(character_intents),
            "session_notes": len(session_intents),
            "rulebook": len(rulebook_intents),
        },
        
        # Global mappings (backward compatible)
        "intent_to_idx": global_intent_to_idx,
        "intent_to_tool": intent_to_tool,
        
        # Class weights for handling imbalance
        "intent_weights_per_tool": intent_weights,
        "ner_tag_weights": ner_weights,
        
        # Metadata
        "num_tools": len(tool_to_idx),
        "num_ner_tags": len(tag_to_idx),
        "total_intents": len(all_intents),
    }


def calculate_intent_weights(intent_counts: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    """Calculate class weights for imbalanced intents using inverse frequency."""
    weights = {}
    
    for tool, counts in intent_counts.items():
        if not counts:
            continue
            
        total = sum(counts.values())
        num_classes = len(counts)
        
        # Inverse frequency weighting: weight = total / (num_classes * count)
        tool_weights = {}
        for intent, count in counts.items():
            weight = total / (num_classes * count) if count > 0 else 1.0
            tool_weights[intent] = round(weight, 4)
        
        weights[tool] = tool_weights
    
    return weights


def calculate_ner_weights(bio_tag_counts: Dict[str, int], tag_to_idx: Dict[str, int]) -> Dict[str, float]:
    """Calculate class weights for NER tags (O tag is usually dominant)."""
    total = sum(bio_tag_counts.values())
    num_tags = len(tag_to_idx)
    
    weights = {}
    for tag in tag_to_idx.keys():
        count = bio_tag_counts.get(tag, 1)  # Avoid division by zero
        weight = total / (num_tags * count) if count > 0 else 1.0
        # Cap the weight to avoid extreme values for rare tags
        weights[tag] = round(min(weight, 10.0), 4)
    
    return weights


def validate_dataset(samples: List[Dict], label_mappings: Dict) -> bool:
    """Validate that all samples have correct structure and valid labels."""
    errors = []
    
    valid_tools = set(label_mappings["tool_to_idx"].keys())
    valid_tags = set(label_mappings["tag_to_idx"].keys())
    
    for i, sample in enumerate(samples):
        # Check tools
        for tool in sample["tools"]:
            if tool not in valid_tools:
                errors.append(f"Sample {i}: Invalid tool '{tool}'")
        
        # Check intents map to correct tools
        for tool, intent in sample["intents"].items():
            if tool not in valid_tools:
                errors.append(f"Sample {i}: Intent for invalid tool '{tool}'")
            elif intent not in label_mappings["intent_to_idx_per_tool"].get(tool, {}):
                errors.append(f"Sample {i}: Invalid intent '{intent}' for tool '{tool}'")
        
        # Check BIO tags
        for tag in sample["bio_tags"]:
            if tag not in valid_tags:
                errors.append(f"Sample {i}: Invalid BIO tag '{tag}'")
        
        # Check entity spans align with BIO tags
        words = sample["query"].split()
        if len(words) != len(sample["bio_tags"]):
            errors.append(f"Sample {i}: Word count ({len(words)}) != tag count ({len(sample['bio_tags'])})")
        
        # Check entity positions
        for entity in sample["entities"]:
            if entity["start"] < 0 or entity["end"] > len(words):
                errors.append(f"Sample {i}: Entity '{entity['text']}' has invalid span [{entity['start']}, {entity['end']})")
    
    if errors:
        print(f"  Found {len(errors)} validation errors:")
        for error in errors[:10]:  # Show first 10
            print(f"    - {error}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")
        return False
    else:
        print("  ✓ All samples validated successfully")
        return True


if __name__ == "__main__":
    main()
