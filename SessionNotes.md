# Session Notes RAG System Design

## Overview
Design for a comprehensive session notes retrieval system that enables intelligent querying across 30+ D&D sessions, supporting both semantic search and entity-specific lookups for narrative continuity and character development tracking.

## Core Architecture

### 1. Data Storage Strategy

**Session Notes Structure:**
```python
@dataclass
class SessionNote:
    session_number: int
    date: str  # YYYY-MM-DD format
    title: str
    summary: str
    
    # Core narrative sections
    key_events: List[str]
    npcs: Dict[str, NPCInteraction]  # NPC name -> interaction details
    locations: List[LocationVisit]
    
    # Combat & mechanics
    encounters: List[Encounter]
    spells_used: List[SpellUsage]
    items_gained_lost: List[ItemTransaction]
    
    # Character development
    character_decisions: Dict[str, List[str]]  # Character -> decisions
    relationship_changes: List[RelationshipChange]
    character_growth: List[CharacterGrowthMoment]
    
    # Session metadata
    cliffhanger: str
    fun_moments: List[str]
    quotes: List[Quote]
    
    # Semantic embeddings (computed)
    summary_embedding: Optional[List[float]]
    event_embeddings: Dict[str, List[float]]  # Event -> embedding
```

**Storage Options:**

1. **Hybrid Approach (Recommended):**
   - **Structured data** → SQLite database for entities, relationships, timelines
   - **Narrative content** → Vector database (ChromaDB/Pinecone) for semantic search
   - **Original markdown** → File system for human readability

2. **Benefits:**
   - Fast entity queries (SQL)
   - Rich semantic search (embeddings)
   - Maintains human-readable source
   - Supports complex temporal queries

### 2. Query Intent System

**Session Notes Query Intents:**

```python
class SessionNotesQueryIntent(Enum):
    # Entity Tracking
    FIND_NPC_INTERACTIONS = "find_npc_interactions"
    TRACK_ITEM_HISTORY = "track_item_history"
    LOCATION_VISITS = "location_visits"
    SPELL_USAGE_HISTORY = "spell_usage_history"
    
    # Character Development
    CHARACTER_ARC_TRACKING = "character_arc_tracking"
    RELATIONSHIP_EVOLUTION = "relationship_evolution"
    DECISION_CONSEQUENCES = "decision_consequences"
    CHARACTER_GROWTH_MOMENTS = "character_growth_moments"
    
    # Narrative Continuity
    PLOT_THREAD_TRACKING = "plot_thread_tracking"
    FORESHADOWING_CALLBACKS = "foreshadowing_callbacks"
    RECURRING_THEMES = "recurring_themes"
    PROPHECY_FULFILLMENT = "prophecy_fulfillment"
    
    # Combat & Mechanics
    COMBAT_PATTERNS = "combat_patterns"
    TACTICAL_EVOLUTION = "tactical_evolution"
    POWER_PROGRESSION = "power_progression"
    
    # Session Context
    RECENT_EVENTS = "recent_events"
    SESSION_SUMMARIES = "session_summaries"
    TEMPORAL_CONTEXT = "temporal_context"
    
    # Cross-Session Analysis
    THEMATIC_ANALYSIS = "thematic_analysis"
    CAMPAIGN_MILESTONES = "campaign_milestones"
    WORLD_STATE_CHANGES = "world_state_changes"
```

### 3. Retrieval Strategies by Intent

#### Entity-Specific Queries
- **Strategy:** Direct database lookup + semantic expansion
- **Example:** "Tell me about all interactions with Ghul'vor"
- **Implementation:** 
  1. SQL query for exact entity matches
  2. Semantic search for related mentions
  3. Temporal ordering of results

#### Character Development Tracking
- **Strategy:** Character-filtered semantic search + relationship graphs
- **Example:** "How has Duskryn's relationship with faith evolved?"
- **Implementation:**
  1. Filter by character name
  2. Semantic search for faith-related concepts
  3. Temporal analysis for progression

#### Narrative Continuity
- **Strategy:** Multi-session semantic search + plot thread linking
- **Example:** "What events led to Duskryn's decision with the Black Benediction?"
- **Implementation:**
  1. Identify key decision point
  2. Semantic search for related themes across sessions
  3. Build causal chain of events

### 4. Technical Implementation

