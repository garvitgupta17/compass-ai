"""
Compass AI - Skill Gap Engine
Deterministically computes skill gaps between user profiles and target career goals.
Differentiates current knowledge, confidence, and exposure evidence.
"""

import os

import pandas as pd
from pydantic import BaseModel, Field

from core.profile import UserProfile

# Numerical mapping of skill levels
LEVEL_SCORES = {
    "none": 0,
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}


class SkillGapItem(BaseModel):
    """
    Detailed gap analysis for a single skill.
    """
    skill: str
    importance: int = Field(..., ge=1, le=10, description="Skill importance for target goal (1-10)")
    user_level: str
    user_score: int
    required_level: str
    required_score: int
    gap_score: int = Field(..., ge=0, description="Numerical gap score (required_score - user_score)")
    confidence: str = Field(default="Medium", description="User confidence rating: 'Low', 'Medium', or 'High'")
    exposure_evidence: list[str] = Field(default_factory=list, description="Evidence from completed courses, projects, or studied topics")
    status: str = Field(..., description="'Existing', 'Needs Improvement', or 'Missing'")
    reason: str = Field(..., description="Explainable reason for gap assessment")


class SkillGapReport(BaseModel):
    """
    Summary report of all skill gaps for a user's target goal.
    """
    goal: str
    existing_skills: list[SkillGapItem] = Field(default_factory=list)
    needs_improvement_skills: list[SkillGapItem] = Field(default_factory=list)
    missing_skills: list[SkillGapItem] = Field(default_factory=list)
    total_required_skills: int = 0


def calculate_skill_gap(
    profile: UserProfile,
    data_dir: str | None = None
) -> SkillGapReport:
    """
    Deterministically computes skill gaps for a given user profile.
    """
    if data_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

    goal_skills_path = os.path.join(data_dir, "goal_skills.csv")
    skills_path = os.path.join(data_dir, "skills.csv")

    if not os.path.exists(goal_skills_path) or not os.path.exists(skills_path):
        raise FileNotFoundError(f"Knowledge base files missing in directory: {data_dir}")

    df_goal_skills = pd.read_csv(goal_skills_path)
    df_skills = pd.read_csv(skills_path)

    # Filter required skills for the target goal
    goal_name = profile.goal.strip()
    df_required = df_goal_skills[df_goal_skills["goal"].str.lower() == goal_name.lower()]

    if df_required.empty:
        raise ValueError(f"Unsupported goal '{goal_name}'. Available goals: {list(df_goal_skills['goal'].unique())}")

    # Merge required level from skills.csv
    skill_level_map = dict(zip(df_skills["skill"].str.lower(), df_skills["level"]))

    # Gather exposure evidence lists from profile
    exposure_list = (
        (profile.completed_courses or []) +
        (profile.existing_projects or []) +
        (profile.topics_studied or []) +
        (profile.topics_already_studied or [])
    )

    existing = []
    needs_improvement = []
    missing = []

    for _, row in df_required.iterrows():
        skill_name = row["skill"].strip()
        skill_name_lower = skill_name.lower()
        importance = int(row["importance"])

        # Determine required level (from skills.csv or default to 'intermediate')
        req_level_str = skill_level_map.get(skill_name_lower, "intermediate").strip().lower()
        req_score = LEVEL_SCORES.get(req_level_str, 2)

        # User current level & confidence
        user_level_str = profile.get_skill_level(skill_name).strip().lower()
        user_score = LEVEL_SCORES.get(user_level_str, 0)
        
        user_conf = "Medium"
        if profile.skill_confidence and isinstance(profile.skill_confidence, dict):
            user_conf = profile.skill_confidence.get(skill_name, profile.skill_confidence.get(skill_name_lower, "Medium"))
            if isinstance(user_conf, int):
                user_conf = "High" if user_conf >= 4 else ("Medium" if user_conf >= 3 else "Low")
            elif isinstance(user_conf, str):
                user_conf = user_conf.capitalize()

        # Find exposure evidence matching this skill
        matching_exposure = [
            item for item in exposure_list 
            if skill_name_lower in str(item).lower() or str(item).lower() in skill_name_lower
        ]

        # Gap calculation
        raw_gap = req_score - user_score
        gap_score = max(0, raw_gap)

        # Status categorization
        if user_score >= req_score:
            status = "Existing"
            reason = (
                f"Your current level ({user_level_str.capitalize()}) meets or exceeds the required level "
                f"({req_level_str.capitalize()}) for {goal_name}."
            )
        elif user_score > 0:
            status = "Needs Improvement"
            reason = (
                f"{skill_name} is required for {goal_name} at {req_level_str.capitalize()} level. "
                f"Your current level is {user_level_str.capitalize()} (Confidence: {user_conf})."
            )
        else:
            status = "Missing"
            reason = (
                f"{skill_name} is a core requirement for {goal_name} ({req_level_str.capitalize()} level), "
                f"but is not present in your current profile."
            )

        if matching_exposure:
            reason += f" Prior exposure noted: {', '.join(matching_exposure)}."

        item = SkillGapItem(
            skill=skill_name,
            importance=importance,
            user_level=user_level_str,
            user_score=user_score,
            required_level=req_level_str,
            required_score=req_score,
            gap_score=gap_score,
            confidence=user_conf,
            exposure_evidence=matching_exposure,
            status=status,
            reason=reason
        )

        if status == "Existing":
            existing.append(item)
        elif status == "Needs Improvement":
            needs_improvement.append(item)
        else:
            missing.append(item)

    # Sort gaps by importance descending
    existing.sort(key=lambda x: x.importance, reverse=True)
    needs_improvement.sort(key=lambda x: x.importance, reverse=True)
    missing.sort(key=lambda x: x.importance, reverse=True)

    return SkillGapReport(
        goal=goal_name,
        existing_skills=existing,
        needs_improvement_skills=needs_improvement,
        missing_skills=missing,
        total_required_skills=len(df_required)
    )
