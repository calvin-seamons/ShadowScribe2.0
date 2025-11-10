#!/usr/bin/env python3
"""
Test script for D&D Beyond character fetcher service.

This script tests the POST /api/characters/fetch endpoint that extracts
character IDs from D&D Beyond URLs and fetches the complete character JSON.
"""

import requests
import json


def test_fetch_character(url: str):
    """Test fetching a character from D&D Beyond URL."""
    api_url = "http://localhost:8000/api/characters/fetch"
    
    print(f"\n{'='*80}")
    print(f"Testing URL: {url}")
    print('='*80)
    
    try:
        response = requests.post(
            api_url,
            json={"url": url},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            character_id = data['character_id']
            character_data = data['json_data']['data']
            
            print(f"\n✅ SUCCESS!")
            print(f"Character ID: {character_id}")
            print(f"Name: {character_data['name']}")
            print(f"Race: {character_data['race']['fullName']}")
            
            classes = ', '.join([
                f"{c['definition']['name']} {c['level']}" 
                for c in character_data['classes']
            ])
            total_level = sum([c['level'] for c in character_data['classes']])
            
            print(f"Classes: {classes}")
            print(f"Total Level: {total_level}")
            print(f"JSON Size: {len(json.dumps(data['json_data']))} bytes")
            
            # Show sample data structure
            print(f"\nData Structure Keys:")
            print(f"  - ID: {character_data['id']}")
            print(f"  - User ID: {character_data['userId']}")
            print(f"  - Read-only URL: {character_data['readonlyUrl']}")
            print(f"  - Has decorations: {bool(character_data.get('decorations'))}")
            print(f"  - Has stats: {bool(character_data.get('stats'))}")
            print(f"  - Has inventory: {bool(character_data.get('inventory'))}")
            print(f"  - Has spells: {bool(character_data.get('spells'))}")
            
            return True
        else:
            error_data = response.json()
            print(f"\n❌ ERROR!")
            print(f"Detail: {error_data.get('detail', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST FAILED!")
        print(f"Error: {str(e)}")
        return False


def main():
    """Run tests."""
    print("\n" + "="*80)
    print("D&D BEYOND CHARACTER FETCHER - TEST SUITE")
    print("="*80)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Character (Nikolai Dragovich)",
            "url": "https://www.dndbeyond.com/characters/152248393",
            "expected": "success"
        },
        {
            "name": "Invalid URL Format",
            "url": "https://www.example.com/invalid",
            "expected": "error"
        },
        {
            "name": "Non-existent Character ID",
            "url": "https://www.dndbeyond.com/characters/999999999999",
            "expected": "error"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n\nTest: {test_case['name']}")
        print("-" * 80)
        success = test_fetch_character(test_case['url'])
        results.append({
            'name': test_case['name'],
            'success': success,
            'expected': test_case['expected']
        })
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for result in results:
        status = "✅ PASS" if result['success'] == (result['expected'] == 'success') else "❌ FAIL"
        print(f"{status} - {result['name']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