#### Database Schema
```sql
-- Core session metadata
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    session_number INTEGER UNIQUE,
    date DATE,
    title TEXT,
    summary TEXT
);

-- Entity tracking
CREATE TABLE npcs (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    first_appearance_session INTEGER,
    description TEXT
);

CREATE TABLE npc_interactions (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    npc_id INTEGER,
    interaction_type TEXT,
    description TEXT,
    character_involved TEXT
);

-- Character decisions and growth
CREATE TABLE character_decisions (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    character_name TEXT,
    decision_description TEXT,
    context TEXT,
    consequences TEXT
);

-- Relationships
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    character_a TEXT,
    character_b TEXT,  -- Can be NPC or PC
    relationship_type TEXT,
    strength INTEGER,  -- -5 to +5 scale
    session_updated INTEGER
);
```

#### Vector Storage Strategy
```python
class SessionNotesVectorStore:
    def __init__(self):
        self.summary_collection = "session_summaries"
        self.event_collection = "key_events"
        self.character_collection = "character_moments"
        self.quote_collection = "memorable_quotes"
    
    def store_session(self, session: SessionNote):
        # Store different content types in focused collections
        # for better retrieval precision
        pass
    
    def search_by_intent(
        self, 
        query: str, 
        intent: SessionNotesQueryIntent,
        character_filter: Optional[str] = None,
        date_range: Optional[Tuple[str, str]] = None
    ) -> List[SessionSearchResult]:
        # Route to appropriate collection(s) based on intent
        pass
```

### 5. Session Notes Query Engine

#### Core Query Interface
```python
class SessionNotesQueryEngine:
    def query(
        self,
        user_query: str,
        intention: SessionNotesQueryIntent,
        entities: List[str],
        k: int = 5
    ) -> List[SessionSearchResult]:
        """
        Query session notes with processed intent and entities.
        
        Args:
            user_query: Original user query for semantic search
            intention: Pre-classified query intention
            entities: Pre-extracted entities (characters, NPCs, locations, etc.)
            k: Number of results to return
            
        Returns:
            List of SessionSearchResult objects with relevant session content
        """
        pass
```

#### Multi-Stage Retrieval Process
1. **Temporal Filtering** → Apply date ranges if specified in entities
2. **Intent-Based Source Selection** → Choose appropriate data sources
3. **Multi-Source Search:**
   - SQL queries for structured entity data
   - Vector search for semantic content matching
   - Relationship graph traversal when needed
4. **Result Fusion** → Combine and rank results from different sources
5. **Context Enrichment** → Add related sessions and background context

#### Example Query Processing
**Inputs:**
- `user_query`: "What led to the conflict between Duskryn and the party?"
- `intention`: `RELATIONSHIP_EVOLUTION`
- `entities`: ["Duskryn", "party"]

**Processing:**
1. **SQL Query:** Find all sessions with Duskryn character decisions
2. **Vector Search:** Semantic search for "conflict", "disagreement", "tension"
3. **Relationship Graph:** Trace Duskryn-party relationship changes over time
4. **Result:** Chronologically ordered SessionSearchResult objects

### 6. Session Search Results

#### SessionSearchResult Structure
```python
@dataclass
class SessionSearchResult:
    session_number: int
    session_title: str
    session_date: str
    relevance_score: float
    
    # Matched content sections
    matched_events: List[str]
    matched_npcs: List[NPCInteraction]
    matched_decisions: List[CharacterDecision]
    matched_quotes: List[Quote]
    
    # Context information
    session_summary: str
    related_sessions: List[int]  # Sessions that provide additional context
    
    # Semantic matches
    highlighted_passages: List[str]  # Key text snippets that matched
    
    def get_full_context(self) -> str:
        """Return formatted context for this session result"""
        pass
```

#### Intent-Specific Result Formatting
Different query intentions return specialized result objects:

```python
# For character development queries
@dataclass
class CharacterArcResult(SessionSearchResult):
    character_name: str
    character_growth_moments: List[CharacterGrowthMoment]
    relationship_changes: List[RelationshipChange]
    decisions_and_consequences: List[Tuple[str, str]]

# For NPC interaction queries  
@dataclass
class NPCInteractionResult(SessionSearchResult):
    npc_name: str
    interaction_type: str
    relationship_status: str
    previous_interactions: List[SessionSearchResult]

# For plot thread queries
@dataclass
class PlotThreadResult(SessionSearchResult):
    thread_name: str
    thread_progression: List[str]
    connected_sessions: List[int]
    unresolved_elements: List[str]
```

