# Central Engine & Context Assembler Design

## Overview

The Central Engine orchestrates intelligent query processing across three specialized knowledge domains using **three parallel LLM calls** - one for each query router. Each LLM call determines both whether that specific knowledge domain is needed and generates the router inputs if needed. This approach ensures specialized prompting for each domain while maintaining efficiency through parallelization.

## System Architecture

```
User Query + Character Name (from frontend)
    ↓
[Central Engine] ← gets prompts from → [Central Prompt Manager]
    ↓
3 Parallel LLM Calls (made by Central Engine):
├── Character Router LLM Call → Character Query Router (if needed)
├── Rulebook Router LLM Call → Rulebook Query Router (if needed)  
└── Session Notes Router LLM Call → Session Notes Query Router (if needed)
    ↓
[Central Prompt Manager] → [Context Assembler] (assembles context)
    ↓
Final Response Prompt → [Central Engine] → Final LLM Response
```

## Key Design Principles

### Specialized LLM Calls
- **One LLM call per query router** - each optimized for that domain
- **Boolean decision + input generation** - each call determines if domain is needed AND generates inputs
- **Domain-specific prompting** - each LLM call uses specialized prompts with relevant context
- **Centralized type definitions** - all intents and entity types pulled from centralized type classes

### Parallel Execution
- All 3 LLM calls execute simultaneously for speed
- Only needed query routers are actually invoked based on LLM decisions
- Results are collected and passed to Context Assembler

### Type System Integration
- Intent definitions stored in type classes with prompt helper methods
- Entity type definitions with examples centralized in type files
- Prompts dynamically generated from type definitions
- Changes to types automatically propagate to prompts

## Class Designs

### 1. Central Engine

**Purpose**: Main orchestrator that makes all LLM calls and coordinates the entire query processing pipeline.

**Location**: `src/rag/central_engine.py`

```python
class CentralEngine:
    """Main orchestrator - makes all LLM calls and coordinates the pipeline."""
    
    def __init__(self, openai_client, anthropic_client, prompt_manager):
        """Initialize with LLM clients and prompt manager."""
        pass
    
    def process_query(self, user_query: str, character_name: str) -> str:
        """
        Main processing pipeline:
        1. Get router decision prompts from Prompt Manager
        2. Make 3 parallel LLM calls for router decisions  
        3. Execute needed query routers in parallel
        4. Get final response prompt from Prompt Manager/Context Assembler
        5. Make final LLM call and return response
        """
        pass
    
    async def make_parallel_router_decisions(self, user_query: str, character_name: str) -> RouterOutputs:
        """
        Make 3 parallel LLM calls to determine router needs and generate inputs.
        Gets prompts from Prompt Manager, makes LLM calls, returns decisions.
        """
        pass
    
    async def execute_needed_routers(self, router_outputs: RouterOutputs) -> Dict[str, Any]:
        """
        Execute only the needed query routers in parallel based on LLM decisions.
        Returns raw router results for context assembly.
        """
        pass
    
    def generate_final_response(self, raw_results: Dict[str, Any], user_query: str) -> str:
        """
        Get final response prompt from Prompt Manager and make final LLM call.
        Returns completed response to user.
        """
        pass
```

### 2. Central Prompt Manager

**Purpose**: Builds all prompts and coordinates between components. No LLM calls - just prompt generation and component coordination.

**Location**: `src/rag/central_prompt_manager.py`

```python
class CentralPromptManager:
    """Builds prompts and coordinates components - no LLM calls."""
    
    def __init__(self, context_assembler):
        """Initialize with context assembler."""
        pass
    
    def get_character_router_prompt(self, user_query: str, character_name: str) -> str:
        """
        Build specialized prompt for Character Router LLM call.
        Uses CharacterPromptHelper to get current intent definitions and entity types.
        """
        pass
    
    def get_rulebook_router_prompt(self, user_query: str) -> str:
        """
        Build specialized prompt for Rulebook Router LLM call.
        Uses RulebookPromptHelper to get current intent definitions and entity types.
        """
        pass
    
    def get_session_notes_router_prompt(self, user_query: str, character_name: str) -> str:
        """
        Build specialized prompt for Session Notes Router LLM call.
        Uses SessionNotesPromptHelper to get current intent definitions and entity types.
        """
        pass
    
    def get_final_response_prompt(self, raw_results: Dict[str, Any], user_query: str) -> str:
        """
        Coordinate with Context Assembler to build final response prompt.
        Context Assembler assembles context, this method builds the final LLM prompt.
        """
        pass
```



### 2. Context Assembler

**Purpose**: Take raw results from multiple query routers and intelligently synthesize them into coherent, contextual responses. Builds context but does not make LLM calls.

