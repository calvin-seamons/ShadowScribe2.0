"""Quick debug script to check AC calculation"""
import json
from pathlib import Path

json_file = Path("DNDBEYONDEXAMPLE.json")
with open(json_file, encoding='utf-8') as f:
    data = json.load(f)

inventory = data['data'].get('inventory', [])

print("=== EQUIPPED ITEMS WITH AC ===")
for item in inventory:
    if item.get('equipped'):
        item_def = item.get('definition', {})
        item_ac = item_def.get('armorClass')
        if item_ac:
            name = item_def.get('name', 'Unknown')
            item_type = item_def.get('type', 'Unknown')
            filter_type = item_def.get('filterType', '')
            armor_type_id = item_def.get('armorTypeId')
            print(f"\n{name}:")
            print(f"  Type: {item_type}")
            print(f"  Filter: {filter_type}")
            print(f"  ArmorTypeId: {armor_type_id}")
            print(f"  AC: {item_ac}")
            
            # Check for granted modifiers
            mods = item_def.get('grantedModifiers', [])
            for mod in mods:
                if mod.get('subType') == 'armor-class':
                    print(f"  AC Modifier: +{mod.get('value', 0)}")

print("\n\n=== CALCULATING AC ===")
armor_ac = None
shield_ac = 0
ac_bonuses = 0

for item in inventory:
    if not item.get('equipped'):
        continue
        
    item_def = item.get('definition', {})
    item_ac = item_def.get('armorClass')
    
    if not item_ac:
        continue
    
    name = item_def.get('name', 'Unknown')
    armor_type = item_def.get('type') or ''
    filter_type = item_def.get('filterType') or ''
    armor_type_id = item_def.get('armorTypeId')
    
    if armor_type == 'Shield' or (filter_type == 'Armor' and armor_type_id == 4):
        print(f"Shield identified: {name} (+{item_ac})")
        shield_ac += item_ac
    elif armor_ac is None:
        print(f"Body armor identified: {name} (AC {item_ac})")
        armor_ac = item_ac
        
    # Check for AC bonuses
    mods = item_def.get('grantedModifiers', [])
    for mod in mods:
        if mod.get('subType') == 'armor-class' and mod.get('isGranted'):
            bonus = mod.get('value', 0)
            print(f"AC bonus from {name}: +{bonus}")
            ac_bonuses += bonus

base_ac = armor_ac if armor_ac else 10
total_ac = base_ac + shield_ac + ac_bonuses
print(f"\nFinal calculation:")
print(f"  Base armor AC: {base_ac}")
print(f"  Shield AC: +{shield_ac}")
print(f"  Magic bonuses: +{ac_bonuses}")
print(f"  TOTAL: {total_ac}")
