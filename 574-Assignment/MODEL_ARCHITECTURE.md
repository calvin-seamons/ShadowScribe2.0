# Two-Stage Joint Model for D&D Query Understanding

## Overview

This document outlines a **two-stage hierarchical model** for understanding D&D player queries. The model performs three tasks:

1. **Tool Classification** - Which RAG tools are needed? (multi-label, 3 classes)
2. **Entity Extraction** - What D&D entities are mentioned? (token-level NER)
3. **Intent Classification** - What specific information is needed per tool? (conditional, gated by tool selection)

---

## Architecture

### Design Philosophy

| Stage | Task | Reasoning |
|-------|------|-----------|
| **Stage 1** | Tools + Entities | **Query-intrinsic**: Can be determined just by looking at the text |
| **Stage 2** | Intents | **Context-dependent**: Requires knowing which tool to select the right intent |

**Key Insight**: Don't predict all 61 intents at once. Use tool predictions to **gate** which intent heads are activated.

---

### Model Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         INPUT                                     │
│         "What's my AC and how does Fireball work?"               │
└─────────────────────────────┬────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    SHARED ENCODER (run once)                      │
│                        DeBERTa-v3-base                            │
│                                                                   │
│  Output: [CLS] embedding (768d) + token embeddings (768d each)   │
└──────────────────────────────┬────────────────────────────────────┘
                              ↓
         ┌────────────────────┴────────────────────┐
         ↓                                         ↓
┌─────────────────────┐                 ┌─────────────────────┐
│   STAGE 1: TOOLS    │                 │   STAGE 1: NER      │
│                     │                 │                     │
│  Input: [CLS]       │                 │  Input: all tokens  │
│  Layer: Linear(768→3)│                │  Layer: Linear(768→num_tags) │
│  Activation: Sigmoid │                │  Activation: Softmax (per token) │
│  Output: [1, 0, 1]  │                 │  Output: BIO tags   │
│                     │                 │                     │
│  character_data ✓   │                 │  O O O O O O B-SPELL O │
│  session_notes  ✗   │                 │                     │
│  rulebook       ✓   │                 │                     │
└──────────┬──────────┘                 └─────────────────────┘
           ↓
           │ Tool mask gates Stage 2
           ↓
┌──────────────────────────────────────────────────────────────────┐
│                    STAGE 2: INTENTS (Conditional)                 │
│                                                                   │
│  Only compute for selected tools!                                │
│                                                                   │
│  IF character_data selected:                                     │
│     [CLS] → Linear(768→10) → Softmax → "combat_info"            │
│                                                                   │
│  IF session_notes selected:                                      │
│     [CLS] → Linear(768→20) → Softmax → (skipped here)           │
│                                                                   │
│  IF rulebook selected:                                           │
│     [CLS] → Linear(768→31) → Softmax → "spell_details"          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                        FINAL OUTPUT                               │
│                                                                   │
│  {                                                                │
│    "tools": ["character_data", "rulebook"],                      │
│    "intents": {                                                   │
│      "character_data": "combat_info",                            │
│      "rulebook": "spell_details"                                 │
│    },                                                             │
│    "entities": [{"text": "Fireball", "type": "SPELL"}]           │
│  }                                                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Model Components

### Shared Encoder
- **Model**: `microsoft/deberta-v3-base` (304M params, 768 hidden dim)
- **Why DeBERTa**: Better than BERT/RoBERTa on classification tasks, disentangled attention helps with entity boundaries
- **Output**: 
  - `[CLS]` token: 768-dim sentence representation
  - Token embeddings: 768-dim per token for NER

### Tool Classification Head
- **Input**: `[CLS]` embedding (768 dims)
- **Architecture**: `Linear(768 → 3)`
- **Activation**: Sigmoid (independent binary decisions)
- **Output**: 3 probabilities, threshold at 0.5
- **Loss**: Binary Cross-Entropy

### NER Head
- **Input**: All token embeddings (batch × seq_len × 768)
- **Architecture**: `Linear(768 → num_bio_tags)`
- **Activation**: Softmax per token
- **Output**: BIO tag sequence
- **Loss**: Cross-Entropy (token-level)
- **Optional Enhancement**: CRF layer for better tag transitions

### Intent Classification Heads (3 separate)
- **Input**: `[CLS]` embedding (768 dims)
- **Architecture**: 
  - `character_intent`: `Linear(768 → 10)`
  - `session_intent`: `Linear(768 → 20)`
  - `rulebook_intent`: `Linear(768 → 31)`
- **Activation**: Softmax (mutually exclusive intents per tool)
- **Gating**: Only activated for selected tools
- **Loss**: Cross-Entropy (only for selected tools)

---

## Training Strategy

### Loss Function

