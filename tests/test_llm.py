"""
Compass AI - Phase 4 LLM Extraction Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile import UserProfile
from llm.client import extract_profile_from_text


def test_natural_language_extraction():
    sample_prompt = (
        "I am a final year student. I know basic SQL and intermediate Python. "
        "I want a Data Engineering internship in 3 months. I can study 10 hours per week "
        "and prefer free English resources."
    )
    
    profile, source = extract_profile_from_text(sample_prompt)
    
    print(f"✓ Extraction Source: {source}")
    print(f"✓ Extracted Profile: {profile.model_dump_json(indent=2)}")
    
    assert isinstance(profile, UserProfile), "Result must be a validated UserProfile instance"
    assert profile.goal == "Data Engineer", f"Expected 'Data Engineer', got '{profile.goal}'"
    assert profile.skills.get("Python") == "intermediate", f"Expected Python 'intermediate', got '{profile.skills.get('Python')}'"
    assert profile.skills.get("SQL") == "beginner", f"Expected SQL 'beginner', got '{profile.skills.get('SQL')}'"
    assert profile.deadline_weeks == 12, f"Expected 12 weeks, got {profile.deadline_weeks}"
    assert profile.hours_per_week == 10, f"Expected 10 hours/week, got {profile.hours_per_week}"
    assert profile.budget == "free", f"Expected budget 'free', got '{profile.budget}'"
    
    print("✓ Natural language profile extraction test passed.")

def test_empty_input_handling():
    try:
        extract_profile_from_text("")
        assert False, "Should have raised ValueError on empty string"
    except ValueError:
        print("✓ Empty input error caught correctly.")

if __name__ == "__main__":
    test_natural_language_extraction()
    test_empty_input_handling()
    print("✓ ALL LLM EXTRACTION TESTS PASSED SUCCESSFULLY!")
