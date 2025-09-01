# D&D 5e Rulebook Content Retrieval System Plan

## Overview
A semantic search and retrieval system for the D&D 5e rulebook that maps user intentions to relevant content sections, optimized for LLM context windows.

## System Architecture

### 1. Content Categorization Structure

The rulebook is divided into 10 main categories for efficient filtering:

1. **Character Creation** - Races, base classes, ability scores, backgrounds
2. **Class Features & Subclasses** - All class abilities and specializations  
3. **Spellcasting System** - Magic rules, spell lists, descriptions
4. **Combat & Actions** - Combat mechanics and tactical rules
5. **Conditions & Status Effects** - All temporary effects and ailments
6. **Equipment & Magic Items** - Gear, weapons, magical equipment
7. **Core Game Mechanics** - Fundamental rules like advantage, proficiency
8. **Exploration & Environment** - Non-combat adventuring and travel
9. **Creatures & Monsters** - All creature stats and abilities
10. **World & Lore** - Planes, deities, campaign setting info

### 2. Core Data Structure

```python
@dataclass
class RulebookSection:
    """Represents a hierarchical section of the D&D 5e rulebook"""
    id: str
    title: str
    level: int  # 1 for chapter (#), 2 for section (##), etc.
    content: str  # Full content until next header
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    vector: Optional[List[float]] = None  # Embedding vector
    categories: List[int] = field(default_factory=list)  # Which of the 10 categories
    
    def get_full_content(self, include_children: bool = False, storage: Optional['RulebookStorage'] = None) -> str:
        """Get content including optional children sections"""
        if not include_children:
            return self.content
        
        # Recursively include children content
        if not storage:
            return self.content
        
        content_parts = [self.content]
        
        # Add all children sections recursively
        for child_id in self.children_ids:
            if child_id in storage.sections:
                child_section = storage.sections[child_id]
                child_content = child_section.get_full_content(include_children=True, storage=storage)
                content_parts.append(child_content)
        
        return '\n\n'.join(content_parts)
```

### 2. Query Intentions (30 Types)

```python
INTENTIONS = {
    "describe_entity": "Get full description of a game element",
    "compare_entities": "Compare two or more game elements",
    "level_progression": "Show advancement for a class/feature",
    "action_options": "List available actions in a situation",
    "rule_mechanics": "Explain how a rule works",
    "calculate_values": "Compute game statistics",
    "spell_details": "Get spell specifics and usage",
    "class_spell_access": "Which classes can use a spell",
    "monster_stats": "Get creature statistics",
    "condition_effects": "Explain status effect mechanics",
    "character_creation": "Character building guidance",
    "multiclass_rules": "Multiclassing mechanics",
    "equipment_properties": "Item stats and properties",
    "damage_types": "Damage type explanations",
    "rest_mechanics": "Short/long rest rules",
    "skill_usage": "How skills work",
    "find_by_criteria": "Search by specific criteria",
    "prerequisite_check": "Check requirements",
    "interaction_rules": "Object/environment interactions",
    "tactical_usage": "Combat tactics and strategies",
    "environmental_rules": "Environmental hazards/effects",
    "creature_abilities": "Monster special abilities",
    "saving_throws": "Save mechanics",
    "magic_item_usage": "How magic items work",
    "planar_properties": "Planes of existence info",
    "downtime_activities": "Between-adventure activities",
    "subclass_features": "Subclass-specific abilities",
    "cost_lookup": "Prices and costs",
    "legendary_mechanics": "Legendary actions/resistance",
    "optimization_advice": "Character optimization tips"
}
```

### 3. Input Parameters

**Primary Inputs:**
- `intention`: One of the 30 defined query intentions
- `entities`: List of entity names (spells, classes, monsters, items, etc.)

**Potential Additional Input for Better Search:**
- `context_hints`: Optional list of keywords or phrases to help narrow search
  - Examples: ["early game", "at level 5", "in combat", "underwater", "against undead"]
  - Helps disambiguate when entities have multiple aspects
  - Provides situational context for rules lookups

### 4. Retrieval Strategy

#### Phase 1: Query Processing
```python
def process_query(
    intention: str, 
    normalized_entities: List[str],  # Already normalized!
    context_hints: Optional[List[str]] = None
):
    """
    Process the search query. Entities are pre-normalized.
    """
    # 1. Map intention to relevant categories
    categories = map_intention_to_categories(intention)
    
    # 2. Generate search queries using the normalized entities
    queries = generate_semantic_queries(intention, normalized_entities, context_hints)
    
    return categories, queries

def generate_semantic_queries(
    intention: str,
    normalized_entities: List[str],
    context_hints: Optional[List[str]]
) -> List[str]:
    """
    Create search queries from normalized entities and context.
    Entities are already in their canonical form (e.g., "fireball" not "FB" or "Fireball")
    """
    query_parts = []
    
    # Add normalized entities directly
    query_parts.extend(normalized_entities)
    
    # Add intention-specific keywords
    if intention == "spell_details":
        query_parts.extend(["spell", "casting", "components", "duration"])
    elif intention == "monster_stats":
        query_parts.extend(["creature", "hit points", "armor class", "actions"])
    # ... etc
    
    # Add context hints if provided
    if context_hints:
        query_parts.extend(context_hints)
    
    return [" ".join(query_parts)]
```

