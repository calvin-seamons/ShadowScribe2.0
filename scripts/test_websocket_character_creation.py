#!/usr/bin/env python3
"""
WebSocket test client for character creation endpoint.

This script tests the /ws/character/create WebSocket endpoint by:
1. Connecting to the WebSocket
2. Sending a create_character message with a D&D Beyond URL
3. Receiving and displaying real-time progress events
4. Verifying the final character data is complete
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any

import websockets


class CharacterCreationClient:
    """WebSocket client for character creation testing."""
    
    def __init__(self, ws_url: str = "ws://localhost:8000/ws/character/create"):
        """Initialize the client with WebSocket URL."""
        self.ws_url = ws_url
        self.events = []
        self.character_data = None
        
    async def connect_and_create(self, url: str):
        """
        Connect to WebSocket and create character from URL.
        
        Args:
            url: D&D Beyond character URL
        """
        print("\n" + "="*80)
        print("CHARACTER CREATION VIA WEBSOCKET")
        print("="*80)
        print(f"WebSocket URL: {self.ws_url}")
        print(f"Character URL: {url}")
        print("\nConnecting to WebSocket...")
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                print("✓ Connected!")
                
                # Send create_character message
                print(f"\nSending create_character message...")
                await websocket.send(json.dumps({
                    'type': 'create_character',
                    'url': url
                }))
                print("✓ Message sent!")
                
                # Receive and process events
                print("\n" + "-"*80)
                print("PROGRESS EVENTS")
                print("-"*80)
                
                async for message in websocket:
                    event = json.loads(message)
                    self.events.append(event)
                    
                    await self.handle_event(event)
                    
                    # Stop if we get creation_complete or creation_error
                    if event['type'] in ['creation_complete', 'creation_error']:
                        break
                
                print("-"*80)
                
        except websockets.exceptions.WebSocketException as e:
            print(f"\n❌ WebSocket error: {e}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    async def handle_event(self, event: Dict[str, Any]):
        """Handle and display a progress event."""
        event_type = event['type']
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if event_type == 'fetch_started':
            print(f"[{timestamp}] 📥 Fetching character {event['character_id']} from D&D Beyond...")
        
        elif event_type == 'fetch_complete':
            print(f"[{timestamp}] ✓  Fetch complete: {event['character_name']}")
        
        elif event_type == 'parser_started':
            print(f"[{timestamp}] ⏳ [{event['completed']}/{event['total']}] Starting {event['parser']}...")
        
        elif event_type == 'parser_complete':
            time_ms = event.get('execution_time_ms', 0)
            print(f"[{timestamp}] ✓  [{event['completed']}/{event['total']}] "
                  f"{event['parser'].capitalize()} complete ({time_ms:.0f}ms)")
        
        elif event_type == 'parser_error':
            print(f"[{timestamp}] ❌ {event['parser'].capitalize()} failed: {event['error']}")
        
        elif event_type == 'assembly_started':
            print(f"[{timestamp}] 🔧 Assembling character object...")
        
        elif event_type == 'creation_complete':
            print(f"[{timestamp}] ✅ Character creation complete!")
            print(f"              Character: {event['character_name']}")
            if 'total_time_ms' in event:
                print(f"              Total time: {event['total_time_ms']:.0f}ms")
            # Store character data - check both possible keys
            if 'character' in event:
                self.character_data = event['character']
            elif 'character_summary' in event:
                self.character_data = event['character_summary']
            
            # Debug: print available keys
            if not self.character_data:
                print(f"              Available keys: {list(event.keys())}")
        
        elif event_type == 'creation_error':
            print(f"[{timestamp}] ❌ Character creation failed: {event['error']}")
    
    def print_summary(self):
        """Print summary of the character creation process."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        # Count event types
        event_counts = {}
        for event in self.events:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        print("\nEvent counts:")
        for event_type, count in sorted(event_counts.items()):
            print(f"  {event_type}: {count}")
        
        # Verify all parsers completed
        parser_complete = [e for e in self.events if e['type'] == 'parser_complete']
        print(f"\nParsers completed: {len(parser_complete)}/6")
        
        if len(parser_complete) == 6:
            print("  ✓ All parsers completed successfully")
            
            # Show parser times
            print("\n  Parser execution times:")
            for event in sorted(parser_complete, key=lambda e: e['execution_time_ms'], reverse=True):
                print(f"    {event['parser']}: {event['execution_time_ms']:.0f}ms")
        else:
            print("  ⚠️  Not all parsers completed")
        
        # Character data verification
        if self.character_data:
            print("\n" + "-"*80)
            print("CHARACTER DATA VERIFICATION")
            print("-"*80)
            
            # Handle both full character dict and summary
            if 'character_base' in self.character_data:
                # Full character dict
                char_base = self.character_data.get('character_base', {})
                combat = self.character_data.get('combat_stats', {})
                abilities = self.character_data.get('ability_scores', {})
            else:
                # Summary format
                char_base = self.character_data
                combat = self.character_data
                abilities = {}
            
            print(f"\n✓ Character Name: {char_base.get('name', 'Unknown')}")
            print(f"✓ Race: {char_base.get('race', 'Unknown')}")
            print(f"✓ Class: {char_base.get('character_class', 'Unknown')}")
            print(f"✓ Level: {char_base.get('total_level') or char_base.get('level', 0)}")
            print(f"✓ HP: {combat.get('max_hp') or combat.get('hp', 0)}")
            print(f"✓ AC: {combat.get('armor_class') or combat.get('ac', 0)}")
            
            if abilities:
                print(f"\nAbility Scores:")
                print(f"  STR: {abilities.get('strength', 0)}")
                print(f"  DEX: {abilities.get('dexterity', 0)}")
                print(f"  CON: {abilities.get('constitution', 0)}")
                print(f"  INT: {abilities.get('intelligence', 0)}")
                print(f"  WIS: {abilities.get('wisdom', 0)}")
                print(f"  CHA: {abilities.get('charisma', 0)}")
            
            # Check optional modules (only for full character dict)
            if 'character_base' in self.character_data:
                has_inventory = self.character_data.get('inventory') is not None
                has_spells = self.character_data.get('spell_list') is not None
                has_actions = self.character_data.get('action_economy') is not None
                has_features = self.character_data.get('features_and_traits') is not None
                
                print(f"\nOptional Modules:")
                print(f"  Inventory: {'✓' if has_inventory else '✗'}")
                print(f"  Spells: {'✓' if has_spells else '✗'}")
                print(f"  Actions: {'✓' if has_actions else '✗'}")
                print(f"  Features: {'✓' if has_features else '✗'}")
                
                all_modules = has_inventory and has_spells and has_actions and has_features
            else:
                all_modules = True  # Summary format doesn't have modules
            
            # Determine if test passed
            all_parsers = len(parser_complete) == 6
            
            print("\n" + "="*80)
            if all_modules and all_parsers:
                print("✅ TEST PASSED")
                print("="*80)
                print("✓ WebSocket connection successful")
                print("✓ Character creation message sent")
                print("✓ All progress events received")
                print("✓ All 6 parsers completed")
                print("✓ Character data complete")
                print("="*80)
                return True
            else:
                print("⚠️  TEST INCOMPLETE")
                print("="*80)
                if not all_parsers:
                    print(f"✗ Only {len(parser_complete)}/6 parsers completed")
                if not all_modules:
                    print("✗ Some character modules missing")
                print("="*80)
                return False
        else:
            print("\n❌ No character data received")
            return False