**Location**: `src/rag/context_assembler.py`

```python
@dataclass
class AssembledContext:
    """Final assembled context ready for LLM response generation."""
    primary_content: str  # Main relevant content
    supporting_content: str  # Additional context
    character_data: Optional[str]  # Formatted character info
    rules_content: Optional[str]  # Relevant rules/mechanics
    session_context: Optional[str]  # Historical context from sessions
    synthesis_notes: List[str]  # Notes about how content relates
    confidence_score: float  # Overall confidence in response

@dataclass 
class ContentPriority:
    """Priority weighting for different content types."""
    character_weight: float = 1.0
    rulebook_weight: float = 1.0
    session_notes_weight: float = 1.0
    recency_bonus: float = 0.1  # Bonus for recent session data

class ContextAssembler:
    """Intelligently assembles context from multiple query router results."""
    
    def __init__(self, openai_client, anthropic_client):
        """Initialize with LLM clients for context synthesis."""
        pass
    
    def prioritize_content(self, raw_results: Dict[str, Any], user_query: str) -> ContentPriority:
        """
        Determine content priorities based on query type and available data.
        Different query types need different content emphasis.
        """
        pass
    
    def format_character_content(self, character_results: Dict[str, Any]) -> Optional[str]:
        """
        Format character query results into readable context.
        Handles inventory lists, spell descriptions, character stats, etc.
        """
        pass
    
    def format_rulebook_content(self, rulebook_results: Dict[str, Any]) -> Optional[str]:
        """
        Format rulebook results into coherent rules explanations.
        Handles rule mechanics, spell details, equipment properties.
        """
        pass
    
    def format_session_content(self, session_results: Dict[str, Any]) -> Optional[str]:
        """
        Format session notes results into narrative context.
        Handles event summaries, character interactions, quest progression.
        """
        pass
    
    def synthesize_cross_domain_relationships(self, raw_results: Dict[str, Any]) -> List[str]:
        """
        Identify relationships between different content domains.
        E.g., "This spell from your character sheet was used in Session 5..."
        """
        pass
    
    def assemble_context(self, raw_results: Dict[str, Any], user_query: str) -> AssembledContext:
        """
        Main assembly method. Takes raw router results and creates coherent context.
        
        Process:
        1. Prioritize content based on query type
        2. Format each content type appropriately
        3. Identify cross-domain relationships
        4. Synthesize into primary/supporting content structure
        5. Calculate confidence score
        """
        pass
    
    def generate_final_response(self, assembled_context: AssembledContext, original_query: str) -> str:
        """
        Build final response prompt using assembled context and original query.
        Does NOT make LLM calls - just builds the prompt for Central Engine to use.
        
        Returns prompt like:
        - "Given this character data, rules, and session history, answer this query"
        - "Be specific and reference sources appropriately" 
        - "Maintain character voice if applicable"
        """
        pass
```

## Integration Points

## Router Input Specifications

### Character Router LLM Call Output
**Generated by**: Character Router LLM Call  
**Used by**: Character Query Router  

```python
{
  "is_needed": boolean,
  "confidence": float,
  "user_intention": "string", // From character UserIntention enum
  "entities": [{"name": "string", "type": "spell|item|feature|etc", "confidence": float}]
}
```

**Input Sources**:
- `character_name`: Provided by frontend (user selection)
- `user_intention`: LLM selects from full list of character intentions with definitions
- `entities`: LLM extracts with types from comprehensive entity type list

### Rulebook Router LLM Call Output  
**Generated by**: Rulebook Router LLM Call  
**Used by**: Rulebook Query Router

```python
{
  "is_needed": boolean,
  "confidence": float,
  "intention": "string", // From RulebookQueryIntent enum
  "user_query": "string", // Original user query
  "entities": [{"name": "string", "type": "string"}],
  "context_hints": ["string1", "string2", "string3"], // max 3
  "k": 5 // decided internally, not by LLM
}
```

**Input Sources**:
- `intention`: LLM selects from full list of rulebook intentions with definitions
- `user_query`: Pass through original user query
- `entities`: LLM extracts relevant entities with types
- `context_hints`: LLM generates up to 3 additional context strings
- `k`: Fixed internally (not LLM decision)

### Session Notes Router LLM Call Output
**Generated by**: Session Notes Router LLM Call  
**Used by**: Session Notes Query Router

```python
{
  "is_needed": boolean,
  "confidence": float,
  "original_query": "string", // Original user query
  "intention": "string", // From session notes UserIntention enum
  "entities": [{"name": "string", "type": "string"}],
  "context_hints": ["string1", "string2", "string3"], // max 3
  "top_k": 5 // decided internally, not by LLM
}
```

