# 574 Assignment: D&D 5e RAG System Comparison

## Objective
Build a testing framework to compare two different RAG system architectures for D&D 5e rulebook queries, isolating the impact of embedding models and storage/retrieval mechanisms.

## System Architectures

### System 1: OpenAI + In-Memory (Baseline)
- **Embedding Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Storage**: In-memory pickle file with NumPy arrays
- **Filtering**: Python-based category pre-filtering
- **Search**: Linear cosine similarity (brute-force over filtered sections)
- **Post-processing**: Entity boosting + context hints enhancement

**Query Flow**:
```
Query → OpenAI API (1536-dim)
      ↓
Category filter in Python (1000 → 50-200 sections)
      ↓
NumPy cosine similarity (linear scan)
      ↓
Entity boosting + context hints (shared logic)
      ↓
Top-k results
```

### System 2: Qwen + Milvus (Modern Vector DB)
- **Embedding Model**: Local `Qwen/Qwen3-Embedding-0.6B` (512 dimensions)
- **Storage**: Milvus Lite vector database
- **Filtering**: Milvus native metadata filtering
- **Search**: HNSW approximate nearest neighbor (ANN)
- **Post-processing**: Entity boosting + context hints enhancement (identical to System 1)

**Query Flow**:
```
Query → Local Qwen (512-dim)
      ↓
Milvus search with native category filter (ANN + metadata filtering)
      ↓
Entity boosting + context hints (shared logic)
      ↓
Top-k results
```

## What We're Testing

### Variables Being Isolated:
1. **Embedding Model**: OpenAI 1536-dim (API) vs Qwen 512-dim (local)
2. **Retrieval Mechanism**: In-memory linear search vs Vector DB ANN search
3. **Filtering Strategy**: Python pre-filter vs Database native filtering

### Controlled Variables (Identical Across Both):
- ✅ Entity boosting logic and weights
- ✅ Context hints enhancement and weights
- ✅ Hierarchical section inclusion
- ✅ Scoring formula: `final_score = semantic * 0.75 + entity * 0.25`
- ✅ Test questions and ground truth data
- ✅ Category-to-intention mappings

## Framework Structure

```
574-Assignment/
├── README.md                          # Experiment description & results
├── config.py                          # Configuration (model paths, hyperparameters)
├── requirements.txt                   # Python dependencies
│
├── shared/                            # IDENTICAL LOGIC (DRY principle)
│   ├── __init__.py
│   ├── intention_mapper.py           # Intention → Categories mapping
│   ├── result_enhancer.py            # Entity boosting + context hints
│   └── section_hierarchy.py          # Hierarchical content inclusion
│
├── implementations/
│   ├── __init__.py
│   ├── base_rag.py                   # Abstract base class interface
│   ├── system1_openai_inmemory.py   # OpenAI + NumPy implementation
│   └── system2_qwen_milvus.py       # Qwen + Milvus implementation
│
├── embeddings/                        # Pre-computed embeddings storage
│   ├── openai_embeddings.pkl         # Rulebook embedded with OpenAI (1536-dim)
│   └── qwen_milvus.db                # Milvus Lite database with Qwen embeddings (512-dim)
│
├── ground_truth/
│   ├── test_questions.json           # 20-30 test queries with metadata
│   └── expected_sections.json        # Ground truth: query → relevant section IDs
│
├── evaluation/
│   ├── __init__.py
│   ├── metrics.py                    # Precision@k, Recall@k, MRR, nDCG
│   └── evaluator.py                  # Orchestrates experiments, collects results
│
├── results/                           # Output directory (gitignored)
│   ├── system1_results.json
│   ├── system2_results.json
│   ├── comparison_metrics.csv
│   └── comparison_report.html
│
└── scripts/
    ├── 1_build_openai_embeddings.py  # Pre-embed rulebook with OpenAI
    ├── 2_build_qwen_milvus.py        # Pre-embed rulebook with Qwen → Milvus
    └── 3_run_evaluation.py           # Main experiment runner
```

## Implementation Plan

### Phase 1: Setup & Dependencies (2-3 hours)

**Install dependencies**:
```bash
pip install pymilvus==2.4.0           # Milvus Lite
pip install transformers==4.36.0      # Qwen model loading
pip install torch==2.1.0              # PyTorch backend
pip install sentence-transformers     # Easier embedding model interface
pip install openai>=1.0.0             # OpenAI API
pip install numpy pandas matplotlib   # Data processing & visualization
```

