Collecting workspace information# CHARACTER_EXTRACTION_API_SCHEMAS.md

## LLM Character Extraction Tool Functions

Complete schema definitions for all 14 parallel extraction tasks using LLM tool calling to convert OCR'd character sheet markdown into structured `Character` dataclass components.

---

## T1: Extract Character Base

**Tool Function Name**: `extract_character_base`

**Purpose**: Extract core character identity information

**Schema**:
```json
{
  "name": "extract_character_base",
  "description": "Extract basic character information including name, race, class, level, and background",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Character's full name"
      },
      "race": {
        "type": "string",
        "description": "Character's race (e.g., 'Human', 'Elf', 'Dwarf')"
      },
      "subrace": {
        "type": ["string", "null"],
        "description": "Character's subrace if applicable (e.g., 'Mountain' for Mountain Dwarf)"
      },
      "character_class": {
        "type": "string",
        "description": "Primary character class (e.g., 'Fighter', 'Wizard')"
      },
      "total_level": {
        "type": "integer",
        "minimum": 1,
        "maximum": 20,
        "description": "Total character level"
      },
      "multiclass_levels": {
        "type": ["object", "null"],
        "additionalProperties": {
          "type": "integer"
        },
        "description": "Multiclass levels as {class_name: level} pairs"
      },
      "alignment": {
        "type": "string",
        "description": "Character alignment (e.g., 'Lawful Good', 'Chaotic Neutral')"
      },
      "background": {
        "type": "string",
        "description": "Character background (e.g., 'Soldier', 'Criminal', 'Noble')"
      },
      "lifestyle": {
        "type": ["string", "null"],
        "description": "Character's lifestyle if mentioned"
      }
    },
    "required": ["name", "race", "character_class", "total_level", "alignment", "background"]
  }
}
```

---

## T2: Extract Physical Characteristics

**Tool Function Name**: `extract_physical_characteristics`

**Purpose**: Extract physical appearance and descriptive traits

**Schema**:
```json
{
  "name": "extract_physical_characteristics",
  "description": "Extract character's physical appearance and characteristics",
  "parameters": {
    "type": "object",
    "properties": {
      "alignment": {
        "type": "string",
        "description": "Character alignment (duplicate for consistency)"
      },
      "gender": {
        "type": "string",
        "description": "Character's gender"
      },
      "eyes": {
        "type": "string",
        "description": "Eye color/description"
      },
      "size": {
        "type": "string",
        "enum": ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"],
        "description": "Character size category"
      },
      "height": {
        "type": "string",
        "description": "Character height (e.g., '5\\'10\\\"')"
      },
      "hair": {
        "type": "string",
        "description": "Hair color/style"
      },
      "skin": {
        "type": "string",
        "description": "Skin color/complexion"
      },
      "age": {
        "type": "integer",
        "minimum": 1,
        "description": "Character age in years"
      },
      "weight": {
        "type": "string",
        "description": "Character weight with units (e.g., '180 lb')"
      },
      "faith": {
        "type": ["string", "null"],
        "description": "Deity or faith if mentioned"
      }
    },
    "required": ["alignment", "gender", "eyes", "size", "height", "hair", "skin", "age", "weight"]
  }
}
```

---

## T3: Extract Ability Scores

**Tool Function Name**: `extract_ability_scores`

**Purpose**: Extract the six core ability scores

**Schema**:
```json
{
  "name": "extract_ability_scores",
  "description": "Extract character's six ability scores",
  "parameters": {
    "type": "object",
    "properties": {
      "strength": {
        "type": "integer",
        "minimum": 1,
        "maximum": 30,
        "description": "Strength score"
      },
      "dexterity": {
        "type": "integer",
        "minimum": 1,
        "maximum": 30,
        "description": "Dexterity score"
      },
      "constitution": {
        "type": "integer",
        "minimum": 1,
        "maximum": 30,
        "description": "Constitution score"
      },
      "intelligence": {
        "type": "integer",
        "minimum": 1,
        "maximum": 30,
        "description": "Intelligence score"
      },
      "wisdom": {
        "type": "integer",
        "minimum": 1,
        "maximum": 30,
        "description": "Wisdom score"
      },
      "charisma": {
        "type": "integer",
        "minimum": 1,
        "maximum": 30,
        "description": "Charisma score"
      }
    },
    "required": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
  }
}
```

