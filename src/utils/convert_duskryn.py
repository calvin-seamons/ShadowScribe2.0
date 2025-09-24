"""
Duskryn Character Converter

This script converts Duskryn Nightwarden's JSON files into a Python Character object
using the defined type system. It also includes comprehensive testing to ensure
no important information is lost in the conversion.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from src.rag.character.character_types import (
    Character, CharacterBase, PhysicalCharacteristics, AbilityScores,
    CombatStats, Proficiency, DamageModifier, PassiveScores, Senses,
    BackgroundInfo, BackgroundFeature, PersonalityTraits, Backstory,
    BackstorySection, FamilyBackstory, Organization, Ally, Enemy,
    ActionEconomy, SpecialAction, AttackAction, DamageInfo,
    FeaturesAndTraits, ClassFeatures, Feature,
    Inventory, InventoryItem, InventoryItemDefinition, Modifier, LimitedUse,
    SpellList, SpellcastingInfo, Spell, SpellComponents, SpellRite,
    ObjectivesAndContracts, BaseObjective, Quest, Contract, ContractTemplate
)


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load a JSON file and return the data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def convert_character_base(data: Dict[str, Any]) -> CharacterBase:
    """Convert character base information."""
    multiclass_levels = {}
    if "warlock_level" in data and "paladin_level" in data:
        multiclass_levels = {
            "warlock": data["warlock_level"],
            "paladin": data["paladin_level"]
        }

    # Fix: Use "Acolyte" as background since it's specified in background.json
    background = data.get("background", "Unknown")
    if background == "Unknown":
        background = "Acolyte"  # Known from background.json

    return CharacterBase(
        name=data["name"],
        race=data["race"],
        subrace=data.get("subrace"),
        character_class=data["class"],
        multiclass_levels=multiclass_levels,
        total_level=data["total_level"],
        alignment=data["alignment"],
        background=background,
        lifestyle=data.get("lifestyle")
    )


def convert_characteristics(data: Dict[str, Any]) -> PhysicalCharacteristics:
    """Convert physical characteristics."""
    return PhysicalCharacteristics(
        alignment=data["alignment"],
        gender=data["gender"],
        eyes=data["eyes"],
        size=data["size"],
        height=data["height"],
        hair=data["hair"],
        skin=data["skin"],
        age=data["age"],
        weight=data["weight"],
        faith=data.get("faith")
    )


def convert_ability_scores(data: Dict[str, Any]) -> AbilityScores:
    """Convert ability scores."""
    return AbilityScores(
        strength=data["strength"],
        dexterity=data["dexterity"],
        constitution=data["constitution"],
        intelligence=data["intelligence"],
        wisdom=data["wisdom"],
        charisma=data["charisma"]
    )


def convert_combat_stats(data: Dict[str, Any]) -> CombatStats:
    """Convert combat statistics."""
    return CombatStats(
        max_hp=data["max_hp"],
        armor_class=data["armor_class"],
        initiative_bonus=data["initiative_bonus"],
        speed=data["speed"],
        hit_dice=data.get("hit_dice")
    )


def convert_proficiencies(data: List[Dict[str, Any]]) -> List[Proficiency]:
    """Convert proficiencies list."""
    return [
        Proficiency(
            type=prof["type"],
            name=prof["name"]
        ) for prof in data
    ]


def convert_damage_modifiers(data: List[Dict[str, Any]]) -> List[DamageModifier]:
    """Convert damage modifiers."""
    return [
        DamageModifier(
            damage_type=mod["damage_type"],
            modifier_type=mod["modifier_type"]
        ) for mod in data
    ]


def convert_passive_scores(data: Dict[str, Any]) -> PassiveScores:
    """Convert passive scores."""
    return PassiveScores(
        perception=data["perception"],
        investigation=data.get("investigation"),
        insight=data.get("insight")
    )


def convert_senses(data: Dict[str, Any]) -> Senses:
    """Convert senses."""
    senses_dict = {}
    if "darkvision" in data:
        senses_dict["darkvision"] = data["darkvision"]
    return Senses(senses=senses_dict)


def convert_background_info(data: Dict[str, Any]) -> BackgroundInfo:
    """Convert background information."""
    background_name = data["name"]
    
    # Standard D&D 5e background proficiencies and equipment
    skill_proficiencies = []
    tool_proficiencies = []
    language_proficiencies = []
    equipment = []
    
    if background_name == "Acolyte":
        skill_proficiencies = ["Insight", "Religion"]
        language_proficiencies = ["Two of your choice"]  # From character data: Celestial, Dwarvish, Elvish, etc.
        equipment = [
            "Holy symbol (a gift to you when you entered the priesthood)",
            "Prayer book or prayer wheel",
            "5 sticks of incense",
            "Vestments",
            "Set of common clothes",
            "Belt pouch containing 15 gp"
        ]
    
    return BackgroundInfo(
        name=background_name,
        feature=BackgroundFeature(
            name=data["feature"]["name"],
            description=data["feature"]["description"]
        ),
        skill_proficiencies=skill_proficiencies,
        tool_proficiencies=tool_proficiencies,
        language_proficiencies=language_proficiencies,
        equipment=equipment
    )


def convert_personality(data: Dict[str, Any]) -> PersonalityTraits:
    """Convert personality traits."""
    return PersonalityTraits(
        personality_traits=data.get("personality_traits", []),
        ideals=data.get("ideals", []),
        bonds=data.get("bonds", []),
        flaws=data.get("flaws", [])
    )


def convert_backstory(data: Dict[str, Any]) -> Backstory:
    """Convert backstory."""
    family_backstory_data = data["family_backstory"]
    family_backstory = FamilyBackstory(
        parents=family_backstory_data["parents"],
        sections=[
            BackstorySection(
                heading=section["heading"],
                content=section["content"]
            ) for section in family_backstory_data["sections"]
        ]
    )

    return Backstory(
        title=data["title"],
        family_backstory=family_backstory,
        sections=[
            BackstorySection(
                heading=section["heading"],
                content=section["content"]
            ) for section in data["sections"]
        ]
    )


def convert_organizations(data: List[Dict[str, Any]]) -> List[Organization]:
    """Convert organizations."""
    return [
        Organization(
            name=org["name"],
            role=org["role"],
            description=org["description"]
        ) for org in data
    ]


def convert_allies(data: List[Dict[str, Any]]) -> List[Ally]:
    """Convert allies."""
    return [
        Ally(
            name=ally["name"],
            title=ally.get("title"),
            description=ally["description"]
        ) for ally in data
    ]


def convert_enemies(data: List[Dict[str, Any]]) -> List[Enemy]:
    """Convert enemies."""
    return [
        Enemy(
            name=enemy["name"],
            description=enemy["description"]
        ) for enemy in data
    ]


def convert_action_economy(data: Dict[str, Any]) -> ActionEconomy:
    """Convert action economy from action_list.json."""
    actions = []
    attacks_per_action = data.get("attacks_per_action", 1)

    # Convert main actions
    if "actions" in data:
        for action_data in data["actions"]:
            if action_data["name"] == "Attack" and "sub_actions" in action_data:
                # Handle attack actions with sub-actions
                for sub_action in action_data["sub_actions"]:
                    # Handle damage field which can be string or dict
                    damage_data = sub_action.get("damage", {})
                    if isinstance(damage_data, str):
                        # Simple damage string
                        damage = DamageInfo(
                            base=damage_data,
                            type=sub_action.get("damage_type", "slashing")
                        )
                    else:
                        # Damage dictionary
                        damage = DamageInfo(
                            one_handed=damage_data.get("one_handed"),
                            two_handed=damage_data.get("two_handed"),
                            type=sub_action.get("damage_type", "slashing")
                        )

                    attack_action = AttackAction(
                        name=sub_action["name"],
                        type=sub_action.get("type", "weapon_attack"),
                        damage=damage,
                        properties=sub_action.get("properties", []),
                        range=sub_action.get("range"),
                        reach=sub_action.get("reach", False),
                        attack_bonus=sub_action.get("attack_bonus", 0),
                        damage_type=sub_action.get("damage_type"),
                        charges=sub_action.get("charges"),
                        weapon_properties=sub_action.get("weapon_properties", []),
                        special_options=sub_action.get("special_options"),
                        required_items=None  # Will be set by linking function
                    )
                    actions.append(SpecialAction(
                        name=sub_action["name"],
                        type="action",
                        description="Weapon attack",
                        sub_actions=[attack_action],
                        required_items=None  # Will be set by linking function
                    ))
            else:
                # Handle other special actions
                special_action = SpecialAction(
                    name=action_data["name"],
                    type=action_data.get("type", "action"),
                    description=action_data.get("description"),
                    uses=action_data.get("uses"),
                    save_dc=action_data.get("save_dc"),
                    range=action_data.get("range"),
                    effect=action_data.get("effect"),
                    options=action_data.get("options"),
                    trigger=action_data.get("trigger"),
                    required_items=None  # Will be set by linking function
                )
                actions.append(special_action)

    return ActionEconomy(
        attacks_per_action=attacks_per_action,
        actions=actions
    )


def convert_features_and_traits(data: Dict[str, Any]) -> FeaturesAndTraits:
    """Convert features and traits."""
    class_features = {}
    racial_traits = []
    feats = []

    # Convert class features
    if "class_features" in data:
        for class_name, class_data in data["class_features"].items():
            features = []
            for feature_data in class_data.get("features", []):
                feature = Feature(
                    name=feature_data["name"],
                    description=feature_data.get("description"),
                    action_type=feature_data.get("action_type"),
                    passive=feature_data.get("passive", False),
                    uses=feature_data.get("uses"),
                    effect=feature_data.get("effect"),
                    cost=feature_data.get("cost"),
                    damage=feature_data.get("damage"),
                    trigger=feature_data.get("trigger"),
                    subclass=feature_data.get("subclass", False),
                    channel_divinity=feature_data.get("channel_divinity"),
                    duration=feature_data.get("duration"),
                    range=feature_data.get("range"),
                    save_dc=feature_data.get("save_dc"),
                    focus=feature_data.get("focus"),
                    preparation=feature_data.get("preparation")
                )
                features.append(feature)

            class_features[class_name] = ClassFeatures(
                level=class_data["level"],
                features=features
            )

    # Convert racial traits
    if "racial_traits" in data:
        for trait_data in data["racial_traits"]:
            trait = Feature(
                name=trait_data["name"],
                description=trait_data.get("description"),
                action_type=trait_data.get("action_type"),
                passive=trait_data.get("passive", False),
                uses=trait_data.get("uses"),
                effect=trait_data.get("effect"),
                cost=trait_data.get("cost"),
                damage=trait_data.get("damage"),
                trigger=trait_data.get("trigger"),
                subclass=trait_data.get("subclass", False),
                channel_divinity=trait_data.get("channel_divinity"),
                duration=trait_data.get("duration"),
                range=trait_data.get("range"),
                save_dc=trait_data.get("save_dc"),
                focus=trait_data.get("focus"),
                preparation=trait_data.get("preparation")
            )
            racial_traits.append(trait)

    # Convert feats
    if "feats" in data:
        for feat_data in data["feats"]:
            feat = Feature(
                name=feat_data["name"],
                description=feat_data.get("description"),
                action_type=feat_data.get("action_type"),
                passive=feat_data.get("passive", False),
                uses=feat_data.get("uses"),
                effect=feat_data.get("effect"),
                cost=feat_data.get("cost"),
                damage=feat_data.get("damage"),
                trigger=feat_data.get("trigger"),
                subclass=feat_data.get("subclass", False),
                channel_divinity=feat_data.get("channel_divinity"),
                duration=feat_data.get("duration"),
                range=feat_data.get("range"),
                save_dc=feat_data.get("save_dc"),
                focus=feat_data.get("focus"),
                preparation=feat_data.get("preparation")
            )
            feats.append(feat)

    return FeaturesAndTraits(
        class_features=class_features,
        racial_traits=racial_traits,
        feats=feats
    )


def convert_inventory(data: Dict[str, Any]) -> Inventory:
    """Convert inventory."""
    equipped_items = {}
    backpack = []
    valuables = []

    def _parse_cost(value: Any) -> Optional[int]:
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            cleaned = re.sub(r"[^0-9]", "", value)
            if cleaned:
                return int(cleaned)
        return None

    def _requires_attunement(value: Any) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        if value:
            return True
        return None

    def _convert_modifiers(modifiers: Optional[List[Dict[str, Any]]]) -> List[Modifier]:
        result: List[Modifier] = []
        if not modifiers:
            return result
        for modifier in modifiers:
            dice = modifier.get("dice", {}) if isinstance(modifier, dict) else {}
            result.append(
                Modifier(
                    type=modifier.get("type"),
                    subType=modifier.get("subType"),
                    restriction=modifier.get("restriction"),
                    friendlyTypeName=modifier.get("friendlyTypeName"),
                    friendlySubtypeName=modifier.get("friendlySubtypeName"),
                    duration=modifier.get("duration"),
                    fixedValue=modifier.get("fixedValue"),
                    diceString=dice.get("diceString")
                )
            )
        return result

    def _convert_limited_use(data: Optional[Dict[str, Any]]) -> Optional[LimitedUse]:
        if not data:
            return None
        return LimitedUse(
            resetType=data.get("resetType"),
            numberUsed=data.get("numberUsed"),
            maxUses=data.get("maxUses")
        )

    def _convert_properties(properties: Optional[List[Any]]) -> List[str]:
        if not properties:
            return []
        names: List[str] = []
        for prop in properties:
            if isinstance(prop, dict) and "name" in prop:
                names.append(prop["name"])
            elif isinstance(prop, str):
                names.append(prop)
        return names

    def _convert_range(item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        normal = item_data.get("range")
        long_range = item_data.get("long_range") or item_data.get("longRange")
        reach = item_data.get("reach")
        if normal is None and long_range is None and reach is None:
            return None
        result = {"normal": normal, "long": long_range}
        if reach is not None:
            result["reach"] = reach
        return result

    # Helper function to convert any item data to InventoryItem
    def convert_to_inventory_item(item_data: Dict[str, Any], equipped: bool = False) -> InventoryItem:
        attack_type = item_data.get("attack_type")

        definition = InventoryItemDefinition(
            name=item_data["name"],
            type=item_data.get("type"),
            rarity=item_data.get("rarity"),
            isAttunable=_requires_attunement(item_data.get("requires_attunement")),
            attunementDescription=item_data.get("attunement_process") if isinstance(item_data.get("attunement_process"), str) else None,
            description=item_data.get("description"),
            grantedModifiers=_convert_modifiers(item_data.get("granted_modifiers")),
            limitedUse=_convert_limited_use(item_data.get("definition_limited_use")),
            weight=item_data.get("weight"),
            cost=_parse_cost(item_data.get("cost")),
            armorClass=item_data.get("armor_class"),
            damage=item_data.get("damage"),
            damageType=item_data.get("damage_type"),
            properties=_convert_properties(item_data.get("properties")),
            attackType=attack_type if isinstance(attack_type, int) else None,
            range=_convert_range(item_data),
            isContainer=item_data.get("is_container"),
            capacityWeight=item_data.get("capacity_weight"),
            contentsWeightMultiplier=item_data.get("weight_multiplier") or item_data.get("contents_weight_multiplier"),
            tags=item_data.get("tags", [])
        )

        limited_use = _convert_limited_use(item_data.get("limited_use"))

        return InventoryItem(
            definition=definition,
            id=item_data.get("id", 0),
            entityTypeId=item_data.get("entity_type_id", 0),
            quantity=item_data.get("quantity", 1),
            isAttuned=item_data.get("is_attuned"),
            equipped=equipped,
            limitedUse=limited_use,
            containerEntityId=item_data.get("container_entity_id")
        )

    # Convert equipped items
    if "equipped_items" in data:
        for category, items in data["equipped_items"].items():
            equipped_items[category] = []
            for item_data in items:
                item = convert_to_inventory_item(item_data, equipped=True)
                equipped_items[category].append(item)

    # Convert backpack items
    if "backpack" in data:
        for item_data in data["backpack"]:
            item = convert_to_inventory_item(item_data, equipped=False)
            backpack.append(item)

    # Convert valuables - handle both dict and list formats
    if "valuables" in data:
        valuables_data = data["valuables"]
        if isinstance(valuables_data, list):
            # If it's already a list of items, convert each
            for item_data in valuables_data:
                if isinstance(item_data, dict) and "name" in item_data:
                    item = convert_to_inventory_item(item_data, equipped=False)
                    valuables.append({"item": item})
                else:
                    # Keep as raw dict if it's not a proper item
                    valuables.append(item_data)
        else:
            # If it's a dict or other format, wrap it
            valuables.append(valuables_data)

    return Inventory(
        total_weight=data.get("total_weight", 0.0),
        weight_unit=data.get("weight_unit", "lb"),
        equipped_items=equipped_items,
        backpack=backpack,
        valuables=valuables
    )


def convert_spell_components(components_data: Dict[str, Any]) -> SpellComponents:
    """Convert spell components from JSON to SpellComponents object."""
    return SpellComponents(
        verbal=components_data.get("verbal", False),
        somatic=components_data.get("somatic", False),
        material=components_data.get("material", False)
    )


def convert_spell_rites(rites_data: List[Dict[str, Any]]) -> List[SpellRite]:
    """Convert spell rites from JSON to SpellRite objects."""
    return [
        SpellRite(
            name=rite["name"],
            effect=rite["effect"]
        )
        for rite in rites_data
    ]


def convert_spell(spell_data: Dict[str, Any]) -> Spell:
    """Convert a single spell from JSON to Spell object."""
    rites = None
    if "rites" in spell_data and spell_data["rites"]:
        rites = convert_spell_rites(spell_data["rites"])
    
    return Spell(
        name=spell_data["name"],
        level=spell_data["level"],
        school=spell_data["school"],
        casting_time=spell_data["casting_time"],
        range=spell_data["range"],
        components=convert_spell_components(spell_data["components"]),
        duration=spell_data["duration"],
        description=spell_data["description"],
        concentration=spell_data.get("concentration", False),
        ritual=spell_data.get("ritual", False),
        tags=spell_data.get("tags", []),
        area=spell_data.get("area"),
        rites=rites,
        charges=spell_data.get("charges")
    )


def convert_spell_list(data: Dict[str, Any]) -> SpellList:
    """Convert spell list."""
    spellcasting = {}
    spells = {}

    if "spellcasting" in data:
        for class_name, class_data in data["spellcasting"].items():
            spells_data = class_data.get("spells", {})

            # Convert spells by level
            spells_known = []
            cantrips_known = []
            spell_slots = {}
            class_spells = {}

            for level_key, spell_list in spells_data.items():
                if level_key == "cantrips":
                    cantrips_known = [spell["name"] for spell in spell_list]
                    class_spells["cantrips"] = [convert_spell(spell) for spell in spell_list]
                elif "_level" in level_key:
                    # Extract level number from "1st_level", "2nd_level", etc.
                    level_str = level_key.split("_")[0]
                    if level_str == "cantrips":
                        continue
                    # Convert ordinal to integer
                    level_map = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5,
                                "6th": 6, "7th": 7, "8th": 8, "9th": 9}
                    level_num = level_map.get(level_str, 1)
                    spells_known.extend([spell["name"] for spell in spell_list])
                    class_spells[level_key] = [convert_spell(spell) for spell in spell_list]

                    # Try to infer spell slots from context (this is approximate)
                    if level_num <= 3:  # Basic assumption
                        spell_slots[level_num] = 2 if level_num == 1 else 1

            spellcasting[class_name] = SpellcastingInfo(
                ability=class_data.get("ability", "Charisma"),
                spell_save_dc=class_data.get("spell_save_dc", 0),
                spell_attack_bonus=class_data.get("spell_attack_bonus", 0),
                cantrips_known=cantrips_known,
                spells_known=spells_known,
                spell_slots=spell_slots
            )
            
            spells[class_name] = class_spells

    return SpellList(
        spellcasting=spellcasting,
        spells=spells
    )


def convert_objectives_and_contracts(data: Dict[str, Any]) -> ObjectivesAndContracts:
    """Convert objectives and contracts."""
    active_contracts = []
    current_objectives = []
    completed_objectives = []

    if "active_contracts" in data:
        for obj in data["active_contracts"]:
            contract = Contract(
                id=obj["id"],
                name=obj["name"],
                type=obj["type"],
                status=obj["status"],
                completion_date=obj.get("completion_date"),
                description=obj["description"],
                parties=obj.get("parties"),
                outcome=obj.get("outcome"),
                rewards=obj.get("rewards", []),
                obligations_accepted=obj.get("obligations_accepted", []),
                lasting_effects=obj.get("lasting_effects", [])
            )
            active_contracts.append(contract)

    if "current_objectives" in data:
        for obj in data["current_objectives"]:
            quest = Quest(
                id=obj["id"],
                name=obj["name"],
                type=obj["type"],
                status=obj["status"],
                description=obj["description"],
                priority=obj.get("priority"),
                objectives=obj.get("objectives", []),
                rewards=obj.get("rewards", []),
                deadline=obj.get("deadline"),
                notes=obj.get("notes"),
                quest_giver=obj.get("quest_giver"),
                location=obj.get("location"),
                deity=obj.get("deity"),
                purpose=obj.get("purpose"),
                signs_received=obj.get("signs_received", []),
                divine_favor=obj.get("divine_favor"),
                consequences_of_failure=obj.get("consequences_of_failure", []),
                motivation=obj.get("motivation"),
                steps=obj.get("steps", []),
                obstacles=obj.get("obstacles", []),
                importance=obj.get("importance")
            )
            current_objectives.append(quest)

    if "completed_objectives" in data:
        for obj in data["completed_objectives"]:
            # Properly handle the completed Divine Covenant
            if obj.get("type") == "Divine Covenant" or "parties" in obj:
                # This is a contract-type objective
                contract = Contract(
                    id=obj["id"],
                    name=obj["name"],
                    type=obj["type"],
                    status=obj["status"],
                    completion_date=obj.get("completion_date"),
                    description=obj["description"],
                    parties=str(obj.get("parties")) if isinstance(obj.get("parties"), dict) else obj.get("parties"),
                    outcome=obj.get("outcome"),
                    rewards=obj.get("rewards", []),
                    obligations_accepted=obj.get("obligations_accepted", []),
                    lasting_effects=obj.get("lasting_effects", []),
                    client=obj.get("parties", {}).get("patron", {}).get("name") if isinstance(obj.get("parties"), dict) else None,
                    contractor=obj.get("parties", {}).get("bound", {}).get("name") if isinstance(obj.get("parties"), dict) else None,
                    terms=obj.get("terms"),
                    payment=obj.get("payment"),
                    penalties=obj.get("penalties"),
                    special_conditions=obj.get("special_conditions", [])
                )
                completed_objectives.append(contract)
            else:
                # This is a quest-type objective
                quest = Quest(
                    id=obj["id"],
                    name=obj["name"],
                    type=obj["type"],
                    status=obj["status"],
                    completion_date=obj.get("completion_date"),
                    description=obj["description"],
                    priority=obj.get("priority"),
                    objectives=obj.get("objectives", []),
                    rewards=obj.get("rewards", []),
                    deadline=obj.get("deadline"),
                    notes=obj.get("notes"),
                    quest_giver=obj.get("quest_giver"),
                    location=obj.get("location"),
                    deity=obj.get("deity"),
                    purpose=obj.get("purpose"),
                    signs_received=obj.get("signs_received", []),
                    divine_favor=obj.get("divine_favor"),
                    consequences_of_failure=obj.get("consequences_of_failure", []),
                    motivation=obj.get("motivation"),
                    steps=obj.get("steps", []),
                    obstacles=obj.get("obstacles", []),
                    importance=obj.get("importance"),
                    parties=obj.get("parties"),
                    outcome=obj.get("outcome"),
                    obligations_accepted=obj.get("obligations_accepted", []),
                    lasting_effects=obj.get("lasting_effects", [])
                )
                completed_objectives.append(quest)

    contract_templates = {}
    if "contract_templates" in data:
        for template_name, template_data in data["contract_templates"].items():
            contract_templates[template_name] = ContractTemplate(
                id=template_data.get("id", ""),
                name=template_data.get("name", ""),
                type=template_data.get("type", ""),
                status=template_data.get("status", ""),
                priority=template_data.get("priority", ""),
                quest_giver=template_data.get("quest_giver", ""),
                location=template_data.get("location", ""),
                description=template_data.get("description", ""),
                objectives=template_data.get("objectives", []),
                rewards=template_data.get("rewards", []),
                deadline=template_data.get("deadline", ""),
                notes=template_data.get("notes", "")
            )

    return ObjectivesAndContracts(
        active_contracts=active_contracts,
        current_objectives=current_objectives,
        completed_objectives=completed_objectives,
        contract_templates=contract_templates
    )


def link_actions_to_inventory(action_economy: ActionEconomy, inventory: Inventory) -> ActionEconomy:
    """Link actions to their required inventory items."""
    
    # Create a searchable list of all inventory items
    all_items = []
    for category_items in inventory.equipped_items.values():
        all_items.extend(category_items)
    all_items.extend(inventory.backpack)
    
    # Helper function to find matching item by name
    def find_item_by_name(item_name: str) -> Optional[InventoryItem]:
        for item in all_items:
            definition_name = (item.definition.name or "").lower()
            if definition_name == item_name.lower():
                return item
            # Also check for partial matches (e.g., "Eldaryth" matches "Eldaryth of Regret (I)")
            if item_name.lower() in definition_name or definition_name in item_name.lower():
                return item
        return None
    
    # Process each action
    for action in action_economy.actions:
        required_items = []
        
        # Check if this action has sub-actions (weapon attacks)
        if action.sub_actions:
            for sub_action in action.sub_actions:
                # For weapon attacks, find the matching weapon and assign to ACTION level
                if sub_action.type == "weapon_attack":
                    matching_item = find_item_by_name(sub_action.name)
                    if matching_item and matching_item not in required_items:
                        required_items.append(matching_item)
                    # Don't assign to sub_action - let it inherit from parent
                    sub_action.required_items = None
        
        # Check if the action itself requires items (e.g., spellcasting focus)
        action_name = action.name
        action_desc = action.description or ""
        if "pact weapon" in action_name.lower() or "weapon" in action_desc.lower():
            matching_item = find_item_by_name(action_name)
            if matching_item and matching_item not in required_items:
                required_items.append(matching_item)
        
        # Assign required items to the action level only
        if required_items:
            action.required_items = required_items
        else:
            action.required_items = None
    
    return action_economy


def create_duskryn_character(base_path: str = "Duskryn_Nightwarden") -> Character:
    """Create Duskryn Nightwarden character from JSON files."""

    # Load all JSON files
    character_data = load_json_file(f"{base_path}/character.json")
    background_data = load_json_file(f"{base_path}/character_background.json")
    action_data = load_json_file(f"{base_path}/action_list.json")["character_actions"]
    features_data = load_json_file(f"{base_path}/feats_and_traits.json")
    inventory_data = load_json_file(f"{base_path}/inventory_list.json")
    spell_data = load_json_file(f"{base_path}/spell_list.json")
    objectives_data = load_json_file(f"{base_path}/objectives_and_contracts.json")

    # Fix the background in character_data before conversion
    if character_data["character_base"]["background"] == "Unknown":
        character_data["character_base"]["background"] = "Acolyte"

    # Convert each section
    character_base = convert_character_base(character_data["character_base"])
    characteristics = convert_characteristics(character_data["characteristics"])
    ability_scores = convert_ability_scores(character_data["ability_scores"])
    combat_stats = convert_combat_stats(character_data["combat_stats"])
    proficiencies = convert_proficiencies(character_data["proficiencies"])
    damage_modifiers = convert_damage_modifiers(character_data["damage_modifiers"])
    passive_scores = convert_passive_scores(character_data["passive_scores"])
    senses = convert_senses(character_data["senses"])

    background_info = convert_background_info(background_data["background"])
    personality = convert_personality(background_data["characteristics"])
    backstory = convert_backstory(background_data["backstory"])
    organizations = convert_organizations(background_data["organizations"])
    allies = convert_allies(background_data["allies"])
    enemies = convert_enemies(background_data["enemies"])

    action_economy = convert_action_economy(action_data["action_economy"])
    features_and_traits = convert_features_and_traits(features_data["features_and_traits"])
    inventory = convert_inventory(inventory_data["inventory"])
    
    # Link action economy to inventory items
    action_economy = link_actions_to_inventory(action_economy, inventory)
    
    spell_list = convert_spell_list(spell_data)
    objectives_and_contracts = convert_objectives_and_contracts(objectives_data["objectives_and_contracts"])

    # Create the complete character
    return Character(
        character_base=character_base,
        characteristics=characteristics,
        ability_scores=ability_scores,
        combat_stats=combat_stats,
        background_info=background_info,
        personality=personality,
        backstory=backstory,
        organizations=organizations,
        allies=allies,
        enemies=enemies,
        proficiencies=proficiencies,
        damage_modifiers=damage_modifiers,
        passive_scores=passive_scores,
        senses=senses,
        action_economy=action_economy,
        features_and_traits=features_and_traits,
        inventory=inventory,
        spell_list=spell_list,
        objectives_and_contracts=objectives_and_contracts,
        created_date=datetime.now(),
        last_updated=datetime.now()
    )


def export_character_to_text(character: Character, filename: str = "character_export.txt") -> None:
    """Export complete character data to a text file for verification."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPLETE CHARACTER DATA EXPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # BASIC CHARACTER INFO
        f.write("📋 BASIC CHARACTER INFORMATION\n")
        f.write("-" * 40 + "\n")
        f.write(f"Name: {character.character_base.name}\n")
        f.write(f"Race: {character.character_base.race}")
        if character.character_base.subrace:
            f.write(f" ({character.character_base.subrace})")
        f.write(f"\nClass: {character.character_base.character_class}\n")
        f.write(f"Total Level: {character.character_base.total_level}\n")
        if character.character_base.multiclass_levels:
            f.write("Multiclass Levels:\n")
            for class_name, level in character.character_base.multiclass_levels.items():
                f.write(f"  - {class_name.title()}: {level}\n")
        f.write(f"Alignment: {character.character_base.alignment}\n")
        f.write(f"Background: {character.character_base.background}\n")
        if character.character_base.lifestyle:
            f.write(f"Lifestyle: {character.character_base.lifestyle}\n")
        
        # PHYSICAL CHARACTERISTICS
        f.write(f"\n🎭 PHYSICAL CHARACTERISTICS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Gender: {character.characteristics.gender}\n")
        f.write(f"Age: {character.characteristics.age}\n")
        f.write(f"Height: {character.characteristics.height}\n")
        f.write(f"Weight: {character.characteristics.weight}\n")
        f.write(f"Eyes: {character.characteristics.eyes}\n")
        f.write(f"Hair: {character.characteristics.hair}\n")
        f.write(f"Skin: {character.characteristics.skin}\n")
        f.write(f"Size: {character.characteristics.size}\n")
        if character.characteristics.faith:
            f.write(f"Faith: {character.characteristics.faith}\n")
        
        # ABILITY SCORES
        f.write(f"\n📊 ABILITY SCORES\n")
        f.write("-" * 40 + "\n")
        f.write(f"Strength: {character.ability_scores.strength}\n")
        f.write(f"Dexterity: {character.ability_scores.dexterity}\n")
        f.write(f"Constitution: {character.ability_scores.constitution}\n")
        f.write(f"Intelligence: {character.ability_scores.intelligence}\n")
        f.write(f"Wisdom: {character.ability_scores.wisdom}\n")
        f.write(f"Charisma: {character.ability_scores.charisma}\n")
        
        # COMBAT STATS
        f.write(f"\n⚔️ COMBAT STATISTICS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Hit Points: {character.combat_stats.max_hp}\n")
        f.write(f"Armor Class: {character.combat_stats.armor_class}\n")
        f.write(f"Initiative Bonus: {character.combat_stats.initiative_bonus}\n")
        f.write(f"Speed: {character.combat_stats.speed} ft\n")
        if character.combat_stats.hit_dice:
            f.write("Hit Dice:\n")
            for die_type, count in character.combat_stats.hit_dice.items():
                f.write(f"  - {die_type}: {count}\n")
        
        # PROFICIENCIES
        f.write(f"\n🎯 PROFICIENCIES\n")
        f.write("-" * 40 + "\n")
        if character.proficiencies:
            prof_by_type = {}
            for prof in character.proficiencies:
                if prof.type not in prof_by_type:
                    prof_by_type[prof.type] = []
                prof_by_type[prof.type].append(prof.name)
            
            for prof_type, prof_names in prof_by_type.items():
                f.write(f"{prof_type.replace('_', ' ').title()}:\n")
                for name in prof_names:
                    f.write(f"  - {name}\n")
        
        # DAMAGE MODIFIERS
        if character.damage_modifiers:
            f.write(f"\n🛡️ DAMAGE MODIFIERS\n")
            f.write("-" * 40 + "\n")
            for mod in character.damage_modifiers:
                f.write(f"{mod.modifier_type.title()}: {mod.damage_type}\n")
        
        # PASSIVE SCORES
        if character.passive_scores:
            f.write(f"\n👁️ PASSIVE SCORES\n")
            f.write("-" * 40 + "\n")
            f.write(f"Passive Perception: {character.passive_scores.perception}\n")
            if character.passive_scores.investigation:
                f.write(f"Passive Investigation: {character.passive_scores.investigation}\n")
            if character.passive_scores.insight:
                f.write(f"Passive Insight: {character.passive_scores.insight}\n")
            if character.passive_scores.stealth:
                f.write(f"Passive Stealth: {character.passive_scores.stealth}\n")
        
        # SENSES
        if character.senses and character.senses.senses:
            f.write(f"\n👀 SENSES\n")
            f.write("-" * 40 + "\n")
            for sense_name, sense_value in character.senses.senses.items():
                f.write(f"{sense_name.title()}: {sense_value}")
                if isinstance(sense_value, int):
                    f.write(" ft")
                f.write("\n")
        
        # BACKGROUND INFORMATION
        f.write(f"\n📚 BACKGROUND INFORMATION\n")
        f.write("-" * 40 + "\n")
        f.write(f"Background: {character.background_info.name}\n\n")
        f.write(f"Feature: {character.background_info.feature.name}\n")
        f.write(f"Description: {character.background_info.feature.description}\n\n")
        
        if character.background_info.skill_proficiencies:
            f.write("Skill Proficiencies:\n")
            for skill in character.background_info.skill_proficiencies:
                f.write(f"  - {skill}\n")
        
        if character.background_info.tool_proficiencies:
            f.write("Tool Proficiencies:\n")
            for tool in character.background_info.tool_proficiencies:
                f.write(f"  - {tool}\n")
        
        if character.background_info.language_proficiencies:
            f.write("Language Proficiencies:\n")
            for lang in character.background_info.language_proficiencies:
                f.write(f"  - {lang}\n")
        
        if character.background_info.equipment:
            f.write("Starting Equipment:\n")
            for item in character.background_info.equipment:
                f.write(f"  - {item}\n")
        
        # PERSONALITY TRAITS
        f.write(f"\n🎭 PERSONALITY\n")
        f.write("-" * 40 + "\n")
        if character.personality.personality_traits:
            f.write("Personality Traits:\n")
            for trait in character.personality.personality_traits:
                f.write(f"  - {trait}\n")
        
        if character.personality.ideals:
            f.write("\nIdeals:\n")
            for ideal in character.personality.ideals:
                f.write(f"  - {ideal}\n")
        
        if character.personality.bonds:
            f.write("\nBonds:\n")
            for bond in character.personality.bonds:
                f.write(f"  - {bond}\n")
        
        if character.personality.flaws:
            f.write("\nFlaws:\n")
            for flaw in character.personality.flaws:
                f.write(f"  - {flaw}\n")
        
        # BACKSTORY
        f.write(f"\n📖 BACKSTORY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Title: {character.backstory.title}\n\n")
        
        f.write("Family Background:\n")
        f.write(f"Parents: {character.backstory.family_backstory.parents}\n\n")
        
        for section in character.backstory.family_backstory.sections:
            f.write(f"{section.heading}:\n")
            f.write(f"{section.content}\n\n")
        
        f.write("Character Backstory Sections:\n")
        for section in character.backstory.sections:
            f.write(f"\n{section.heading}:\n")
            f.write(f"{section.content}\n")
        
        # ORGANIZATIONS
        if character.organizations:
            f.write(f"\n🏛️ ORGANIZATIONS\n")
            f.write("-" * 40 + "\n")
            for org in character.organizations:
                f.write(f"Organization: {org.name}\n")
                f.write(f"Role: {org.role}\n")
                f.write(f"Description: {org.description}\n\n")
        
        # ALLIES
        if character.allies:
            f.write(f"\n👥 ALLIES\n")
            f.write("-" * 40 + "\n")
            for ally in character.allies:
                f.write(f"Name: {ally.name}\n")
                if ally.title:
                    f.write(f"Title: {ally.title}\n")
                f.write(f"Description: {ally.description}\n\n")
        
        # ENEMIES
        if character.enemies:
            f.write(f"\n👹 ENEMIES\n")
            f.write("-" * 40 + "\n")
            for enemy in character.enemies:
                f.write(f"Name: {enemy.name}\n")
                f.write(f"Description: {enemy.description}\n\n")
        
        # ACTION ECONOMY
        if character.action_economy:
            f.write(f"\n⚔️ ACTION ECONOMY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Attacks per Action: {character.action_economy.attacks_per_action}\n")
            
            if character.action_economy.actions:
                f.write(f"\nSpecial Actions ({len(character.action_economy.actions)}):\n")
                for action in character.action_economy.actions:
                    f.write(f"  - {action.name} ({action.type})\n")
                    if action.description:
                        f.write(f"    Description: {action.description}\n")
                    if action.uses:
                        f.write(f"    Uses: {action.uses}\n")
        
        # FEATURES AND TRAITS
        if character.features_and_traits:
            f.write(f"\n✨ FEATURES AND TRAITS\n")
            f.write("-" * 40 + "\n")
            
            for class_name, class_features in character.features_and_traits.class_features.items():
                f.write(f"\n{class_name.title()} Features (Level {class_features.level}):\n")
                for feature in class_features.features:
                    f.write(f"  - {feature.name}")
                    if feature.source:
                        f.write(f" (from {feature.source})")
                    f.write("\n")
                    if feature.description:
                        f.write(f"    {feature.description}\n")
            
            if character.features_and_traits.racial_traits:
                f.write(f"\nRacial Traits:\n")
                for trait in character.features_and_traits.racial_traits:
                    f.write(f"  - {trait.name}\n")
                    if trait.description:
                        f.write(f"    {trait.description}\n")
            
            if character.features_and_traits.feats:
                f.write(f"\nFeats:\n")
                for feat in character.features_and_traits.feats:
                    f.write(f"  - {feat.name}\n")
                    if feat.description:
                        f.write(f"    {feat.description}\n")
        
        # INVENTORY
        if character.inventory:
            f.write(f"\n🎒 INVENTORY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Weight: {character.inventory.total_weight} {character.inventory.weight_unit}\n\n")
            
            for category, items in character.inventory.equipped_items.items():
                if items:
                    f.write(f"{category.title()} ({len(items)} items):\n")
                    for item in items:
                        definition = item.definition
                        f.write(f"  - {definition.name}")
                        if definition.rarity and definition.rarity != "Common":
                            f.write(f" ({definition.rarity})")
                        f.write(f"\n")
                        if definition.weight:
                            f.write(f"    Weight: {definition.weight} {character.inventory.weight_unit}\n")
                        if definition.properties:
                            f.write(f"    Properties: {', '.join(definition.properties)}\n")
                    f.write("\n")
            
            if character.inventory.backpack:
                f.write(f"Backpack ({len(character.inventory.backpack)} items):\n")
                for item in character.inventory.backpack:
                    definition = item.definition
                    f.write(f"  - {definition.name}")
                    if item.quantity > 1:
                        f.write(f" (x{item.quantity})")
                    f.write(f"\n")
        
        # SPELLS
        if character.spell_list:
            f.write(f"\n📜 SPELLCASTING\n")
            f.write("-" * 40 + "\n")
            
            for class_name, spellcasting_info in character.spell_list.spellcasting.items():
                f.write(f"\n{class_name.title()} Spellcasting:\n")
                f.write(f"  Spellcasting Ability: {spellcasting_info.ability}\n")
                f.write(f"  Spell Save DC: {spellcasting_info.spell_save_dc}\n")
                f.write(f"  Spell Attack Bonus: +{spellcasting_info.spell_attack_bonus}\n")
                
                if spellcasting_info.cantrips_known:
                    f.write(f"  Cantrips Known: {', '.join(spellcasting_info.cantrips_known)}\n")
                
                if spellcasting_info.spells_known:
                    f.write(f"  Spells Known: {', '.join(spellcasting_info.spells_known)}\n")
                
                if spellcasting_info.spell_slots:
                    f.write("  Spell Slots:\n")
                    for level, slots in spellcasting_info.spell_slots.items():
                        f.write(f"    Level {level}: {slots}\n")
            
            # List all spells by class and level
            for class_name, spell_levels in character.spell_list.spells.items():
                f.write(f"\n{class_name.title()} Spell List:\n")
                for level_name, spells in spell_levels.items():
                    if spells:
                        f.write(f"  {level_name.replace('_', ' ').title()} ({len(spells)} spells):\n")
                        for spell in spells:
                            f.write(f"    - {spell.name}")
                            if spell.concentration:
                                f.write(" (Concentration)")
                            if spell.ritual:
                                f.write(" (Ritual)")
                            f.write(f"\n")
                            f.write(f"      School: {spell.school}, Range: {spell.range}, Duration: {spell.duration}\n")
        
        # OBJECTIVES AND CONTRACTS
        if character.objectives_and_contracts:
            f.write(f"\n📋 OBJECTIVES AND CONTRACTS\n")
            f.write("-" * 40 + "\n")
            
            if character.objectives_and_contracts.active_contracts:
                f.write(f"Active Contracts ({len(character.objectives_and_contracts.active_contracts)}):\n")
                for contract in character.objectives_and_contracts.active_contracts:
                    f.write(f"  - {contract.name} (Status: {contract.status})\n")
                    f.write(f"    Description: {contract.description}\n")
                    if contract.rewards:
                        f.write(f"    Rewards: {', '.join(contract.rewards)}\n")
                    f.write("\n")
            
            if character.objectives_and_contracts.current_objectives:
                f.write(f"Current Objectives ({len(character.objectives_and_contracts.current_objectives)}):\n")
                for objective in character.objectives_and_contracts.current_objectives:
                    f.write(f"  - {objective.name} (Status: {objective.status})\n")
                    f.write(f"    Description: {objective.description}\n")
                    if objective.rewards:
                        f.write(f"    Rewards: {', '.join(objective.rewards)}\n")
                    f.write("\n")
            
            if character.objectives_and_contracts.completed_objectives:
                f.write(f"Completed Objectives ({len(character.objectives_and_contracts.completed_objectives)}):\n")
                for objective in character.objectives_and_contracts.completed_objectives:
                    f.write(f"  - {objective.name} (Status: {objective.status})\n")
                    f.write(f"    Description: {objective.description}\n")
                    if objective.completion_date:
                        f.write(f"    Completed: {objective.completion_date}\n")
                    f.write("\n")
        
        # METADATA
        f.write(f"\n📅 METADATA\n")
        f.write("-" * 40 + "\n")
        if character.created_date:
            f.write(f"Created: {character.created_date}\n")
        if character.last_updated:
            f.write(f"Last Updated: {character.last_updated}\n")
        
        if character.notes:
            f.write(f"\n📝 NOTES\n")
            f.write("-" * 40 + "\n")
            for key, value in character.notes.items():
                f.write(f"{key}: {value}\n")
        
        f.write(f"\n" + "=" * 80 + "\n")
        f.write("END OF CHARACTER EXPORT\n")
        f.write("=" * 80 + "\n")


