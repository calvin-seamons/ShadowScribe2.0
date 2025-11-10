"""
Test script for Character CRUD API endpoints.

Tests POST, PUT, and PATCH endpoints with real character data.
"""
import sys
from pathlib import Path
import json
import asyncio
from dataclasses import asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx

from src.utils.character_manager import CharacterManager
from src.rag.character.character_types import Character


BASE_URL = "http://localhost:8000/api"


async def test_create_character():
    """Test POST /api/characters endpoint."""
    print("\n" + "="*60)
    print("TEST 1: POST /api/characters - Create New Character")
    print("="*60)
    
    # Load a test character
    manager = CharacterManager()
    characters = manager.list_saved_characters()
    
    if not characters:
        print("❌ No saved characters found. Run character builder first.")
        return None
    
    character_name = characters[0]
    print(f"Loading test character: {character_name}")
    character = manager.load_character(character_name)
    
    # Convert to dict
    character_dict = asdict(character)
    
    # Convert datetime objects to strings
    def serialize_datetime(obj):
        """Recursively convert datetime objects to ISO strings."""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [serialize_datetime(v) for v in obj]
        return obj
    
    character_dict = serialize_datetime(character_dict)
    
    # Make API request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/characters",
                json={"character": character_dict},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Character created successfully")
                print(f"   ID: {data['id']}")
                print(f"   Name: {data['name']}")
                print(f"   Race: {data.get('race', 'N/A')}")
                print(f"   Class: {data.get('character_class', 'N/A')}")
                print(f"   Level: {data.get('level', 'N/A')}")
                print(f"   Created: {data.get('created_at', 'N/A')}")
                return data['id']
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return None
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None


async def test_get_character(character_id: str):
    """Test GET /api/characters/{id} endpoint."""
    print("\n" + "="*60)
    print(f"TEST 2: GET /api/characters/{character_id}")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/characters/{character_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Character retrieved successfully")
                print(f"   ID: {data['id']}")
                print(f"   Name: {data['name']}")
                print(f"   Has ability_scores: {'ability_scores' in data['data']}")
                print(f"   Has inventory: {'inventory' in data['data']}")
                print(f"   Has spell_list: {'spell_list' in data['data']}")
                return data
            else:
                print(f"❌ Failed with status {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None


async def test_patch_section(character_id: str, section: str, data: dict):
    """Test PATCH /api/characters/{id}/{section} endpoint."""
    print("\n" + "="*60)
    print(f"TEST 3: PATCH /api/characters/{character_id}/{section}")
    print("="*60)
    
    print(f"Updating {section} with data:")
    print(json.dumps(data, indent=2))
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{BASE_URL}/characters/{character_id}/{section}",
                json={"data": data},
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Section updated successfully")
                print(f"   Updated: {result['updated']}")
                print(f"   Section: {result['section']}")
                print(f"   Message: {result.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False


async def test_put_character(character_id: str, character_data: dict):
    """Test PUT /api/characters/{id} endpoint."""
    print("\n" + "="*60)
    print(f"TEST 4: PUT /api/characters/{character_id} - Full Update")
    print("="*60)
    
    # Modify some data to verify update
    character_data['data']['character_base']['total_level'] = 99
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{BASE_URL}/characters/{character_id}",
                json={"character": character_data['data']},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Character updated successfully")
                print(f"   ID: {data['id']}")
                print(f"   Name: {data['name']}")
                print(f"   Level: {data.get('level', 'N/A')} (should be 99)")
                print(f"   Updated: {data.get('updated_at', 'N/A')}")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False


async def test_invalid_section(character_id: str):
    """Test PATCH with invalid section name."""
    print("\n" + "="*60)
    print(f"TEST 5: PATCH /api/characters/{character_id}/invalid_section")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{BASE_URL}/characters/{character_id}/invalid_section",
                json={"data": {"test": "data"}},
                timeout=10.0
            )
            
            if response.status_code == 400:
                print(f"✅ Correctly rejected invalid section")
                print(f"   Error: {response.json().get('detail', 'N/A')}")
                return True
            else:
                print(f"❌ Unexpected status {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False


async def test_delete_character(character_id: str):
    """Test DELETE /api/characters/{id} endpoint."""
    print("\n" + "="*60)
    print(f"TEST 6: DELETE /api/characters/{character_id}")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{BASE_URL}/characters/{character_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Character deleted successfully")
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   ID: {data.get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CHARACTER CRUD ENDPOINTS TEST SUITE")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    
    # Track test results
    results = {
        'passed': 0,
        'failed': 0,
        'total': 6
    }
    
    # Test 1: Create character
    character_id = await test_create_character()
    if character_id:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n❌ Cannot continue tests without character ID")
        return
    
    # Test 2: Get character
    character_data = await test_get_character(character_id)
    if character_data:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: Patch section (ability scores)
    ability_scores_update = {
        "strength": 20,
        "dexterity": 18,
        "constitution": 16,
        "intelligence": 14,
        "wisdom": 12,
        "charisma": 10
    }
    if await test_patch_section(character_id, "ability_scores", ability_scores_update):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Verify the patch worked
    print("\nVerifying section update...")
    updated_char = await test_get_character(character_id)
    if updated_char:
        ability_scores = updated_char['data'].get('ability_scores', {})
        if ability_scores.get('strength') == 20:
            print("✅ Section update verified (STR = 20)")
        else:
            print(f"❌ Section update failed (STR = {ability_scores.get('strength')})")
    
    # Test 4: Put character (full update)
    if character_data:
        if await test_put_character(character_id, character_data):
            results['passed'] += 1
        else:
            results['failed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: Invalid section
    if await test_invalid_section(character_id):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 6: Delete character
    if await test_delete_character(character_id):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    print(f"Success Rate: {(results['passed']/results['total'])*100:.1f}%")
    
    if results['passed'] == results['total']:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