#### Phase 2: Semantic Search
```python
def semantic_search(queries: List[str], categories: List[int], storage: RulebookStorage):
    # 1. Filter sections by category
    relevant_sections = [
        section for section in storage.sections.values()
        if any(cat in section.categories for cat in categories)
    ]
    
    # 2. Vectorize queries
    query_vectors = embed_queries(queries)
    
    # 3. Search with scoring against full sections
    results = []
    for section in relevant_sections:
        score = calculate_similarity(query_vectors, section.vector)
        results.append((section, score))
    
    # 4. Sort by relevance
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results
```

#### Phase 3: Content Selection
```python
def select_content(search_results, storage: RulebookStorage, max_tokens=8000):
    selected_sections = []
    current_tokens = 0
    included_section_ids = set()
    
    # Always include top result with all children
    if search_results:
        top_section = search_results[0][0]
        full_content = top_section.get_full_content(include_children=True, storage=storage)
        selected_sections.append({
            'section': top_section,
            'content': full_content,
            'includes_children': True
        })
        current_tokens += estimate_tokens(full_content)
        included_section_ids.add(top_section.id)
        # Mark all children as included
        mark_children_included(top_section, included_section_ids, storage)
    
    # Add additional relevant sections (without children if already included)
    for section, score in search_results[1:]:
        if section.id in included_section_ids:
            continue  # Skip if already included as child
            
        section_content = section.content  # Just this section, not children
        section_tokens = estimate_tokens(section_content)
        
        if current_tokens + section_tokens <= max_tokens:
            selected_sections.append({
                'section': section,
                'content': section_content,
                'includes_children': False
            })
            current_tokens += section_tokens
            included_section_ids.add(section.id)
        else:
            break
    
    return selected_sections
```

### 4. Intention-to-Category Mapping

```python
INTENTION_CATEGORY_MAP = {
    "describe_entity": [1, 2, 3, 6, 9],  # Could be any entity type
    "compare_entities": [1, 2, 3, 6, 9],
    "level_progression": [2],  # Class Features
    "action_options": [4, 7],  # Combat & Core Mechanics
    "rule_mechanics": [7],  # Core Mechanics
    "calculate_values": [1, 2, 7],  # Character, Classes, Core
    "spell_details": [3],  # Spellcasting
    "class_spell_access": [2, 3],  # Classes & Spellcasting
    "monster_stats": [9],  # Creatures
    "condition_effects": [5],  # Conditions
    "character_creation": [1],  # Character Creation
    "multiclass_rules": [1, 2],  # Character & Classes
    "equipment_properties": [6],  # Equipment
    "damage_types": [4, 7],  # Combat & Core
    "rest_mechanics": [7, 8],  # Core & Exploration
    "skill_usage": [7],  # Core Mechanics
    "find_by_criteria": [1, 2, 3, 6, 9],  # Varies by criteria
    "prerequisite_check": [1, 2, 6],  # Character, Classes, Items
    "interaction_rules": [7, 8],  # Core & Exploration
    "tactical_usage": [4],  # Combat
    "environmental_rules": [8],  # Exploration
    "creature_abilities": [9],  # Creatures
    "saving_throws": [4, 7],  # Combat & Core
    "magic_item_usage": [6],  # Equipment
    "planar_properties": [10],  # World & Lore
    "downtime_activities": [8],  # Exploration
    "subclass_features": [2],  # Class Features
    "cost_lookup": [6, 8],  # Equipment & Exploration
    "legendary_mechanics": [9],  # Creatures
    "optimization_advice": [1, 2]  # Character & Classes
}
```

### 5. Section Organization Strategy

