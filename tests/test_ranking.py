"""
Compass AI - Phase 11 Resource Ranking Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile import UserProfile
from rag.ranking import filter_and_rank_resources
from rag.retriever import FAISSRetriever


def test_free_budget_filtering():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Analyst",
        budget="free",
        language=["English"]
    )
    
    retriever = FAISSRetriever()
    retriever.build_index()
    
    results = filter_and_rank_resources(
        skill_name="Python",
        required_level="beginner",
        profile=profile,
        retriever=retriever,
        top_k=3
    )
    
    print(f"✓ Ranked Free Python Resources Count: {len(results)}")
    for res in results:
        doc = res.resource
        print(f"   [{res.final_score:.3f}] {doc.title} ({doc.cost}, {doc.language}) - {doc.url}")
        assert doc.cost.lower() == "free", f"Resource must be free, got {doc.cost}"
        assert doc.language.lower() == "english", f"Resource must be English, got {doc.language}"
        
    print("✓ Free budget and English language filtering test passed successfully.")

def test_hindi_language_filtering():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Analyst",
        budget="free",
        language=["Hindi"]
    )
    
    retriever = FAISSRetriever()
    retriever.build_index()
    
    results = filter_and_rank_resources(
        skill_name="Python",
        required_level="beginner",
        profile=profile,
        retriever=retriever,
        top_k=3
    )
    
    print(f"\n✓ Ranked Hindi Python Resources Count: {len(results)}")
    for res in results:
        doc = res.resource
        print(f"   [{res.final_score:.3f}] {doc.title} ({doc.cost}, {doc.language}) - {doc.url}")
        assert doc.language.lower() == "hindi", f"Resource must be Hindi, got {doc.language}"
        
    print("✓ Hindi language filtering test passed successfully.")

if __name__ == "__main__":
    test_free_budget_filtering()
    test_hindi_language_filtering()
    print("✓ ALL FILTERING & RANKING ENGINE TESTS PASSED SUCCESSFULLY!")
