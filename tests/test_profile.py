"""
Compass AI - Phase 3 UserProfile Schema Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile import UserProfile


def test_valid_profile_creation():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Engineer",
        skills={"Python": "intermediate", "SQL": "beginner"},
        deadline_weeks=12,
        hours_per_week=10,
        budget="free",
        language=["English", "Hindi"],
        learning_preference="video"
    )
    
    assert profile.education == "B.Tech Student"
    assert profile.goal == "Data Engineer"
    assert profile.skills["Python"] == "intermediate"
    assert profile.skills["SQL"] == "beginner"
    assert profile.get_skill_level("Python") == "intermediate"
    assert profile.get_skill_level("Cloud Fundamentals") == "none"
    print("✓ Valid profile creation test passed.")

def test_skill_level_normalization():
    profile = UserProfile(
        education="Student",
        experience="Fresh Graduate",
        goal="Data Analyst",
        skills={"python": "INTERMEDIATE", "SQL": "Beginner "}
    )
    assert profile.skills["python"] == "intermediate"
    assert profile.skills["SQL"] == "beginner"
    print("✓ Skill level normalization test passed.")

def test_invalid_skill_level():
    try:
        UserProfile(
            education="Student",
            experience="Student",
            goal="ML Engineer",
            skills={"Python": "master"}
        )
        assert False, "Should have raised ValueError for invalid skill level 'master'"
    except (ValueError, AssertionError) as e:
        assert "Invalid level" in str(e) or "master" in str(e)
        print("✓ Invalid skill level validation error caught correctly.")

def test_invalid_budget():
    try:
        UserProfile(
            education="Student",
            experience="Student",
            goal="ML Engineer",
            budget="expensive"
        )
        assert False, "Should have raised ValueError for invalid budget 'expensive'"
    except (ValueError, AssertionError) as e:
        assert "Invalid budget" in str(e) or "expensive" in str(e)
        print("✓ Invalid budget validation error caught correctly.")

if __name__ == "__main__":
    test_valid_profile_creation()
    test_skill_level_normalization()
    test_invalid_skill_level()
    test_invalid_budget()
    print("✓ ALL USER PROFILE SCHEMA TESTS PASSED SUCCESSFULLY!")
