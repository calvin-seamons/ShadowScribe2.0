"""
Gazetteer-based Entity Extractor using Fuzzy Matching.

Uses fuzzy string matching against known D&D 5e SRD entities for reliable
entity extraction in a closed domain.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from difflib import SequenceMatcher

# Use try/except for sklearn as it may not be installed
try:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
except ImportError:
    # Fallback minimal set of stop words
    ENGLISH_STOP_WORDS = frozenset({
        'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few',
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now',
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
        'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
        'who', 'whom', 'this', 'that', 'these', 'those', 'am'
    })


@dataclass
class Entity:
    """Extracted entity with type and confidence."""
    text: str           # The matched text from the query
    canonical: str      # The canonical entity name
    type: str          # Entity type (SPELL, CLASS, etc.)
    confidence: float  # Match confidence (0.0 - 1.0)
    start: int         # Start position in query
    end: int           # End position in query


class GazetteerEntityExtractor:
    """
    Extract D&D entities from text using fuzzy matching against known gazetteers.
    
    Uses a two-phase approach:
    1. Exact substring matching (fast, high precision)
    2. Fuzzy matching for misspellings (slower, catches typos)
    """
    
    # Mapping from SRD cache file to entity type
    GAZETTEER_MAPPING = {
        'spells': 'SPELL',
        'classes': 'CLASS',
        'subclasses': 'CLASS',
        'races': 'RACE',
        'monsters': 'CREATURE',
        'equipment': 'ITEM',
        'magic-items': 'ITEM',
        'conditions': 'CONDITION',
        'damage-types': 'DAMAGE_TYPE',
        'skills': 'SKILL',
        'features': 'FEAT',
        'traits': 'FEAT',
        'backgrounds': 'BACKGROUND',
        'ability-scores': 'ABILITY',
    }
    
    # D&D-specific common words that aren't entity names
    DND_SKIP_WORDS: Set[str] = {
        'cast', 'casting', 'casts', 'damage', 'damages', 'damaging',
        'range', 'ranged', 'attack', 'attacks', 'attacking',
        'spell', 'spells', 'class', 'classes', 'level', 'levels',
        'roll', 'rolls', 'rolling', 'hit', 'hits', 'hitting',
        'save', 'saves', 'saving', 'check', 'checks', 'checking',
        'ability', 'abilities', 'score', 'scores', 'modifier', 'modifiers',
        'bonus', 'bonuses', 'action', 'actions', 'reaction', 'reactions',
        'target', 'targets', 'targeting', 'creature', 'creatures',
        'character', 'characters', 'player', 'players', 'enemy', 'enemies',
        'effect', 'effects', 'duration', 'concentration', 'concentrating',
        'weapon', 'weapons', 'armor', 'armors', 'shield', 'shields',
        'melee', 'dice', 'die', 'round', 'rounds', 'turn', 'turns',
        'slot', 'slots', 'component', 'components', 'verbal', 'somatic',
        'material', 'ritual', 'cantrip', 'cantrips', 'feature', 'features',
        'trait', 'traits', 'proficiency', 'proficiencies', 'proficient',
        'resistance', 'resistances', 'immunity', 'immunities', 'vulnerable',
        'advantage', 'disadvantage', 'succeed', 'fail', 'success', 'failure',
    }
    
    def __init__(self, cache_path: Path, min_similarity: float = 0.85):
        """
        Initialize with path to SRD cache directory.
        
        Args:
            cache_path: Path to data/srd_cache/
            min_similarity: Minimum similarity score for fuzzy matching (0.0-1.0)
        """
        self.cache_path = Path(cache_path)
        self.min_similarity = min_similarity
        self.gazetteers: Dict[str, Tuple[str, str]] = {}  # {lowercase_name: (canonical_name, type)}
        self.skip_words: Set[str] = set(ENGLISH_STOP_WORDS) | self.DND_SKIP_WORDS
        self._load_gazetteers()
    
    def _load_gazetteers(self) -> None:
        """Load all entity gazetteers from SRD cache."""
        self.gazetteers = {}
        
        for filename, entity_type in self.GAZETTEER_MAPPING.items():
            filepath = self.cache_path / f"{filename}.json"
            if not filepath.exists():
                continue
            
            try:
                with open(filepath) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue
            
            # Handle different file structures
            if 'results' in data:
                entities = data['results']
            elif isinstance(data, list):
                entities = data
            else:
                continue
            
            for entity in entities:
                if isinstance(entity, dict) and 'name' in entity:
                    name = entity['name']
                    self.gazetteers[name.lower()] = (name, entity_type)
        
        print(f"[GazetteerNER] Loaded {len(self.gazetteers)} entities from gazetteers")
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    
    def _find_exact_matches(self, text: str) -> List[Entity]:
        """Find exact substring matches (case-insensitive)."""
        entities = []
        text_lower = text.lower()
        
        # Sort by length (longest first) to prefer longer matches
        sorted_names = sorted(self.gazetteers.keys(), key=len, reverse=True)
        
        # Track matched spans to avoid overlaps
        matched_spans: List[Tuple[int, int]] = []
        
        for name_lower in sorted_names:
            canonical, entity_type = self.gazetteers[name_lower]
            
            # Find all occurrences
            start = 0
            while True:
                idx = text_lower.find(name_lower, start)
                if idx == -1:
                    break
                
                end = idx + len(name_lower)
                
                # Check word boundaries
                before_ok = idx == 0 or not text[idx-1].isalnum()
                after_ok = end == len(text) or not text[end].isalnum()
                
                # Check for overlap with existing matches
                overlaps = any(
                    not (end <= s or idx >= e) 
                    for s, e in matched_spans
                )
                
                if before_ok and after_ok and not overlaps:
                    entities.append(Entity(
                        text=text[idx:end],
                        canonical=canonical,
                        type=entity_type,
                        confidence=1.0,
                        start=idx,
                        end=end
                    ))
                    matched_spans.append((idx, end))
                
                start = end
        
        return entities
    
    def _find_fuzzy_matches(self, text: str, exact_spans: List[Tuple[int, int]]) -> List[Entity]:
        """Find fuzzy matches for words not already matched."""
        entities = []
        
        # Tokenize into words with positions
        words = []
        for match in re.finditer(r'\b\w+\b', text):
            word = match.group()
            if word.lower() in self.skip_words:
                continue
            start, end = match.span()
            # Skip if overlaps with exact match
            if any(not (end <= s or start >= e) for s, e in exact_spans):
                continue
            words.append((word, start, end))
        
        # Build phrases (1-3 words)
        phrases = []
        for i in range(len(words)):
            phrases.append(words[i])
            if i + 1 < len(words):
                w1, s1, e1 = words[i]
                w2, s2, e2 = words[i+1]
                if s2 - e1 <= 2:
                    phrases.append((f"{w1} {w2}", s1, e2))
            if i + 2 < len(words):
                w1, s1, e1 = words[i]
                w2, s2, e2 = words[i+1]
                w3, s3, e3 = words[i+2]
                if s2 - e1 <= 2 and s3 - e2 <= 2:
                    phrases.append((f"{w1} {w2} {w3}", s1, e3))
        
        # Check each phrase against gazetteers
        for phrase, start, end in phrases:
            if len(phrase) < 4:
                continue
            if ' ' not in phrase and len(phrase) < 5:
                continue
            
            best_match: Optional[Tuple[str, str]] = None
            best_score = 0.0
            
            for name_lower, (canonical, entity_type) in self.gazetteers.items():
                len_ratio = len(phrase) / len(name_lower) if len(name_lower) > 0 else 0
                if len_ratio < 0.6 or len_ratio > 1.7:
                    continue
                    
                score = self._similarity(phrase, name_lower)
                if score >= self.min_similarity and score > best_score:
                    best_score = score
                    best_match = (canonical, entity_type)
            
            if best_match:
                entities.append(Entity(
                    text=phrase,
                    canonical=best_match[0],
                    type=best_match[1],
                    confidence=best_score,
                    start=start,
                    end=end
                ))
        
        return entities
    
    def _deduplicate_overlapping(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, preferring higher confidence and longer spans."""
        if not entities:
            return []
        
        sorted_entities = sorted(
            entities,
            key=lambda e: (-e.confidence, -(e.end - e.start), e.start)
        )
        
        kept = []
        kept_spans: List[Tuple[int, int]] = []
        
        for entity in sorted_entities:
            overlaps = any(
                not (entity.end <= s or entity.start >= e)
                for s, e in kept_spans
            )
            
            if not overlaps:
                kept.append(entity)
                kept_spans.append((entity.start, entity.end))
        
        return kept
    
    def extract(self, text: str, use_fuzzy: bool = True) -> List[Entity]:
        """
        Extract all entities from text.
        
        Args:
            text: The query text to extract entities from
            use_fuzzy: Whether to use fuzzy matching for typos
            
        Returns:
            List of Entity objects, sorted by position
        """
        entities = self._find_exact_matches(text)
        exact_spans = [(e.start, e.end) for e in entities]
        
        if use_fuzzy:
            fuzzy_entities = self._find_fuzzy_matches(text, exact_spans)
            entities.extend(fuzzy_entities)
        
        entities = self._deduplicate_overlapping(entities)
        entities.sort(key=lambda e: e.start)
        
        return entities
    
    def extract_simple(self, text: str) -> List[Dict[str, str]]:
        """
        Simple extraction returning just text and type.
        
        Returns:
            List of dicts with 'text', 'type', 'canonical', and 'confidence' keys
        """
        entities = self.extract(text)
        return [
            {
                'text': e.text,
                'type': e.type,
                'canonical': e.canonical,
                'confidence': e.confidence
            }
            for e in entities
        ]
