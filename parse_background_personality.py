#!/usr/bin/env python3
"""
D&D Beyond Background and Personality Parser

This script parses a D&D Beyond character JSON export and extracts background and personality information:
- BackgroundInfo (background feature, proficiencies, equipment)
- PersonalityTraits (personality traits, ideals, bonds, flaws)
- Backstory (backstory sections and family info)
- Organizations (organizations the character belongs to)
- Allies (allies and contacts)
- Enemies (enemies and rivals)

This parser uses LLM assistance to extract structured data from unstructured text fields.

Usage:
    python parse_background_personality.py <path_to_json_file>

Output:
    Parsed background and personality data in JSON format
"""

import json
import sys
import re
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))
from rag.llm_client import LLMClientFactory
from rag.json_repair import JSONRepair
from rag.character.character_types import (
    BackgroundInfo,
    BackgroundFeature,
    PersonalityTraits,
    Backstory,
    BackstorySection,
    FamilyBackstory,
    Organization,
    Ally,
    Enemy
)


class DNDBeyondBackgroundPersonalityParser:
    """Parser for extracting background and personality information from D&D Beyond JSON."""
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize parser with D&D Beyond JSON data."""
        self.data = json_data.get("data", {})
        self.llm_client = LLMClientFactory.create_router_client()
        
    def clean_html_description(self, description: str) -> str:
        """Clean HTML tags and format text."""
        if not description:
            return ""
            
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', description)
        
        # Replace HTML entities
        replacements = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&nbsp;': ' ',
            '&rsquo;': "'", '&ldquo;': '"', '&rdquo;': '"',
            '&mdash;': '—', '&ndash;': '–', '&hellip;': '...',
            '\u003C': '<', '\u003E': '>', '\r\n': '\n'
        }
        for old, new in replacements.items():
            clean_text = clean_text.replace(old, new)
        
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def parse_background_info_basic(self) -> BackgroundInfo:
        """
        Parse basic background information that doesn't require LLM.
        This extracts the structured parts from the background definition.
        """
        background_data = self.data.get("background", {})
        definition = background_data.get("definition", {})
        
        # Extract basic info
        name = definition.get("name", "Unknown")
        feature_name = definition.get("featureName", "Unknown Feature")
        feature_description = self.clean_html_description(definition.get("featureDescription", ""))
        
        # Create background feature
        feature = BackgroundFeature(
            name=feature_name,
            description=feature_description
        )
        
        # Extract proficiency descriptions (will be parsed by LLM if needed)
        skill_prof_desc = definition.get("skillProficienciesDescription", "")
        tool_prof_desc = definition.get("toolProficienciesDescription", "")
        lang_prof_desc = definition.get("languagesDescription", "")
        equipment_desc = definition.get("equipmentDescription", "")
        
        # Basic parsing of comma-separated lists
        skill_profs = [s.strip() for s in skill_prof_desc.split(",")] if skill_prof_desc else []
        tool_profs = [t.strip() for t in tool_prof_desc.split(",")] if tool_prof_desc else []
        
        # Languages and equipment might need more complex parsing
        lang_profs = []
        equipment = []
        
        return BackgroundInfo(
            name=name,
            feature=feature,
            skill_proficiencies=skill_profs,
            tool_proficiencies=tool_profs,
            language_proficiencies=lang_profs,
            equipment=equipment,
            feature_description=feature_description
        ), lang_prof_desc, equipment_desc
    
    async def parse_background_info_with_llm(self, lang_desc: str, equip_desc: str) -> tuple[List[str], List[str]]:
        """
        Use LLM to parse language and equipment descriptions.
        
        Args:
            lang_desc: Language proficiencies description
            equip_desc: Equipment description
            
        Returns:
            Tuple of (languages, equipment) lists
        """
        prompt = f"""Parse the following D&D Beyond background information into structured lists.

Language Description: {lang_desc if lang_desc else "None"}
Equipment Description: {equip_desc if equip_desc else "None"}

Extract:
1. A list of specific languages (if "Two of your choice" or similar, return empty list)
2. A list of equipment items (parse the comma-separated or "and" separated list)

IMPORTANT: Preserve the exact wording from the original text. Do not summarize or paraphrase.

Return JSON in this exact format:
{{
  "languages": ["language1", "language2", ...],
  "equipment": ["item1", "item2", ...]
}}

