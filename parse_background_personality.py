#!/usr/bin/env python3
"""
D&D Beyond Background & Personality Parser

This script parses a D&D Beyond character JSON export and extracts background and personality
information using LLM assistance for unstructured text fields:
- BackgroundInfo (background feature and proficiencies)
- PersonalityTraits (personality traits, ideals, bonds, flaws)
- Backstory (complete backstory with sections and family info)
- Organization (character's organizations)
- Ally (character's allies)
- Enemy (character's enemies)

These fields require LLM parsing because they are stored as unstructured markdown/text in the JSON.

Usage:
    python parse_background_personality.py <path_to_json_file>

Output:
    Parsed background and personality data in JSON format
"""

import json
import sys
import asyncio
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))
from rag.character.character_types import (
    BackgroundInfo, BackgroundFeature, PersonalityTraits,
    Backstory, BackstorySection, FamilyBackstory,
    Organization, Ally, Enemy
)
from rag.llm_client import LLMClientFactory
from rag.json_repair import JSONRepair, JSONRepairError


class BackgroundPersonalityParser:
    """Parser for D&D Beyond character JSON background and personality data."""
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize parser with JSON data."""
        self.data = json_data
        # Create LLM client for parsing unstructured text
        self.llm_client = LLMClientFactory.create_final_response_client()
        
    async def parse_all(self) -> Dict[str, Any]:
        """Parse all background and personality data in parallel."""
        print("Parsing background and personality data with LLM assistance...")
        
        # Run all parsers in parallel for efficiency
        results = await asyncio.gather(
            self.parse_background_info(),
            self.parse_personality_traits(),
            self.parse_backstory(),
            self.parse_organizations(),
            self.parse_allies(),
            self.parse_enemies(),
            return_exceptions=True
        )
        
        # Unpack results (handle any exceptions)
        background_info = results[0] if not isinstance(results[0], Exception) else None
        personality_traits = results[1] if not isinstance(results[1], Exception) else None
        backstory = results[2] if not isinstance(results[2], Exception) else None
        organizations = results[3] if not isinstance(results[3], Exception) else []
        allies = results[4] if not isinstance(results[4], Exception) else []
        enemies = results[5] if not isinstance(results[5], Exception) else []
        
        return {
            'background_info': background_info,
            'personality_traits': personality_traits,
            'backstory': backstory,
            'organizations': organizations,
            'allies': allies,
            'enemies': enemies
        }
    
    async def parse_background_info(self) -> Optional[BackgroundInfo]:
        """Parse character background information.
        
        EXTRACTION PATHS:
        - name: data.background.definition.name
        - feature: Parse from data.background.definition.featureName and featureDescription
        - equipment: Parse from equipmentDescription
        
        NOTE: Proficiencies are NOT parsed here - they are already extracted from
        data.modifiers[] in parse_core_character.py as Proficiency objects.
        """
        background_data = self.data.get('background', {})
        
        # Handle custom backgrounds
        if background_data.get('hasCustomBackground'):
            definition = background_data.get('customBackground', {})
        else:
            definition = background_data.get('definition', {})
        
        if not definition:
            return None
        
        # Get basic info (already structured)
        name = definition.get('name', 'Unknown')
        feature_name = definition.get('featureName', '')
        feature_description = definition.get('featureDescription', '')
        
        # Clean HTML from feature description
        feature_desc_clean = self._clean_html(feature_description)
        
        # Get equipment description and parse it
        equipment_desc = definition.get('equipmentDescription', '')
        equipment = await self._parse_equipment(equipment_desc)
        
        return BackgroundInfo(
            name=name,
            feature=BackgroundFeature(
                name=feature_name,
                description=feature_desc_clean
            ),
            equipment=equipment,
            feature_description=feature_desc_clean
        )
    
    async def _parse_equipment(self, equipment_desc: str) -> List[str]:
        """Use LLM to parse equipment description into a list of items."""
        
        if not equipment_desc:
            return []
        
        prompt = f"""Parse the following D&D 5e background equipment description into a clean list.
