"""
Session Notes Markdown Parser

Parses structured markdown session notes into SessionNotes dataclasses.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

from .session_types import (
    SessionNotes, Entity, EntityType, CharacterStatus, CombatEncounter,
    SpellAbilityUse, CharacterDecision, Memory, QuestObjective, SessionEvent
)


class SessionNotesParser:
    """Parser for structured markdown session notes"""
    
    def __init__(self):
        self.current_session: Optional[SessionNotes] = None
        self.raw_sections: Dict[str, str] = {}
    
    def parse_file(self, file_path: Path) -> SessionNotes:
        """Parse a single markdown file into a SessionNotes object"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content, file_path.stem)
    
    def parse_content(self, content: str, filename: str = "") -> SessionNotes:
        """Parse markdown content into a SessionNotes object"""
        lines = content.split('\n')
        
        # Initialize session notes with defaults
        session_number = self._extract_session_number(lines, filename)
        title = self._extract_title(lines)
        date = self._extract_date(lines)
        
        self.current_session = SessionNotes(
            session_number=session_number,
            date=date,
            title=title,
            summary=""
        )
        
        # Parse sections
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith('## '):
                # Process previous section
                if current_section and section_content:
                    self._process_section(current_section, section_content)
                
                # Start new section
                current_section = line[3:].strip()
                section_content = []
            else:
                section_content.append(line)
        
        # Process final section
        if current_section and section_content:
            self._process_section(current_section, section_content)
        
        return self.current_session
    
    def _extract_session_number(self, lines: List[str], filename: str) -> int:
        """Extract session number from title or filename"""
        for line in lines:
            if line.startswith('# Session'):
                match = re.search(r'Session\s*\[?(\d+)\]?', line)
                if match:
                    return int(match.group(1))
        
        # Try to extract from filename
        match = re.search(r'(\d+)', filename)
        if match:
            return int(match.group(1))
        
        return 0
    
    def _extract_title(self, lines: List[str]) -> str:
        """Extract session title from the first heading"""
        for line in lines:
            if line.startswith('# Session'):
                # Extract everything after "Session [number] - "
                match = re.search(r'Session\s*\[?\d+\]?\s*-\s*(.+)', line)
                if match:
                    return match.group(1).strip()
                return line[1:].strip()
        return "Untitled Session"
    
    def _extract_date(self, lines: List[str]) -> datetime:
        """Extract date from the Date: line"""
        for line in lines:
            if line.startswith('Date:'):
                date_str = line[5:].strip()
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    # Try alternative formats
                    try:
                        return datetime.strptime(date_str, '%Y-%m-%d (%A, %B)')
                    except ValueError:
                        pass
        
        return datetime.now()
    
    def _process_section(self, section_name: str, content: List[str]) -> None:
        """Process a section based on its name"""
        content_text = '\n'.join(content).strip()
        
        # Store raw section
        self.raw_sections[section_name] = content_text
        
        # Route to specific parsers
        if section_name == "Summary":
            self.current_session.summary = content_text
        
        elif section_name == "Player Characters Present":
            self._parse_player_characters(content)
        
        elif section_name == "NPCs Encountered":
            self._parse_npcs(content)
        
        elif section_name == "Locations Visited":
            self._parse_locations(content)
        
        elif section_name == "Key Events":
            self._parse_key_events(content)
        
        elif section_name == "Combat Encounters":
            self._parse_combat_encounters(content)
        
        elif section_name == "Spells & Abilities Used":
            self._parse_spells_abilities(content)
        
        elif section_name == "Character Decisions & Motivations":
            self._parse_character_decisions(content)
        
        elif section_name == "Memories, Visions & Dreams":
            self._parse_memories_visions(content)
        
        elif section_name == "Quest & Objective Updates":
            self._parse_quest_updates(content)
        
        elif section_name == "Loot & Rewards":
            self._parse_loot_rewards(content)
        
        elif section_name == "Death & Revival Events":
            self._parse_death_revival(content)
        
        elif section_name == "Divine & Religious Elements":
            self._parse_divine_religious(content)
        
        elif section_name == "Party Dynamics":
            self._parse_party_dynamics(content)
        
        elif section_name == "Memorable Quotes":
            self._parse_memorable_quotes(content)
        
        elif section_name == "Fun Moments":
            self._parse_fun_moments(content)
        
        elif section_name == "Rules Clarifications":
            self._parse_rules_clarifications(content)
        
        elif section_name == "DM Notes":
            self._parse_dm_notes(content)
        
        elif section_name in ["Cliffhanger/Session End", "Session End"]:
            self._parse_cliffhanger(content)
        
        elif section_name == "Next Session Hooks":
            self._parse_next_session_hooks(content)
        
        # Store in raw_sections for any complex content
        self.current_session.raw_sections[section_name] = content_text
    
    def _parse_player_characters(self, content: List[str]) -> None:
        """Parse player character information"""
        for line in content:
            if line.strip().startswith('- **'):
                char_match = re.search(r'\*\*([^*]+)\*\*', line)
                if char_match:
                    char_name = char_match.group(1)
                    entity = Entity(
                        name=char_name,
                        entity_type=EntityType.PC,
                        first_appearance=self.current_session.session_number
                    )
                    self.current_session.player_characters.append(entity)
                    
                    # Parse character status if present
                    status = self._parse_character_status_from_line(line, char_name)
                    if status:
                        self.current_session.character_statuses[char_name] = status
    
    def _parse_character_status_from_line(self, line: str, char_name: str) -> Optional[CharacterStatus]:
        """Extract character status from a line"""
        status = CharacterStatus(session_number=self.current_session.session_number)
        
        # HP extraction
        hp_match = re.search(r'HP:\s*(\d+)/(\d+)', line)
        if hp_match:
            status.hp_current = int(hp_match.group(1))
            status.hp_max = int(hp_match.group(2))
        
        # Status extraction
        if 'Status:' in line:
            status_match = re.search(r'Status:\s*([^-\n]+)', line)
            if status_match:
                status_text = status_match.group(1).strip()
                status.is_alive = 'dead' not in status_text.lower()
        
        # Location extraction
        if 'Location:' in line:
            loc_match = re.search(r'Location:\s*([^-\n]+)', line)
            if loc_match:
                status.location = loc_match.group(1).strip()
        
        return status
    
    def _parse_npcs(self, content: List[str]) -> None:
        """Parse NPC information"""
        for line in content:
            if line.strip().startswith('- **'):
                npc_match = re.search(r'\*\*([^*]+)\*\*', line)
                if npc_match:
                    npc_name = npc_match.group(1)
                    entity = Entity(
                        name=npc_name,
                        entity_type=EntityType.NPC,
                        first_appearance=self.current_session.session_number
                    )
                    
                    # Extract description from the line
                    if ' - ' in line:
                        description = line.split(' - ', 1)[1].strip()
                        entity.description = description
                    
                    self.current_session.npcs.append(entity)
    
    def _parse_locations(self, content: List[str]) -> None:
        """Parse location information"""
        for line in content:
            if line.strip().startswith('- **'):
                loc_match = re.search(r'\*\*([^*]+)\*\*', line)
                if loc_match:
                    loc_name = loc_match.group(1)
                    entity = Entity(
                        name=loc_name,
                        entity_type=EntityType.LOCATION,
                        first_appearance=self.current_session.session_number
                    )
                    
                    # Extract description
                    if ' - ' in line:
                        description = line.split(' - ', 1)[1].strip()
                        entity.description = description
                    
                    self.current_session.locations.append(entity)
    
    def _parse_key_events(self, content: List[str]) -> None:
        """Parse key events section"""
        current_event = None
        event_content = []
        
        for line in content:
            if line.startswith('### '):
                # Save previous event
                if current_event:
                    self._finalize_event(current_event, event_content)
                
                # Start new event
                event_title = line[4:].strip()
                current_event = SessionEvent(
                    session_number=self.current_session.session_number,
                    description=event_title,
                    event_type="general",
                    participants=[]
                )
                event_content = []
            else:
                event_content.append(line)
        
        # Save final event
        if current_event:
            self._finalize_event(current_event, event_content)
    
    def _finalize_event(self, event: SessionEvent, content: List[str]) -> None:
        """Finalize an event with its content"""
        content_text = '\n'.join(content).strip()
        
        # Update description with full content
        if content_text:
            event.description += '\n' + content_text
        
        # Extract structured information
        for line in content:
            if line.strip().startswith('- **Time**:'):
                event.timestamp = line.split(':', 1)[1].strip()
            elif line.strip().startswith('- **Location**:'):
                event.location = line.split(':', 1)[1].strip()
            elif line.strip().startswith('- **Outcome**:'):
                outcome = line.split(':', 1)[1].strip()
                event.outcomes.append(outcome)
        
        self.current_session.key_events.append(event)
    
    def _parse_combat_encounters(self, content: List[str]) -> None:
        """Parse combat encounters"""
        current_encounter = None
        
        for line in content:
            if line.startswith('### '):
                if current_encounter:
                    self.current_session.combat_encounters.append(current_encounter)
                
                encounter_name = line[4:].strip()
                current_encounter = CombatEncounter(enemies=[])
                # Parse enemy names from title if format is "Encounter 1: Enemy Name"
                if ':' in encounter_name:
                    enemy_name = encounter_name.split(':', 1)[1].strip()
                    enemy = Entity(name=enemy_name, entity_type=EntityType.CREATURE)
                    current_encounter.enemies.append(enemy)
            
            elif current_encounter and line.strip().startswith('- **'):
                self._parse_combat_detail(line, current_encounter)
        
        if current_encounter:
            self.current_session.combat_encounters.append(current_encounter)
    
    def _parse_combat_detail(self, line: str, encounter: CombatEncounter) -> None:
        """Parse a specific combat detail line"""
        if '**Location**:' in line:
            encounter.location = line.split(':', 1)[1].strip()
        elif '**Outcome**:' in line:
            encounter.outcome = line.split(':', 1)[1].strip()
        elif '**Killing Blow**:' in line:
            encounter.killing_blow = line.split(':', 1)[1].strip()
    
    def _parse_spells_abilities(self, content: List[str]) -> None:
        """Parse spells and abilities used"""
        for line in content:
            if line.strip().startswith('- **'):
                spell_match = re.search(r'\*\*([^*]+)\*\*.*Cast by:\s*([^-\n]+)', line)
                if spell_match:
                    spell_name = spell_match.group(1)
                    caster = spell_match.group(2).strip()
                    
                    spell_use = SpellAbilityUse(
                        name=spell_name,
                        caster=caster
                    )
                    self.current_session.spells_abilities_used.append(spell_use)
    
    def _parse_character_decisions(self, content: List[str]) -> None:
        """Parse character decisions and motivations"""
        current_character = None
        decision_content = []
        
        for line in content:
            if line.startswith('### '):
                if current_character and decision_content:
                    self._finalize_character_decision(current_character, decision_content)
                
                current_character = line[4:].strip()
                decision_content = []
            else:
                decision_content.append(line)
        
        if current_character and decision_content:
            self._finalize_character_decision(current_character, decision_content)
    
    def _finalize_character_decision(self, character: str, content: List[str]) -> None:
        """Finalize a character decision"""
        decision_text = ""
        context = ""
        motivation = ""
        consequences = ""
        
        for line in content:
            if line.strip().startswith('- **Decision**:'):
                decision_text = line.split(':', 1)[1].strip()
            elif line.strip().startswith('- **Context**:'):
                context = line.split(':', 1)[1].strip()
            elif line.strip().startswith('- **Motivation**:'):
                motivation = line.split(':', 1)[1].strip()
            elif line.strip().startswith('- **Consequences**:'):
                consequences = line.split(':', 1)[1].strip()
        
        if decision_text:
            decision = CharacterDecision(
                character=character,
                decision=decision_text,
                context=context,
                consequences=consequences if consequences else None,
                motivation=motivation if motivation else None
            )
            self.current_session.character_decisions.append(decision)
    
    def _parse_memories_visions(self, content: List[str]) -> None:
        """Parse memories, visions, and dreams"""
        current_memory = None
        memory_content = []
        
        for line in content:
            if line.startswith('### '):
                if current_memory and memory_content:
                    self._finalize_memory(current_memory, memory_content)
                
                # Extract character and memory type from title
                title = line[4:].strip()
                if "'s " in title:
                    parts = title.split("'s ", 1)
                    character = parts[0]
                    memory_type = parts[1] if len(parts) > 1 else "memory"
                else:
                    character = "Unknown"
                    memory_type = title
                
                current_memory = Memory(
                    character=character,
                    memory_type=memory_type,
                    content=""
                )
                memory_content = []
            else:
                memory_content.append(line)
        
        if current_memory and memory_content:
            self._finalize_memory(current_memory, memory_content)
    
    def _finalize_memory(self, memory: Memory, content: List[str]) -> None:
        """Finalize a memory/vision"""
        content_text = ""
        
        for line in content:
            if line.strip().startswith('- **Content**:'):
                content_text = line.split(':', 1)[1].strip()
            elif line.strip().startswith('- **Emotional Context**:'):
                memory.emotional_context = line.split(':', 1)[1].strip()
            elif line.strip().startswith('- **Significance**:'):
                memory.significance = line.split(':', 1)[1].strip()
        
        if not content_text:
            content_text = '\n'.join(content).strip()
        
        memory.content = content_text
        self.current_session.memories_visions.append(memory)
    
    def _parse_quest_updates(self, content: List[str]) -> None:
        """Parse quest and objective updates"""
        # This would parse quest information - simplified for now
        quest_text = '\n'.join(content).strip()
        if quest_text:
            # Store in raw_sections for now, could be expanded later
            self.current_session.raw_sections["Quest Updates"] = quest_text
    
    def _parse_loot_rewards(self, content: List[str]) -> None:
        """Parse loot and rewards"""
        current_character = None
        
        for line in content:
            if line.strip().startswith('- **') and '**:' in line:
                # Character heading
                char_match = re.search(r'\*\*([^*]+)\*\*:', line)
                if char_match:
                    current_character = char_match.group(1)
                    if current_character not in self.current_session.loot_obtained:
                        self.current_session.loot_obtained[current_character] = []
            elif line.strip().startswith('  - ') and current_character:
                # Item under character
                item = line.strip()[4:].strip()
                self.current_session.loot_obtained[current_character].append(item)
    
    def _parse_death_revival(self, content: List[str]) -> None:
        """Parse death and revival events"""
        content_text = '\n'.join(content).strip()
        
        # Look for death events
        if 'Deaths' in content_text or 'death' in content_text.lower():
            # Parse death information - simplified
            death_info = {"content": content_text, "session": self.current_session.session_number}
            self.current_session.deaths.append(death_info)
        
        # Look for revival events
        if 'Revival' in content_text or 'revival' in content_text.lower():
            revival_info = {"content": content_text, "session": self.current_session.session_number}
            self.current_session.revivals.append(revival_info)
    
    def _parse_divine_religious(self, content: List[str]) -> None:
        """Parse divine and religious elements"""
        for line in content:
            if 'divine' in line.lower() or 'intervention' in line.lower():
                self.current_session.divine_interventions.append(line.strip())
            if 'religious' in line.lower() or 'ritual' in line.lower():
                self.current_session.religious_elements.append(line.strip())
    
    def _parse_party_dynamics(self, content: List[str]) -> None:
        """Parse party dynamics"""
        for line in content:
            if 'conflict' in line.lower():
                self.current_session.party_conflicts.append(line.strip())
            elif 'bond' in line.lower() or 'friendship' in line.lower():
                self.current_session.party_bonds.append(line.strip())
    
    def _parse_memorable_quotes(self, content: List[str]) -> None:
        """Parse memorable quotes"""
        for line in content:
            if line.strip().startswith('- "') and '" - ' in line:
                # Format: - "quote" - Speaker, Context: context
                parts = line.split('" - ', 1)
                if len(parts) == 2:
                    quote = parts[0][3:]  # Remove '- "'
                    speaker_context = parts[1]
                    
                    if ', Context:' in speaker_context:
                        speaker, context = speaker_context.split(', Context:', 1)
                    else:
                        speaker = speaker_context
                        context = ""
                    
                    quote_dict = {
                        "speaker": speaker.strip(),
                        "quote": quote,
                        "context": context.strip()
                    }
                    self.current_session.quotes.append(quote_dict)
    
    def _parse_fun_moments(self, content: List[str]) -> None:
        """Parse fun moments"""
        for line in content:
            if line.strip().startswith('- '):
                moment = line.strip()[2:].strip()
                if moment:
                    self.current_session.funny_moments.append(moment)
    
    def _parse_rules_clarifications(self, content: List[str]) -> None:
        """Parse rules clarifications"""
        for line in content:
            if line.strip().startswith('- '):
                rule = line.strip()[2:].strip()
                if rule:
                    self.current_session.rules_clarifications.append(rule)
    
    def _parse_dm_notes(self, content: List[str]) -> None:
        """Parse DM notes"""
        for line in content:
            if line.strip().startswith('- '):
                note = line.strip()[2:].strip()
                if note:
                    self.current_session.dm_notes.append(note)
    
    def _parse_cliffhanger(self, content: List[str]) -> None:
        """Parse cliffhanger/session end"""
        content_text = '\n'.join(content).strip()
        
        # Look for cliffhanger specifically
        for line in content:
            if line.strip().startswith('**Cliffhanger**:'):
                self.current_session.cliffhanger = line.split(':', 1)[1].strip()
                break
        
        if not self.current_session.cliffhanger and content_text:
            self.current_session.cliffhanger = content_text
    
    def _parse_next_session_hooks(self, content: List[str]) -> None:
        """Parse next session hooks"""
        hooks = []
        for line in content:
            if line.strip().startswith('- '):
                hook = line.strip()[2:].strip()
                if hook:
                    hooks.append(hook)
        
        if hooks:
            self.current_session.next_session_hook = '; '.join(hooks)


def parse_session_notes_directory(directory_path: str) -> List[SessionNotes]:
    """Parse all markdown files in a directory into SessionNotes objects"""
    directory = Path(directory_path)
    parser = SessionNotesParser()
    session_notes = []
    
    # Find all markdown files
    md_files = list(directory.glob("*.md"))
    md_files.sort()  # Sort to process in order
    
    for md_file in md_files:
        try:
            session_note = parser.parse_file(md_file)
            session_notes.append(session_note)
            print(f"✓ Parsed {md_file.name}: Session {session_note.session_number}")
        except Exception as e:
            print(f"✗ Error parsing {md_file.name}: {e}")
    
    return session_notes