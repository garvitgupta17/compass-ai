"""
Compass AI - Agentic Tools
Wraps existing deterministic engines and FAISS/RAG retrieval functions as tools
for the Compass Agent.
"""
from typing import Any

from core.evaluator import EvaluationResult, evaluate_skill_query
from core.profile import UserProfile
from core.roadmap import generate_roadmap
from core.skill_gap import calculate_skill_gap
from rag.ranking import RankedResource, filter_and_rank_resources


def tool_get_skill_gap(profile: UserProfile, skill_name: str | None = None) -> dict[str, Any]:
    """
    Tool 1: Retrieve learner's skill gap breakdown from the deterministic Skill Gap Engine.
    """
    gap_report = calculate_skill_gap(profile)

    if skill_name:
        skill_lower = skill_name.strip().lower()
        all_items = gap_report.existing_skills + gap_report.needs_improvement_skills + gap_report.missing_skills
        for item in all_items:
            if item.skill.lower() == skill_lower:
                return {
                    "skill": item.skill,
                    "status": item.status,
                    "user_level": item.user_level,
                    "required_level": item.required_level,
                    "gap_score": item.gap_score,
                    "reason": item.reason
                }

    return {
        "goal": gap_report.goal,
        "existing_count": len(gap_report.existing_skills),
        "needs_improvement_count": len(gap_report.needs_improvement_skills),
        "missing_count": len(gap_report.missing_skills),
        "missing_skills": [s.skill for s in gap_report.missing_skills],
        "needs_improvement_skills": [s.skill for s in gap_report.needs_improvement_skills]
    }


def tool_evaluate_skill_priority(profile: UserProfile, query_skill: str) -> dict[str, Any]:
    """
    Tool 2: Evaluates skill priority, prerequisites, and timing using the deterministic Priority Engine & Evaluator.
    """
    eval_res: EvaluationResult = evaluate_skill_query(query_skill, profile)
    return {
        "query_skill": eval_res.query_skill,
        "verdict": eval_res.verdict,
        "priority_tier": eval_res.priority_tier,
        "relevance_score": eval_res.relevance_score,
        "recommendation_timing": eval_res.recommendation_timing,
        "tradeoff_analysis": eval_res.tradeoff_analysis
    }


def tool_search_learning_resources(
    profile: UserProfile,
    skill_name: str,
    retriever: Any = None,
    top_k: int = 2
) -> list[dict[str, Any]]:
    """
    Tool 3: Calls FAISS vector similarity search and multi-factor ranking for learning resources.
    """
    if retriever is None:
        from rag.retriever import FAISSRetriever
        retriever = FAISSRetriever()
        retriever.build_index()

    ranked: list[RankedResource] = filter_and_rank_resources(
        skill_name=skill_name,
        required_level="intermediate",
        profile=profile,
        retriever=retriever,
        top_k=top_k
    )

    results = []
    for r in ranked:
        results.append({
            "title": r.resource.title,
            "provider": r.resource.provider,
            "format": r.resource.format,
            "cost": r.resource.cost,
            "language": r.resource.language,
            "url": r.resource.url,
            "composite_score": r.final_score,
            "fit_explanation": r.fit_explanation
        })
    return results


def tool_get_roadmap_context(profile: UserProfile, skill_name: str | None = None) -> dict[str, Any]:
    """
    Tool 4: Retrieves weekly roadmap schedule, capacity limits, and skill milestones.
    """
    roadmap = generate_roadmap(profile)

    if skill_name:
        skill_lower = skill_name.strip().lower()
        for item in roadmap.items:
            if item.skill.lower() == skill_lower:
                return {
                    "skill": item.skill,
                    "week_start": item.week_start,
                    "week_end": item.week_end,
                    "estimated_hours": item.estimated_hours,
                    "priority_category": item.priority_category,
                    "milestone": item.milestone,
                    "why_now": item.why_now
                }

    return {
        "total_available_capacity_hours": roadmap.total_available_capacity_hours,
        "total_estimated_hours": roadmap.total_estimated_hours,
        "total_weeks_allocated": roadmap.total_weeks_allocated,
        "capacity_tradeoff_explanation": roadmap.capacity_tradeoff_explanation,
        "scheduled_skills": [i.skill for i in roadmap.items],
        "overflow_skills": [i.skill for i in roadmap.overflow_items]
    }