If there are no specific languages mentioned (e.g., "Two of your choice"), return an empty languages array.
Parse equipment descriptions into individual items, preserving their exact names."""

        try:
            response = await self.llm_client.generate_json_response(prompt)
            
            # Repair and validate response
            if isinstance(response, str):
                repair_result = JSONRepair.repair_json_string(response)
            else:
                repair_result = JSONRepair.repair_json_string(json.dumps(response))
            data = repair_result.data
            
            languages = data.get("languages", [])
            equipment = data.get("equipment", [])
            
            return languages, equipment
            
        except Exception as e:
            print(f"Warning: LLM parsing of background info failed: {e}")
            return [], []
    
    async def parse_personality_traits_with_llm(self) -> PersonalityTraits:
        """
        Parse personality traits from the traits section.
        D&D Beyond stores these as newline-separated strings.
        """
        traits_data = self.data.get("traits", {})
        
        personality_text = traits_data.get("personalityTraits", "")
        ideals_text = traits_data.get("ideals", "")
        bonds_text = traits_data.get("bonds", "")
        flaws_text = traits_data.get("flaws", "")
        
        prompt = f"""Parse the following D&D character personality information into structured lists.
Each field may contain multiple entries separated by newlines.

Personality Traits:
{personality_text}

Ideals:
{ideals_text}

Bonds:
{bonds_text}

Flaws:
{flaws_text}

IMPORTANT: Preserve the EXACT original text. Do not summarize, paraphrase, or shorten anything.
Only clean up whitespace and split on newlines.

Return JSON in this exact format:
{{
  "personality_traits": ["trait1", "trait2", ...],
  "ideals": ["ideal1", "ideal2", ...],
  "bonds": ["bond1", "bond2", ...],
  "flaws": ["flaw1", "flaw2", ...]
}}

Split on newlines and clean up whitespace, but preserve the complete original text of each entry."""

        try:
            response = await self.llm_client.generate_json_response(prompt)
            
            # Repair and validate response
            if isinstance(response, str):
                repair_result = JSONRepair.repair_json_string(response)
            else:
                repair_result = JSONRepair.repair_json_string(json.dumps(response))
            data = repair_result.data
            
            return PersonalityTraits(
                personality_traits=data.get("personality_traits", []),
                ideals=data.get("ideals", []),
                bonds=data.get("bonds", []),
                flaws=data.get("flaws", [])
            )
            
        except Exception as e:
            print(f"Warning: LLM parsing of personality traits failed: {e}")
            # Fallback: simple split on newlines
            return PersonalityTraits(
                personality_traits=[t.strip() for t in personality_text.split('\n') if t.strip()],
                ideals=[i.strip() for i in ideals_text.split('\n') if i.strip()],
                bonds=[b.strip() for b in bonds_text.split('\n') if b.strip()],
                flaws=[f.strip() for f in flaws_text.split('\n') if f.strip()]
            )
    
    async def parse_backstory_with_llm(self) -> Backstory:
        """
        Parse backstory from notes.backstory using LLM.
        D&D Beyond stores backstory as markdown-formatted text.
        """
        notes = self.data.get("notes", {})
        backstory_text = notes.get("backstory", "")
        
        if not backstory_text:
            return Backstory(
                title="No Backstory",
                family_backstory=FamilyBackstory(parents="Unknown"),
                sections=[]
            )
        
        prompt = f"""Parse the following D&D character backstory into structured sections.
The backstory is in markdown format with headers marked by **Header** and sections separated by paragraphs.

Backstory Text:
{backstory_text}

IMPORTANT: Preserve the COMPLETE ORIGINAL TEXT. Do not summarize, shorten, or paraphrase ANY content.
You are structuring the text, not rewriting it.

Extract:
1. The main title (first markdown header or create one from context)
2. Family backstory information (parents, siblings, family relationships) - PRESERVE EXACT TEXT
3. All story sections with their headings and COMPLETE content

Return JSON in this exact format:
{{
  "title": "Main backstory title",
  "family_backstory": {{
    "parents": "COMPLETE EXACT information about parents and family from the text",
    "sections": [
      {{"heading": "Family section heading", "content": "COMPLETE EXACT family section content"}},
      ...
    ]
  }},
  "sections": [
    {{"heading": "Section heading", "content": "COMPLETE EXACT section content - do not shorten"}},
    {{"heading": "Another heading", "content": "COMPLETE EXACT section content - do not shorten"}},
    ...
  ]
}}