**Download Qwen model**:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')
```

**Model specs**:
- Qwen3-Embedding-0.6B: 0.6B parameters, ~1.2GB disk, 512 dimensions
- Fast on CPU (~10-50ms), very fast on GPU (~5-10ms)

### Phase 2: Ground Truth Creation (3-4 hours)

**Select test questions**:
- Source: `docs/test_questions/rulebook-testqs.md`
- Target: 20-30 diverse queries covering all 18 intention types
- Examples:
  - "How does concentration work?" → Expected: `[spells_concentration, combat_concentration]`
  - "What is the attack bonus for a +2 weapon?" → Expected: `[combat_attack_modifiers]`
  - "Can a wizard cast spells in armor?" → Expected: `[spellcasting_armor_restrictions]`

**Create ground truth structure**:
```json
// ground_truth/test_questions.json
[
  {
    "id": 1,
    "query": "How does concentration work?",
    "intention": "describe_mechanic",
    "entities": ["concentration"],
    "expected_categories": ["SPELLCASTING", "COMBAT"],
    "expected_sections": [
      "spells_concentration_rules",
      "combat_maintaining_concentration",
      "spellcasting_concentration_duration"
    ],
    "relevance_scores": {
      "spells_concentration_rules": 1.0,
      "combat_maintaining_concentration": 0.8,
      "spellcasting_concentration_duration": 0.6
    }
  }
]
```

### Phase 3: Shared Components (3-4 hours)

**Extract from existing system**:
```python
# shared/intention_mapper.py
# Reuse from src/rag/rulebook/rulebook_types.py
class IntentionMapper:
    """Maps user intentions to D&D content categories"""
    
    @staticmethod
    def get_categories(intention: str) -> List[str]:
        """Returns list of relevant category names for filtering"""
        # Extract existing mapping from RulebookQueryIntent
        pass

# shared/result_enhancer.py
class ResultEnhancer:
    """Post-processing: entity boosting + context hints"""
    
    def enhance_results(self, search_results, entities, context_hints):
        """Apply identical scoring to both systems"""
        for result in search_results:
            semantic_score = result.similarity_score
            entity_score = self._calculate_entity_boost(result, entities)
            context_score = self._calculate_context_boost(result, context_hints)
            
            # Same weights as current system
            result.final_score = (
                semantic_score * 0.75 +
                entity_score * 0.25 +
                context_score * 0.15
            )
        
        return sorted(search_results, key=lambda x: x.final_score, reverse=True)
    
    def _calculate_entity_boost(self, result, entities):
        """Entity matching in title/content (extract from current system)"""
        pass
    
    def _calculate_context_boost(self, result, context_hints):
        """Context hint similarity (extract from current system)"""
        pass
```

### Phase 4: System Implementations (4-6 hours)

**Base interface**:
```python
# implementations/base_rag.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRAG(ABC):
    """Abstract interface ensuring both systems implement same API"""
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Embed query text into vector"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], intention: str, k: int = 10) -> List[Dict]:
        """Search with intention-based filtering"""
        pass
    
    def query(self, user_query: str, intention: str, entities: List[str], k: int = 10):
        """Complete query pipeline (same for both systems)"""
        # 1. Embed query (system-specific)
        query_embedding = self.embed_query(user_query)
        
        # 2. Search with filtering (system-specific)
        raw_results = self.search(query_embedding, intention, k=50)
        
        # 3. Post-processing (shared)
        enhanced_results = self.result_enhancer.enhance_results(
            raw_results, entities, context_hints=[]
        )
        
        return enhanced_results[:k]