#### Section Creation Rules:
1. **One section per header**: Each markdown header (#, ##, ###, ####) starts a new RulebookSection
2. **Content until next header**: Each section contains content from its header until ANY next header (regardless of level)
3. **Child relationships**: Headers of lower level (more #s) become children of the current section
4. **Leaf nodes hold most content**: The deepest level headers (###, ####) typically contain the actual rules text
5. **No size limits**: Sections maintain their natural boundaries regardless of length
6. **Category assignment**: Each section tagged with relevant categories from the 10 main categories

#### Section Hierarchy Example:
```
# Classes (level 1)
  Content: Brief intro paragraph only
  Children: [Barbarian, Bard, Cleric, ...]

## Barbarian (level 2)  
  Content: Class overview paragraph
  Children: [Class Features, Rage, Unarmored Defense, ...]

### Rage (level 3)
  Content: Full rage rules (most content here)
  Children: [Rage Damage Table, Usage Notes]

#### Rage Damage Table (level 4)
  Content: The actual table and notes
  Children: []
```

#### RulebookStorage Class Structure:
```python
class RulebookStorage:
    def __init__(self):
        self.sections: Dict[str, RulebookSection] = {}
        self.category_index: Dict[int, List[str]] = defaultdict(list)
        self.title_index: Dict[str, str] = {}  # title -> section_id
        
    def parse_markdown(self, markdown_content: str):
        """Parse markdown into hierarchical RulebookSection objects"""
        lines = markdown_content.split('\n')
        section_stack = []  # Track hierarchy
        current_content = []
        
        for line in lines:
            if line.startswith('#'):
                # Save previous section if exists
                if section_stack:
                    self.save_section(section_stack[-1], current_content)
                    current_content = []
                
                # Determine level and create new section
                level = len(line.split()[0])  # Count #s
                title = line.lstrip('#').strip()
                section_id = generate_id(title)
                
                # Find parent
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()
                
                parent_id = section_stack[-1].id if section_stack else None
                
                # Create new section
                new_section = RulebookSection(
                    id=section_id,
                    title=title,
                    level=level,
                    content="",  # Will be set when we hit next header
                    parent_id=parent_id
                )
                
                # Update parent's children
                if parent_id:
                    self.sections[parent_id].children_ids.append(section_id)
                
                section_stack.append(new_section)
                self.sections[section_id] = new_section
            else:
                # Accumulate content
                current_content.append(line)
        
        # Save final section
        if section_stack:
            self.save_section(section_stack[-1], current_content)
            
    def vectorize_sections(self):
        """Generate embeddings for all sections"""
        for section in self.sections.values():
            # For leaf nodes with lots of content, use full text
            # For parent nodes with little content, include title prominently
            if section.children_ids:
                # Parent node - emphasize structure
                text_for_embedding = f"{section.title}\n{section.title}\n{section.content}"
            else:
                # Leaf node - full content matters most
                text_for_embedding = f"{section.title}\n{section.content}"
            
            section.vector = generate_embedding(text_for_embedding)
            
    def get_sections_by_category(self, categories: List[int]) -> List[RulebookSection]:
        """Retrieve all sections in given categories"""
        section_ids = set()
        for cat in categories:
            section_ids.update(self.category_index[cat])
        return [self.sections[sid] for sid in section_ids]
```

### 6. Entity Recognition & Normalization

```python
# Note: Entity normalization happens BEFORE the search system
# The search functions receive already-normalized entity names

# Common entity variations handled during pre-processing
ENTITY_VARIATIONS = {
    # Spells
    "fb": "fireball",
    "mm": "magic missile",
    "cure": "cure wounds",
    
    # Classes
    "barb": "barbarian",
    "wiz": "wizard",
    "sorc": "sorcerer",
    
    # Conditions
    "ko": "unconscious",
    "koed": "unconscious",
    
    # Common abbreviations
    "ac": "armor class",
    "hp": "hit points",
    "dc": "difficulty class",
    "aoe": "area of effect"
}

def normalize_entity_names(entities: List[str]) -> List[str]:
    """
    Pre-processing step: Normalize entity names before search.
    This happens OUTSIDE the main search pipeline.
    """
    normalized = []
    for entity in entities:
        # Basic normalization
        cleaned = entity.lower().strip()
        
        # Remove common articles
        for article in ["the", "a", "an"]:
            if cleaned.startswith(f"{article} "):
                cleaned = cleaned[len(article)+1:]
        
        # Check for known variations
        cleaned = ENTITY_VARIATIONS.get(cleaned, cleaned)
        
        # Handle possessives
        cleaned = cleaned.replace("'s", "").replace("s'", "s")
        
        normalized.append(cleaned)
    
    return normalized

# The search system assumes entities are already normalized
def search_with_normalized_entities(
    intention: str, 
    normalized_entities: List[str],  # Already normalized!
    context_hints: Optional[List[str]] = None
):
    """Main search entry point - expects pre-normalized entities"""
    # No further normalization needed
    categories = map_intention_to_categories(intention)
    queries = generate_semantic_queries(intention, normalized_entities, context_hints)
    return semantic_search(queries, categories)
```

### 7. Scoring & Ranking Algorithm

```python
def calculate_relevance_score(
    section: RulebookSection,
    intention: str, 
    entities: List[str],
    context_hints: List[str],
    query_vector: List[float]
):
    # Base semantic similarity (0-1)
    semantic_score = cosine_similarity(section.vector, query_vector)
    
    # Entity match bonus (0-0.4) - Higher weight since content is in leaf nodes
    entity_score = 0
    for entity in entities:
        # Check both title and content
        if entity.lower() in section.title.lower():
            entity_score += 0.2  # High weight for title matches
        if entity.lower() in section.content.lower():
            # More weight for content matches in leaf nodes
            weight = 0.1 if section.children_ids else 0.15
            entity_score += weight
    entity_score = min(entity_score, 0.4)
    
    # Context hint bonus (0-0.2)
    context_score = 0
    if context_hints:
        for hint in context_hints:
            if hint.lower() in section.content.lower():
                context_score += 0.05
    context_score = min(context_score, 0.2)
    
    # Section level adjustment - prefer leaf nodes where content lives
    level_adjustment = 0
    if section.level == 1:  # Chapter level - usually just overview
        level_adjustment = -0.15
    elif section.level == 2:  # Section level - some content
        level_adjustment = -0.05
    elif section.level >= 3 and not section.children_ids:  # Leaf nodes with content
        level_adjustment = 0.1
    
    # Category match bonus (0-0.2)
    category_bonus = 0.2 if any(
        cat in section.categories 
        for cat in INTENTION_CATEGORY_MAP[intention]
    ) else 0
    
    # Final score
    final_score = (semantic_score + entity_score + 
                   context_score + category_bonus + 
                   level_adjustment)
    
    return min(max(final_score, 0), 1)  # Clamp to [0, 1]
```

### 8. Response Assembly

```python
def assemble_response(selected_sections, intention, entities):
    response = {
        "intention": intention,
        "entities": entities,
        "sections": [],
        "total_tokens": 0
    }
    
    for section in selected_sections:
        section_data = {
            "id": section.id,
            "title": section.title,
            "content": section.content,
            "relevance": section.relevance_score,
            "includes_children": section.has_children_included
        }
        response["sections"].append(section_data)
        response["total_tokens"] += section.token_count
    
    return response
```

### 9. Optimization Techniques

1. **Pre-compute embeddings** for all chunks
2. **Index by category** for faster filtering
3. **Cache frequent queries** (common spells, classes)
4. **Use approximate nearest neighbor** search (FAISS, Annoy)
5. **Batch process** similar queries
6. **Progressive loading**: Start with essential sections, load more if needed

### 10. Example Query Flow

**Input:**
- Intention: `spell_details`
- Entities: `["fireball", "wizard"]`  ← Already normalized
- Context hints: `["3rd level", "area damage"]` (optional)

**Process:**
1. Categories identified: [3 (Spellcasting), 2 (Classes)]
2. Entities already normalized: ["fireball", "wizard"]
3. Search query generated: "fireball wizard spell casting components duration 3rd level area damage"
4. Top results (RulebookSections):
   - Section: "Spell Descriptions > Fireball" (score: 0.95)
     - Level 3 section with full spell text
   - Section: "Wizard > Spellcasting" (score: 0.72)
     - Level 3 section with wizard spell rules
   - Section: "Areas of Effect > Sphere" (score: 0.65)
     - Level 4 section with specific mechanics
5. Selected content:
   - Full "Fireball" section with all children (if any)
   - "Wizard > Spellcasting" section (without children)
   - Total: ~3500 tokens

**Output:**
```python
{
    "intention": "spell_details",
    "entities": ["fireball", "wizard"],  # Normalized form
    "sections": [
        {
            "id": "spell_fireball",
            "title": "Fireball",
            "level": 3,  # Actual content is here
            "content": "[Full spell description...]",
            "relevance": 0.95,
            "includes_children": True
        },
        {
            "id": "class_wizard_spellcasting",
            "title": "Wizard - Spellcasting",
            "level": 3,  # Actual rules are here
            "content": "[Wizard spellcasting rules...]",
            "relevance": 0.72,
            "includes_children": False
        }
    ],
    "total_tokens": 3500
}
```

## Implementation Checklist

- [ ] Parse markdown file into hierarchical sections
- [ ] Assign categories to each section
- [ ] Create chunks with proper metadata
- [ ] Generate embeddings for all chunks
- [ ] Build category-based indices
- [ ] Implement entity recognition/normalization
- [ ] Create semantic search function
- [ ] Build scoring algorithm
- [ ] Implement content selection logic
- [ ] Add caching layer
- [ ] Test with various query types
- [ ] Optimize for performance
- [ ] Add fallback strategies
- [ ] Implement progressive loading
- [ ] Create evaluation metrics