"""
Compass AI - Phase 15 Adaptation Engine Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.adaptation import adapt_roadmap_progress
from core.profile import UserProfile


def test_roadmap_adaptation():
    initial_profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Engineer",
        skills={"Python": "intermediate", "SQL": "beginner"},
        deadline_weeks=12,
        hours_per_week=10
    )
    
    # User completes SQL in week 3
    report = adapt_roadmap_progress(
        profile=initial_profile,
        completed_skills=["SQL"],
        current_week=3,
        new_hours_per_week=10
    )
    
    print(f"✓ Adaptation Status: {report.status}")
    print(f"✓ Summary: {report.adaptation_summary}")
    print(f"✓ Updated Remaining Deadline: {report.updated_profile.deadline_weeks} weeks")
    print(f"✓ Updated SQL Skill Level: {report.updated_profile.skills.get('SQL')}")
    
    assert report.updated_profile.skills.get("SQL") == "intermediate", "SQL level must be updated to intermediate"
    assert report.updated_profile.deadline_weeks == 10, "Remaining deadline should be 10 weeks"
    
    print("✓ Roadmap adaptation test passed successfully.")

if __name__ == "__main__":
    test_roadmap_adaptation()
    print("✓ ALL ADAPTATION ENGINE TESTS PASSED SUCCESSFULLY!")
