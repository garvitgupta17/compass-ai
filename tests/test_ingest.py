"""
Compass AI - Phase 8 Resource Ingestion Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.ingest import ResourceDocument, load_and_preprocess_resources


def test_resource_ingestion():
    docs = load_and_preprocess_resources()
    
    print(f"✓ Successfully ingested {len(docs)} resource documents.")
    assert len(docs) >= 20, "Expected at least 20 resource documents"
    
    first_doc = docs[0]
    assert isinstance(first_doc, ResourceDocument), "Items must be ResourceDocument instances"
    assert len(first_doc.title) > 0, "Title cannot be empty"
    assert "Title:" in first_doc.text_content, "Text content must contain composite text"
    assert "Skill:" in first_doc.text_content, "Text content must contain skill field"
    
    print(f"✓ First Document Preview:\n{first_doc.text_content}")
    print("✓ Resource ingestion test passed successfully.")

if __name__ == "__main__":
    test_resource_ingestion()
    print("✓ ALL RESOURCE INGESTION TESTS PASSED SUCCESSFULLY!")
