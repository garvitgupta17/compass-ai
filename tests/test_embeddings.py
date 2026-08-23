"""
Compass AI - Phase 9 Embeddings Generator Unit Tests
"""
import os
import sys

import numpy as np

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.embeddings import EMBEDDING_DIM, EmbeddingGenerator


def test_embedding_generation():
    generator = EmbeddingGenerator()
    print(f"✓ Active Embedding Provider: {generator.provider}")
    
    # 1. Single string embedding
    single_text = "Python for Beginner Data Engineers"
    emb1 = generator.embed_text(single_text)
    
    assert isinstance(emb1, np.ndarray), "Output must be numpy ndarray"
    assert emb1.shape == (1, EMBEDDING_DIM), f"Expected shape (1, {EMBEDDING_DIM}), got {emb1.shape}"
    assert emb1.dtype == np.float32, f"Expected float32, got {emb1.dtype}"
    
    norm1 = np.linalg.norm(emb1[0])
    assert np.isclose(norm1, 1.0, atol=1e-3), f"Vector must be unit normalized, got norm {norm1}"
    print("✓ Single string embedding shape and normalization verified.")
    
    # 2. Batch list embedding
    texts = [
        "SQL queries and database optimization",
        "Spark distributed big data processing",
        "ETL data pipeline engineering"
    ]
    emb_batch = generator.embed_text(texts)
    assert emb_batch.shape == (3, EMBEDDING_DIM), f"Expected shape (3, {EMBEDDING_DIM}), got {emb_batch.shape}"
    print("✓ Batch list embedding verified.")
    
    # 3. Similarity check
    emb_copy = generator.embed_text(single_text)
    similarity = np.dot(emb1[0], emb_copy[0])
    assert np.isclose(similarity, 1.0, atol=1e-3), "Identical texts must have cosine similarity == 1.0"
    print("✓ Vector cosine similarity check passed.")

if __name__ == "__main__":
    test_embedding_generation()
    print("✓ ALL EMBEDDINGS GENERATOR TESTS PASSED SUCCESSFULLY!")
