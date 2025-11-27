## Plan: Improve Local Classifier Training & Inference

Improve the Two-Stage Joint Model with confidence calibration, data augmentation (typos, variations), and placeholder-based name handling for character/party/NPC references. Remove NER from training (use gazetteer), consolidate notebooks. Add query resolution for conversational context.

### Steps

1. **Create augmentation module** at [`574-Assignment/data/augmentation.py`](574-Assignment/data/augmentation.py) with typo injection, case/contraction variations, and name placeholder pools (`{CHARACTER}`, `{PARTY_MEMBER}`, `{NPC}`).

2. **Add placeholder templates** to [`574-Assignment/data/templates/character_templates.py`](574-Assignment/data/templates/character_templates.py) and [`574-Assignment/data/templates/session_templates.py`](574-Assignment/data/templates/session_templates.py) with `{CHARACTER}`, `{PARTY_MEMBER}`, `{NPC}` patterns.

3. **Update dataset generator** [`574-Assignment/scripts/generate_dataset.py`](574-Assignment/scripts/generate_dataset.py) to apply augmentations and remove NER label generation.

4. **Create consolidated training notebook** [`574-Assignment/notebooks/model_training.ipynb`](574-Assignment/notebooks/model_training.ipynb) with: simplified model (no NER head), Focal Loss + label smoothing, temperature scaling calibration.

5. **Delete old notebooks** — remove [`574-Assignment/notebooks/02_joint_models_training.ipynb`](574-Assignment/notebooks/02_joint_models_training.ipynb) and [`574-Assignment/notebooks/03_evaluation.ipynb`](574-Assignment/notebooks/03_evaluation.ipynb).

6. **Update LocalClassifier inference** in [`src/classifiers/local_classifier.py`](src/classifiers/local_classifier.py) to add `_normalize_names()` method that replaces known character/party/NPC names with placeholder tokens before model inference.

7. **Add Query Resolver using Llama-3.2-1B-Instruct**:
   - Create [`src/classifiers/query_resolver.py`](src/classifiers/query_resolver.py) with `QueryResolver` class
   - Use `meta-llama/Llama-3.2-1B-Instruct` via Hugging Face Transformers (or Ollama for easier setup)
   - Resolves ambiguous follow-up queries: "How does the second one work?" → "How does Shield work?"
   - Add `needs_resolution()` heuristic to skip resolver for clear queries
   - No fine-tuning needed — works out of the box

8. **Update inference pipeline**:
   - `LocalClassifier` accepts optional `prev_query` and `prev_response` params
   - If `needs_resolution()` is True, resolve query first via Llama-3.2-1B
   - Chain: Resolve (if needed) → Normalize names → Classify

### Query Resolver Model Choice

**Primary: Llama-3.2-1B-Instruct** (~1GB RAM)
- More robust on complex positional references ("the second to last one")
- Highly supported by Ollama, llama.cpp, Transformers
- ~100-200ms on GPU/MPS, ~500ms on CPU

### Further Considerations

1. **Where does context come from?** At inference time, we need `character_name`, `party_members`, `known_npcs`. Option A: Pass from CentralEngine (has character loaded) / Option B: Extract from session notes storage / Option C: Both merged.

2. **Augmentation multiplier?** How many augmented variants per template? Suggest 3-5x for balance between variety and training time.

3. **Retrain immediately?** After implementing, should we regenerate dataset and retrain, or review the changes first?

4. **Ollama vs Transformers for Query Resolver?** Ollama is easier to set up and manage, Transformers gives more control. Recommend Ollama for simplicity.