Parse the markdown headers (text between ** **) as section headings.
Extract any information about parents, family, upbringing into the family_backstory.
Organize the rest into logical sections.
PRESERVE ALL ORIGINAL TEXT - copy it exactly, do not summarize or paraphrase."""

        try:
            response = await self.llm_client.generate_json_response(prompt)
            
            # Repair and validate response
            if isinstance(response, str):
                repair_result = JSONRepair.repair_json_string(response)
            else:
                repair_result = JSONRepair.repair_json_string(json.dumps(response))
            data = repair_result.data
            
            # Parse family backstory
            family_data = data.get("family_backstory", {})
            family_sections = [
                BackstorySection(heading=s["heading"], content=s["content"])
                for s in family_data.get("sections", [])
            ]
            
            family_backstory = FamilyBackstory(
                parents=family_data.get("parents") if family_data.get("parents") else "Unknown",
                sections=family_sections
            )
            
            # Parse main sections
            main_sections = [
                BackstorySection(heading=s["heading"], content=s["content"])
                for s in data.get("sections", [])
            ]
            
            return Backstory(
                title=data.get("title", "Character Backstory"),
                family_backstory=family_backstory,
                sections=main_sections
            )
            
        except Exception as e:
            print(f"Warning: LLM parsing of backstory failed: {e}")
            # Fallback: create basic structure
            return Backstory(
                title="Character Backstory",
                family_backstory=FamilyBackstory(parents="Unknown"),
                sections=[BackstorySection(heading="Backstory", content=backstory_text[:500])]
            )
    
    async def parse_organizations_with_llm(self) -> List[Organization]:
        """
        Parse organizations from notes.organizations using LLM.
        D&D Beyond stores this as free-form text describing organizations.
        """
        notes = self.data.get("notes", {})
        organizations_text = notes.get("organizations", "")
        
        if not organizations_text:
            return []
        
        prompt = f"""Parse the following D&D character's organization affiliations into structured data.
The text describes organizations the character belongs to, their role, and the organization's purpose.

Organizations Text:
{organizations_text}

IMPORTANT: Preserve the EXACT original text. Do not summarize or paraphrase descriptions.

Extract each organization and return JSON in this exact format:
{{
  "organizations": [
    {{
      "name": "Organization Name",
      "role": "Character's role/position in the organization",
      "description": "COMPLETE EXACT description of the organization and character's involvement"
    }},
    ...
  ]
}}

Look for organization names (often at the start of sections or after colons).
Extract the character's role/rank in each organization.
Include the COMPLETE original text describing the organization's purpose and the character's involvement."""

        try:
            response = await self.llm_client.generate_json_response(prompt)
            
            # Repair and validate response
            if isinstance(response, str):
                repair_result = JSONRepair.repair_json_string(response)
            else:
                repair_result = JSONRepair.repair_json_string(json.dumps(response))
            data = repair_result.data
            
            organizations = []
            for org_data in data.get("organizations", []):
                organizations.append(Organization(
                    name=org_data.get("name", "Unknown Organization"),
                    role=org_data.get("role", "Member"),
                    description=org_data.get("description", "")
                ))
            
            return organizations
            
        except Exception as e:
            print(f"Warning: LLM parsing of organizations failed: {e}")
            return []
    
    async def parse_allies_with_llm(self) -> List[Ally]:
        """
        Parse allies from notes.allies using LLM.
        D&D Beyond stores this as numbered/bulleted list with markdown formatting.
        """
        notes = self.data.get("notes", {})
        allies_text = notes.get("allies", "")
        
        if not allies_text:
            return []
        
        prompt = f"""Parse the following D&D character's allies and contacts into structured data.
The text is a formatted list with names (often in bold **Name**) and descriptions.

Allies Text:
{allies_text}

IMPORTANT: Preserve the EXACT original text of descriptions. Do not summarize or paraphrase.

Extract each ally and return JSON in this exact format:
{{
  "allies": [
    {{
      "name": "Ally Name",
      "description": "COMPLETE EXACT description of the ally and their relationship",
      "title": "Ally's title/position (if mentioned, otherwise null)"
    }},
    ...
  ]
}}

