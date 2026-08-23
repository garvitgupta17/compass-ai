"""
Compass AI - "Should I Learn X?" Evaluation Engine
Evaluates whether learning a specific query skill is critical, elective, or a distraction
for a user's target career goal and timeline.
"""
import os
import re

import pandas as pd
from pydantic import BaseModel, Field

from core.priority import calculate_priorities
from core.profile import UserProfile
from core.skill_gap import calculate_skill_gap


class EvaluationResult(BaseModel):
    """
    Structured outcome of the 'Should I Learn X?' evaluation.
    """
    query_skill: str
    target_goal: str
    verdict: str = Field(..., description="'YES - CRITICAL FOR GOAL', 'YES - VALUABLE ELECTIVE', or 'NO - DISTRACTION FOR NOW'")
    priority_tier: str = Field(default="LATER", description="'NOW', 'NEXT', 'LATER', or 'SKIP'")
    verdict_badge: str = Field(..., description="'success', 'warning', or 'error'")
    relevance_score: int = Field(..., ge=1, le=10)
    tradeoff_analysis: str = Field(..., description="Opportunity cost analysis relative to deadline and core gaps")
    recommendation_timing: str = Field(..., description="'Learn Now', 'Learn After Core Roadmap', or 'Skip for Current Goal'")


def evaluate_skill_query(
    query_skill: str,
    profile: UserProfile,
    data_dir: str | None = None
) -> EvaluationResult:
    """
    Deterministically evaluates whether learning a given skill X aligns with user's goal and timeline.
    Supports natural questions like 'Should I learn RAG now?', 'Should I learn Kafka before Spark?', 'Can I skip SQL?'.
    """
    if data_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

    goal_skills_path = os.path.join(data_dir, "goal_skills.csv")
    df_gs = pd.read_csv(goal_skills_path)

    raw_query = query_skill.strip()
    raw_lower = raw_query.lower()
    goal_name = profile.goal.strip()

    # Extract target skill name from natural query if phrases are present
    clean_skill = raw_query
    is_skip_query = "skip" in raw_lower
    
    # Extract skill names if question format is used
    patterns = [
        r"should i learn\s+([a-zA-Z0-9\s]+?)(?:\s+now|\s+before|\s+for|\?|$)",
        r"can i skip\s+([a-zA-Z0-9\s]+?)(?:\?|$)",
        r"do i need\s+([a-zA-Z0-9\s]+?)(?:\?|$)",
        r"should i study\s+([a-zA-Z0-9\s]+?)(?:\?|$)"
    ]
    for p in patterns:
        m = re.search(p, raw_lower)
        if m:
            clean_skill = m.group(1).strip().title()
            break

    query_lower = clean_skill.lower()

    # Filter required skills for target goal
    goal_df = df_gs[df_gs["goal"].str.lower() == goal_name.lower()]
    required_skills = dict(zip(goal_df["skill"].str.lower(), goal_df["importance"]))

    gap_report = calculate_skill_gap(profile, data_dir=data_dir)
    priority_report = calculate_priorities(profile, gap_report=gap_report, data_dir=data_dir)
    urgent_gaps = [s.skill for s in gap_report.missing_skills + gap_report.needs_improvement_skills]

    # Map priority category if present in priority report
    all_priority_items = priority_report.now + priority_report.next_skills + priority_report.later + priority_report.skip
    priority_map = {item.skill.lower(): item for item in all_priority_items}
    p_item = priority_map.get(query_lower)

    # 1. Skip Query Handling ("Can I skip SQL?")
    if is_skip_query and query_lower in required_skills:
        importance = int(required_skills[query_lower])
        user_level = profile.get_skill_level(clean_skill)
        if user_level.lower() in ["intermediate", "advanced"]:
            verdict = "SKIP - ALREADY MASTERED"
            tier = "SKIP"
            badge = "warning"
            relevance = importance
            timing = "Skip for Current Goal"
            tradeoff = f"Yes, you can skip {clean_skill} because you already possess {user_level} proficiency."
        else:
            verdict = "NO - DO NOT SKIP"
            tier = "NOW" if query_lower in [s.skill.lower() for s in priority_report.now] else "NEXT"
            badge = "error"
            relevance = importance
            timing = "Learn Now"
            tradeoff = f"Do NOT skip {clean_skill}. It is a core requirement (Importance: {importance}/10) for {goal_name}."
        return EvaluationResult(
            query_skill=clean_skill,
            target_goal=goal_name,
            verdict=verdict,
            priority_tier=tier,
            verdict_badge=badge,
            relevance_score=relevance,
            tradeoff_analysis=tradeoff,
            recommendation_timing=timing
        )

    # 2. Directly Required Skill
    if query_lower in required_skills:
        importance = int(required_skills[query_lower])
        user_level = profile.get_skill_level(clean_skill)

        if user_level.lower() in ["intermediate", "advanced"]:
            verdict = "YES - VALUABLE ELECTIVE"
            tier = "SKIP"
            badge = "warning"
            relevance = importance
            timing = "Learn After Core Roadmap"
            tradeoff = (
                f"You already possess {user_level} proficiency in {clean_skill}. Focusing further time on it "
                f"yields diminishing returns compared to closing urgent missing gaps like {', '.join(urgent_gaps[:2])}."
            )
        else:
            verdict = "YES - CRITICAL FOR YOUR GOAL"
            tier = p_item.priority_category if p_item else "NOW"
            badge = "success"
            relevance = importance
            timing = "Learn Now"
            tradeoff = (
                f"{clean_skill} is a core foundation for {goal_name} (Importance: {importance}/10). "
                f"Prioritize learning this immediately to meet your {profile.deadline_weeks}-week target."
            )

    # 3. Known Elective / Complementary Skills
    elif query_lower in ["docker", "git", "linux", "dbt", "kubernetes", "airflow", "fastapi", "rag", "kafka"]:
        verdict = "YES - VALUABLE ELECTIVE"
        tier = "LATER"
        badge = "warning"
        relevance = 6
        timing = "Learn After Core Roadmap"
        tradeoff = (
            f"{clean_skill} is a great complementary skill for software & data roles, but it is not strictly required "
            f"for your core {goal_name} roadmap. Focus on urgent core gaps ({', '.join(urgent_gaps[:2])}) first."
        )

    # 4. Distraction / Misaligned Skill for Current Goal
    else:
        verdict = "NO - DISTRACTION FOR NOW"
        tier = "SKIP"
        badge = "error"
        relevance = 2
        timing = "Skip for Current Goal"
        tradeoff = (
            f"Learning {clean_skill} will consume valuable hours from your {profile.deadline_weeks}-week deadline "
            f"without advancing your core {goal_name} requirements. Focus strictly on core missing skills "
            f"({', '.join(urgent_gaps[:2])}) instead."
        )

    return EvaluationResult(
        query_skill=clean_skill,
        target_goal=goal_name,
        verdict=verdict,
        priority_tier=tier,
        verdict_badge=badge,
        relevance_score=relevance,
        tradeoff_analysis=tradeoff,
        recommendation_timing=timing
    )
