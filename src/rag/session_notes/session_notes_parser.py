"""
Session Notes Parser

Converts markdown session notes to structured SessionNote objects.
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

from .session_notes_types import (
    SessionNote, Quote, NPCInteraction, LocationVisit, Encounter,
    SpellUsage, ItemTransaction, CharacterDecision, RelationshipChange,
    CharacterGrowthMoment
)


class SessionNotesParser:
    """Parses markdown session notes into structured data"""
    
    def __init__(self):
        # Regex patterns for parsing different sections
        self.session_title_pattern = r'^# Session (?:\[(\d+)\] - |(\d+) - )(.+)$'
        self.date_pattern = r'Date: (.+)$'
        self.section_pattern = r'^## (.+)$'
        self.subsection_pattern = r'^### (.+)$'
        self.npc_pattern = r'^\*\*(.+?)\*\* - (.+)$'
        self.character_decision_pattern = r'^\*\*(.+?)\*\*: (.+)$'
        self.quote_pattern = r'^- "(.+?)" - (.+?)(?:\s+\((.+?)\))?$'
        self.spell_pattern = r'(.+?) by (.+?) - (.+)$'
        
    def parse_file(self, file_path: str) -> SessionNote:
        """Parse a markdown file into a SessionNote object"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> SessionNote:
        """Parse markdown content into a SessionNote object"""
        lines = content.split('\n')
        
        # Initialize session note
        session_note = SessionNote(
            session_number=0,
            date="",
            title="",
            summary=""
        )
        
        # Parse header information
        session_note = self._parse_header(lines, session_note)
        
        # Parse sections
        current_section = None
        current_subsection = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            
            # Check for main sections
            section_match = re.match(self.section_pattern, line)
            if section_match:
                # Process previous section
                if current_section:
                    self._process_section(current_section, section_content, session_note)
                
                current_section = section_match.group(1).lower()
                current_subsection = None
                section_content = []
                continue
            
            # Check for subsections
            subsection_match = re.match(self.subsection_pattern, line)
            if subsection_match:
                current_subsection = subsection_match.group(1).lower()
                section_content.append(('subsection', current_subsection, line))
                continue
            
            # Add content to current section
            if line and current_section:
                section_content.append(('content', current_subsection, line))
        
        # Process final section
        if current_section:
            self._process_section(current_section, section_content, session_note)
        
        return session_note
    
    def _parse_header(self, lines: List[str], session_note: SessionNote) -> SessionNote:
        """Parse session title, number, and date from header"""
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            
            # Parse session title and number
            title_match = re.match(self.session_title_pattern, line)
            if title_match:
                session_num = title_match.group(1) or title_match.group(2)
                session_note.session_number = int(session_num)
                session_note.title = title_match.group(3).strip()
            
            # Parse date
            date_match = re.match(self.date_pattern, line)
            if date_match:
                session_note.date = self._normalize_date(date_match.group(1).strip())
        
        return session_note
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        # Handle various date formats
        date_str = date_str.replace('Date: ', '').strip()
        
        # Try parsing common formats
        formats = ['%Y-%m-%d', '%m-%d-%Y', '%Y/%m/%d', '%m/%d/%Y']
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If parsing fails, return as-is
        return date_str
    
    def _process_section(self, section_name: str, content: List[Tuple], session_note: SessionNote):
        """Process a section based on its name"""
        section_name = section_name.lower()
        
        if section_name == 'summary':
            session_note.summary = self._extract_summary(content)
        elif section_name == 'key events':
            session_note.key_events = self._extract_key_events(content)
        elif section_name == 'npcs':
            session_note.npcs = self._extract_npcs(content)
        elif section_name == 'locations visited':
            session_note.locations = self._extract_locations(content)
        elif section_name in ['combat/encounters', 'encounters']:
            session_note.encounters = self._extract_encounters(content)
        elif section_name in ['spells/abilities used', 'spells used']:
            session_note.spells_used = self._extract_spells(content)
        elif section_name == 'character decisions':
            session_note.character_decisions = self._extract_character_decisions(content)
        elif section_name in ['fun moments/quotes', 'quotes', 'notable quotes']:
            session_note.quotes = self._extract_quotes(content)
        elif section_name in ['cliffhanger/next session hook', 'cliffhanger']:
            session_note.cliffhanger = self._extract_cliffhanger(content)
    
    def _extract_summary(self, content: List[Tuple]) -> str:
        """Extract session summary"""
        summary_parts = []
        for content_type, subsection, line in content:
            if content_type == 'content' and line:
                summary_parts.append(line)
        return ' '.join(summary_parts)
    
    def _extract_key_events(self, content: List[Tuple]) -> List[str]:
        """Extract key events as list"""
        events = []
        for content_type, subsection, line in content:
            if content_type == 'content' and line.startswith('- '):
                events.append(line[2:].strip())
        return events
    
    def _extract_npcs(self, content: List[Tuple]) -> Dict[str, NPCInteraction]:
        """Extract NPC interactions"""
        npcs = {}
        for content_type, subsection, line in content:
            if content_type == 'content' and line.startswith('- '):
                # Handle bullet point format: - **Name** - description
                line_content = line[2:].strip()  # Remove "- "
                npc_match = re.match(self.npc_pattern, line_content)
                if npc_match:
                    npc_name = npc_match.group(1).strip()
                    description = npc_match.group(2).strip()
                    npcs[npc_name] = NPCInteraction(
                        npc_name=npc_name,
                        interaction_type="general",
                        description=description
                    )
        return npcs
    
    def _extract_locations(self, content: List[Tuple]) -> List[LocationVisit]:
        """Extract location visits"""
        locations = []
        for content_type, subsection, line in content:
            if content_type == 'content' and line.startswith('- '):
                # Handle bullet point format: - **Name** - description
                line_content = line[2:].strip()  # Remove "- "
                location_match = re.match(self.npc_pattern, line_content)  # Same pattern as NPCs
                if location_match:
                    location_name = location_match.group(1).strip()
                    description = location_match.group(2).strip()
                    locations.append(LocationVisit(
                        location_name=location_name,
                        description=description
                    ))
        return locations
    
    def _extract_encounters(self, content: List[Tuple]) -> List[Encounter]:
        """Extract combat encounters"""
        encounters = []
        for content_type, subsection, line in content:
            if content_type == 'content' and line.startswith('- '):
                encounter_text = line[2:].strip()
                encounters.append(Encounter(
                    encounter_type="combat",
                    description=encounter_text
                ))
        return encounters
    
    def _extract_spells(self, content: List[Tuple]) -> List[SpellUsage]:
        """Extract spell usage"""
        spells = []
        for content_type, subsection, line in content:
            if content_type == 'content' and line.startswith('- '):
                spell_text = line[2:].strip()
                spell_match = re.match(self.spell_pattern, spell_text)
                if spell_match:
                    spell_name = spell_match.group(1).strip()
                    caster = spell_match.group(2).strip()
                    outcome = spell_match.group(3).strip()
                    spells.append(SpellUsage(
                        spell_name=spell_name,
                        caster=caster,
                        outcome=outcome
                    ))
                else:
                    # Fallback parsing
                    parts = spell_text.split(' by ')
                    if len(parts) >= 2:
                        spell_name = parts[0].strip()
                        caster = parts[1].strip()
                        spells.append(SpellUsage(
                            spell_name=spell_name,
                            caster=caster
                        ))
        return spells
    
    def _extract_character_decisions(self, content: List[Tuple]) -> Dict[str, List[CharacterDecision]]:
        """Extract character decisions"""
        decisions = {}
        for content_type, subsection, line in content:
            if content_type == 'content' and line.startswith('- '):
                # Handle bullet point format: - **Character**: decision description
                line_content = line[2:].strip()  # Remove "- "
                decision_match = re.match(self.character_decision_pattern, line_content)
                if decision_match:
                    character = decision_match.group(1).strip()
                    decision_text = decision_match.group(2).strip()
                    
                    if character not in decisions:
                        decisions[character] = []
                    
                    decisions[character].append(CharacterDecision(
                        character_name=character,
                        decision_description=decision_text,
                        context=""
                    ))
        return decisions
    
    def _extract_quotes(self, content: List[Tuple]) -> List[Quote]:
        """Extract memorable quotes"""
        quotes = []
        for content_type, subsection, line in content:
            if content_type == 'content':
                quote_match = re.match(self.quote_pattern, line)
                if quote_match:
                    quote_text = quote_match.group(1).strip()
                    speaker = quote_match.group(2).strip()
                    context = quote_match.group(3).strip() if quote_match.group(3) else None
                    quotes.append(Quote(
                        text=quote_text,
                        speaker=speaker,
                        context=context
                    ))
        return quotes
    
    def _extract_cliffhanger(self, content: List[Tuple]) -> str:
        """Extract cliffhanger/next session hook"""
        cliffhanger_parts = []
        for content_type, subsection, line in content:
            if content_type == 'content' and line:
                cliffhanger_parts.append(line)
        return ' '.join(cliffhanger_parts)


def parse_session_notes_directory(directory_path: str) -> List[SessionNote]:
    """Parse all session note files in a directory"""
    parser = SessionNotesParser()
    session_notes = []
    
    directory = Path(directory_path)
    for file_path in directory.glob("*.md"):
        try:
            session_note = parser.parse_file(str(file_path))
            session_notes.append(session_note)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    
    # Sort by session number
    session_notes.sort(key=lambda x: x.session_number)
    return session_notes