Parse markdown bold text (**text**) as names.
Extract any titles (like "High Acolyte", "Captain", etc.) into the title field.
Include the COMPLETE original description of their relationship and role - do not shorten it."""

        try:
            response = await self.llm_client.generate_json_response(prompt)
            
            # Repair and validate response
            if isinstance(response, str):
                repair_result = JSONRepair.repair_json_string(response)
            else:
                repair_result = JSONRepair.repair_json_string(json.dumps(response))
            data = repair_result.data
            
            allies = []
            for ally_data in data.get("allies", []):
                allies.append(Ally(
                    name=ally_data.get("name", "Unknown Ally"),
                    description=ally_data.get("description", ""),
                    title=ally_data.get("title")
                ))
            
            return allies
            
        except Exception as e:
            print(f"Warning: LLM parsing of allies failed: {e}")
            return []
    
    async def parse_enemies_with_llm(self) -> List[Enemy]:
        """
        Parse enemies from notes.enemies using LLM.
        D&D Beyond stores this as simple text list.
        """
        notes = self.data.get("notes", {})
        enemies_text = notes.get("enemies", "")
        
        if not enemies_text:
            return []
        
        prompt = f"""Parse the following D&D character's enemies and rivals into structured data.
The text lists enemy names and may include brief descriptions.

Enemies Text:
{enemies_text}

IMPORTANT: Preserve the EXACT original text. Do not summarize or paraphrase descriptions.

Extract each enemy and return JSON in this exact format:
{{
  "enemies": [
    {{
      "name": "Enemy Name",
      "description": "COMPLETE EXACT description of the enemy and why they're an enemy"
    }},
    ...
  ]
}}

