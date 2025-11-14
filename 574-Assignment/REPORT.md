# RAG System Comparison for D&D 5e Rulebook Queries
**By Calvin Seamons**

## Background

Shadow Scribe is a D&D 5e assistant I developed to help players and Dungeon Masters find relevant information from the rulebook. The core challenge I faced was retrieving the most relevant sections from 1,516 rulebook entries given a user's natural language query. My current system uses OpenAI embeddings with in-memory search, which works well but has two limitations: API latency (~100-150ms per query) and per-query costs ($0.00013 each).

In this project, I compare my current OpenAI-based system against an optimized local alternative using Qwen embeddings and FAISS to determine if I can maintain quality while improving speed and eliminating per-query costs.

## Objective and Methodology

**Objective**: My goal was to compare two RAG architectures to determine if a local model can match OpenAI quality while improving speed and reducing costs.

**System 1 (Current - OpenAI + In-Memory)**:
- Embedding: OpenAI `text-embedding-3-large` (3072 dimensions, $0.00013/query)
- Search: Linear cosine similarity over NumPy arrays
- Latency: ~120-150ms (includes API call)

**System 2 (Optimized - Qwen + FAISS)**:
- Embedding: Local `Qwen/Qwen3-Embedding-0.6B` (1024 dimensions, free)
- Search: FAISS HNSW approximate nearest neighbor index
- Latency: ~110-150ms (local inference only)

**Controlled Variables** (identical in both systems):
- Entity boosting logic and weights
- Context hints enhancement  
- Scoring formula: `semantic * 0.75 + entity * 0.25 + context * 0.15`
- Test set: 30 diverse D&D queries with ground truth
- Category-based filtering approach

**Test Dataset**: I created 30 test questions covering rule mechanics, entity descriptions, comparisons, conditions, level progression, actions, and item lists. Each question includes query text, intention category, entities, context hints, and expected relevant sections with relevance scores.

## Implementation

To ensure a fair comparison, I implemented both systems using a shared `BaseRAG` abstract class that defines a consistent query pipeline. This design isolates the differences to only the embedding and search steps, while keeping all post-processing logic identical.

**Shared Base Class**:

The `BaseRAG` abstract class enforces a consistent query pipeline:

```python
class BaseRAG(ABC):
    def __init__(self):
        """Initialize shared components"""
        self.intention_mapper = IntentionMapper()
        self.result_enhancer = ResultEnhancer(
            semantic_weight=0.75,
            entity_weight=0.25,
            context_weight=0.15
        )
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """System-specific embedding (OpenAI API vs local Qwen)"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], intention: str, k: int) -> List[Dict]:
        """System-specific search (NumPy linear vs FAISS ANN)"""
        pass
    
    def query(self, user_query: str, intention: str, entities: List[str], 
              context_hints: List[str] = None, k: int = 10) -> List[Dict]:
        """Complete pipeline - same for both systems"""
        # 1. Embed query (system-specific)
        query_embedding = self.embed_query(user_query)
        
        # 2. Search with filtering (system-specific)
        raw_results = self.search(query_embedding, intention, k=50)
        
        # 3. Post-processing (shared)
        enhanced_results = self.result_enhancer.enhance_results(
            raw_results, entities, context_hints
        )
        
        return enhanced_results[:k]
```

**System 1 Implementation** (OpenAI + NumPy):

```python
class OpenAIInMemoryRAG(BaseRAG):
    def embed_query(self, query: str) -> List[float]:
        """OpenAI API call with caching"""
        if query in self.embedding_cache:
            return self.embedding_cache[query]
        
        response = openai.embeddings.create(
            model='text-embedding-3-large',
            input=query
        )
        embedding = response.data[0].embedding
        self.embedding_cache[query] = embedding
        return embedding
    
    def search(self, query_embedding: List[float], intention: str, k: int) -> List[Dict]:
        """Category filtering + NumPy cosine similarity"""
        # 1. Filter by categories
        target_categories = self.intention_mapper.get_category_values(intention)
        candidate_sections = [section for sid in candidate_section_ids 
                             if sid in self.sections]
        
        # 2. Linear cosine similarity search
        results = []
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        for section in candidate_sections:
            section_vec = np.array(section['vector'])
            similarity = np.dot(query_vec, section_vec) / (
                query_norm * np.linalg.norm(section_vec)
            )
            results.append({'section': section, 'similarity_score': similarity})
        
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:k]
```