**Input Sources**:
- `original_query`: Pass through original user query
- `intention`: LLM selects from full list of session notes intentions with definitions
- `entities`: LLM extracts relevant entities with types
- `context_hints`: LLM generates up to 3 additional context strings  
- `top_k`: Fixed internally (not LLM decision)

## Prompt Design Philosophy

### Specialized Domain Prompts
- **Three specialized LLM calls**: Each optimized for specific knowledge domain
- **Boolean decision + input generation**: Each call determines need AND generates inputs
- **Domain expertise**: Each prompt includes comprehensive domain-specific context
- **Dynamic prompt generation**: Prompts built from centralized type definitions using helper classes

### Type System Integration
The design centralizes all intent definitions and entity types in the respective type files:

#### Character Types (`character_query_types.py`)
- `CharacterPromptHelper.get_intent_definitions()` - All character intentions with descriptions
- `CharacterPromptHelper.get_entity_type_definitions()` - All entity types with examples
- `CharacterPromptHelper.get_all_intents()` - List of all intention names
- `CharacterPromptHelper.get_all_entity_types()` - List of all entity type names

#### Rulebook Types (`rulebook_types.py`) 
- `RulebookPromptHelper.get_intent_definitions()` - All rulebook query intentions with descriptions
- `RulebookPromptHelper.get_entity_type_definitions()` - All entity types with examples
- `RulebookPromptHelper.get_all_intents()` - List of all intention names

#### Session Notes Types (`session_types.py`)
- `SessionNotesPromptHelper.get_intent_definitions()` - All session intentions with descriptions  
- `SessionNotesPromptHelper.get_entity_type_definitions()` - All entity types with examples
- `SessionNotesPromptHelper.get_all_intents()` - List of all intention names
- `SessionNotesPromptHelper.get_all_entity_types()` - List of all entity type names

### Character Router LLM Prompt
```python
def _build_character_router_prompt(self, user_query: str, character_name: str) -> str:
    """Build specialized prompt for Character Router LLM call."""
    intent_definitions = CharacterPromptHelper.get_intent_definitions()
    entity_type_definitions = CharacterPromptHelper.get_entity_type_definitions()
    
    # Format intentions for prompt
    intention_lines = [f"- {intent}: {definition}" for intent, definition in intent_definitions.items()]
    intentions_text = "\n".join(intention_lines)
    
    # Format entity types for prompt
    entity_lines = [f"- {entity_type}: {definition}" for entity_type, definition in entity_type_definitions.items()]
    entities_text = "\n".join(entity_lines)
    
    return f'''You are an expert D&D character assistant. Analyze this query for CHARACTER DATA needs.

Query: "{user_query}"
Character: "{character_name}"

TASK: Determine if this query needs CHARACTER DATA (stats, inventory, spells, abilities) and generate inputs. If not, ensure that "is_needed" is false.

CHARACTER INTENTIONS (choose the most relevant):
{intentions_text}

ENTITY TYPES:
{entities_text}

Return JSON:
{{
  "is_needed": boolean,
  "confidence": float,
  "user_intention": "intention_name" or null,
  "entities": [{{"name": "string", "type": "type", "confidence": float}}]
}}'''
```

### Rulebook Router LLM Prompt  
```python
def _build_rulebook_router_prompt(self, user_query: str) -> str:
    """Build specialized prompt for Rulebook Router LLM call."""
    intent_definitions = RulebookPromptHelper.get_intent_definitions()
    entity_type_definitions = RulebookPromptHelper.get_entity_type_definitions()
    
    # Format intentions for prompt  
    intention_lines = [f"- {intent}: {definition}" for intent, definition in intent_definitions.items()]
    intentions_text = "\n".join(intention_lines)
    
    # Format entity types for prompt
    entity_lines = [f"- {entity_type}: {definition}" for entity_type, definition in entity_type_definitions.items()]
    entities_text = "\n".join(entity_lines)
    
    return f'''You are an expert D&D rules assistant. Analyze this query for RULEBOOK INFO needs.

Query: "{user_query}"

TASK: Determine if this query needs RULEBOOK INFO (rules, mechanics, spells) and generate inputs. If not, ensure that "is_needed" is false.

RULEBOOK INTENTIONS (choose the most relevant):
{intentions_text}

ENTITY TYPES:
{entities_text}

Return JSON:
{{
  "is_needed": boolean,
  "confidence": float,
  "intention": "intention_name" or null,
  "entities": [{{"name": "string", "type": "type"}}],
  "context_hints": ["hint1", "hint2", "hint3"]
}}'''
```