---

## T4: Extract Combat Stats

**Tool Function Name**: `extract_combat_stats`

**Purpose**: Extract combat-related statistics

**Schema**:
```json
{
  "name": "extract_combat_stats",
  "description": "Extract combat statistics including HP, AC, initiative, and speed",
  "parameters": {
    "type": "object",
    "properties": {
      "max_hp": {
        "type": "integer",
        "minimum": 1,
        "description": "Maximum hit points"
      },
      "armor_class": {
        "type": "integer",
        "minimum": 1,
        "description": "Armor class value"
      },
      "initiative_bonus": {
        "type": "integer",
        "description": "Initiative modifier (can be negative)"
      },
      "speed": {
        "type": "integer",
        "minimum": 0,
        "description": "Movement speed in feet"
      },
      "hit_dice": {
        "type": ["object", "null"],
        "additionalProperties": {
          "type": "string"
        },
        "description": "Hit dice by type (e.g., {'d10': '5', 'd8': '3'})"
      }
    },
    "required": ["max_hp", "armor_class", "initiative_bonus", "speed"]
  }
}
```

---

## T5: Extract Background Info

**Tool Function Name**: `extract_background_info`

**Purpose**: Extract character background details and features

**Schema**:
```json
{
  "name": "extract_background_info",
  "description": "Extract background information, features, and proficiencies",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Background name (e.g., 'Soldier', 'Criminal')"
      },
      "feature": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Background feature name"
          },
          "description": {
            "type": "string",
            "description": "Feature description"
          }
        },
        "required": ["name", "description"]
      },
      "skill_proficiencies": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Skills granted by background"
      },
      "tool_proficiencies": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Tools granted by background"
      },
      "language_proficiencies": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Languages granted by background"
      },
      "equipment": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Starting equipment from background"
      },
      "feature_description": {
        "type": ["string", "null"],
        "description": "Additional feature details"
      }
    },
    "required": ["name", "feature"]
  }
}
```

---

## T6: Extract Personality Traits

**Tool Function Name**: `extract_personality_traits`

**Purpose**: Extract personality traits, ideals, bonds, and flaws

**Schema**:
```json
{
  "name": "extract_personality_traits",
  "description": "Extract character personality, ideals, bonds, and flaws",
  "parameters": {
    "type": "object",
    "properties": {
      "personality_traits": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Character personality traits"
      },
      "ideals": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Character ideals and beliefs"
      },
      "bonds": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Character bonds and connections"
      },
      "flaws": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Character flaws and weaknesses"
      }
    },
    "required": ["personality_traits", "ideals", "bonds", "flaws"]
  }
}
```

---

## T7: Extract Proficiencies and Modifiers

**Tool Function Name**: `extract_proficiencies_and_modifiers`

**Purpose**: Extract all proficiencies and damage modifiers

**Schema**:
```json
{
  "name": "extract_proficiencies_and_modifiers",
  "description": "Extract proficiencies (skills, tools, languages, armor, weapons) and damage modifiers",
  "parameters": {
    "type": "object",
    "properties": {
      "proficiencies": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["armor", "weapon", "tool", "language", "skill", "saving_throw"]
            },
            "name": {
              "type": "string"
            }
          },
          "required": ["type", "name"]
        },
        "description": "All character proficiencies"
      },
      "damage_modifiers": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "damage_type": {
              "type": "string",
              "description": "Type of damage (e.g., 'fire', 'slashing')"
            },
            "modifier_type": {
              "type": "string",
              "enum": ["resistance", "immunity", "vulnerability"]
            }
          },
          "required": ["damage_type", "modifier_type"]
        },
        "description": "Damage resistances, immunities, and vulnerabilities"
      }
    },
    "required": ["proficiencies", "damage_modifiers"]
  }
}
```

