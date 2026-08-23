"""
Compass AI - Phase 10 FAISS Retrieval Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.ingest import ResourceDocument
from rag.retriever import FAISSRetriever


def test_faiss_retrieval():
    retriever = FAISSRetriever()
    retriever.build_index()
    
    assert retriever.index.ntotal >= 20, "FAISS index must contain at least 20 vectors"
    
    # 1. Query Python
    results_python = retriever.search("Python programming basics for beginner data analyst", top_k=3)
    print(f"\n✓ Top Python Results ({len(results_python)}):")
    for doc, score in results_python:
        print(f"   [{score:.3f}] {doc.title} ({doc.skill}) - {doc.provider}")
    
    assert len(results_python) == 3, "Expected 3 search results"
    assert isinstance(results_python[0][0], ResourceDocument), "Result item must be ResourceDocument"
    
    # 2. Query SQL
    results_sql = retriever.search("SQL window functions and complex queries", top_k=3)
    print(f"\n✓ Top SQL Results ({len(results_sql)}):")
    for doc, score in results_sql:
        print(f"   [{score:.3f}] {doc.title} ({doc.skill}) - {doc.provider}")
        
    assert len(results_sql) == 3, "Expected 3 search results"
    
    print("\n✓ FAISS retrieval test passed successfully.")

if __name__ == "__main__":
    test_faiss_retrieval()
    print("✓ ALL FAISS RETRIEVAL TESTS PASSED SUCCESSFULLY!")