```python
total_loss = α * tool_loss + β * ner_loss + γ * intent_loss

# Suggested weights
α = 1.0  # Tool classification
β = 1.0  # NER
γ = 1.0  # Intent (naturally smaller due to masking)
```

### Tool Loss
```python
tool_loss = BCEWithLogitsLoss(tool_logits, tool_labels)
# tool_labels: [1, 0, 1] multi-hot encoding
```

### NER Loss
```python
ner_loss = CrossEntropyLoss(ner_logits.view(-1, num_tags), ner_labels.view(-1))
# Ignore padding tokens with ignore_index=-100
```

### Intent Loss (Masked)
```python
intent_loss = 0
for tool_name, tool_idx in [("character", 0), ("session", 1), ("rulebook", 2)]:
    # Only compute loss if tool is selected in ground truth
    mask = tool_labels[:, tool_idx] == 1
    if mask.any():
        intent_loss += CrossEntropyLoss(
            intent_logits[tool_name][mask], 
            intent_labels[tool_name][mask]
        )
```

### Training Procedure

1. **Stage 1 Focus (Epochs 1-3)**: Freeze intent heads, train tool + NER
2. **Joint Training (Epochs 4-10)**: Train all heads together
3. **Fine-tuning (Epochs 11-15)**: Lower learning rate, focus on hard examples

### Hyperparameters

| Parameter | Value |
|-----------|-------|
| Encoder | `deberta-v3-base` |
| Learning Rate | 2e-5 (encoder), 1e-4 (heads) |
| Batch Size | 16-32 |
| Max Sequence Length | 128 |
| Optimizer | AdamW |
| Weight Decay | 0.01 |
| Warmup Steps | 10% of total |
| Epochs | 10-15 |

---

## Dataset Requirements

### Current Format (Already Correct)
```json
{
  "query": "What's my AC and how does Fireball work?",
  "tools": ["character_data", "rulebook"],
  "intents": {
    "character_data": "combat_info",
    "rulebook": "spell_details"
  },
  "bio_tags": ["O", "O", "O", "O", "O", "O", "B-SPELL", "O"],
  "entities": [{"text": "Fireball", "type": "SPELL", "start": 6, "end": 7}]
}
```

### Required Transformations for Training

#### 1. Tool Labels → Multi-Hot Encoding
```python
# Current: ["character_data", "rulebook"]
# Needed:  [1, 0, 1]  (binary for each tool)

TOOL_ORDER = ["character_data", "session_notes", "rulebook"]
tool_labels = [1 if t in sample["tools"] else 0 for t in TOOL_ORDER]
```

#### 2. Intent Labels → Per-Tool Indices
```python
# Current: {"character_data": "combat_info", "rulebook": "spell_details"}
# Needed: {"character": 2, "rulebook": 15}  (index in each intent list)

CHAR_INTENTS = ["basic_info", "ability_scores", "combat_info", ...]  # 10 total
intent_labels = {
    "character": CHAR_INTENTS.index(sample["intents"].get("character_data", None)),
    # ... etc
}
```

#### 3. BIO Tags → Token-Aligned IDs
```python
# Current: ["O", "O", "O", "O", "O", "O", "B-SPELL", "O"]
# Needed: [0, 0, 0, 0, 0, 0, 5, 0]  (integer tag IDs)

# IMPORTANT: Must align with tokenizer subwords!
```

---

## Dataset Enhancements

### Issue 1: Tokenizer Alignment for NER

**Problem**: Our BIO tags are word-level, but DeBERTa uses subword tokenization.

```
Word:      "Fireball"
Subwords:  ["Fire", "##ball"]
Tags:      [B-SPELL, ???]  # What tag for ##ball?
```

**Solution**: Align tags during preprocessing

```python
def align_tags_to_tokens(words, tags, tokenizer):
    """Convert word-level tags to subword-level tags."""
    encoding = tokenizer(words, is_split_into_words=True, return_offsets_mapping=True)
    
    aligned_tags = []
    previous_word_idx = None
    
    for word_idx in encoding.word_ids():
        if word_idx is None:
            aligned_tags.append(-100)  # Special tokens
        elif word_idx != previous_word_idx:
            aligned_tags.append(tag_to_id[tags[word_idx]])  # First subword
        else:
            # Subsequent subwords: use I- tag or same tag
            if tags[word_idx].startswith("B-"):
                aligned_tags.append(tag_to_id["I-" + tags[word_idx][2:]])
            else:
                aligned_tags.append(tag_to_id[tags[word_idx]])
        previous_word_idx = word_idx
    
    return aligned_tags
```

**Dataset Change**: Add `aligned_bio_tags` field or compute during DataLoader.

---

### Issue 2: Intent Label Indexing

**Problem**: Current intents are strings, need integer indices.

**Solution**: Create and save label mappings (already in `label_mappings.json`)

