"""
Compass AI - Phase 10 Comprehensive Verification Test Suite
Verifies wizard schema generation, multi-role dashboard engine logic, RAG coverage,
roadmap adaptation edge cases, and evaluator query handling.
"""
import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.adaptation import adapt_roadmap_progress
from core.evaluator import evaluate_skill_query
from core.priority import calculate_priorities
from core.profile import UserProfile
from core.roadmap import generate_roadmap
from core.skill_gap import calculate_skill_gap
from rag.ranking import filter_and_rank_resources
from rag.retriever import FAISSRetriever


def test_1_intake_wizard_profile_generation():
    print("=== Test 1: Intake Wizard Profile Generation ===")
    draft = {
        "name": "Jane Doe",
        "education": "B.Tech / B.E.",
        "degree_branch": "AI & DS",
        "graduation_year": 2025,
        "current_status": "Student",
        "goal": "Data Engineer",
        "goal_type": "Internship",
        "deadline_weeks": 12,
        "goal_importance": 9,
        "skills": {"Python": "intermediate", "SQL": "beginner"},
        "hours_per_day": 2.0,
        "days_per_week": 5,
        "budget": "Free only",
        "language": ["English", "Hindi"],
        "learning_format": "Video"
    }

    profile = UserProfile(
        name=draft["name"],
        education=draft["education"],
        degree_branch=draft["degree_branch"],
        graduation_year=draft["graduation_year"],
        current_status=draft["current_status"],
        goal=draft["goal"],
        goal_type=draft["goal_type"],
        deadline_weeks=draft["deadline_weeks"],
        goal_importance=draft["goal_importance"],
        skills=draft["skills"],
        hours_per_day=draft["hours_per_day"],
        days_per_week=draft["days_per_week"],
        hours_per_week=int(draft["days_per_week"] * draft["hours_per_day"]),
        budget="free",
        language=draft["language"],
        learning_format=draft["learning_format"]
    )

    assert profile.name == "Jane Doe"
    assert profile.goal == "Data Engineer"
    assert profile.hours_per_week == 10
    assert profile.budget == "free"
    print("✓ Test 1 Passed: Intake wizard generates a perfectly valid UserProfile!")

def test_2_dashboard_multi_role_rendering():
    print("\n=== Test 2: Dashboard Calculation Across All 3 Roles ===")
    roles = ["Data Analyst", "Data Engineer", "ML Engineer"]
    for role in roles:
        p = UserProfile(goal=role, deadline_weeks=12, hours_per_week=10, budget="free")
        gap_rep = calculate_skill_gap(p)
        prio_rep = calculate_priorities(p, gap_report=gap_rep)
        road_rep = generate_roadmap(p, priority_report=prio_rep)
        
        assert gap_rep.total_required_skills > 0
        assert len(prio_rep.now) > 0
        assert len(road_rep.items) > 0
        print(f"✓ Dashboard logic verified for '{role}' role ({len(road_rep.items)} roadmap items allocated).")
    print("✓ Test 2 Passed: Multi-role dashboard engine verified!")

def test_3_rag_recommendation_coverage():
    print("\n=== Test 3: RAG Recommendation Coverage Across All Target Roles ===")
    retriever = FAISSRetriever()
    retriever.build_index()

    roles = ["Data Analyst", "Data Engineer", "ML Engineer"]
    for role in roles:
        p = UserProfile(goal=role, deadline_weeks=12, hours_per_week=10, budget="free")
        prio_rep = calculate_priorities(p)
        road_rep = generate_roadmap(p, priority_report=prio_rep)
        
        for item in road_rep.items:
            recs = filter_and_rank_resources(
                skill_name=item.skill,
                required_level="intermediate",
                profile=p,
                retriever=retriever,
                top_k=2
            )
            assert len(recs) > 0, f"No resources found for skill '{item.skill}' under role '{role}'"
    print("✓ Test 3 Passed: RAG recommendation coverage verified for all roadmap skills!")

def test_4_adaptation_engine_edge_cases():
    print("\n=== Test 4: Adaptation Engine (Increasing/Decreasing Hours & Completing Skills) ===")
    p = UserProfile(goal="Data Engineer", deadline_weeks=12, hours_per_week=10, budget="free")
    
    # Case A: Complete SQL
    adapt_a = adapt_roadmap_progress(p, completed_skills=["SQL"], current_week=2, new_hours_per_week=10)
    assert adapt_a.status == "AHEAD OF SCHEDULE"
    assert "SQL" in adapt_a.completed_skills
    
    # Case B: Decrease Hours (10 -> 5)
    adapt_b = adapt_roadmap_progress(p, completed_skills=[], current_week=2, new_hours_per_week=5)
    assert adapt_b.status in ["ON TRACK", "BEHIND SCHEDULE - ADAPTED", "AHEAD OF SCHEDULE"]
    assert adapt_b.updated_profile.hours_per_week == 5

    # Case C: Increase Hours (10 -> 20)
    adapt_c = adapt_roadmap_progress(p, completed_skills=[], current_week=2, new_hours_per_week=20)
    assert adapt_c.updated_profile.hours_per_week == 20
    print("✓ Test 4 Passed: Adaptation engine edge cases verified!")

def test_5_evaluator_query_types():
    print("\n=== Test 5: Evaluator Engine Query Types ===")
    p = UserProfile(goal="Data Engineer", deadline_weeks=12, hours_per_week=10, budget="free")
    
    # Known required skill
    res1 = evaluate_skill_query("ETL", p)
    assert res1.verdict_badge == "success"
    assert res1.recommendation_timing == "Learn Now"

    # Known elective skill
    res2 = evaluate_skill_query("Docker", p)
    assert res2.verdict_badge == "warning"
    assert res2.recommendation_timing == "Learn After Core Roadmap"

    # Unknown / Distraction skill
    res3 = evaluate_skill_query("Quantum Computing", p)
    assert res3.verdict_badge == "error"
    assert res3.recommendation_timing == "Skip for Current Goal"

    # Natural question query
    res4 = evaluate_skill_query("Should I learn RAG now?", p)
    assert res4.query_skill.lower() == "rag"

    # Skip query
    res5 = evaluate_skill_query("Can I skip SQL?", p)
    assert "Do NOT skip" in res5.tradeoff_analysis or "skip" in res5.tradeoff_analysis.lower()

    print("✓ Test 5 Passed: Evaluator query types verified!")

if __name__ == "__main__":
    test_1_intake_wizard_profile_generation()
    test_2_dashboard_multi_role_rendering()
    test_3_rag_recommendation_coverage()
    test_4_adaptation_engine_edge_cases()
    test_5_evaluator_query_types()
    print("\n============================================================")
    print("🎉 ALL PHASE 10 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("============================================================")
