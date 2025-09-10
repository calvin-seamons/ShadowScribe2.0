# LLM Character Extraction System

A parallel extraction system using LLM APIs with tool calling to convert messy OCR'd character sheet markdown into structured `Character` dataclass instances.

## System Overview

**Input**: Raw OCR'd markdown document (messy, inconsistent formatting)
**Output**: Complete `Character` dataclass populated with all sub-components
**Method**: Parallel LLM API calls with tool calling, each targeting specific character components

**📋 API Schemas**: See [CHARACTER_EXTRACTION_API_SCHEMAS.md](CHARACTER_EXTRACTION_API_SCHEMAS.md) for detailed tool function definitions

## Core Architecture

```
OCR Markdown Document
         ↓
   Document Analyzer
         ↓
┌─────────────────────────────────┐
│    Parallel Extraction Layer   │
├─────────────────────────────────┤
│ 12+ Concurrent LLM API Calls   │
│ Each with specialized tools     │
└─────────────────────────────────┘
         ↓
    Result Aggregator
         ↓
   Character Dataclass
```

## Extraction Pipeline Overview

**14 Parallel Extraction Tasks** targeting specific character components:

- **T1-T4**: Core Identity (Base, Physical, Abilities, Combat)
- **T5-T6**: Background & Personality (Background, Traits)
- **T7-T8**: Capabilities (Proficiencies, Passive Scores & Senses)
- **T9-T10**: Features & Abilities (Class/Racial Features, Traits)
- **T11-T12**: Equipment & Magic (Inventory, Spellcasting Info)
- **T13-T14**: Narrative (Spell List, Backstory, Relationships)

**🔧 Complete tool schemas**: [CHARACTER_EXTRACTION_API_SCHEMAS.md](CHARACTER_EXTRACTION_API_SCHEMAS.md)

## Tool Function Design

Each extraction task uses a specialized tool function with JSON schema validation:

- **Schema-Enforced Output**: LLM must call tool function with valid JSON
- **OCR-Tolerant Prompts**: Handle formatting inconsistencies and missing data  
- **Required vs Optional Fields**: Core fields required, details optional
- **Type Validation**: Integer ranges, string enums, nested object constraints

**📝 All 14 tool definitions**: [CHARACTER_EXTRACTION_API_SCHEMAS.md](CHARACTER_EXTRACTION_API_SCHEMAS.md)

## Prompt Strategy for OCR Tolerance

### System Prompt Template
```
You are a D&D character sheet data extractor. You will receive messy OCR'd markdown text that may contain:
- Formatting inconsistencies
- Missing table borders
- OCR artifacts ("0" instead of "O", extra spaces)
- Information scattered across the document

Your task: Extract {COMPONENT_TYPE} information and call the {TOOL_FUNCTION} with accurate data.

Guidelines:
1. Use fuzzy matching - "STR" = "Strength" = "STRENGTH"
2. Handle missing data gracefully - use null for unavailable fields
3. Infer reasonable defaults when appropriate
4. Look for context clues throughout the entire document
5. Call the tool function exactly once with your best extraction
```

### User Message
```
Here is the complete OCR'd character sheet markdown:

{FULL_MARKDOWN_DOCUMENT}

Extract the {COMPONENT_TYPE} information and call the appropriate tool function.
```

## Parallel Execution Framework

```python
class CharacterExtractionSystem:
    async def extract_character(self, ocr_markdown: str) -> Character:
        """Main extraction pipeline"""
        
        # Launch all 14 extraction tasks in parallel
        tasks = [
            self.extract_component(ocr_markdown, task_id, tool_function)
            for task_id, tool_function in self.extraction_tasks
        ]
        
        # Wait for all extractions to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results into Character dataclass
        character = self.merge_extraction_results(results)
        
        # Run gap-filling pass if needed
        character = await self.fill_missing_fields(character, ocr_markdown)
        
        return character
    
    async def extract_component(self, markdown: str, task_id: str, tool_function: str):
        """Extract single component using LLM tool calling"""
        
        response = await self.llm_client.chat_completion_with_tools(
            messages=self.build_extraction_messages(markdown, task_id),
            tools=[self.get_tool_definition(tool_function)],
            tool_choice={"type": "function", "function": {"name": tool_function}}
        )
        
        # Extract and validate tool call result
        tool_call = response.choices[0].message.tool_calls[0]
        extracted_data = json.loads(tool_call.function.arguments)
        
        return self.create_extraction_result(task_id, extracted_data)
```

## Smart Defaults & Inference Rules

When data is missing or unclear, the system applies intelligent defaults:

### Character Level Defaults
- **Level 1**: If no level found, assume level 1
- **Single Class**: If no multiclass indicators, assume single class
- **Standard Array**: If no ability scores, use [15,14,13,12,10,8] distributed logically

### Race-Based Inference
- **Size**: Medium for most races, Small for halflings/gnomes
- **Speed**: 30ft standard, 25ft for small races, racial variations
- **Darkvision**: 60ft for elves/dwarves/tieflings, none for humans/halflings
- **Languages**: Common + racial language(s)

