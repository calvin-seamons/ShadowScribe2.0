# 574 Assignment: D&D 5e RAG System Comparison

Comprehensive testing framework comparing two RAG system architectures for D&D 5e rulebook queries.

## Systems Under Test

### System 1: OpenAI + In-Memory (Baseline)
- **Embedding Model**: OpenAI `text-embedding-3-large` (3072 dimensions)
- **Storage**: In-memory pickle file with NumPy arrays
- **Filtering**: Python-based category pre-filtering
- **Search**: Linear cosine similarity (brute-force)
- **Expected**: ~120-135ms query latency, $0.00013 per query

### System 2: Qwen + FAISS (Local Vector Search)
- **Embedding Model**: Local `Qwen/Qwen3-Embedding-0.6B` (1024 dimensions)
- **Storage**: FAISS HNSW index with metadata pickle
- **Filtering**: Python-based category pre-filtering with FAISS subset search
- **Search**: HNSW approximate nearest neighbor (ANN)
- **Expected**: ~120-150ms query latency, $0 per query

## What We're Comparing

**Variables Being Isolated:**
1. Embedding Model: OpenAI 3072-dim (API) vs Qwen3 1024-dim (local)
2. Retrieval Mechanism: In-memory linear search vs FAISS HNSW ANN search
3. Filtering Strategy: Python pre-filter in both systems
4. Cost vs Performance Trade-off

**Controlled (Identical) Across Both:**
- ✅ Entity boosting logic and weights
- ✅ Context hints enhancement
- ✅ Scoring formula: `semantic * 0.75 + entity * 0.25`
- ✅ Test questions and ground truth
- ✅ Category-to-intention mappings

## Quick Start

