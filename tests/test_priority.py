"""
Compass AI - Phase 6 Priority Engine Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.priority import calculate_priorities
from core.profile import UserProfile


def test_data_engineer_priorities():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Engineer",
        skills={
            "Python": "intermediate",
            "SQL": "beginner"
        }
    )
    
    report = calculate_priorities(profile)
    
    print(f"✓ Goal: {report.goal}")
    print(f"✓ NOW ({len(report.now)}): {[s.skill for s in report.now]}")
    print(f"✓ NEXT ({len(report.next_skills)}): {[s.skill for s in report.next_skills]}")
    print(f"✓ LATER ({len(report.later)}): {[s.skill for s in report.later]}")
    print(f"✓ SKIP ({len(report.skip)}): {[s.skill for s in report.skip]}")
    
    now_skills = [s.skill for s in report.now]
    skip_skills = [s.skill for s in report.skip]
    
    assert "SQL" in now_skills, "SQL should be categorized as NOW"
    assert "Python" in skip_skills, "Python should be categorized as SKIP"
    
    # Check reasoning formatting
    sql_item = next(s for s in report.now if s.skill == "SQL")
    assert sql_item.priority_score > 0, "Priority score must be > 0"
    print(f"✓ SQL Priority Reasoning: {sql_item.reasoning}")
    
    print("✓ Priority calculation test passed successfully.")

if __name__ == "__main__":
    test_data_engineer_priorities()
    print("✓ ALL PRIORITY ENGINE TESTS PASSED SUCCESSFULLY!")