```

**System 1 implementation**:
```python
# implementations/system1_openai_inmemory.py
class OpenAIInMemoryRAG(BaseRAG):
    """Current system: OpenAI embeddings + in-memory NumPy search"""
    
    def __init__(self, storage_path: str):
        with open(storage_path, 'rb') as f:
            data = pickle.load(f)
        
        self.sections = data['sections']
        self.category_index = data['category_index']
        self.embedding_cache = {}  # LRU cache for queries
    
    def embed_query(self, query: str) -> List[float]:
        """OpenAI API call with caching"""
        if query in self.embedding_cache:
            return self.embedding_cache[query]
        
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        embedding = response.data[0].embedding
        self.embedding_cache[query] = embedding
        return embedding
    
    def search(self, query_embedding: List[float], intention: str, k: int = 10):
        """Python category filtering + NumPy cosine similarity"""
        # 1. Filter by categories (Python)
        target_categories = self.intention_mapper.get_categories(intention)
        candidate_section_ids = set()
        for cat in target_categories:
            candidate_section_ids.update(self.category_index[cat])
        
        candidate_sections = [
            self.sections[sid] for sid in candidate_section_ids
        ]
        
        # 2. Cosine similarity (NumPy linear scan)
        results = []
        query_vec = np.array(query_embedding)
        
        for section in candidate_sections:
            section_vec = np.array(section['vector'])
            similarity = np.dot(query_vec, section_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(section_vec)
            )
            results.append({
                'section': section,
                'similarity_score': similarity
            })
        
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)[:k]
```

**System 2 implementation**:
```python
# implementations/system2_qwen_milvus.py
class QwenMilvusRAG(BaseRAG):
    """Modern system: Local Qwen embeddings + Milvus vector DB"""
    
    def __init__(self, milvus_uri: str):
        # Initialize Qwen model
        from sentence_transformers import SentenceTransformer
        self.qwen_model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')
        
        # Connect to Milvus
        from pymilvus import connections, Collection
        connections.connect("default", uri=milvus_uri)
        self.collection = Collection("rulebook_sections")
        self.collection.load()
    
    def embed_query(self, query: str) -> List[float]:
        """Local Qwen inference"""
        embedding = self.qwen_model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
    
    def search(self, query_embedding: List[float], intention: str, k: int = 10):
        """Milvus ANN search with native category filtering"""
        # 1. Get categories for intention
        target_categories = self.intention_mapper.get_categories(intention)
        
        # 2. Milvus search with native filtering
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 100}  # HNSW search parameter
        }
        
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            filter=f"categories in {target_categories}",  # Native Milvus filtering!
            limit=k,
            output_fields=["section_id", "title", "content", "categories", "level"]
        )
        
        # 3. Convert Milvus results to standard format
        formatted_results = []
        for hit in results[0]:
            formatted_results.append({
                'section': {
                    'id': hit.entity.get('section_id'),
                    'title': hit.entity.get('title'),
                    'content': hit.entity.get('content'),
                    'categories': hit.entity.get('categories'),
                    'level': hit.entity.get('level')
                },
                'similarity_score': hit.score
            })
        
        return formatted_results
```

### Phase 5: Build Embeddings (2-3 hours)

**Script 1: OpenAI embeddings**:
```python
# scripts/1_build_openai_embeddings.py
"""Pre-embed rulebook with OpenAI and save as pickle"""

def build_openai_embeddings():
    # 1. Load rulebook sections from existing storage
    from src.rag.rulebook.rulebook_storage import RulebookStorage
    storage = RulebookStorage()
    
    # 2. Sections already have OpenAI embeddings!
    # Just save in simplified format for System 1
    save_data = {
        'sections': {sid: section.to_dict() for sid, section in storage.sections.items()},
        'category_index': storage.category_index,
        'embedding_model': 'text-embedding-3-small'
    }
    
    with open('574-Assignment/embeddings/openai_embeddings.pkl', 'wb') as f:
        pickle.dump(save_data, f)
    
    print(f"✅ Saved {len(storage.sections)} sections with OpenAI embeddings")

if __name__ == "__main__":
    build_openai_embeddings()
```

**Script 2: Qwen + Milvus**:
```python
# scripts/2_build_qwen_milvus.py
"""Pre-embed rulebook with Qwen and store in Milvus"""

