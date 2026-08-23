"""
Compass AI - Phase 5 Skill Gap Engine Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile import UserProfile
from core.skill_gap import calculate_skill_gap


def test_data_engineer_skill_gap():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Engineer",
        skills={
            "Python": "intermediate",
            "SQL": "beginner"
        }
    )
    
    report = calculate_skill_gap(profile)
    
    print(f"✓ Total Required Skills for Data Engineer: {report.total_required_skills}")
    print(f"✓ Existing Skills ({len(report.existing_skills)}): {[s.skill for s in report.existing_skills]}")
    print(f"✓ Needs Improvement ({len(report.needs_improvement_skills)}): {[s.skill for s in report.needs_improvement_skills]}")
    print(f"✓ Missing Skills ({len(report.missing_skills)}): {[s.skill for s in report.missing_skills]}")
    
    # Assertions
    existing_names = [s.skill for s in report.existing_skills]
    needs_imp_names = [s.skill for s in report.needs_improvement_skills]
    missing_names = [s.skill for s in report.missing_skills]
    
    assert "Python" in existing_names, "Python should be in Existing"
    assert "SQL" in needs_imp_names, "SQL should be in Needs Improvement"
    assert "ETL" in missing_names, "ETL should be in Missing"
    assert "Data Modeling" in missing_names, "Data Modeling should be in Missing"
    
    print("✓ Data Engineer skill gap calculation verified successfully.")

def test_unsupported_goal():
    profile = UserProfile(
        education="Student",
        experience="Student",
        goal="Astronaut",
        skills={}
    )
    try:
        calculate_skill_gap(profile)
        assert False, "Should have raised ValueError for unsupported goal 'Astronaut'"
    except ValueError:
        print("✓ Unsupported goal error caught correctly.")

if __name__ == "__main__":
    test_data_engineer_skill_gap()
    test_unsupported_goal()
    print("✓ ALL SKILL GAP ENGINE TESTS PASSED SUCCESSFULLY!")
