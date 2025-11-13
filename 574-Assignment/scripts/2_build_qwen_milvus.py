"""
Script 2: Build Qwen + Milvus Storage
Pre-embed rulebook with Qwen and store in Milvus
"""
import sys
import pickle
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import dependencies
try:
    from sentence_transformers import SentenceTransformer
    from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"Error: Required dependencies not installed: {e}")
    print("Install with: uv sync")


def build_qwen_milvus():
    """Embed rulebook with Qwen and store in Milvus"""
    if not DEPENDENCIES_AVAILABLE:
        return False
    
    print("="*60)
    print("Building Qwen + Milvus Storage for System 2")
    print("="*60)
    
    # 1. Load rulebook sections from pickle file directly
    print("\n1. Loading rulebook sections from pickle...")
    
    storage_file = project_root / "knowledge_base" / "processed_rulebook" / "rulebook_storage.pkl"
    if not storage_file.exists():
        print(f"Error: Rulebook storage not found at {storage_file}")
        return False
    
    # Load pickle directly without importing RulebookStorage
    with open(storage_file, 'rb') as f:
        storage_data = pickle.load(f)
    
    sections = storage_data.get('sections', {})
    print(f"Loaded {len(sections)} sections")
    
    # 2. Initialize Qwen model
    print("\n2. Loading Qwen embedding model...")
    print("   This will download ~600MB on first run...")
    model_name = 'Qwen/Qwen2.5-Coder-0.5B-Instruct'
    
    try:
        qwen_model = SentenceTransformer(model_name)
        print(f"✅ Qwen model loaded: {model_name}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return False
    
    # 3. Setup Milvus
    print("\n3. Setting up Milvus database...")
    milvus_path = Path(__file__).parent.parent / "embeddings" / "qwen_milvus.db"
    milvus_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database if it exists
    if milvus_path.exists():
        print(f"   Removing existing database: {milvus_path}")
        milvus_path.unlink()
    
    # Connect to Milvus Lite
    connections.connect("default", uri=str(milvus_path))
    print(f"   Connected to: {milvus_path}")
    
    # Drop collection if exists
    collection_name = "rulebook_sections"
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
    
    # Define schema
    fields = [
        FieldSchema(name="section_id", dtype=DataType.VARCHAR, max_length=200, is_primary=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=896),  # Qwen2.5-Coder dimension
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8000),
        FieldSchema(name="categories", dtype=DataType.ARRAY, element_type=DataType.INT64, max_capacity=10),
        FieldSchema(name="level", dtype=DataType.INT64)
    ]
    
    schema = CollectionSchema(fields, description="D&D 5e Rulebook Sections")
    collection = Collection(name=collection_name, schema=schema)
    print(f"   Created collection: {collection_name}")
    
    # 4. Embed and insert sections
    print("\n4. Embedding sections with Qwen and inserting into Milvus...")
    batch_size = 32
    batch_data = []
    
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
        text = text[:8000]  # Limit length
        
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
            
            # Add to batch as a single row dict
            batch_data.append({
                "section_id": sid,
                "embedding": embedding.tolist(),
                "title": title[:500],
                "content": content[:8000],
                "categories": cat_values,
                "level": int(level) if level else 0
            })
            
            # Insert batch when full
            if len(batch_data) >= batch_size:
                collection.insert(batch_data)
                print(f"   Inserted batch: {idx}/{total_sections} sections")
                # Reset batch
                batch_data = []
        
        except Exception as e:
            print(f"   Error processing section {sid}: {e}")
            continue
    
    # Insert remaining
    if batch_data:
        collection.insert(batch_data)
        print(f"   Inserted final batch: {total_sections}/{total_sections} sections")
    
    # 5. Create indexes
    print("\n5. Creating indexes...")
    index_params = {
        "index_type": "AUTOINDEX",  # Milvus Lite only supports FLAT, IVF_FLAT, AUTOINDEX
        "metric_type": "COSINE"
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print("   Created AUTOINDEX index on embeddings")
    
    # Flush to ensure all data is written
    collection.flush()
    
    print(f"\n✅ Stored {collection.num_entities} sections in Milvus")
    print(f"   Database: {milvus_path}")
    print(f"   Size: {milvus_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True


if __name__ == "__main__":
    success = build_qwen_milvus()
    sys.exit(0 if success else 1)