def build_qwen_milvus():
    # 1. Load rulebook sections
    from src.rag.rulebook.rulebook_storage import RulebookStorage
    storage = RulebookStorage()
    
    # 2. Initialize Qwen model
    from sentence_transformers import SentenceTransformer
    qwen_model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')
    
    # 3. Setup Milvus
    from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
    
    connections.connect("default", uri="574-Assignment/embeddings/qwen_milvus.db")
    
    # Define schema
    fields = [
        FieldSchema(name="section_id", dtype=DataType.VARCHAR, max_length=200, is_primary=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=512),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8000),
        FieldSchema(name="categories", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=10),
        FieldSchema(name="level", dtype=DataType.INT64)
    ]
    
    schema = CollectionSchema(fields, description="D&D 5e Rulebook Sections")
    collection = Collection(name="rulebook_sections", schema=schema)
    
    # 4. Embed and insert sections
    print("Embedding sections with Qwen...")
    for sid, section in storage.sections.items():
        # Embed with Qwen
        text = f"{section.title}\n\n{section.content}"
        embedding = qwen_model.encode(text[:8000], convert_to_numpy=True).tolist()
        
        # Insert into Milvus
        collection.insert({
            "section_id": [section.id],
            "embedding": [embedding],
            "title": [section.title],
            "content": [section.content[:8000]],
            "categories": [[cat.value for cat in section.categories]],
            "level": [section.level]
        })
    
    # 5. Create indexes
    print("Creating indexes...")
    index_params = {
        "index_type": "HNSW",
        "metric_type": "COSINE",
        "params": {"M": 16, "efConstruction": 200}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.create_index(field_name="categories")
    
    print(f"✅ Stored {collection.num_entities} sections in Milvus")

if __name__ == "__main__":
    build_qwen_milvus()
```

### Phase 6: Evaluation Framework (3-4 hours)

**Metrics implementation**:
```python
# evaluation/metrics.py
class RetrievalMetrics:
    """Standard information retrieval metrics"""
    
    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """Precision@k: % of top-k results that are relevant"""
        retrieved_at_k = retrieved[:k]
        relevant_retrieved = set(retrieved_at_k) & set(relevant)
        return len(relevant_retrieved) / k if k > 0 else 0.0
    
    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        """Recall@k: % of relevant results found in top-k"""
        retrieved_at_k = retrieved[:k]
        relevant_retrieved = set(retrieved_at_k) & set(relevant)
        return len(relevant_retrieved) / len(relevant) if relevant else 0.0
    
    @staticmethod
    def mean_reciprocal_rank(retrieved: List[str], relevant: List[str]) -> float:
        """MRR: 1 / rank of first relevant result"""
        for i, section_id in enumerate(retrieved, 1):
            if section_id in relevant:
                return 1.0 / i
        return 0.0
    
    @staticmethod
    def ndcg_at_k(retrieved: List[str], relevance_scores: Dict[str, float], k: int) -> float:
        """nDCG@k: Normalized discounted cumulative gain"""
        # DCG calculation with position-based discounting
        dcg = 0.0
        for i, section_id in enumerate(retrieved[:k], 1):
            rel = relevance_scores.get(section_id, 0.0)
            dcg += rel / np.log2(i + 1)
        
        # IDCG (ideal DCG)
        ideal_scores = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_scores))
        
        return dcg / idcg if idcg > 0 else 0.0
```

**Evaluator**:
```python
# evaluation/evaluator.py
class RAGEvaluator:
    """Run experiments and collect comparative metrics"""
    
    def __init__(self, system1: BaseRAG, system2: BaseRAG):
        self.system1 = system1
        self.system2 = system2
        self.metrics = RetrievalMetrics()
    
    def evaluate_all(self, test_questions: List[Dict], k_values: List[int] = [1, 3, 10]):
        """Run both systems on all test questions"""
        results = {
            'system1': [],
            'system2': [],
            'comparative_metrics': {}
        }
        
        for question in test_questions:
            # Run System 1
            start = time.perf_counter()
            s1_results = self.system1.query(
                question['query'],
                question['intention'],
                question['entities'],
                k=max(k_values)
            )
            s1_time = (time.perf_counter() - start) * 1000
            
            # Run System 2
            start = time.perf_counter()
            s2_results = self.system2.query(
                question['query'],
                question['intention'],
                question['entities'],
                k=max(k_values)
            )
            s2_time = (time.perf_counter() - start) * 1000
            
            # Compute metrics for each k
            s1_metrics = self._compute_metrics(s1_results, question, k_values)
            s2_metrics = self._compute_metrics(s2_results, question, k_values)
            
            results['system1'].append({
                'question_id': question['id'],
                'latency_ms': s1_time,
                'metrics': s1_metrics,
                'retrieved_sections': [r['section']['id'] for r in s1_results]
            })
            
            results['system2'].append({
                'question_id': question['id'],
                'latency_ms': s2_time,
                'metrics': s2_metrics,
                'retrieved_sections': [r['section']['id'] for r in s2_results]
            })
        
        # Aggregate metrics
        results['comparative_metrics'] = self._aggregate_results(results)
        
        return results
    
    def _compute_metrics(self, results, question, k_values):
        """Compute all metrics for a single query"""
        retrieved_ids = [r['section']['id'] for r in results]
        expected_ids = question['expected_sections']
        relevance_scores = question.get('relevance_scores', {})
        
        metrics = {}
        for k in k_values:
            metrics[f'precision@{k}'] = self.metrics.precision_at_k(retrieved_ids, expected_ids, k)
            metrics[f'recall@{k}'] = self.metrics.recall_at_k(retrieved_ids, expected_ids, k)
            metrics[f'ndcg@{k}'] = self.metrics.ndcg_at_k(retrieved_ids, relevance_scores, k)
        
        metrics['mrr'] = self.metrics.mean_reciprocal_rank(retrieved_ids, expected_ids)
        
        return metrics
