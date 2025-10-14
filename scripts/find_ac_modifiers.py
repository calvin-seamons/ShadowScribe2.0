"""Find all AC modifiers in character JSON"""
import json

with open("DNDBEYONDEXAMPLE.json", encoding='utf-8') as f:
    data = json.load(f)

modifiers = data['data'].get('modifiers', {})

print("=== ALL AC MODIFIERS ===\n")

for category in ['race', 'class', 'background', 'item', 'feat']:
    mod_list = modifiers.get(category, [])
    if isinstance(mod_list, list):
        for mod in mod_list:
            if (mod.get('type') == 'bonus' and 
                mod.get('subType') == 'armor-class'):
                is_granted = mod.get('isGranted', False)
                value = mod.get('value', 0)
                component_id = mod.get('componentId', 'unknown')
                
                print(f"Category: {category}")
                print(f"  Value: +{value}")
                print(f"  Component ID: {component_id}")
                print(f"  Is Granted: {is_granted}")
                print()