```python
# In generate_dataset.py, ensure we output:
{
  "tool_to_idx": {"character_data": 0, "session_notes": 1, "rulebook": 2},
  "bio_tag_to_idx": {"O": 0, "B-SPELL": 1, "I-SPELL": 2, ...},
  "intent_to_idx": {
    "character_data": {"basic_info": 0, "ability_scores": 1, ...},
    "session_notes": {"session_summary": 0, "npc_interactions": 1, ...},
    "rulebook": {"spell_details": 0, "combat_rules": 1, ...}
  }
}
```

---

### Issue 3: Add Negative Intent Handling

**Problem**: When a tool is NOT selected, what's the intent label?

**Solution**: Use -100 (PyTorch ignore index) for non-selected tools.

```python
sample = {
    "tools": ["character_data"],  # Only character
    "intents": {
        "character_data": "combat_info"
    }
}

# During preprocessing:
intent_labels = {
    "character": 2,     # combat_info index
    "session": -100,    # IGNORE - tool not selected
    "rulebook": -100    # IGNORE - tool not selected
}
```

---

### Issue 4: Class Imbalance

**Problem**: Some intents appear much more frequently than others.

**Solutions**:
1. **Weighted Loss**: Higher weight for rare intents
2. **Oversampling**: Generate more examples for rare intents
3. **Focal Loss**: Automatically focuses on hard examples

```python
# In dataset generation, track intent frequencies
intent_counts = Counter(sample["intents"][tool] for sample in data for tool in sample["tools"])

# Generate class weights
intent_weights = {intent: total / count for intent, count in intent_counts.items()}
```

---

### Issue 5: Add I- Tags for Multi-Token Entities

**Current**: Only B- tags exist
```json
"bio_tags": ["O", "O", "B-SPELL", "O"]  # "Burning Hands" → B-SPELL only?
```

**Needed**: B- and I- tags
```json
"bio_tags": ["O", "O", "B-SPELL", "I-SPELL", "O"]  # "Burning Hands" → B-SPELL I-SPELL
```

**Fix in `generate_dataset.py`**:
```python
def generate_bio_tags(query, entities):
    words = query.split()
    tags = ["O"] * len(words)
    
    for entity in entities:
        start, end = entity["start"], entity["end"]
        entity_type = entity["type"]
        
        tags[start] = f"B-{entity_type}"
        for i in range(start + 1, end):
            tags[i] = f"I-{entity_type}"  # ADD THIS
    
    return tags
```

---

## Proposed Dataset Changes Summary

| Change | Priority | Effort |
|--------|----------|--------|
| Fix I- tags for multi-word entities | **High** | Low |
| Add tokenizer-aligned tags (runtime) | **High** | Medium |
| Ensure label_mappings.json is complete | **High** | Low |
| Handle -100 for non-selected intents | **High** | Low |
| Add class weights for imbalanced intents | Medium | Low |
| Validate all intents map correctly | Medium | Low |

---

## Evaluation Metrics

### Tool Classification
- **Metric**: Exact Match Accuracy, Hamming Loss, F1 per tool
- **Target**: >95% exact match

### NER
- **Metric**: Entity-level F1 (strict and partial)
- **Strict**: Exact span + exact type match
- **Partial**: Overlap + correct type
- **Target**: >90% strict F1

### Intent Classification
- **Metric**: Accuracy per tool, Macro F1 across intents
- **Target**: >85% accuracy per tool

### Overall
- **Metric**: Full Query Accuracy (all 3 outputs correct)
- **Target**: >80%

---

## Implementation Checklist

### Dataset Generation (`generate_dataset.py`)
- [ ] Fix I- tag generation for multi-word entities
- [ ] Validate all intent strings match label_mappings.json
- [ ] Add class balance statistics to output
- [ ] Ensure consistent word tokenization (split on spaces)

### Data Loader (`dataset.py` - to create)
- [ ] Load train/val/test JSON files
- [ ] Convert tools to multi-hot encoding
- [ ] Convert intents to indices with -100 for non-selected
- [ ] Align BIO tags to subword tokenization
- [ ] Handle padding and attention masks

### Model (`model.py` - to create)
- [ ] Implement TwoStageJointModel class
- [ ] Tool head with sigmoid activation
- [ ] NER head with optional CRF
- [ ] Gated intent heads
- [ ] Forward pass with stage parameter

### Training (`train.py` - to create)
- [ ] Multi-task loss function
- [ ] Masked intent loss
- [ ] Learning rate scheduling
- [ ] Validation loop with all metrics
- [ ] Early stopping on validation loss

### Evaluation (`evaluate.py` - to create)
- [ ] Tool classification metrics
- [ ] Entity-level NER metrics
- [ ] Intent accuracy per tool
- [ ] Full query accuracy
- [ ] Confusion matrices for error analysis
