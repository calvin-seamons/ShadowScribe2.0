"""
Script 1: Build OpenAI Embeddings Storage
Pre-embed rulebook with OpenAI and save as pickle
"""
import sys
import pickle
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook.rulebook_storage import RulebookStorage


def build_openai_embeddings():
    """Load existing OpenAI embeddings and save in simplified format"""
    print("="*60)
    print("Building OpenAI Embeddings Storage for System 1")
    print("="*60)
    
    # 1. Load rulebook sections from existing storage
    print("\n1. Loading rulebook sections from existing storage...")
    storage = RulebookStorage()
    
    # Load from disk
    storage_file = project_root / "knowledge_base" / "processed_rulebook" / "rulebook_storage.pkl"
    if not storage_file.exists():
        print(f"Error: Rulebook storage not found at {storage_file}")
        print("Please run: uv run python -m scripts.build_rulebook_storage")
        return False
    
    success = storage.load_from_disk(str(storage_file))
    if not success:
        print("Error: Failed to load rulebook storage")
        return False
    
    print(f"Loaded {len(storage.sections)} sections")
    
    # Check embeddings
    sections_with_embeddings = sum(1 for s in storage.sections.values() if s.vector is not None)
    print(f"Sections with embeddings: {sections_with_embeddings}/{len(storage.sections)}")
    
    if sections_with_embeddings == 0:
        print("\nError: No embeddings found. Please generate embeddings first:")
        print("  uv run python -m scripts.build_rulebook_storage")
        return False
    
    # 2. Build category index by category value (integer)
    print("\n2. Building category index...")
    category_index = {}
    for section_id, section in storage.sections.items():
        for category in section.categories:
            cat_value = category.value
            if cat_value not in category_index:
                category_index[cat_value] = set()
            category_index[cat_value].add(section_id)
    
    # Convert sets to lists for JSON serialization
    category_index = {k: list(v) for k, v in category_index.items()}
    
    print(f"Built index for {len(category_index)} categories")
    
    # 3. Save in simplified format for System 1
    print("\n3. Saving to 574-Assignment/embeddings/...")
    output_path = Path(__file__).parent.parent / "embeddings" / "openai_embeddings.pkl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_data = {
        'sections': {sid: section.to_dict() for sid, section in storage.sections.items()},
        'category_index': category_index,
        'embedding_model': storage.embedding_model
    }
    
    with open(output_path, 'wb') as f:
        pickle.dump(save_data, f)
    
    print(f"✅ Saved {len(storage.sections)} sections with OpenAI embeddings")
    print(f"   Model: {storage.embedding_model}")
    print(f"   File: {output_path}")
    print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True


if __name__ == "__main__":
    success = build_openai_embeddings()
    sys.exit(0 if success else 1)
