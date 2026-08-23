"""
Compass AI - Phase 16 End-to-End Automated Integration Test Suite
Validates the complete pipeline end-to-end from natural language prompt extraction to
gap analysis, priority scoring, roadmap generation, vector retrieval, resource ranking,
grounded explanation, skill query evaluation, and dynamic progress adaptation.
"""
import os
import sys

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.adaptation import adapt_roadmap_progress
from core.evaluator import evaluate_skill_query
from core.priority import calculate_priorities
from core.roadmap import generate_roadmap
from core.skill_gap import calculate_skill_gap
from llm.client import extract_profile_from_text
from llm.explain import generate_recommendation_explanation
from rag.ranking import filter_and_rank_resources
from rag.retriever import FAISSRetriever


def run_e2e_pipeline_test():
    print("=" * 60)
    print("🚀 STARTING COMPASS AI END-TO-END PIPELINE VERIFICATION")
    print("=" * 60)

    # STEP 1: Natural Language Prompt Extraction
    raw_prompt = (
        "I am a final year student. I know basic SQL and intermediate Python. "
        "I want a Data Engineering internship in 3 months. I can study 10 hours per week "
        "and prefer free English resources."
    )
    print("\n[Step 1] Parsing Natural Language User Prompt...")
    profile, extraction_source = extract_profile_from_text(raw_prompt)
    print(f"✓ Source: {extraction_source}")
    print(f"✓ Profile Target Goal: {profile.goal} | Deadline: {profile.deadline_weeks}w | Commitment: {profile.hours_per_week}h/w")

    assert profile.goal == "Data Engineer", f"Expected Data Engineer, got {profile.goal}"
    assert profile.deadline_weeks == 12, f"Expected 12 weeks, got {profile.deadline_weeks}"

    # STEP 2: Skill Gap Calculation
    print("\n[Step 2] Calculating Deterministic Skill Gaps...")
    gap_report = calculate_skill_gap(profile)
    print(f"✓ Total Required Skills: {gap_report.total_required_skills}")
    print(f"✓ Existing: {len(gap_report.existing_skills)} | Needs Improvement: {len(gap_report.needs_improvement_skills)} | Missing: {len(gap_report.missing_skills)}")
    
    assert len(gap_report.existing_skills) > 0, "Should have existing skills (Python)"
    assert len(gap_report.missing_skills) > 0, "Should have missing skills (ETL, Data Modeling...)"

    # STEP 3: Priority Scoring & Categorization
    print("\n[Step 3] Computing Transparent Priority Matrix...")
    priority_report = calculate_priorities(profile, gap_report=gap_report)
    print(f"✓ NOW Tiers: {len(priority_report.now)} | NEXT Tiers: {len(priority_report.next_skills)} | SKIP Tiers: {len(priority_report.skip)}")
    
    assert len(priority_report.now) > 0, "NOW category cannot be empty"

    # STEP 4: Weekly Study Roadmap Generation
    print("\n[Step 4] Generating Weekly Study Roadmap...")
    roadmap_report = generate_roadmap(profile, priority_report=priority_report)
    print(f"✓ Allocated Weeks: {roadmap_report.total_weeks_allocated} / {profile.deadline_weeks} max")
    print(f"✓ Total Study Hours: {roadmap_report.total_estimated_hours}h")

    assert roadmap_report.total_weeks_allocated <= profile.deadline_weeks, "Roadmap must fit user deadline"
    assert len(roadmap_report.items) > 0, "Roadmap must contain scheduled items"

    # STEP 5: FAISS Vector Ingestion & Semantic Retrieval
    print("\n[Step 5] Building FAISS Vector Store Index...")
    retriever = FAISSRetriever()
    retriever.build_index()
    print(f"✓ Indexed Vectors Count: {retriever.index.ntotal}")
    assert retriever.index.ntotal >= 20, "FAISS index must contain resource vectors"

    # STEP 6: Resource Filtering & Multi-Factor Ranking
    print("\n[Step 6] Filtering & Hybrid Ranking for Top Roadmap Skill...")
    top_skill_item = roadmap_report.items[0]
    ranked_resources = filter_and_rank_resources(
        skill_name=top_skill_item.skill,
        required_level="intermediate",
        profile=profile,
        retriever=retriever,
        top_k=2
    )
    print(f"✓ Top Resource for '{top_skill_item.skill}': {ranked_resources[0].resource.title} ({ranked_resources[0].resource.cost})")
    assert len(ranked_resources) > 0, "Must return ranked resources"
    assert ranked_resources[0].resource.cost.lower() == "free", "Resource must respect free budget"

    # STEP 7: Grounded Mentorship Explanation Generation
    print("\n[Step 7] Generating Grounded Recommendation Explanation...")
    explanation = generate_recommendation_explanation(
        skill_name=top_skill_item.skill,
        priority_category=top_skill_item.priority_category,
        roadmap_weeks=f"Weeks {top_skill_item.week_start}-{top_skill_item.week_end}",
        resource=ranked_resources[0].resource,
        profile=profile
    )
    print(f"✓ Generated Explanation Preview:\n{explanation[:150]}...")
    assert len(explanation) > 50, "Explanation text cannot be empty"

    # STEP 8: "Should I Learn X?" Query Evaluation
    print("\n[Step 8] Evaluating Skill Query ('Docker')...")
    eval_res = evaluate_skill_query("Docker", profile)
    print(f"✓ Verdict for Docker: {eval_res.verdict} (Badge: {eval_res.verdict_badge})")
    assert eval_res.verdict == "YES - VALUABLE ELECTIVE"

    # STEP 9: Progress Tracking & Dynamic Roadmap Adaptation
    print("\n[Step 9] Simulating Roadmap Adaptation (SQL Completed)...")
    adapt_report = adapt_roadmap_progress(
        profile=profile,
        completed_skills=["SQL"],
        current_week=3
    )
    print(f"✓ Adaptation Status: {adapt_report.status}")
    print(f"✓ Updated Deadline: {adapt_report.updated_profile.deadline_weeks} weeks remaining")
    assert adapt_report.updated_profile.skills.get("SQL") == "intermediate"

    print("\n" + "=" * 60)
    print("🎉 ALL END-TO-END PIPELINE INTEGRATION TESTS PASSED CLEANLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_pipeline_test()