### 7. Query Engine Implementation Strategy

#### Intent-to-Strategy Mapping
```python
INTENT_STRATEGY_MAP = {
    SessionNotesQueryIntent.FIND_NPC_INTERACTIONS: NPCInteractionStrategy(),
    SessionNotesQueryIntent.CHARACTER_ARC_TRACKING: CharacterArcStrategy(),
    SessionNotesQueryIntent.RELATIONSHIP_EVOLUTION: RelationshipStrategy(),
    SessionNotesQueryIntent.PLOT_THREAD_TRACKING: PlotThreadStrategy(),
    SessionNotesQueryIntent.RECENT_EVENTS: RecentEventsStrategy(),
    # ... etc
}

class SessionNotesQueryEngine:
    def query(self, user_query: str, intention: SessionNotesQueryIntent, 
              entities: List[str], k: int = 5) -> List[SessionSearchResult]:
        
        strategy = INTENT_STRATEGY_MAP[intention]
        return strategy.execute_search(
            query=user_query,
            entities=entities,
            vector_store=self.vector_store,
            database=self.database,
            k=k
        )
```

#### Search Strategy Examples

**NPC Interaction Strategy:**
```python
class NPCInteractionStrategy:
    def execute_search(self, query: str, entities: List[str], 
                      vector_store, database, k: int) -> List[NPCInteractionResult]:
        npc_name = self._extract_npc_from_entities(entities)
        
        # 1. Direct database lookup for all NPC interactions
        direct_interactions = database.get_npc_interactions(npc_name)
        
        # 2. Semantic search for indirect mentions
        semantic_matches = vector_store.search(f"{npc_name} {query}", k=k*2)
        
        # 3. Combine and rank results
        return self._format_npc_results(direct_interactions, semantic_matches)
```

**Character Arc Strategy:**
```python
class CharacterArcStrategy:
    def execute_search(self, query: str, entities: List[str], 
                      vector_store, database, k: int) -> List[CharacterArcResult]:
        character_name = self._extract_character_from_entities(entities)
        
        # 1. Get character decisions across all sessions
        decisions = database.get_character_decisions(character_name)
        
        # 2. Get relationship changes
        relationships = database.get_relationship_history(character_name)
        
        # 3. Semantic search for character growth moments
        growth_moments = vector_store.search_character_collection(
            f"{character_name} growth development change", k=k
        )
        
        # 4. Temporal ordering and context building
        return self._build_character_arc_timeline(decisions, relationships, growth_moments)
```

### 8. Specialized Features for Session Notes

#### Temporal Intelligence
```python
class TemporalQueryEngine:
    def find_progression(
        self, 
        entity: str, 
        aspect: str,
        session_range: Optional[Tuple[int, int]] = None
    ) -> List[ProgressionPoint]:
        """Track how an entity/aspect changes over time"""
        pass
    
    def find_buildup_events(
        self, 
        climax_session: int,
        lookback_sessions: int = 5
    ) -> List[BuildupEvent]:
        """Find events that led to a major moment"""
        pass
```

#### Narrative Analysis
```python
class NarrativeAnalyzer:
    def identify_themes(self, sessions: List[SessionNote]) -> Dict[str, float]:
        """Extract recurring themes across sessions"""
        pass
    
    def find_callbacks(
        self, 
        current_session: SessionNote,
        previous_sessions: List[SessionNote]
    ) -> List[CallbackMoment]:
        """Identify references to past events"""
        pass
```

### 9. Implementation Priority

**Phase 1 (Core Functionality):**
1. Session note parser (markdown → structured data)
2. Basic vector storage and search
3. Entity tracking system
4. Core query intents (5-7 most important)

**Phase 2 (Enhanced Features):**
1. Relationship tracking
2. Temporal analysis
3. Advanced query intents
4. Multi-session narrative analysis

**Phase 3 (Intelligence Features):**
1. Automatic plot thread detection
2. Character development insights
3. Predictive narrative suggestions
4. Campaign health metrics

### 10. Integration with Existing Systems

**With Character System:**
- Cross-reference character decisions with session events
- Validate character development against session history
- Provide session context for character queries

**With Rulebook System:**
- Link spell usage to rulebook explanations
- Provide mechanical context for session events
- Support "what if" scenarios using rules + session history

This design provides the foundation for rich, intelligent querying across your session history while maintaining consistency with your existing architecture and supporting the complex narrative needs of a long-running D&D campaign.