async def test_character_creation(url: str):
    """Test character creation via WebSocket."""
    client = CharacterCreationClient()
    success = await client.connect_and_create(url)
    
    if success:
        return client.print_summary()
    else:
        print("\n❌ Test failed - unable to complete character creation")
        return False


async def test_with_json(json_file: str):
    """Test character creation with pre-loaded JSON file."""
    print("\n" + "="*80)
    print("CHARACTER CREATION VIA WEBSOCKET (JSON FILE)")
    print("="*80)
    
    # Load JSON file
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    
    print(f"Loaded JSON file: {json_file}")
    print(f"Character: {json_data.get('data', {}).get('name', 'Unknown')}")
    
    ws_url = "ws://localhost:8000/ws/character/create"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("\n✓ Connected to WebSocket")
            
            # Send create_character message with JSON data
            print("Sending create_character message with JSON data...")
            await websocket.send(json.dumps({
                'type': 'create_character',
                'json_data': json_data
            }))
            
            print("\nProgress events:")
            print("-"*80)
            
            # Receive events
            async for message in websocket:
                event = json.loads(message)
                event_type = event['type']
                
                if event_type == 'parser_started':
                    print(f"  ⏳ [{event['completed']}/{event['total']}] {event['parser']}")
                elif event_type == 'parser_complete':
                    print(f"  ✓  [{event['completed']}/{event['total']}] {event['parser']} ({event['execution_time_ms']:.0f}ms)")
                elif event_type == 'creation_complete':
                    print(f"  ✅ Complete: {event['character_name']}")
                    break
                elif event_type == 'creation_error':
                    print(f"  ❌ Error: {event['error']}")
                    break
            
            print("-"*80)
            print("\n✅ Test complete!")
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_websocket_character_creation.py <dndbeyond_url>")
        print("  python test_websocket_character_creation.py --json <json_file>")
        print("\nExample:")
        print("  python scripts/test_websocket_character_creation.py https://www.dndbeyond.com/characters/152248393")
        print("  python scripts/test_websocket_character_creation.py --json /tmp/nikolai_dragovich.json")
        sys.exit(1)
    
    if sys.argv[1] == "--json":
        if len(sys.argv) < 3:
            print("Error: JSON file path required")
            sys.exit(1)
        success = asyncio.run(test_with_json(sys.argv[2]))
    else:
        success = asyncio.run(test_character_creation(sys.argv[1]))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
