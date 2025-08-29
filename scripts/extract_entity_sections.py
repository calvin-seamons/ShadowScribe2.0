"""
Script to extract specific sections from the D&D 5e rulebook for entity extractor analysis.

This script extracts the raw text from sections that correspond to each entity extractor function,
allowing for analysis of content patterns and improved parsing logic.
"""

import sys
from pathlib import Path

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, List, Tuple


def find_section_boundaries(content: str) -> Dict[str, Tuple[int, int]]:
    """Find the start and end line numbers for each major section."""
    lines = content.split('\n')
    sections = {}
    
    # Find all sections with their start lines
    for i, line in enumerate(lines):
        if line.startswith('# ') and '{#chapter-' in line:
            # Extract chapter ID
            start = line.find('{#') + 2
            end = line.find('}', start)
            if start > 1 and end > start:
                chapter_id = line[start:end]
                sections[chapter_id] = (i + 1, None)  # Store 1-based line numbers
        elif line.startswith('## ') and '{#section-' in line:
            # Extract section ID
            start = line.find('{#') + 2
            end = line.find('}', start)
            if start > 1 and end > start:
                section_id = line[start:end]
                sections[section_id] = (i + 1, None)  # Store 1-based line numbers
    
    # Sort sections by start line
    sorted_sections = sorted(sections.items(), key=lambda x: x[1][0])
    
    # Set end boundaries
    final_sections = {}
    for i, (section_id, (start_line, _)) in enumerate(sorted_sections):
        if i + 1 < len(sorted_sections):
            next_start = sorted_sections[i + 1][1][0]
            end_line = next_start - 1
        else:
            # Last section goes to end of file
            end_line = len(lines)
        
        final_sections[section_id] = (start_line, end_line)
    
    return final_sections


def extract_section_content(content: str, start_line: int, end_line: int) -> str:
    """Extract content between specific line numbers (1-based)."""
    lines = content.split('\n')
    # Convert to 0-based indexing for slicing
    section_lines = lines[start_line - 1:end_line]
    return '\n'.join(section_lines)


def extract_entity_sections():
    """Extract sections corresponding to each entity extractor function."""
    
    # Read the rulebook
    rulebook_path = project_root / "knowledge_base" / "dnd5rulebook.md"
    if not rulebook_path.exists():
        print(f"Error: Rulebook not found at {rulebook_path}")
        return
    
    print(f"Reading rulebook from: {rulebook_path}")
    with open(rulebook_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find section boundaries
    sections = find_section_boundaries(content)
    print(f"Found {len(sections)} sections in rulebook")
    
    # Create output directory
    output_dir = project_root / "entity_analysis"
    output_dir.mkdir(exist_ok=True)
    
    # Define extraction logic for each entity type
    extractions = {
        "_extract_races.txt": {
            "chapter": "chapter-races", 
            "description": "races chapter and all race subsections"
        },
        "_extract_classes.txt": {
            "chapter": "chapter-classes",
            "description": "classes chapter and all class subsections"
        },
        "_extract_spells.txt": {
            "sections": ["chapter-spellcasting", "chapter-spell-lists", "section-spell-descriptions"],
            "description": "spellcasting, spell lists, and spell descriptions"
        },
        "_extract_conditions.txt": {
            "sections": ["section-conditions"],
            "description": "conditions section"
        }
    }
    
    # Extract each entity type
    for output_filename, config in extractions.items():
        print(f"\nExtracting {output_filename}...")
        combined_content = []
        
        # Method 1: Extract by chapter (includes all subsections)
        if "chapter" in config:
            chapter_id = config["chapter"]
            
            # Find the chapter start and next chapter start
            chapter_start = None
            next_chapter_start = None
            
            # Get all chapter positions sorted by line number
            chapters = [(name, start, end) for name, (start, end) in sections.items() if name.startswith('chapter-')]
            chapters.sort(key=lambda x: x[1])
            
            for i, (name, start, end) in enumerate(chapters):
                if name == chapter_id:
                    chapter_start = start
                    if i + 1 < len(chapters):
                        next_chapter_start = chapters[i + 1][1]
                    else:
                        # Last chapter - goes to end
                        with open(rulebook_path, 'r', encoding='utf-8') as f:
                            next_chapter_start = len(f.readlines()) + 1
                    break
            
            if chapter_start:
                end_line = next_chapter_start - 1 if next_chapter_start else len(content.split('\n'))
                section_content = extract_section_content(content, chapter_start, end_line)
                
                combined_content.append(f"=== {chapter_id.upper()} AND SUBSECTIONS ===\n")
                combined_content.append(section_content)
                combined_content.append(f"\n=== END {chapter_id.upper()} ===\n\n")
                
                print(f"  Found {chapter_id}: lines {chapter_start}-{end_line} ({end_line - chapter_start + 1} lines)")
            else:
                print(f"  WARNING: Chapter '{chapter_id}' not found")
        
        # Method 2: Extract specific sections
        elif "sections" in config:
            for section_id in config["sections"]:
                if section_id in sections:
                    start_line, end_line = sections[section_id]
                    section_content = extract_section_content(content, start_line, end_line)
                    
                    combined_content.append(f"=== {section_id.upper()} ===\n")
                    combined_content.append(section_content)
                    combined_content.append(f"\n=== END {section_id.upper()} ===\n\n")
                    
                    print(f"  Found {section_id}: lines {start_line}-{end_line} ({end_line - start_line + 1} lines)")
                else:
                    print(f"  WARNING: Section '{section_id}' not found in rulebook")
        
        if combined_content:
            output_path = output_dir / output_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(''.join(combined_content))
            print(f"  Saved to: {output_path}")
            print(f"  Description: {config['description']}")
        else:
            print(f"  No content found for {output_filename}")
    
    # Print summary of all available sections for reference
    print(f"\n=== AVAILABLE SECTIONS (First 20) ===")
    sorted_sections = sorted(sections.items(), key=lambda x: x[1][0])
    for i, (section_id, (start_line, end_line)) in enumerate(sorted_sections[:20]):
        line_count = end_line - start_line + 1 if end_line else "unknown"
        print(f"{section_id:30} lines {start_line:5}-{end_line:5} ({line_count:6} lines)")
    
    if len(sorted_sections) > 20:
        print(f"... and {len(sorted_sections) - 20} more sections")


if __name__ == "__main__":
    extract_entity_sections()