### Class-Based Inference  
- **Hit Dice**: d6-d12 based on class
- **Proficiencies**: Standard class proficiencies if not explicitly listed
- **Spellcasting**: Detect if class is spellcaster, infer ability (WIS/INT/CHA)
- **Features**: Core class features based on level

### Background Defaults
- **Skills**: 2 skills typically granted by background
- **Tools/Languages**: Standard background proficiencies
- **Equipment**: Basic background starting gear

## Error Handling & Validation

```python
class ExtractionValidator:
    @staticmethod
    def validate_extraction_result(component_type: str, data: dict) -> bool:
        """Validate extracted data against dataclass schema"""
        try:
            # Attempt to create dataclass instance
            component_class = globals()[component_type]
            instance = component_class(**data)
            return True
        except (TypeError, ValueError) as e:
            logger.warning(f"Validation failed for {component_type}: {e}")
            return False
    
    @staticmethod
    def retry_extraction_with_feedback(original_data: dict, error: str, 
                                     markdown: str, tool_function: str):
        """Retry extraction with error feedback"""
        enhanced_prompt = f"""
        Previous extraction failed with error: {error}
        
        Original attempt returned: {json.dumps(original_data, indent=2)}
        
        Please correct the extraction and try again.
        """
        # Re-run LLM call with enhanced prompt
```

## Confidence Scoring

Each extraction receives a confidence score based on:

- **Data Completeness**: Percentage of required fields populated
- **Field Validation**: Whether values pass type/range checks  
- **Cross-Reference**: Consistency with other extracted components
- **OCR Quality**: Presence of clear section headers and structure

```python
def calculate_confidence(extracted_data: dict, component_type: str) -> float:
    """Calculate confidence score 0.0 - 1.0"""
    
    required_fields = get_required_fields(component_type)
    optional_fields = get_optional_fields(component_type)
    
    # Base score from required field completion
    required_score = sum(1 for field in required_fields 
                        if extracted_data.get(field) is not None) / len(required_fields)
    
    # Bonus from optional field completion  
    optional_score = sum(1 for field in optional_fields 
                        if extracted_data.get(field) is not None) / len(optional_fields)
    
    # Validation bonus
    validation_score = 1.0 if validate_field_types(extracted_data) else 0.5
    
    return min(1.0, required_score * 0.7 + optional_score * 0.2 + validation_score * 0.1)
```

## Gap Filling Strategy

After initial parallel extraction, run a targeted gap-filling pass:

```python
async def fill_missing_fields(self, character: Character, markdown: str) -> Character:
    """Fill missing or low-confidence fields"""
    
    # Identify gaps
    missing_fields = self.find_missing_critical_fields(character)
    low_confidence_fields = self.find_low_confidence_fields(character)
    
    if not missing_fields and not low_confidence_fields:
        return character
    
    # Create targeted gap-filling prompt
    gap_fill_prompt = f"""
    Review this partially extracted character and fill missing information:
    
    Current Character State: {self.serialize_character_summary(character)}
    
    Missing Fields: {missing_fields}
    Low Confidence Fields: {low_confidence_fields}
    
    Original Document: {markdown}
    
    Provide updates for the missing/uncertain fields only.
    """
    
    # Run gap-filling LLM call
    updates = await self.llm_client.gap_fill_extraction(gap_fill_prompt)
    
    # Merge updates back into character
    return self.apply_character_updates(character, updates)
```

## Implementation Phases

### Phase 1: Core Framework
1. Set up LLM client with tool calling support
2. Implement parallel task execution framework  
3. Create tool definitions for T1-T4 (CharacterBase, PhysicalCharacteristics, AbilityScores, CombatStats)
4. Build result aggregation pipeline

### Phase 2: Basic Extraction
5. Implement remaining tool functions (T5-T12)
6. Add validation and retry logic
7. Create confidence scoring system
8. Test with sample OCR'd character sheets

### Phase 3: Enhancement
9. Implement smart defaults and inference rules
10. Add gap-filling system
11. Create cross-component validation
12. Performance optimization and caching

### Phase 4: Production
13. Error monitoring and logging
14. Batch processing capabilities  
15. Character sheet template detection
16. Quality assurance dashboards

## Usage Example

```python
# Initialize extraction system
extractor = CharacterExtractionSystem(llm_client)

# Load OCR'd character sheet
with open('character_sheet.md', 'r') as f:
    ocr_markdown = f.read()

# Extract complete character
character = await extractor.extract_character(ocr_markdown)

# Validate and save
if extractor.validate_character(character):
    character_dict = asdict(character)
    save_character(character_dict)
    print(f"Successfully extracted: {character.character_base.name}")
else:
    print("Extraction validation failed")
```

## Success Metrics

- **Accuracy**: >95% correct field extraction on clean OCR
- **Completeness**: >90% of character fields populated
- **Performance**: Complete extraction in <30 seconds
- **Robustness**: Handles 80%+ of OCR artifacts gracefully
- **Scalability**: Process 100+ character sheets per hour

This system provides a robust, parallel approach to converting messy OCR data into clean, structured character objects using the power of LLM tool calling.