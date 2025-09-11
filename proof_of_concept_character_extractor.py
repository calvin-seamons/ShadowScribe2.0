#!/usr/bin/env python3
"""
Proof of Concept Character Extraction System

This script demonstrates parallel extraction of character data from OCR'd markdown
using the defined API schemas and Anthropic's Claude Sonnet model with tool calling.

Input: knowledge_base/ceej10_125292496.md
Output: character_extraction_results.txt
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

from src.rag.llm_client import AnthropicLLMClient


@dataclass
class ExtractionResult:
    task_name: str
    tool_function: str
    success: bool
    data: Dict[str, Any]
    error: str = ""


class CharacterExtractionPOC:
    def __init__(self):
        self.client = AnthropicLLMClient(default_model="claude-3-5-haiku-latest")
        
        # Define the extraction tasks with their schemas
        self.extraction_tasks = self._get_extraction_tasks()
    
    def _get_extraction_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Define all 14 extraction tasks with their schemas"""
        return {
            "T1_character_base": {
                "name": "extract_character_base",
                "description": "Extract basic character information including name, race, class, level, and background",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Character's full name"},
                        "race": {"type": "string", "description": "Character's race (e.g., 'Human', 'Elf', 'Dwarf')"},
                        "subrace": {"type": ["string", "null"], "description": "Character's subrace if applicable"},
                        "character_class": {"type": "string", "description": "Primary character class (e.g., 'Fighter', 'Wizard')"},
                        "total_level": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Total character level"},
                        "multiclass_levels": {"type": ["object", "null"], "additionalProperties": {"type": "integer"}},
                        "alignment": {"type": "string", "description": "Character alignment"},
                        "background": {"type": "string", "description": "Character background"},
                        "lifestyle": {"type": ["string", "null"], "description": "Character's lifestyle if mentioned"}
                    },
                    "required": ["name", "race", "character_class", "total_level", "alignment", "background"]
                }
            },
            
            "T2_physical_characteristics": {
                "name": "extract_physical_characteristics", 
                "description": "Extract character's physical appearance and characteristics",
                "schema": {
                    "type": "object",
                    "properties": {
                        "gender": {"type": "string", "description": "Character's gender"},
                        "eyes": {"type": "string", "description": "Eye color/description"},
                        "size": {"type": "string", "enum": ["Tiny", "Small", "Medium", "Large"], "description": "Character size category"},
                        "height": {"type": "string", "description": "Character height"},
                        "hair": {"type": "string", "description": "Hair color/style"},
                        "skin": {"type": "string", "description": "Skin color/complexion"},
                        "age": {"type": "integer", "minimum": 1, "description": "Character age in years"},
                        "weight": {"type": "string", "description": "Character weight with units"},
                        "faith": {"type": ["string", "null"], "description": "Deity or faith if mentioned"}
                    },
                    "required": ["gender", "eyes", "size", "height", "hair", "skin", "age", "weight"]
                }
            },
            
            "T3_ability_scores": {
                "name": "extract_ability_scores",
                "description": "Extract character's six ability scores",
                "schema": {
                    "type": "object", 
                    "properties": {
                        "strength": {"type": "integer", "minimum": 1, "maximum": 30},
                        "dexterity": {"type": "integer", "minimum": 1, "maximum": 30},
                        "constitution": {"type": "integer", "minimum": 1, "maximum": 30},
                        "intelligence": {"type": "integer", "minimum": 1, "maximum": 30},
                        "wisdom": {"type": "integer", "minimum": 1, "maximum": 30},
                        "charisma": {"type": "integer", "minimum": 1, "maximum": 30}
                    },
                    "required": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
                }
            },
            
            "T4_combat_stats": {
                "name": "extract_combat_stats",
                "description": "Extract combat statistics including HP, AC, initiative, and speed",
                "schema": {
                    "type": "object",
                    "properties": {
                        "max_hp": {"type": "integer", "minimum": 1, "description": "Maximum hit points"},
                        "armor_class": {"type": "integer", "minimum": 1, "description": "Armor class value"},
                        "initiative_bonus": {"type": "integer", "description": "Initiative modifier"},
                        "speed": {"type": "integer", "minimum": 0, "description": "Movement speed in feet"},
                        "hit_dice": {"type": ["object", "null"], "additionalProperties": {"type": "string"}}
                    },
                    "required": ["max_hp", "armor_class", "initiative_bonus", "speed"]
                }
            },
            
            "T8_passive_scores_and_senses": {
                "name": "extract_passive_scores_and_senses", 
                "description": "Extract passive scores and special senses",
                "schema": {
                    "type": "object",
                    "properties": {
                        "passive_scores": {
                            "type": "object",
                            "properties": {
                                "perception": {"type": "integer", "description": "Passive perception score"},
                                "investigation": {"type": ["integer", "null"]},
                                "insight": {"type": ["integer", "null"]},
                                "stealth": {"type": ["integer", "null"]}
                            },
                            "required": ["perception"]
                        },
                        "senses": {
                            "type": "object",
                            "additionalProperties": {"type": ["integer", "string"]},
                            "description": "Special senses like darkvision, blindsight, etc."
                        }
                    },
                    "required": ["passive_scores", "senses"]
                }
            }
        }
    
    async def extract_single_component(self, task_name: str, task_config: Dict[str, Any], ocr_markdown: str) -> ExtractionResult:
        """Extract a single character component using tool calling"""
        try:
            system_prompt = f"""You are a D&D character sheet data extractor. You will receive messy OCR'd markdown text that may contain:
- Formatting inconsistencies  
- Missing table borders
- OCR artifacts ("0" instead of "O", extra spaces)
- Information scattered across the document

Your task: Extract {task_name} information and call the {task_config['name']} tool with accurate data.

Guidelines:
1. Use fuzzy matching - "STR" = "Strength" = "STRENGTH"
2. Handle missing data gracefully - use null for unavailable fields
3. Infer reasonable defaults when appropriate (e.g., Medium size for most races)
4. Look for context clues throughout the entire document
5. Call the tool function exactly once with your best extraction

If you cannot find specific information, use reasonable D&D defaults based on race/class context."""

            user_prompt = f"""Here is the complete OCR'd character sheet markdown:

{ocr_markdown}

Extract the {task_name} information and call the appropriate tool function."""

            # Create the tool definition
            tools = [{
                "name": task_config["name"],
                "description": task_config["description"],
                "input_schema": task_config["schema"]
            }]
            
            # Make the API call with tool enforcement
            response = await self.client.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=2000,
                temperature=0.1,
                system=system_prompt,
                tools=tools,
                tool_choice={"type": "tool", "name": task_config["name"]},
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Extract the tool call result
            for block in response.content:
                if block.type == "tool_use" and block.name == task_config["name"]:
                    return ExtractionResult(
                        task_name=task_name,
                        tool_function=task_config["name"], 
                        success=True,
                        data=block.input
                    )
            
            # If no tool call found
            return ExtractionResult(
                task_name=task_name,
                tool_function=task_config["name"],
                success=False,
                data={},
                error="No tool call found in response"
            )
            
        except Exception as e:
            return ExtractionResult(
                task_name=task_name,
                tool_function=task_config["name"],
                success=False,
                data={},
                error=str(e)
            )
    
    async def extract_all_components(self, ocr_markdown: str) -> List[ExtractionResult]:
        """Extract all character components in parallel"""
        print(f"Starting parallel extraction of {len(self.extraction_tasks)} components...")
        
        # Create all extraction tasks
        tasks = [
            self.extract_single_component(task_name, task_config, ocr_markdown)
            for task_name, task_config in self.extraction_tasks.items()
        ]
        
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert any exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                task_name = list(self.extraction_tasks.keys())[i]
                final_results.append(ExtractionResult(
                    task_name=task_name,
                    tool_function=self.extraction_tasks[task_name]["name"],
                    success=False,
                    data={},
                    error=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    def format_results(self, results: List[ExtractionResult]) -> str:
        """Format extraction results for output"""
        output = ["=" * 80]
        output.append("CHARACTER EXTRACTION PROOF OF CONCEPT RESULTS")
        output.append("=" * 80)
        output.append("")
        
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        output.append(f"✅ Successful extractions: {len(successful_results)}/{len(results)}")
        output.append(f"❌ Failed extractions: {len(failed_results)}/{len(results)}")
        output.append("")
        
        # Show successful results
        if successful_results:
            output.append("SUCCESSFUL EXTRACTIONS:")
            output.append("-" * 40)
            
            for result in successful_results:
                output.append(f"\n📋 {result.task_name.upper()}")
                output.append(f"Tool Function: {result.tool_function}")
                output.append("Extracted Data:")
                output.append(json.dumps(result.data, indent=2))
                output.append("-" * 40)
        
        # Show failed results
        if failed_results:
            output.append("\nFAILED EXTRACTIONS:")
            output.append("-" * 40)
            
            for result in failed_results:
                output.append(f"\n❌ {result.task_name.upper()}")
                output.append(f"Tool Function: {result.tool_function}")
                output.append(f"Error: {result.error}")
                output.append("-" * 40)
        
        output.append("\n" + "=" * 80)
        output.append("END OF RESULTS")
        output.append("=" * 80)
        
        return "\n".join(output)


async def main():
    """Main execution function"""
    print("🧙‍♂️ ShadowScribe 2.0 - Character Extraction Proof of Concept")
    print("=" * 60)
    
    # Load the OCR markdown file
    ocr_file_path = Path("knowledge_base/ceej10_125292496.md")
    
    if not ocr_file_path.exists():
        print(f"❌ Error: OCR file not found: {ocr_file_path}")
        return
    
    print(f"📖 Loading OCR markdown from: {ocr_file_path}")
    with open(ocr_file_path, 'r', encoding='utf-8') as f:
        ocr_markdown = f.read()
    
    print(f"📄 Loaded {len(ocr_markdown):,} characters of OCR text")
    
    # Initialize the extraction system
    extractor = CharacterExtractionPOC()
    
    # Run the parallel extraction
    print("\n🚀 Starting parallel extraction...")
    results = await extractor.extract_all_components(ocr_markdown)
    
    # Format and save results
    formatted_output = extractor.format_results(results)
    
    # Write results to file
    output_file = Path("character_extraction_results.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_output)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Summary: {sum(1 for r in results if r.success)}/{len(results)} successful extractions")
    
    # Also print a summary to console
    print("\n🔍 QUICK SUMMARY:")
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.task_name}: {result.tool_function}")
        if not result.success:
            print(f"   Error: {result.error[:100]}...")


if __name__ == "__main__":
    asyncio.run(main())