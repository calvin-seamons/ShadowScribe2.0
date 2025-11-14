"""
Script 2: Build Qwen + FAISS Storage
Pre-embed rulebook with Qwen and store in FAISS index
"""
import sys
import pickle
from pathlib import Path
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import dependencies
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"Error: Required dependencies not installed: {e}")
    print("Install with: uv sync")


def build_qwen_faiss():
    """Embed rulebook with Qwen and store in FAISS index"""
    if not DEPENDENCIES_AVAILABLE:
        return False
    
    print("="*60)
    print("Building Qwen + FAISS Storage for System 2")
    print("="*60)
    
    # 1. Load rulebook sections from pickle file directly
    print("\n1. Loading rulebook sections from pickle...")
    
    storage_file = project_root / "knowledge_base" / "processed_rulebook" / "rulebook_storage.pkl"
    if not storage_file.exists():
        print(f"Error: Rulebook storage not found at {storage_file}")
        print("Please run: uv run python -m scripts.build_rulebook_storage")
        return False
    
    # Load pickle directly without importing RulebookStorage
    with open(storage_file, 'rb') as f:
        storage_data = pickle.load(f)
    
    sections = storage_data.get('sections', {})
    print(f"Loaded {len(sections)} sections")
    
    # 2. Initialize Qwen model
    print("\n2. Loading Qwen3 embedding model...")
    print("   This will download model on first run...")
    model_name = 'Qwen/Qwen3-Embedding-0.6B'
    
    try:
        qwen_model = SentenceTransformer(model_name)
        embedding_dim = qwen_model.get_sentence_embedding_dimension()
        print(f"✅ Qwen model loaded: {model_name}")
        print(f"   Embedding dimension: {embedding_dim}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return False
    
    # 3. Prepare data structures
    print("\n3. Preparing data structures...")
    section_ids = []
    section_metadata = []
    embeddings_list = []
    
    # 4. Embed sections
    print("\n4. Embedding sections with Qwen...")
    total_sections = len(sections)
    
    for idx, (sid, section) in enumerate(sections.items(), 1):
        # Handle both dict and object formats
        def get_field(obj, field, default=''):
            if isinstance(obj, dict):
                return obj.get(field, default)
            return getattr(obj, field, default)
        
        # Embed with Qwen
        title = get_field(section, 'title', '')
        content = get_field(section, 'content', '')
        text = f"{title}\n\n{content}"
        
        try:
            embedding = qwen_model.encode(text, convert_to_numpy=True, show_progress_bar=False)
            
            # Convert category enums to integers
            cats = get_field(section, 'categories', [])
            if cats and hasattr(cats[0], 'value'):
                cat_values = [cat.value for cat in cats]
            elif isinstance(cats, list):
                cat_values = cats
            else:
                cat_values = [cats] if cats else []
            
            level = get_field(section, 'level', 0)
            
            # Store data
            section_ids.append(sid)
            section_metadata.append({
                'id': sid,
                'title': title,
                'content': content,
                'categories': cat_values,
                'level': int(level) if level else 0
            })
            embeddings_list.append(embedding)
            
            if idx % 100 == 0:
                print(f"   Processed {idx}/{total_sections} sections")
        
        except Exception as e:
            print(f"   Error processing section {sid}: {e}")
            continue
    
    print(f"   ✅ Embedded {len(embeddings_list)} sections")
    
    # 5. Build FAISS index
    print("\n5. Building FAISS index...")
    embeddings_matrix = np.array(embeddings_list).astype('float32')
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings_matrix)
    
    # Create HNSW index for fast ANN search
    index = faiss.IndexHNSWFlat(embedding_dim, 32)  # 32 = number of neighbors
    index.hnsw.efConstruction = 100  # Higher = better quality, slower build
    
    print(f"   Adding {len(embeddings_matrix)} vectors to index...")
    index.add(embeddings_matrix)
    print(f"   ✅ FAISS index built with {index.ntotal} vectors")
    
    # 6. Build category index for filtering
    print("\n6. Building category index for fast filtering...")
    category_index = {}
    for idx, metadata in enumerate(section_metadata):
        for cat in metadata['categories']:
            if cat not in category_index:
                category_index[cat] = []
            category_index[cat].append(idx)
    
    print(f"   Built index for {len(category_index)} categories")
    
    # 7. Save everything
    print("\n7. Saving to 574-Assignment/embeddings/...")
    output_path = Path(__file__).parent.parent / "embeddings"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    faiss_index_path = output_path / "qwen_faiss.index"
    faiss.write_index(index, str(faiss_index_path))
    
    # Save metadata and mappings
    metadata_path = output_path / "qwen_metadata.pkl"
    save_data = {
        'section_ids': section_ids,
        'section_metadata': section_metadata,
        'category_index': category_index,
        'embedding_model': model_name,
        'embedding_dim': embedding_dim
    }
    
    with open(metadata_path, 'wb') as f:
        pickle.dump(save_data, f)
    
    print(f"✅ Saved FAISS index and metadata")
    print(f"   FAISS index: {faiss_index_path} ({faiss_index_path.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"   Metadata: {metadata_path} ({metadata_path.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"   Total sections: {len(section_ids)}")
    print(f"   Model: {model_name}")
    
    return True


if __name__ == "__main__":
    success = build_qwen_faiss()
    sys.exit(0 if success else 1)