---

## T8: Extract Passive Scores and Senses

**Tool Function Name**: `extract_passive_scores_and_senses`

**Purpose**: Extract passive perception, other passive scores, and special senses

**Schema**:
```json
{
  "name": "extract_passive_scores_and_senses",
  "description": "Extract passive scores and special senses",
  "parameters": {
    "type": "object",
    "properties": {
      "passive_scores": {
        "type": "object",
        "properties": {
          "perception": {
            "type": "integer",
            "description": "Passive perception score"
          },
          "investigation": {
            "type": ["integer", "null"],
            "description": "Passive investigation if mentioned"
          },
          "insight": {
            "type": ["integer", "null"],
            "description": "Passive insight if mentioned"
          },
          "stealth": {
            "type": ["integer", "null"],
            "description": "Passive stealth if mentioned"
          }
        },
        "required": ["perception"]
      },
      "senses": {
        "type": "object",
        "additionalProperties": {
          "type": ["integer", "string"],
          "description": "Sense range in feet or descriptive value"
        },
        "description": "Special senses like darkvision, blindsight, etc."
      }
    },
    "required": ["passive_scores", "senses"]
  }
}
```

---

## T9: Extract Features and Traits

**Tool Function Name**: `extract_features_and_traits`

**Purpose**: Extract class features, racial traits, and feats

**Schema**:
```json
{
  "name": "extract_features_and_traits",
  "description": "Extract all class features, racial traits, and feats",
  "parameters": {
    "type": "object",
    "properties": {
      "class_features": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "class_name": {"type": "string"},
            "level": {"type": "integer"},
            "features": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": {"type": "string"},
                  "description": {"type": ["string", "null"]},
                  "action_type": {
                    "type": ["string", "null"],
                    "enum": ["action", "bonus_action", "reaction", "no_action", null]
                  },
                  "passive": {"type": "boolean"},
                  "uses": {"type": ["object", "null"]},
                  "effect": {"type": ["string", "null"]},
                  "range": {"type": ["string", "null"]},
                  "duration": {"type": ["string", "null"]},
                  "save_dc": {"type": ["integer", "null"]},
                  "subclass": {"type": "boolean"}
                },
                "required": ["name"]
              }
            }
          },
          "required": ["class_name", "level", "features"]
        }
      },
      "racial_traits": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "description": {"type": ["string", "null"]},
            "passive": {"type": "boolean"}
          },
          "required": ["name"]
        }
      },
      "feats": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "description": {"type": ["string", "null"]},
            "effect": {"type": ["string", "null"]}
          },
          "required": ["name"]
        }
      }
    },
    "required": ["class_features", "racial_traits", "feats"]
  }
}
```

---

## T10: Extract Action Economy

**Tool Function Name**: `extract_action_economy`

**Purpose**: Extract combat actions, attacks, and special abilities

**Schema**:
```json
{
  "name": "extract_action_economy",
  "description": "Extract all combat actions, attacks, and action economy options",
  "parameters": {
    "type": "object",
    "properties": {
      "attacks_per_action": {
        "type": "integer",
        "minimum": 1,
        "description": "Number of attacks per Attack action"
      },
      "actions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "type": {
              "type": "string",
              "enum": ["action", "bonus_action", "reaction", "no_action", "feature"]
            },
            "description": {"type": ["string", "null"]},
            "uses": {"type": ["object", "null"]},
            "save_dc": {"type": ["integer", "null"]},
            "range": {"type": ["string", "null"]},
            "effect": {"type": ["string", "null"]},
            "trigger": {"type": ["string", "null"]},
            "damage": {
              "type": ["object", "null"],
              "properties": {
                "dice": {"type": "string"},
                "type": {"type": "string"}
              }
            }
          },
          "required": ["name", "type"]
        }
      }
    },
    "required": ["attacks_per_action", "actions"]
  }
}
```

---

## T11: Extract Inventory

**Tool Function Name**: `extract_inventory`