Return ONLY valid JSON with a single key "equipment" containing an array of strings.
Each item should be listed separately (don't include quantities in item names if possible).

Equipment Description: {equipment_desc}

Return JSON in this exact format:
{{
  "equipment": ["item1", "item2", "item3"]
}}"""

        try:
            result = await self.llm_client.generate_json_response(prompt)
            
            # Handle string responses or malformed JSON
            if isinstance(result, str):
                try:
                    repair_result = JSONRepair.repair_json_string(result)
                    result = repair_result.data
                    if repair_result.was_repaired:
                        print(f"  [JSON Repair] Equipment: {', '.join(repair_result.repair_details)}")
                except JSONRepairError as e:
                    print(f"  [Error] Failed to repair equipment JSON: {e}")
                    return []
            
            # Handle error responses from LLM
            if isinstance(result, dict) and 'error' in result:
                print(f"  [Error] LLM returned error for equipment: {result['error']}")
                return []
            
            return result.get('equipment', [])
        except Exception as e:
            print(f"Error parsing equipment: {e}")
            return []
    
    async def parse_personality_traits(self) -> Optional[PersonalityTraits]:
        """Parse personality traits, ideals, bonds, and flaws.
        
        EXTRACTION PATHS:
        - personality_traits: Split data.traits.personalityTraits on newlines
        - ideals: Split data.traits.ideals on newlines
        - bonds: Split data.traits.bonds on newlines
        - flaws: Split data.traits.flaws on newlines
        
        These are stored as single strings with newline separators.
        """
        traits_data = self.data.get('traits', {})
        
        personality_text = traits_data.get('personalityTraits', '')
        ideals_text = traits_data.get('ideals', '')
        bonds_text = traits_data.get('bonds', '')
        flaws_text = traits_data.get('flaws', '')
        
        # Simple splitting on newlines, filtering empty strings
        personality_traits = [t.strip() for t in personality_text.split('\n') if t.strip()]
        ideals = [i.strip() for i in ideals_text.split('\n') if i.strip()]
        bonds = [b.strip() for b in bonds_text.split('\n') if b.strip()]
        flaws = [f.strip() for f in flaws_text.split('\n') if f.strip()]
        
        return PersonalityTraits(
            personality_traits=personality_traits,
            ideals=ideals,
            bonds=bonds,
            flaws=flaws
        )
    
    async def parse_backstory(self) -> Optional[Backstory]:
        """Parse complete character backstory with sections.
        
        EXTRACTION PATHS:
        - data.notes.backstory contains markdown-formatted backstory
        - data.notes.otherNotes may contain additional backstory context
        - Must parse markdown headers (** text **) to extract sections
        - Must extract family information using LLM (may not exist)
        """
        notes = self.data.get('notes', {})
        backstory_text = notes.get('backstory', '')
        other_notes = notes.get('otherNotes', '')
        
        if not backstory_text:
            # Return minimal backstory
            return Backstory(
                title="Unknown",
                family_backstory=FamilyBackstory(parents=None),
                sections=[]
            )
        
        # Use LLM to parse the markdown backstory into structured sections
        # Pass both backstory and otherNotes for full context
        parsed = await self._parse_backstory_with_llm(backstory_text, other_notes)
        
        return Backstory(
            title=parsed['title'],
            family_backstory=FamilyBackstory(
                parents=parsed['family']['parents'],
                sections=parsed['family']['sections']
            ),
            sections=parsed['sections']
        )
    
    async def _parse_backstory_with_llm(self, backstory_text: str, other_notes: str = '') -> Dict[str, Any]:
        """Use LLM to parse markdown backstory into structured sections."""
        
        # Combine all available context
        full_context = backstory_text
        if other_notes:
            full_context += "\n\n--- Additional Notes ---\n\n" + other_notes
        
        prompt = f"""Parse this D&D character backstory (in markdown format) into structured JSON.

Extract:
1. Title (the main title or first section heading)
2. All sections with their headings and content
3. Family information (parents and any family-related sections) - may not exist

BACKSTORY TEXT:
{full_context}

Return JSON in this exact format:
{{
  "title": "Main title or first heading",
  "sections": [
    {{"heading": "Section Heading 1", "content": "Section content here"}},
    {{"heading": "Section Heading 2", "content": "Section content here"}}
  ],
  "family": {{
    "parents": "Description of parents or family origin, or null if not mentioned",
    "sections": [
      {{"heading": "Family-related heading", "content": "Family-related content"}}
    ]
  }}
}}

Notes:
- Extract markdown headers (text between ** markers or starting with #) as section headings
- Content is the text between headers
- For family.parents, extract any mention of parents, family background, or origin
- Set family.parents to null if no family information exists
- For family.sections, include any sections specifically about family
- If no family information exists, use null for parents and empty array for sections"""

        try:
            result = await self.llm_client.generate_json_response(prompt)
            
            # Handle string responses or malformed JSON
            if isinstance(result, str):
                try:
                    repair_result = JSONRepair.repair_json_string(result)
                    result = repair_result.data
                    if repair_result.was_repaired:
                        print(f"  [JSON Repair] Backstory: {', '.join(repair_result.repair_details)}")
                except JSONRepairError as e:
                    print(f"  [Error] Failed to repair backstory JSON: {e}")
                    print(f"  [Error] Raw response was: {result[:500]}")
                    return {
                        'title': 'Unknown',
                        'sections': [],
                        'family': {'parents': None, 'sections': []}
                    }
            
            # Handle error responses from LLM
            if isinstance(result, dict) and 'error' in result:
                print(f"  [Error] LLM returned error for backstory: {result['error']}")
                return {
                    'title': 'Unknown',
                    'sections': [],
                    'family': {'parents': None, 'sections': []}
                }
            
            # Check if result has required keys
            if not isinstance(result, dict) or 'title' not in result or 'sections' not in result:
                print(f"  [Error] LLM returned incomplete backstory data. Keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                return {
                    'title': 'Unknown',
                    'sections': [],
                    'family': {'parents': None, 'sections': []}
                }
            
            # Convert sections to BackstorySection objects
            sections = [
                BackstorySection(heading=s['heading'], content=s['content'])
                for s in result.get('sections', [])
            ]
            
            family_sections = [
                BackstorySection(heading=s['heading'], content=s['content'])
                for s in result.get('family', {}).get('sections', [])
            ]
            
            return {
                'title': result.get('title', 'Unknown'),
                'sections': sections,
                'family': {
                    'parents': result.get('family', {}).get('parents'),  # May be None
                    'sections': family_sections
                }
            }
        except Exception as e:
            print(f"Error parsing backstory: {e}")
            import traceback
            traceback.print_exc()
            return {
                'title': 'Unknown',
                'sections': [],
                'family': {'parents': None, 'sections': []}
            }
    
    async def parse_organizations(self) -> List[Organization]:
        """Parse character organizations from notes.
        
        EXTRACTION PATHS:
        - data.notes.organizations contains free text descriptions
        - Format: "Organization Name: Description of role and involvement"
        """
        notes = self.data.get('notes', {})
        organizations_text = notes.get('organizations', '')
        
        if not organizations_text:
            return []
        
        # Use LLM to parse organizations
        return await self._parse_organizations_with_llm(organizations_text)
    
    async def _parse_organizations_with_llm(self, org_text: str) -> List[Organization]:
        """Use LLM to parse organization descriptions."""
        
        prompt = f"""Parse this text describing a D&D character's organizational memberships into structured JSON.

ORGANIZATIONS TEXT:
{org_text}

Extract each organization with:
- name: The organization's name
- role: The character's role/position in the organization
- description: What the organization does and the character's involvement

Return JSON in this exact format:
{{
  "organizations": [
    {{
      "name": "Organization Name",
      "role": "Character's role/position",
      "description": "Organization purpose and character involvement"
    }}
  ]
}}

If no organizations are mentioned, return {{"organizations": []}}"""

        try:
            result = await self.llm_client.generate_json_response(prompt)
            
            # Handle string responses or malformed JSON
            if isinstance(result, str):
                try:
                    repair_result = JSONRepair.repair_json_string(result)
                    result = repair_result.data
                    if repair_result.was_repaired:
                        print(f"  [JSON Repair] Organizations: {', '.join(repair_result.repair_details)}")
                except JSONRepairError as e:
                    print(f"  [Error] Failed to repair organizations JSON: {e}")
                    return []
            
            # Handle error responses from LLM
            if isinstance(result, dict) and 'error' in result:
                print(f"  [Error] LLM returned error for organizations: {result['error']}")
                return []
            
            organizations = []
            for org_data in result.get('organizations', []):
                organizations.append(Organization(
                    name=org_data.get('name', 'Unknown'),
                    role=org_data.get('role', 'Unknown'),
                    description=org_data.get('description', '')
                ))
            
            return organizations
        except Exception as e:
            print(f"Error parsing organizations: {e}")
            return []
    
    async def parse_allies(self) -> List[Ally]:
        """Parse character allies from notes.
        
        EXTRACTION PATHS:
        - data.notes.allies contains markdown-formatted numbered list
        - Format: "1. **Name**: Description of relationship"
        """
        notes = self.data.get('notes', {})
        allies_text = notes.get('allies', '')
        
        if not allies_text:
            return []
        
        # Use LLM to parse allies
        return await self._parse_allies_with_llm(allies_text)
    
    async def _parse_allies_with_llm(self, allies_text: str) -> List[Ally]:
        """Use LLM to parse ally descriptions."""
        
        prompt = f"""Parse this markdown-formatted list of a D&D character's allies into structured JSON.

ALLIES TEXT:
{allies_text}

Extract each ally with:
- name: The ally's name (often in bold or at the start)
- title: Their title or position (if mentioned)
- description: Description of the relationship and who they are

Return JSON in this exact format:
{{
  "allies": [
    {{
      "name": "Ally Name",
      "title": "Their Title",
      "description": "Description of relationship and background"
    }}
  ]
}}

Notes:
- Extract names from bold text (**Name**) or numbered list prefixes
- Title is optional (null if not mentioned)
- If no allies are mentioned, return {{"allies": []}}"""

        try:
            result = await self.llm_client.generate_json_response(prompt)
            
            # Handle string responses or malformed JSON
            if isinstance(result, str):
                try:
                    repair_result = JSONRepair.repair_json_string(result)
                    result = repair_result.data
                    if repair_result.was_repaired:
                        print(f"  [JSON Repair] Allies: {', '.join(repair_result.repair_details)}")
                except JSONRepairError as e:
                    print(f"  [Error] Failed to repair allies JSON: {e}")
                    return []
            
            # Handle error responses from LLM
            if isinstance(result, dict) and 'error' in result:
                print(f"  [Error] LLM returned error for allies: {result['error']}")
                return []
            
            allies = []
            for ally_data in result.get('allies', []):
                allies.append(Ally(
                    name=ally_data.get('name', 'Unknown'),
                    description=ally_data.get('description', ''),
                    title=ally_data.get('title')
                ))
            
            return allies
        except Exception as e:
            print(f"Error parsing allies: {e}")
            return []
    
    async def parse_enemies(self) -> List[Enemy]:
        """Parse character enemies from notes.
        
        EXTRACTION PATHS:
        - data.notes.enemies contains newline-separated text
        - Format: Simple list of enemy names, sometimes with descriptions
        """
        notes = self.data.get('notes', {})
        enemies_text = notes.get('enemies', '')
        
        if not enemies_text:
            return []
        
        # Use LLM to parse enemies
        return await self._parse_enemies_with_llm(enemies_text)
    
    async def _parse_enemies_with_llm(self, enemies_text: str) -> List[Enemy]:
        """Use LLM to parse enemy descriptions."""
        
        prompt = f"""Parse this text describing a D&D character's enemies into structured JSON.

ENEMIES TEXT:
{enemies_text}

Extract each enemy with:
- name: The enemy's name
- description: Why they are an enemy or what they represent (infer if needed)

Return JSON in this exact format:
{{
  "enemies": [
    {{
      "name": "Enemy Name",
      "description": "Why they are an enemy or what threat they pose"
    }}
  ]
}}

Notes:
- Names are usually on separate lines or in a list
- Descriptions may need to be inferred from context or backstory
- If description is unclear, provide a brief placeholder
- If no enemies are mentioned, return {{"enemies": []}}"""

        try:
            result = await self.llm_client.generate_json_response(prompt)
            
            # Handle string responses or malformed JSON
            if isinstance(result, str):
                try:
                    repair_result = JSONRepair.repair_json_string(result)
                    result = repair_result.data
                    if repair_result.was_repaired:
                        print(f"  [JSON Repair] Enemies: {', '.join(repair_result.repair_details)}")
                except JSONRepairError as e:
                    print(f"  [Error] Failed to repair enemies JSON: {e}")
                    return []
            
            # Handle error responses from LLM
            if isinstance(result, dict) and 'error' in result:
                print(f"  [Error] LLM returned error for enemies: {result['error']}")
                return []
            
            enemies = []
            for enemy_data in result.get('enemies', []):
                enemies.append(Enemy(
                    name=enemy_data.get('name', 'Unknown'),
                    description=enemy_data.get('description', 'Enemy of the character')
                ))
            
            return enemies
        except Exception as e:
            print(f"Error parsing enemies: {e}")
            return []
    
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags and clean up text."""
        if not html_text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        return text.strip()


async def main_async():
    """Main async function to parse background and personality data."""
    if len(sys.argv) != 2:
        print("Usage: python parse_background_personality.py <path_to_json_file>")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    if not json_file.exists():
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    
    # Load JSON data
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)
    
    # Extract character data (handle D&D Beyond API wrapper)
    if 'data' in json_data and isinstance(json_data['data'], dict):
        data = json_data['data']
    else:
        data = json_data
    
    # Parse background and personality data
    parser = BackgroundPersonalityParser(data)
    
    print("=== D&D BEYOND BACKGROUND & PERSONALITY PARSER ===\n")
    print("Note: This parser uses LLM assistance to parse unstructured text fields.")
    print("Processing may take 10-30 seconds depending on text length...\n")
    
    try:
        # Parse all data in parallel
        result = await parser.parse_all()
        
        # Display results
        print("\n--- BACKGROUND INFO ---")
        if result['background_info']:
            bg = result['background_info']
            print(f"Background: {bg.name}")
            print(f"Feature: {bg.feature.name}")
            if bg.equipment:
                print(f"Equipment: {', '.join(bg.equipment[:5])}" + (" ..." if len(bg.equipment) > 5 else ""))
        else:
            print("No background information found")
        
        print("\n--- PERSONALITY TRAITS ---")
        if result['personality_traits']:
            pt = result['personality_traits']
            if pt.personality_traits:
                print(f"Traits: {len(pt.personality_traits)} trait(s)")
                for trait in pt.personality_traits:
                    print(f"  - {trait}")
            if pt.ideals:
                print(f"Ideals: {len(pt.ideals)} ideal(s)")
                for ideal in pt.ideals:
                    print(f"  - {ideal}")
            if pt.bonds:
                print(f"Bonds: {len(pt.bonds)} bond(s)")
                for bond in pt.bonds:
                    print(f"  - {bond}")
            if pt.flaws:
                print(f"Flaws: {len(pt.flaws)} flaw(s)")
                for flaw in pt.flaws:
                    print(f"  - {flaw}")
        else:
            print("No personality traits found")
        
        print("\n--- BACKSTORY ---")
        if result['backstory']:
            bs = result['backstory']
            print(f"Title: {bs.title}")
            print(f"Sections: {len(bs.sections)} section(s)")
            if bs.family_backstory.parents:
                parents_preview = bs.family_backstory.parents[:100] + ("..." if len(bs.family_backstory.parents) > 100 else "")
                print(f"Family - Parents: {parents_preview}")
            else:
                print(f"Family - Parents: Not specified")
        else:
            print("No backstory found")
        
        print("\n--- ORGANIZATIONS ---")
        if result['organizations']:
            print(f"Found {len(result['organizations'])} organization(s):")
            for org in result['organizations']:
                print(f"  - {org.name} ({org.role})")
        else:
            print("No organizations found")
        
        print("\n--- ALLIES ---")
        if result['allies']:
            print(f"Found {len(result['allies'])} ally/allies:")
            for ally in result['allies']:
                title_str = f" ({ally.title})" if ally.title else ""
                print(f"  - {ally.name}{title_str}")
        else:
            print("No allies found")
        
        print("\n--- ENEMIES ---")
        if result['enemies']:
            print(f"Found {len(result['enemies'])} enemy/enemies:")
            for enemy in result['enemies']:
                print(f"  - {enemy.name}")
        else:
            print("No enemies found")
        
        # Convert to serializable format
        serializable_result = {
            'background_info': asdict(result['background_info']) if result['background_info'] else None,
            'personality_traits': asdict(result['personality_traits']) if result['personality_traits'] else None,
            'backstory': asdict(result['backstory']) if result['backstory'] else None,
            'organizations': [asdict(org) for org in result['organizations']],
            'allies': [asdict(ally) for ally in result['allies']],
            'enemies': [asdict(enemy) for enemy in result['enemies']]
        }
        
        # Save to JSON file
        output_file = json_file.stem + "_background_personality_parsed.json"
        output_path = json_file.parent / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_result, f, indent=2, ensure_ascii=False)
            print(f"\n--- SAVED TO FILE ---")
            print(f"Parsed data saved to: {output_path}")
        except Exception as e:
            print(f"\nError saving to file: {e}")
        
        # Also output as JSON for console viewing
        print(f"\n--- JSON OUTPUT ---")
        print(json.dumps(serializable_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error parsing character: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Synchronous entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