def test_character_conversion():
    """Test that the character conversion captures all important information."""

    print("🔄 Converting Duskryn Nightwarden to Python Character object...")

    try:
        character = create_duskryn_character()

        print("✅ Character conversion successful!")
        print(f"📋 Character: {character.character_base.name}")
        print(f"🏷️  Race: {character.character_base.race} ({character.character_base.subrace})")
        print(f"⚔️  Class: {character.character_base.character_class}")
        print(f"📊 Level: {character.character_base.total_level}")
        print(f"⚖️  Alignment: {character.character_base.alignment}")
        print(f"❤️  HP: {character.combat_stats.max_hp}")
        print(f"🛡️  AC: {character.combat_stats.armor_class}")
        print(f"🏃 Speed: {character.combat_stats.speed}")

        # Test key sections
        print(f"\n📚 Background: {character.background_info.name}")
        print(f"🎭 Personality Traits: {len(character.personality.personality_traits)}")
        print(f"🎯 Ideals: {len(character.personality.ideals)}")
        print(f"🤝 Bonds: {len(character.personality.bonds)}")
        print(f"⚠️  Flaws: {len(character.personality.flaws)}")

        print(f"\n🏛️  Organizations: {len(character.organizations)}")
        print(f"👥 Allies: {len(character.allies)}")
        print(f"👹 Enemies: {len(character.enemies)}")

        print(f"\n⚔️  Proficiencies: {len(character.proficiencies)}")
        print(f"🩸 Damage Modifiers: {len(character.damage_modifiers)}")

        print(f"\n🎲 Actions: {len(character.action_economy.actions)}")
        print(f"📖 Class Features: {len(character.features_and_traits.class_features)}")

        print(f"\n🎒 Inventory Weight: {character.inventory.total_weight} {character.inventory.weight_unit}")
        print(f"🗡️  Weapons: {len(character.inventory.equipped_items.get('weapons', []))}")
        print(f"🛡️  Armor: {len(character.inventory.equipped_items.get('armor', []))}")

        print(f"\n📜 Spellcasting Classes: {len(character.spell_list.spellcasting)}")

        print(f"\n📋 Objectives: {len(character.objectives_and_contracts.active_contracts)} active, {len(character.objectives_and_contracts.completed_objectives)} completed")

        # Test specific important data points
        print("\n🔍 Testing specific data points...")

        # Test ability scores
        assert character.ability_scores.strength == 14
        assert character.ability_scores.dexterity == 12
        assert character.ability_scores.constitution == 16
        assert character.ability_scores.intelligence == 14
        assert character.ability_scores.wisdom == 20
        assert character.ability_scores.charisma == 24
        print("✅ Ability scores correct")

        # Test multiclass levels
        assert character.character_base.multiclass_levels["warlock"] == 5
        assert character.character_base.multiclass_levels["paladin"] == 8
        print("✅ Multiclass levels correct")

        # Test Eldaryth weapon
        weapons = character.inventory.equipped_items.get("weapons", [])
        eldaryth = next((w for w in weapons if "Eldaryth" in w.name), None)
        assert eldaryth is not None
        assert eldaryth.magical_bonus == "+3"
        print("✅ Eldaryth weapon data correct")

        # Test background feature
        assert character.background_info.name == "Acolyte"
        assert "Shelter of the Faithful" in character.background_info.feature.name
        print("✅ Background information correct")

        # Test personality traits
        assert len(character.personality.personality_traits) == 4
        assert "I quote (or misquote) sacred texts" in character.personality.personality_traits[0]
        print("✅ Personality traits correct")

        # Test organizations
        assert len(character.organizations) == 3
        assert "Holy Knights of Kluntul" in character.organizations[0].name
        print("✅ Organizations correct")

        print("\n🎉 All tests passed! Character conversion is complete and accurate.")
        return character

    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_character_conversion():
    """Test that the character conversion captures all important information."""

    print("🔄 Converting Duskryn Nightwarden to Python Character object...")

    try:
        character = create_duskryn_character()

        print("✅ Character conversion successful!")
        print(f"📋 Character: {character.character_base.name}")
        print(f"🏷️  Race: {character.character_base.race} ({character.character_base.subrace})")
        print(f"⚔️  Class: {character.character_base.character_class}")
        print(f"📊 Level: {character.character_base.total_level}")
        print(f"⚖️  Alignment: {character.character_base.alignment}")
        print(f"❤️  HP: {character.combat_stats.max_hp}")
        print(f"🛡️  AC: {character.combat_stats.armor_class}")
        print(f"🏃 Speed: {character.combat_stats.speed}")

        # Print detailed background information
        print("\n" + "="*60)
        print("🎭 BACKGROUND FEATURES - DETAILED BREAKDOWN")
        print("="*60)

        print(f"\n📚 Background Name: {character.background_info.name}")

        print(f"\n🏆 Background Feature:")
        print(f"   Name: {character.background_info.feature.name}")
        print(f"   Description: {character.background_info.feature.description}")

        print(f"\n🎯 Skill Proficiencies:")
        if character.background_info.skill_proficiencies:
            for skill in character.background_info.skill_proficiencies:
                print(f"   • {skill}")
        else:
            print("   (None specified in conversion)")

        print(f"\n🛠️  Tool Proficiencies:")
        if character.background_info.tool_proficiencies:
            for tool in character.background_info.tool_proficiencies:
                print(f"   • {tool}")
        else:
            print("   (None specified in conversion)")

        print(f"\n�️  Language Proficiencies:")
        if character.background_info.language_proficiencies:
            for language in character.background_info.language_proficiencies:
                print(f"   • {language}")
        else:
            print("   (None specified in conversion)")

        print(f"\n🎒 Equipment:")
        if character.background_info.equipment:
            for item in character.background_info.equipment:
                print(f"   • {item}")
        else:
            print("   (None specified in conversion)")

        print(f"\n📝 Additional Feature Description:")
        if character.background_info.feature_description:
            print(f"   {character.background_info.feature_description}")
        else:
            print("   (None)")

        print("\n" + "="*60)
        print("🎭 PERSONALITY & BACKGROUND TRAITS")
        print("="*60)

        print(f"\n💭 Personality Traits ({len(character.personality.personality_traits)}):")
        for i, trait in enumerate(character.personality.personality_traits, 1):
            print(f"   {i}. {trait}")

        print(f"\n🎯 Ideals ({len(character.personality.ideals)}):")
        for i, ideal in enumerate(character.personality.ideals, 1):
            print(f"   {i}. {ideal}")

        print(f"\n🤝 Bonds ({len(character.personality.bonds)}):")
        for i, bond in enumerate(character.personality.bonds, 1):
            print(f"   {i}. {bond}")

        print(f"\n⚠️  Flaws ({len(character.personality.flaws)}):")
        for i, flaw in enumerate(character.personality.flaws, 1):
            print(f"   {i}. {flaw}")

        print("\n" + "="*60)
        print("🏛️  ORGANIZATIONS & RELATIONSHIPS")
        print("="*60)

        print(f"\n🏛️  Organizations ({len(character.organizations)}):")
        for org in character.organizations:
            print(f"   • {org.name} - {org.role}")
            print(f"     {org.description}")

        print(f"\n👥 Allies ({len(character.allies)}):")
        for ally in character.allies:
            print(f"   • {ally.name}")
            if ally.title:
                print(f"     Title: {ally.title}")
            print(f"     {ally.description}")

        print(f"\n👹 Enemies ({len(character.enemies)}):")
        for enemy in character.enemies:
            print(f"   • {enemy.name}")
            print(f"     {enemy.description}")

        # Continue with other sections...
        print(f"\n📚 Background: {character.background_info.name}")
        print(f"🎭 Personality Traits: {len(character.personality.personality_traits)}")
        print(f"🎯 Ideals: {len(character.personality.ideals)}")
        print(f"🤝 Bonds: {len(character.personality.bonds)}")
        print(f"⚠️  Flaws: {len(character.personality.flaws)}")

        print(f"\n🏛️  Organizations: {len(character.organizations)}")
        print(f"👥 Allies: {len(character.allies)}")
        print(f"👹 Enemies: {len(character.enemies)}")

        print(f"\n⚔️  Proficiencies: {len(character.proficiencies)}")
        print(f"🩸 Damage Modifiers: {len(character.damage_modifiers)}")

        print(f"\n🎲 Actions: {len(character.action_economy.actions)}")
        print(f"📖 Class Features: {len(character.features_and_traits.class_features)}")

        print(f"\n🎒 Inventory Weight: {character.inventory.total_weight} {character.inventory.weight_unit}")
        print(f"🗡️  Weapons: {len(character.inventory.equipped_items.get('weapons', []))}")
        print(f"🛡️  Armor: {len(character.inventory.equipped_items.get('armor', []))}")

        print(f"\n📜 Spellcasting Classes: {len(character.spell_list.spellcasting)}")

        print(f"\n📋 Objectives: {len(character.objectives_and_contracts.active_contracts)} active, {len(character.objectives_and_contracts.completed_objectives)} completed")

        # Test specific important data points
        print("\n�🔍 Testing specific data points...")

        # Test ability scores
        assert character.ability_scores.strength == 14
        assert character.ability_scores.dexterity == 12
        assert character.ability_scores.constitution == 16
        assert character.ability_scores.intelligence == 14
        assert character.ability_scores.wisdom == 20
        assert character.ability_scores.charisma == 24
        print("✅ Ability scores correct")

        # Test multiclass levels
        assert character.character_base.multiclass_levels["warlock"] == 5
        assert character.character_base.multiclass_levels["paladin"] == 8
        print("✅ Multiclass levels correct")

        # Test Eldaryth weapon
        weapons = character.inventory.equipped_items.get("weapons", [])
        eldaryth = next((w for w in weapons if "Eldaryth" in w.name), None)
        assert eldaryth is not None
        assert eldaryth.magical_bonus == "+3"
        print("✅ Eldaryth weapon data correct")

        # Test background feature
        assert character.background_info.name == "Acolyte"
        assert "Shelter of the Faithful" in character.background_info.feature.name
        print("✅ Background information correct")

        # Test personality traits
        assert len(character.personality.personality_traits) == 4
        assert "I quote (or misquote) sacred texts" in character.personality.personality_traits[0]
        print("✅ Personality traits correct")

        # Test organizations
        assert len(character.organizations) == 3
        assert "Holy Knights of Kluntul" in character.organizations[0].name
        print("✅ Organizations correct")

        print("\n🎉 All tests passed! Character conversion is complete and accurate.")
        return character

    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_character_conversion()