**Purpose**: Extract all equipment, items, and possessions

**Schema**:
```json
{
  "name": "extract_inventory",
  "description": "Extract complete inventory including equipped items and backpack contents",
  "parameters": {
    "type": "object",
    "properties": {
      "total_weight": {
        "type": "number",
        "description": "Total weight carried"
      },
      "weight_unit": {
        "type": "string",
        "default": "lb",
        "description": "Weight unit (usually 'lb')"
      },
      "equipped_items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "slot": {"type": "string"},
            "items": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": {"type": "string"},
                  "type": {"type": "string"},
                  "rarity": {"type": "string", "default": "Common"},
                  "requires_attunement": {"type": "boolean"},
                  "weight": {"type": ["number", "null"]},
                  "quantity": {"type": "integer", "default": 1},
                  "magical_bonus": {"type": ["string", "null"]},
                  "armor_class": {"type": ["integer", "null"]},
                  "damage": {"type": ["object", "null"]},
                  "properties": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["name", "type"]
              }
            }
          },
          "required": ["slot", "items"]
        }
      },
      "backpack": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "quantity": {"type": "integer", "default": 1},
            "weight": {"type": ["number", "null"]}
          },
          "required": ["name", "type"]
        }
      },
      "valuables": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "type": {"type": "string"},
            "amount": {"type": ["integer", "string"]}
          }
        },
        "description": "Currency and valuable items"
      }
    },
    "required": ["total_weight", "equipped_items", "backpack"]
  }
}
```

---

## T12: Extract Spellcasting Info

**Tool Function Name**: `extract_spellcasting_info`

**Purpose**: Extract spellcasting abilities and spell slots

**Schema**:
```json
{
  "name": "extract_spellcasting_info",
  "description": "Extract spellcasting information including ability, DC, and spell slots",
  "parameters": {
    "type": "object",
    "properties": {
      "spellcasting_classes": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "class_name": {"type": "string"},
            "ability": {
              "type": "string",
              "enum": ["Intelligence", "Wisdom", "Charisma"]
            },
            "spell_save_dc": {"type": "integer"},
            "spell_attack_bonus": {"type": "integer"},
            "cantrips_known": {
              "type": "array",
              "items": {"type": "string"}
            },
            "spells_known": {
              "type": "array",
              "items": {"type": "string"}
            },
            "spell_slots": {
              "type": "object",
              "additionalProperties": {"type": "integer"},
              "description": "Spell slots by level (1-9)"
            }
          },
          "required": ["class_name", "ability", "spell_save_dc", "spell_attack_bonus"]
        }
      }
    },
    "required": ["spellcasting_classes"]
  }
}
```

---

## T13: Extract Spell List

**Tool Function Name**: `extract_spell_list`

**Purpose**: Extract complete spell list organized by level

**Schema**:
```json
{
  "name": "extract_spell_list",
  "description": "Extract all spells organized by class and level",
  "parameters": {
    "type": "object",
    "properties": {
      "spells_by_class": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "class_name": {"type": "string"},
            "spells_by_level": {
              "type": "object",
              "additionalProperties": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "name": {"type": "string"},
                    "level": {"type": "integer"},
                    "school": {"type": "string"},
                    "casting_time": {"type": "string"},
                    "range": {"type": "string"},
                    "components": {
                      "type": "object",
                      "properties": {
                        "verbal": {"type": "boolean"},
                        "somatic": {"type": "boolean"},
                        "material": {"type": ["boolean", "string"]}
                      }
                    },
                    "duration": {"type": "string"},
                    "concentration": {"type": "boolean"},
                    "ritual": {"type": "boolean"},
                    "description": {"type": "string"}
                  },
                  "required": ["name", "level", "school", "casting_time", "range", "components", "duration"]
                }
              }
            }
          },
          "required": ["class_name", "spells_by_level"]
        }
      }
    },
    "required": ["spells_by_class"]
  }
}
```

---

## T14: Extract Backstory and Relationships

**Tool Function Name**: `extract_backstory_and_relationships`