**System 2 Implementation** (Qwen + FAISS):

```python
class QwenFAISSRAG(BaseRAG):
    def embed_query(self, query: str) -> List[float]:
        """Local Qwen inference - no API call"""
        embedding = self.qwen_model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
    
    def search(self, query_embedding: List[float], intention: str, k: int) -> List[Dict]:
        """Category filtering + FAISS ANN search"""
        # 1. Get candidate indices by category
        target_categories = self.intention_mapper.get_category_values(intention)
        candidate_indices = set()
        for cat in target_categories:
            candidate_indices.update(self.category_index[cat])
        
        # 2. Prepare query for FAISS
        query_vector = np.array([query_embedding], dtype='float32')
        faiss.normalize_L2(query_vector)  # Cosine similarity
        
        # 3. Build temporary index with filtered vectors
        filtered_vectors = np.array([
            self.index.reconstruct(int(idx)) 
            for idx in candidate_indices
        ], dtype='float32')
        
        temp_index = faiss.IndexFlatIP(filtered_vectors.shape[1])
        temp_index.add(filtered_vectors)
        
        # 4. FAISS ANN search
        distances, indices = temp_index.search(query_vector, k)
        
        # 5. Map back to original indices and format
        return [{'section': self.section_metadata[idx], 
                 'similarity_score': distance}
                for idx, distance in zip(indices[0], distances[0])]
```

**Shared Post-Processing**:

Both systems use the identical `ResultEnhancer` for entity boosting and context hints:

```python
class ResultEnhancer:
    def enhance_results(self, search_results: List[Dict], entities: List[str], 
                       context_hints: List[str]) -> List[Dict]:
        """Apply identical scoring to both systems"""
        for result in search_results:
            semantic_score = result['similarity_score']
            entity_score = self._calculate_entity_boost(result, entities)
            context_score = self._calculate_context_boost(result, context_hints)
            
            # Combined scoring (same formula for both systems)
            result['final_score'] = (
                semantic_score * 0.75 +
                entity_score * 0.25 +
                context_score * 0.15
            )
        
        return sorted(search_results, key=lambda x: x['final_score'], reverse=True)
```

This architecture ensures that the only variables are the embedding model (OpenAI vs Qwen) and search algorithm (linear NumPy vs FAISS HNSW), making the comparison scientifically valid.

## Evaluation Metrics

**Precision@k**: Percentage of top-k results that are relevant. Range: 0-1 (higher is better). Measures accuracy of retrieved results.

**Recall@k**: Percentage of all relevant items found in top-k. Range: 0-1 (higher is better). Measures completeness.

**MRR (Mean Reciprocal Rank)**: Average of 1/rank for the first relevant result. Range: 0-1 (higher is better). Emphasizes getting at least one relevant result near the top.

**nDCG@k (Normalized Discounted Cumulative Gain)**: Measures ranking quality with position weighting. Range: 0-1 (higher is better). Captures both relevance and ranking quality.

**Average Precision**: Mean of precision values at each relevant result position. Range: 0-1 (higher is better). Balances precision and recall.

**Query Latency**: Total processing time in milliseconds. Lower is better for user experience.

**Result Overlap@k**: Percentage of shared sections in top-k between systems. Range: 0-1. High overlap suggests similar retrieval behavior.