### Prerequisites
- **Python 3.12** (required for dependency compatibility)
- **uv** package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **pyenv** (recommended): `brew install pyenv` or visit [pyenv](https://github.com/pyenv/pyenv)

### 1. Install Dependencies

**Automated Setup with uv (Recommended):**

**macOS/Linux:**
```bash
cd 574-Assignment
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
cd 574-Assignment
setup.bat
```

**Manual Setup:**
```bash
# Ensure Python 3.12 is installed and active
pyenv install 3.12
pyenv local 3.12

# Install dependencies with uv
uv sync

# Build embeddings
uv run python scripts/1_build_openai_embeddings.py
uv run python scripts/2_build_qwen_faiss.py

# Run evaluation
uv run python scripts/3_run_evaluation.py
```

**Manual Installation:**
```bash
cd 574-Assignment
pip install -r requirements.txt
```

### 2. Build Embeddings (if not using setup script)

**System 1 (OpenAI):**
```bash
# macOS/Linux
python scripts/1_build_openai_embeddings.py

# Windows
python scripts\1_build_openai_embeddings.py
```

**System 2 (Qwen + FAISS):**
```bash
# macOS/Linux
python scripts/2_build_qwen_faiss.py

# Windows
python scripts\2_build_qwen_faiss.py
```
*Note: First run downloads Qwen3-Embedding model*

### 3. Run Evaluation
```bash
# macOS/Linux
python scripts/3_run_evaluation.py

# Windows
python scripts\3_run_evaluation.py
```

## Project Structure

```
574-Assignment/
├── README.md                          # This file
├── config.py                          # Configuration
├── requirements.txt                   # Dependencies
│
├── shared/                            # Shared components (DRY)
│   ├── intention_mapper.py           # Intention → Categories
│   └── result_enhancer.py            # Entity boosting + context hints
│
├── implementations/                   # RAG systems
│   ├── base_rag.py                   # Abstract interface
│   ├── system1_openai_inmemory.py   # OpenAI + NumPy
│   └── system2_qwen_faiss.py        # Qwen + FAISS
│
├── embeddings/                        # Pre-computed storage
│   ├── openai_embeddings.pkl         # System 1 (generated)
│   ├── qwen_faiss.index              # System 2 FAISS index (generated)
│   └── qwen_metadata.pkl             # System 2 metadata (generated)
│
├── ground_truth/                      # Test data
│   └── test_questions.json           # 10 test queries
│
├── evaluation/                        # Metrics framework
│   ├── metrics.py                    # Precision@k, Recall@k, MRR, nDCG
│   └── evaluator.py                  # Experiment orchestration
│
├── results/                           # Generated outputs
│   ├── system1_results_*.json
│   ├── system2_results_*.json
│   ├── comparative_metrics_*.json
│   └── comparison_report_*.csv
│
└── scripts/                           # Build & run scripts
    ├── 1_build_openai_embeddings.py
    ├── 2_build_qwen_faiss.py
    └── 3_run_evaluation.py
```

## Evaluation Metrics

### Retrieval Quality
- **Precision@k**: % of top-k results that are relevant
- **Recall@k**: % of relevant results found in top-k
- **MRR**: Mean Reciprocal Rank of first relevant result
- **nDCG@k**: Normalized Discounted Cumulative Gain
- **Average Precision**: Mean precision at relevant positions

### Performance
- **Query Latency**: Total time per query (ms)
  - Cold start (first query)
  - Warm cache (repeated queries)
- **Memory Footprint**: RAM usage during queries
- **Storage Size**: Disk space for embeddings

### Result Agreement
- **Top-k Overlap**: % of shared sections in top-k
- **Rank Correlation**: Spearman's rho between rankings
- **Category Diversity**: Distribution of categories in results

## Expected Findings

### Speed
- System 2 likely **2-3x faster** (no API latency)
- System 1: ~120-135ms (100ms+ for OpenAI API call)
- System 2: ~20-70ms (local Qwen inference)

### Quality
- OpenAI 3072-dim may have slight edge in semantic understanding
- Test if 3.4x more dimensions translates to better retrieval
- Qwen 896-dim may be "good enough" for D&D rules

### Cost-Quality Trade-off
- System 1: $0.00013 per query (adds up at scale)
- System 2: $0 per query (one-time setup cost)
- **Break-even**: ~7,700 queries makes System 2 cheaper

### Scalability
- System 1: Linear growth O(n) with brute-force search
- System 2: Sub-linear growth O(log n) with HNSW ANN
- At 10,000 sections: System 2 advantage increases significantly

## Test Questions

10 diverse questions covering:
- Rule mechanics (concentration, resting)
- Entity descriptions (dwarf traits, fireball spell)
- Level progression (fighter abilities)
- Combat actions (turn options, attack calculations)
- Conditions (poisoned status)
- Comparisons (wizard vs sorcerer)
- Creature abilities (lich powers)

See `ground_truth/test_questions.json` for details.

## Results Interpretation

### Good Performance
- Precision@1 > 0.8 (top result is relevant)
- Recall@10 > 0.7 (most relevant sections found)
- MRR > 0.7 (relevant results near top)
- nDCG@10 > 0.75 (good ranking quality)

### System Comparison
- **If System 2 matches System 1 quality**: Clear win (faster, cheaper, scales better)
- **If System 2 lags 5-10%**: Still viable for cost-sensitive applications
- **If System 2 lags >15%**: OpenAI's extra dimensions are worth the cost

## Configuration

Edit `config.py` to customize:
- Embedding models and dimensions
- FAISS index parameters
- Scoring weights (semantic, entity, context)
- Evaluation k-values

## Troubleshooting

**"Rulebook storage not found"**
```bash
# Build rulebook embeddings first
cd ..
# macOS/Linux
python -m scripts.build_rulebook_storage
# Windows
python -m scripts.build_rulebook_storage
```

**"FAISS or SentenceTransformers not installed"**
```bash
uv sync
```

**"OpenAI API key not found"**
```bash
# Add to .env file in project root
# macOS/Linux
echo "OPENAI_API_KEY=sk-..." >> ../.env
# Windows (PowerShell)
Add-Content ..\.env "OPENAI_API_KEY=sk-..."
```

**"torch version incompatible"**
```bash
# Install latest PyTorch for your platform
# Visit: https://pytorch.org/get-started/locally/
pip install torch --upgrade
```

## Citation

If you use this framework:
```
574 Assignment: RAG System Comparison Framework
Author: [Your Name]
Course: CSE 574
Year: 2025
```

## License

MIT License - See project root for details