### Session Notes Router LLM Prompt
```python
def _build_session_notes_router_prompt(self, user_query: str, character_name: str) -> str:
    """Build specialized prompt for Session Notes Router LLM call."""
    intent_definitions = SessionNotesPromptHelper.get_intent_definitions()
    entity_type_definitions = SessionNotesPromptHelper.get_entity_type_definitions()
    
    # Format intentions for prompt
    intention_lines = [f"- {intent}: {definition}" for intent, definition in intent_definitions.items()]
    intentions_text = "\n".join(intention_lines)
    
    # Format entity types for prompt
    entity_lines = [f"- {entity_type}: {definition}" for entity_type, definition in entity_type_definitions.items()]
    entities_text = "\n".join(entity_lines)
    
    return f'''You are an expert D&D session assistant. Analyze this query for SESSION HISTORY needs.

Query: "{user_query}"
Character: "{character_name}"

TASK: Determine if this query needs SESSION HISTORY (past events, NPCs, decisions) and generate inputs. If not, ensure that "is_needed" is false.

SESSION INTENTIONS (choose the most relevant):
{intentions_text}

ENTITY TYPES:
{entities_text}

Return JSON:
{{
  "is_needed": boolean,
  "confidence": float,
  "intention": "intention_name" or null,
  "entities": [{{"name": "string", "type": "type"}}],
  "context_hints": ["hint1", "hint2", "hint3"]
}}'''
```
{
  "character_needed": boolean,
  "rulebook_needed": boolean, 
  "session_notes_needed": boolean,
  "character_name": string or null,
  "entities": [{"name": "string", "type": "string"}],
  "query_type": "simple|complex|comparison|synthesis"
}
```

### Context Synthesis Prompt (Context Assembler)
```
Given this information, provide a comprehensive answer to the user's query:

CHARACTER DATA: {character_content}
RULES: {rules_content}  
SESSION HISTORY: {session_content}

Original Query: {original_query}

Provide a complete, accurate answer that references specific sources when relevant.
```

## Parallel Processing Strategy

### Asyncio Implementation
```python
async def execute_parallel_queries(self, router_inputs: RouterInputs):
    """Execute all needed router queries in parallel."""
    tasks = []
    
    if router_inputs.character_input:
        tasks.append(self._query_character_router(router_inputs.character_input))
    
    if router_inputs.rulebook_input:
        tasks.append(self._query_rulebook_router(router_inputs.rulebook_input))
    
    if router_inputs.session_notes_input:
        tasks.append(self._query_session_router(router_inputs.session_notes_input))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return self._combine_results(results)
```

## Error Handling & Fallbacks

### Graceful Degradation
- If one router fails, continue with available results and throw an error
- Provide confidence scores based on available data
- Clear error messages when critical data is missing

### Performance Monitoring
- Track query analysis time
- Monitor parallel query execution
- Log context assembly performance
- Track overall response quality

## Usage Example

```python
# Initialize system
prompt_manager = CentralPromptManager(context_assembler)
central_engine = CentralEngine(openai_client, anthropic_client, prompt_manager)

# Process user query
user_query = "What spells can Duskryn cast that would be useful in the underdark?"
character_name = "Duskryn Nightwarden"

# Central Engine orchestrates entire pipeline and returns final response
final_response = central_engine.process_query(user_query, character_name)

print(final_response)
```

## Future Enhancements

### Query Learning
- Track successful query patterns
- Improve entity recognition over time
- Optimize content prioritization based on user feedback

### Context Caching
- Cache assembled contexts for similar queries
- Reuse character data for session-based queries  
- Smart cache invalidation when data changes

### Response Personalization
- Learn user preferences for response style
- Adapt character voice based on personality traits
- Customize detail level based on query history

## Benefits of Centralized Type System

### Maintainability
- **Single source of truth**: All intents and entity types defined in one place per domain
- **Automatic propagation**: Changes to types immediately reflected in prompts
- **Consistent definitions**: No manual synchronization between type definitions and prompts
- **Easy testing**: Can validate all intents and entity types from centralized helpers

### Extensibility  
- **Add new intents**: Simply add to enum and helper method, prompts update automatically
- **Modify descriptions**: Update helper method, all prompts reflect changes instantly
- **Entity type evolution**: Add new types in one place, available across all prompts
- **Localization ready**: Helper methods can be extended to support multiple languages

### Developer Experience
- **Clear contract**: Type files serve as documentation for available intents
- **IDE support**: Full autocomplete and type checking for all intents and entities  
- **Refactoring safe**: Renaming intents updates everywhere automatically
- **Code reuse**: Helper methods can be used in tests, validation, and other components

### Quality Assurance
- **Consistent formatting**: All prompts use same format for intents and entities
- **Complete coverage**: Helper methods ensure no intents are missed in prompts
- **Version control**: Easy to see what changed when types are modified
- **Validation possible**: Can validate that all enum values have descriptions