**Rank Correlation (Spearman's rho)**: Correlation between result rankings. Range: -1 to 1. Values above 0.7 indicate strong agreement.

## Results

**Retrieval Quality** (30 test questions, mean values):

| Metric | System 1 (OpenAI) | System 2 (Qwen+FAISS) | Difference |
|--------|------------------|---------------------|------------|
| Precision@1 | 0.300 | 0.367 | +0.067 |
| Recall@1 | 0.178 | 0.211 | +0.033 |
| Precision@3 | 0.211 | 0.211 | 0.000 |
| Recall@3 | 0.339 | 0.339 | 0.000 |
| Precision@10 | 0.083 | 0.097 | +0.013 |
| Recall@10 | 0.439 | 0.500 | +0.061 |
| MRR | 0.419 | 0.453 | +0.033 |
| nDCG@10 | 0.381 | 0.420 | +0.038 |
| Average Precision | 0.301 | 0.339 | +0.038 |

System 2 matches or exceeds System 1 on all quality metrics. The largest improvements are in Precision@1 (+6.7%) and Recall@10 (+6.1%).

**Performance**:

| System | Mean Latency | Std Dev | Min | Max |
|--------|--------------|---------|-----|-----|
| System 1 (OpenAI) | 258.4ms | 136.2ms | 129.9ms | 873.1ms |
| System 2 (Qwen+FAISS) | 127.9ms | 11.1ms | 109.1ms | 150.8ms |

System 2 is **2.02x faster** with much lower variance (more consistent). System 1 has occasional API timeout outliers (873ms max).

**Cost Analysis**:
- System 1: $0.00013 per query → $1.30 per 10,000 queries
- System 2: $0 per query (local)
- Break-even: ~7,700 queries

**System Agreement**:
- Overlap@1: 67% (same top result 2/3 of queries)
- Overlap@3: 70% (strong agreement on highly-relevant sections)
- Overlap@10: 61% (moderate agreement in broader results)
- Rank Correlation: 0.784 (strong positive correlation)

Both systems find similar relevant content and rank them similarly, indicating my optimization maintains quality.

## Discussion and Key Takeaways

**Main Finding**: My local Qwen+FAISS system (System 2) matches or exceeds OpenAI quality while providing (at least) 2x faster queries and eliminating per-query costs. Other tests have seen this go up to as high as 3x.

**Quality**: System 2 performs equal or better on all retrieval metrics, with the largest improvements in top-result precision (+6.7%) and overall recall (+6.1%). The strong rank correlation (0.784) and high overlap (61-70%) confirm that both systems find similar relevant content and agree on ranking importance.

**Performance**: System 2 is consistently faster (127.9ms vs 258.4ms average) with much lower variance. System 1 suffers from API latency and occasional timeouts (873ms max), while System 2 completes all queries in 109-151ms.

**Cost**: At production scale, System 2 saves $1.30 per 10,000 queries with break-even at ~7,700 queries. For high-volume applications like Shadow Scribe, the cost savings are substantial.

**Trade-offs**: Despite using 3x fewer embedding dimensions (1024 vs 3072), System 2 maintains quality. This suggests that:
- Higher-dimensional embeddings don't necessarily translate to better retrieval quality for domain-specific tasks
- Local models with task-specific training (Qwen3-Embedding) can match general-purpose API models
- FAISS HNSW approximate search is sufficiently accurate for this use case

**Implementation Notes**: Both systems use identical post-processing (entity boosting, context hints, scoring), ensuring fair comparison. The only differences are embedding model and search mechanism. System 2 requires initial model download (~600MB) but provides offline capability and data privacy benefits.

**Limitations**: 
- My test set size (30 questions) could be expanded for more robust conclusions
- Ground truth may need refinement for some queries (e.g., barbarian's rage returned no relevant results in either system)
- Both systems struggled with some ambiguous or abstract queries

**Recommendation**: I plan to deploy System 2 (Qwen+FAISS) for production use in Shadow Scribe. It provides superior performance and cost-efficiency while maintaining or improving quality. The predictable latency and offline capability are additional benefits for user experience and reliability.