Parse newline-separated or comma-separated lists of enemies.
Extract any descriptive information about why they're enemies.
Preserve the complete original text - do not shorten descriptions.
If no description is provided, leave the description field empty."""

        try:
            response = await self.llm_client.generate_json_response(prompt)
            
            # Repair and validate response
            if isinstance(response, str):
                repair_result = JSONRepair.repair_json_string(response)
            else:
                repair_result = JSONRepair.repair_json_string(json.dumps(response))
            data = repair_result.data
            
            enemies = []
            for enemy_data in data.get("enemies", []):
                enemies.append(Enemy(
                    name=enemy_data.get("name", "Unknown Enemy"),
                    description=enemy_data.get("description", "")
                ))
            
            return enemies
            
        except Exception as e:
            print(f"Warning: LLM parsing of enemies failed: {e}")
            # Fallback: simple split on newlines
            enemy_names = [e.strip() for e in enemies_text.split('\n') if e.strip()]
            return [Enemy(name=name, description="") for name in enemy_names]
    
    async def parse_all_async(self) -> Dict[str, Any]:
        """
        Parse all background and personality information using parallel LLM calls.
        
        Returns:
            Dictionary containing all parsed data
        """
        # Parse basic background info first (no LLM needed)
        background_info, lang_desc, equip_desc = self.parse_background_info_basic()
        
        # Run all LLM parsing tasks in parallel
        print("Parsing background and personality with LLM (parallel execution)...")
        
        results = await asyncio.gather(
            self.parse_background_info_with_llm(lang_desc, equip_desc),
            self.parse_personality_traits_with_llm(),
            self.parse_backstory_with_llm(),
            self.parse_organizations_with_llm(),
            self.parse_allies_with_llm(),
            self.parse_enemies_with_llm(),
            return_exceptions=True
        )
        
        # Unpack results
        (languages, equipment), personality_traits, backstory, organizations, allies, enemies = results
        
        # Update background info with LLM-parsed data
        background_info.language_proficiencies = languages
        background_info.equipment = equipment
        
        return {
            "background_info": background_info,
            "personality_traits": personality_traits,
            "backstory": backstory,
            "organizations": organizations,
            "allies": allies,
            "enemies": enemies
        }
    
    def print_summary(self, parsed_data: Dict[str, Any]):
        """Print a summary of parsed background and personality information."""
        print("\n" + "="*80)
        print("BACKGROUND AND PERSONALITY SUMMARY")
        print("="*80)
        
        # Background Info
        bg_info = parsed_data["background_info"]
        print(f"\n📋 BACKGROUND: {bg_info.name}")
        print(f"   Feature: {bg_info.feature.name}")
        print(f"   Skills: {', '.join(bg_info.skill_proficiencies) if bg_info.skill_proficiencies else 'None'}")
        print(f"   Tools: {', '.join(bg_info.tool_proficiencies) if bg_info.tool_proficiencies else 'None'}")
        print(f"   Languages: {', '.join(bg_info.language_proficiencies) if bg_info.language_proficiencies else 'None'}")
        print(f"   Equipment: {len(bg_info.equipment)} items")
        
        # Personality Traits
        personality = parsed_data["personality_traits"]
        print(f"\n🎭 PERSONALITY")
        print(f"   Traits: {len(personality.personality_traits)}")
        for trait in personality.personality_traits[:3]:
            print(f"      - {trait[:80]}...")
        print(f"   Ideals: {len(personality.ideals)}")
        for ideal in personality.ideals[:2]:
            print(f"      - {ideal[:80]}...")
        print(f"   Bonds: {len(personality.bonds)}")
        for bond in personality.bonds[:2]:
            print(f"      - {bond[:80]}...")
        print(f"   Flaws: {len(personality.flaws)}")
        for flaw in personality.flaws[:2]:
            print(f"      - {flaw[:80]}...")
        
        # Backstory
        backstory = parsed_data["backstory"]
        print(f"\n📖 BACKSTORY: {backstory.title}")
        family_info = backstory.family_backstory.parents if backstory.family_backstory.parents else "Unknown"
        print(f"   Family: {family_info[:100]}..." if len(family_info) > 100 else f"   Family: {family_info}")
        print(f"   Sections: {len(backstory.sections)}")
        for section in backstory.sections[:3]:
            print(f"      - {section.heading}")
        
        # Organizations
        organizations = parsed_data["organizations"]
        print(f"\n🏛️  ORGANIZATIONS: {len(organizations)}")
        for org in organizations[:3]:
            print(f"   - {org.name}: {org.role}")
        
        # Allies
        allies = parsed_data["allies"]
        print(f"\n🤝 ALLIES: {len(allies)}")
        for ally in allies[:5]:
            title_str = f" ({ally.title})" if ally.title else ""
            print(f"   - {ally.name}{title_str}")
        
        # Enemies
        enemies = parsed_data["enemies"]
        print(f"\n⚔️  ENEMIES: {len(enemies)}")
        for enemy in enemies[:5]:
            print(f"   - {enemy.name}")
        
        print("\n" + "="*80)


def clean_dict_for_json(obj):
    """Remove None values and empty collections recursively."""
    if isinstance(obj, dict):
        return {
            k: clean_dict_for_json(v)
            for k, v in obj.items()
            if v is not None and v != [] and v != {} and v != ""
        }
    elif isinstance(obj, list):
        cleaned = [clean_dict_for_json(item) for item in obj]
        return [item for item in cleaned if item is not None and item != {} and item != ""]
    else:
        return obj


async def main_async(json_file_path: str):
    """Async main function to parse D&D Beyond JSON."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f"Loaded character JSON from: {json_file_path}")
        character_name = json_data.get("data", {}).get("name", "Unknown")
        print(f"Character: {character_name}")
        
        # Parse all data
        parser = DNDBeyondBackgroundPersonalityParser(json_data)
        parsed_data = await parser.parse_all_async()
        
        # Print summary
        parser.print_summary(parsed_data)
        
        # Convert to JSON-serializable format
        output = {
            "character_name": character_name,
            "background_info": clean_dict_for_json(asdict(parsed_data["background_info"])),
            "personality_traits": clean_dict_for_json(asdict(parsed_data["personality_traits"])),
            "backstory": clean_dict_for_json(asdict(parsed_data["backstory"])),
            "organizations": [clean_dict_for_json(asdict(org)) for org in parsed_data["organizations"]],
            "allies": [clean_dict_for_json(asdict(ally)) for ally in parsed_data["allies"]],
            "enemies": [clean_dict_for_json(asdict(enemy)) for enemy in parsed_data["enemies"]]
        }
        
        # Save to output file
        output_file = json_file_path.replace('.json', '_background_personality_parsed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Parsed data saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main function to parse D&D Beyond JSON and extract background/personality."""
    if len(sys.argv) != 2:
        print("Usage: python parse_background_personality.py <path_to_json_file>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    # Run async main
    asyncio.run(main_async(json_file_path))


if __name__ == "__main__":
    main()
