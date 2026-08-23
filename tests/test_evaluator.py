"""
Compass AI - Phase 13 Evaluation Engine Unit Tests
"""
import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.evaluator import evaluate_skill_query
from core.profile import UserProfile


def test_evaluation_engine():
    profile = UserProfile(
        education="B.Tech Student",
        experience="Student",
        goal="Data Engineer",
        skills={"Python": "intermediate", "SQL": "beginner"},
        deadline_weeks=12
    )
    
    # 1. Direct Critical Core Skill
    res_critical = evaluate_skill_query("ETL", profile)
    print(f"✓ Query 'ETL': [{res_critical.verdict}] - Timing: {res_critical.recommendation_timing}")
    assert res_critical.verdict == "YES - CRITICAL FOR YOUR GOAL", "ETL must be critical for Data Engineer"
    assert res_critical.verdict_badge == "success"
    
    # 2. Complementary Elective Skill
    res_elective = evaluate_skill_query("Docker", profile)
    print(f"✓ Query 'Docker': [{res_elective.verdict}] - Timing: {res_elective.recommendation_timing}")
    assert res_elective.verdict == "YES - VALUABLE ELECTIVE", "Docker must be elective"
    assert res_elective.verdict_badge == "warning"
    
    # 3. Distraction Skill
    res_distraction = evaluate_skill_query("Rust", profile)
    print(f"✓ Query 'Rust': [{res_distraction.verdict}] - Timing: {res_distraction.recommendation_timing}")
    assert res_distraction.verdict == "NO - DISTRACTION FOR NOW", "Rust must be a distraction for Data Engineer"
    assert res_distraction.verdict_badge == "error"
    
    print("✓ 'Should I Learn X?' evaluation engine tests passed successfully.")

if __name__ == "__main__":
    test_evaluation_engine()
    print("✓ ALL EVALUATION ENGINE TESTS PASSED SUCCESSFULLY!")
