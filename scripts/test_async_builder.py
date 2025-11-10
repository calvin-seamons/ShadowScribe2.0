#!/usr/bin/env python3
"""
Test script for async character builder with detailed timing analysis.

This script tests the async character builder and verifies that all parsers
run in parallel, providing real-time progress updates.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.character_creation.async_character_builder import AsyncCharacterBuilder


class ProgressTracker:
    """Track and display progress events with detailed timing."""
    
    def __init__(self):
        self.events = []
        self.start_time = None
        self.parser_starts = {}
        
    async def handle_progress(self, event: Dict[str, Any]):
        """Handle progress event and store for analysis."""
        if self.start_time is None:
            self.start_time = time.time()
        
        # Store event with timestamp
        event_with_time = {
            **event,
            'timestamp': time.time() - self.start_time
        }
        self.events.append(event_with_time)
        
        # Display event
        event_type = event['type']
        timestamp = event_with_time['timestamp']
        
        if event_type == 'parser_started':
            self.parser_starts[event['parser']] = timestamp
            print(f"  [{timestamp:6.2f}s] ⏳ Starting {event['parser']}...")
        
        elif event_type == 'parser_complete':
            start_time = self.parser_starts.get(event['parser'], 0)
            duration = timestamp - start_time
            print(f"  [{timestamp:6.2f}s] ✓  {event['parser'].capitalize()} complete "
                  f"({event['execution_time_ms']:.0f}ms)")
        
        elif event_type == 'parser_error':
            print(f"  [{timestamp:6.2f}s] ✗  {event['parser'].capitalize()} failed: {event['error']}")
        
        elif event_type == 'assembly_started':
            print(f"  [{timestamp:6.2f}s] 🔧 Assembling character object...")
        
        elif event_type == 'creation_complete':
            print(f"  [{timestamp:6.2f}s] ✓  Character creation complete!")
    
    def print_analysis(self):
        """Print detailed timing analysis."""
        print("\n" + "="*80)
        print("PARALLEL EXECUTION ANALYSIS")
        print("="*80)
        
        # Find parser start and complete events
        parser_starts = {}
        parser_completes = {}
        
        for event in self.events:
            if event['type'] == 'parser_started':
                parser_starts[event['parser']] = event['timestamp']
            elif event['type'] == 'parser_complete':
                parser_completes[event['parser']] = event['timestamp']
        
        # Calculate overlap
        print("\nParser Execution Timeline:")
        print("-" * 80)
        print(f"{'Parser':<15} {'Start (s)':<12} {'End (s)':<12} {'Duration (ms)':<15}")
        print("-" * 80)
        
        parsers = sorted(parser_starts.keys(), key=lambda p: parser_starts[p])
        for parser in parsers:
            start = parser_starts[parser]
            end = parser_completes[parser]
            duration = (end - start) * 1000
            print(f"{parser:<15} {start:>8.3f}     {end:>8.3f}     {duration:>10.0f}")
        
        # Check for parallel execution
        print("\n" + "-" * 80)
        print("Parallel Execution Verification:")
        print("-" * 80)
        
        # All parsers should start within ~50ms of each other
        start_times = list(parser_starts.values())
        if start_times:
            min_start = min(start_times)
            max_start = max(start_times)
            start_spread = (max_start - min_start) * 1000
            
            print(f"  All parsers started within: {start_spread:.0f}ms")
            
            if start_spread < 100:
                print(f"  ✓ PASS: Parsers started nearly simultaneously (parallel execution confirmed)")
            else:
                print(f"  ⚠ WARNING: Large start time spread may indicate sequential execution")
        
        # Calculate overlap percentage
        if parser_starts and parser_completes:
            total_sequential_time = sum(
                (parser_completes[p] - parser_starts[p]) * 1000
                for p in parser_starts.keys()
            )
            
            actual_wall_time = (max(parser_completes.values()) - min(parser_starts.values())) * 1000
            
            speedup = total_sequential_time / actual_wall_time
            
            print(f"\n  Sequential execution time: {total_sequential_time:.0f}ms")
            print(f"  Actual wall-clock time:    {actual_wall_time:.0f}ms")
            print(f"  Speedup factor:            {speedup:.2f}x")
            
            if speedup >= 2.0:
                print(f"  ✓ EXCELLENT: Significant parallel speedup achieved!")
            elif speedup >= 1.5:
                print(f"  ✓ GOOD: Moderate parallel speedup achieved")
            else:
                print(f"  ⚠ WARNING: Limited parallel speedup")
        
        print("="*80)


async def test_with_url(url: str):
    """Test async builder by fetching character from URL."""
    import httpx
    
    print("\n" + "="*80)
    print("ASYNC CHARACTER BUILDER - COMPREHENSIVE TEST")
    print("="*80)
    print(f"Fetching character from: {url}")
    
    # Fetch character data
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:8000/api/characters/fetch",
            json={"url": url}
        )
        response.raise_for_status()
        data = response.json()
        json_data = data['json_data']
        character_id = data['character_id']
    
    print(f"Character ID: {character_id}")
    print(f"JSON size: {len(json.dumps(json_data))} bytes")
    print("\n" + "-"*80)
    print("Starting async build with progress tracking...")
    print("-"*80 + "\n")
    
    # Create progress tracker
    tracker = ProgressTracker()
    
    # Build character
    builder = AsyncCharacterBuilder(json_data)
    character = await builder.build_async(progress_callback=tracker.handle_progress)
    
    # Print analysis
    tracker.print_analysis()
    
    # Print character summary
    print("\n" + "="*80)
    print("CHARACTER SUMMARY")
    print("="*80)
    print(f"Name: {character.character_base.name}")
    print(f"Race: {character.character_base.race}")
    print(f"Class: {character.character_base.character_class}")
    print(f"Level: {character.character_base.total_level}")
    print(f"Background: {character.character_base.background}")
    print(f"Alignment: {character.character_base.alignment}")
    
    print(f"\nHP: {character.combat_stats.max_hp}")
    print(f"AC: {character.combat_stats.armor_class}")
    print(f"Initiative: +{character.combat_stats.initiative_bonus}")
    print(f"Speed: {character.combat_stats.speed} ft")
    
    print("\nAbility Scores:")
    print(f"  STR: {character.ability_scores.strength}")
    print(f"  DEX: {character.ability_scores.dexterity}")
    print(f"  CON: {character.ability_scores.constitution}")
    print(f"  INT: {character.ability_scores.intelligence}")
    print(f"  WIS: {character.ability_scores.wisdom}")
    print(f"  CHA: {character.ability_scores.charisma}")
    
    if character.features_and_traits:
        total_features = sum(
            len(features)
            for levels in character.features_and_traits.class_features.values()
            for features in levels.values()
        )
        print(f"\nFeatures: {total_features} class features, "
              f"{len(character.features_and_traits.racial_traits)} racial traits, "
              f"{len(character.features_and_traits.feats)} feats")
    
    if character.action_economy:
        print(f"\nActions: {len(character.action_economy.actions)} total actions")
        print(f"Attacks per action: {character.action_economy.attacks_per_action}")
    
    if character.inventory:
        equipped = sum(len(items) for items in character.inventory.equipped_items.values())
        backpack = len(character.inventory.backpack)
        print(f"\nInventory: {equipped + backpack} items "
              f"({equipped} equipped, {backpack} in backpack)")
        print(f"Total weight: {character.inventory.total_weight} {character.inventory.weight_unit}")
    
    if character.spell_list:
        total_spells = sum(
            len(spells)
            for class_spells in character.spell_list.spells.values()
            for spells in class_spells.values()
        )
        print(f"\nSpells: {total_spells} spells known")
        for class_name, spellcasting_info in character.spell_list.spellcasting.items():
            print(f"  {class_name}: DC {spellcasting_info.spell_save_dc}, "
                  f"+{spellcasting_info.spell_attack_bonus} to hit")
    
    print("\n" + "="*80)
    print("✓ TEST COMPLETE - Async builder working correctly!")
    print("="*80)


async def test_with_file(json_file: str):
    """Test async builder with local JSON file."""
    print("\n" + "="*80)
    print("ASYNC CHARACTER BUILDER - FILE TEST")
    print("="*80)
    print(f"Input file: {json_file}")
    
    # Load JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print(f"JSON size: {len(json.dumps(json_data))} bytes")
    print("\n" + "-"*80)
    print("Starting async build with progress tracking...")
    print("-"*80 + "\n")
    
    # Create progress tracker
    tracker = ProgressTracker()
    
    # Build character
    builder = AsyncCharacterBuilder(json_data)
    character = await builder.build_async(progress_callback=tracker.handle_progress)
    
    # Print analysis
    tracker.print_analysis()
    
    print("\n✓ Character built: " + character.character_base.name)


async def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_async_builder.py <path_to_json>")
        print("  python test_async_builder.py --url <dndbeyond_url>")
        sys.exit(1)
    
    if sys.argv[1] == "--url":
        if len(sys.argv) < 3:
            print("Error: URL required after --url flag")
            sys.exit(1)
        await test_with_url(sys.argv[2])
    else:
        await test_with_file(sys.argv[1])


if __name__ == "__main__":
    asyncio.run(main())