```

### Phase 7: Run Experiments (1-2 hours)

```python
# scripts/3_run_evaluation.py
"""Main experiment runner"""

def main():
    # 1. Load test questions
    with open('574-Assignment/ground_truth/test_questions.json') as f:
        test_questions = json.load(f)
    
    # 2. Initialize both systems
    system1 = OpenAIInMemoryRAG('574-Assignment/embeddings/openai_embeddings.pkl')
    system2 = QwenMilvusRAG('574-Assignment/embeddings/qwen_milvus.db')
    
    # 3. Run evaluation
    evaluator = RAGEvaluator(system1, system2)
    results = evaluator.evaluate_all(test_questions, k_values=[1, 3, 10])
    
    # 4. Save results
    with open('574-Assignment/results/system1_results.json', 'w') as f:
        json.dump(results['system1'], f, indent=2)
    
    with open('574-Assignment/results/system2_results.json', 'w') as f:
        json.dump(results['system2'], f, indent=2)
    
    # 5. Generate comparison report
    generate_report(results)
    
    print("✅ Evaluation complete!")
    print(f"Results saved to 574-Assignment/results/")

if __name__ == "__main__":
    main()
```

## Expected Performance Comparison

### System 1 (OpenAI + In-Memory):
- **Query latency**: ~115-125ms
  - Embedding: ~100ms (API call)
  - Filtering: ~1ms
  - Search: ~10-20ms (NumPy linear)
  - Post-processing: ~5ms
- **Memory**: ~100MB (loaded sections)
- **Storage**: ~50MB (pickle file)
- **Cost**: $0.0001 per query (API)

### System 2 (Qwen + Milvus):
- **Query latency**: ~20-70ms
  - Embedding: ~10-50ms (local CPU/GPU)
  - Search: ~5-15ms (Milvus ANN)
  - Post-processing: ~5ms
- **Memory**: ~800MB (Qwen model + Milvus)
- **Storage**: ~70MB (Milvus DB)
- **Cost**: $0 per query (local)

### Expected Findings:
- **Speed**: System 2 likely faster (no API latency)
- **Quality**: Comparable retrieval quality (test with metrics)
- **Scalability**: System 2 better for larger datasets
- **Cost**: System 2 better for high query volume
- **Setup**: System 1 simpler, System 2 requires more infrastructure

## Evaluation Metrics Summary

### Retrieval Quality:
- **Precision@1**: Is the top result relevant?
- **Precision@3**: Are top 3 results relevant?
- **Recall@10**: Did we find most relevant sections?
- **MRR**: How quickly do we find relevant results?
- **nDCG@k**: Quality of ranking with graded relevance

### Performance:
- **Query latency** (ms)
- **Embedding time** (ms)
- **Search time** (ms)
- **Memory footprint** (MB)
- **Storage size** (MB)

### Cost (if applicable):
- API costs per 1000 queries
- Compute costs (GPU/CPU time)

## Dependencies

```txt
# requirements.txt
pymilvus==2.4.0              # Milvus Lite
transformers==4.36.0         # Qwen model
torch==2.1.0                 # PyTorch backend
sentence-transformers==2.2.2 # Easier model interface
openai>=1.0.0               # OpenAI API
numpy>=1.24.0               # NumPy operations
pandas                       # Results analysis
matplotlib                   # Visualization
seaborn                      # Enhanced plots
jupyter                      # Notebook for analysis
```

## Timeline

- **Phase 1** (Setup): 2-3 hours
- **Phase 2** (Ground truth): 3-4 hours
- **Phase 3** (Shared components): 3-4 hours
- **Phase 4** (System implementations): 4-6 hours
- **Phase 5** (Build embeddings): 2-3 hours
- **Phase 6** (Evaluation framework): 3-4 hours
- **Phase 7** (Run experiments): 1-2 hours

**Total estimated time**: 18-26 hours

## Key Design Principles

1. **Comparability**: Identical post-processing ensures fair comparison
2. **Isolation**: Only embedding model and retrieval mechanism differ
3. **Realism**: Both systems reflect production-ready architectures
4. **Reproducibility**: Clear scripts and configuration
5. **Extensibility**: Easy to add more systems or metrics

## Success Criteria

- ✅ Both systems run identical test questions
- ✅ Metrics computed consistently across both
- ✅ Performance data collected for all queries
- ✅ Results demonstrate clear differences or similarities
- ✅ Analysis explains why differences occur
- ✅ Recommendations for production use cases
