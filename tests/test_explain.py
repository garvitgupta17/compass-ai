"""
Compass AI - Phase 12 Explanation Module Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile import UserProfile
from llm.explain import generate_recommendation_explanation
from rag.ingest import ResourceDocument


def test_explanation_generation():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Analyst",
        budget="free",
        language=["English"]
    )
    
    doc = ResourceDocument(
        id=1,
        title="Python for Beginners",
        skill="Python",
        level="beginner",
        language="English",
        cost="free",
        format="video",
        duration="6h",
        provider="FreeCodeCamp",
        url="https://www.youtube.com/watch?v=rfscVS0vtbw",
        text_content="Python course"
    )
    
    exp = generate_recommendation_explanation(
        skill_name="Python",
        priority_category="NOW",
        roadmap_weeks="Weeks 1-2",
        resource=doc,
        profile=profile
    )
    
    print(f"✓ Generated Explanation:\n{exp}")
    assert len(exp) > 50, "Explanation must be a detailed text string"
    assert "Python" in exp, "Explanation must reference skill name"
    assert "FreeCodeCamp" in exp or "free" in exp.lower(), "Explanation must reference provider or cost"
    
    print("✓ Explanation generation test passed successfully.")

if __name__ == "__main__":
    test_explanation_generation()
    print("✓ ALL EXPLANATION MODULE TESTS PASSED SUCCESSFULLY!")