**Purpose**: Extract backstory, organizations, allies, enemies, and objectives

**Schema**:
```json
{
  "name": "extract_backstory_and_relationships",
  "description": "Extract character backstory, relationships, and current objectives",
  "parameters": {
    "type": "object",
    "properties": {
      "backstory": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "family_backstory": {
            "type": "object",
            "properties": {
              "parents": {"type": "string"},
              "sections": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "heading": {"type": "string"},
                    "content": {"type": "string"}
                  },
                  "required": ["heading", "content"]
                }
              }
            },
            "required": ["parents"]
          },
          "sections": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "heading": {"type": "string"},
                "content": {"type": "string"}
              },
              "required": ["heading", "content"]
            }
          }
        },
        "required": ["title", "family_backstory"]
      },
      "organizations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "role": {"type": "string"},
            "description": {"type": "string"}
          },
          "required": ["name", "role", "description"]
        }
      },
      "allies": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "title": {"type": ["string", "null"]}
          },
          "required": ["name", "description"]
        }
      },
      "enemies": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"}
          },
          "required": ["name", "description"]
        }
      },
      "objectives": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "type": {"type": "string"},
            "status": {
              "type": "string",
              "enum": ["Active", "In Progress", "Completed", "Failed", "Suspended", "Abandoned"]
            },
            "description": {"type": "string"},
            "priority": {
              "type": ["string", "null"],
              "enum": ["Absolute", "Critical", "High", "Medium", "Low", null]
            },
            "objectives": {"type": "array", "items": {"type": "string"}},
            "rewards": {"type": "array", "items": {"type": "string"}},
            "deadline": {"type": ["string", "null"]},
            "quest_giver": {"type": ["string", "null"]},
            "location": {"type": ["string", "null"]}
          },
          "required": ["id", "name", "type", "status", "description"]
        }
      }
    },
    "required": ["backstory", "organizations", "allies", "enemies", "objectives"]
  }
}
```

---

## Schema Coverage Matrix

| Character Component | Tool Function | Character Type Coverage |
|-------------------|--------------|------------------------|
| Core Identity | T1: extract_character_base | CharacterBase |
| Physical Traits | T2: extract_physical_characteristics | PhysicalCharacteristics |
| Ability Scores | T3: extract_ability_scores | AbilityScores |
| Combat Stats | T4: extract_combat_stats | CombatStats |
| Background | T5: extract_background_info | BackgroundInfo |
| Personality | T6: extract_personality_traits | PersonalityTraits |
| Proficiencies | T7: extract_proficiencies_and_modifiers | Proficiency, DamageModifier |
| Senses | T8: extract_passive_scores_and_senses | PassiveScores, Senses |
| Features | T9: extract_features_and_traits | FeaturesAndTraits, Feature |
| Actions | T10: extract_action_economy | ActionEconomy, CharacterAction |
| Equipment | T11: extract_inventory | Inventory, InventoryItem |
| Spellcasting | T12: extract_spellcasting_info | SpellcastingInfo |
| Spells | T13: extract_spell_list | SpellList, Spell |
| Story & Social | T14: extract_backstory_and_relationships | Backstory, Organization, Ally, Enemy, Quest, Contract |

## Implementation Notes

1. **Parallel Execution**: All 14 tool functions can be called simultaneously with the same OCR markdown input
2. **Required vs Optional**: Each schema clearly marks required fields while allowing optional data
3. **Type Safety**: Schemas use strict typing with enums for constrained values
4. **OCR Tolerance**: Fields accept various formats (e.g., "5'10\"" or "5 ft 10 in" for height)
5. **Smart Defaults**: Missing data can be inferred based on race/class/level patterns
6. **Validation**: Each tool response should be validated against its schema before aggregation
7. **Conflict Resolution**: When multiple extractions overlap, prefer the most specific tool's result
8. **Gap Filling**: After initial extraction, identify missing critical fields for targeted follow-up

This comprehensive schema set ensures complete character data extraction from messy OCR sources while maintaining type safety and data integrity.

Similar code found with 2 license types