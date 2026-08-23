"""
Compass AI - Roadmap Engine
Generates realistic, prerequisite-aware weekly study roadmaps based on
priority tiers, available capacity (hours/week), session duration preferences, and deadline constraints.
"""

import math
import os

import pandas as pd
from pydantic import BaseModel, Field

from core.priority import PrioritizedSkillItem, PriorityReport, calculate_priorities
from core.profile import UserProfile


class RoadmapItem(BaseModel):
    """
    Individual scheduled item in the weekly roadmap.
    """
    skill: str
    priority_category: str
    priority_score: float
    estimated_hours: int
    week_start: int
    week_end: int
    prerequisites: list[str] = Field(default_factory=list)
    milestone: str
    why_now: str
    recommended_session_length: str = Field(default="1 hour", description="Target session duration: 30 min, 1 hour, 2 hours")
    is_overflow: bool = Field(default=False, description="True if scheduled beyond user deadline")


class RoadmapReport(BaseModel):
    """
    Complete weekly study roadmap report.
    """
    goal: str
    total_weeks_allocated: int
    deadline_weeks: int
    hours_per_week: int
    total_estimated_hours: int
    total_available_capacity_hours: int
    capacity_tradeoff_explanation: str = Field(default="", description="Explanation of workload vs capacity tradeoffs")
    items: list[RoadmapItem] = Field(default_factory=list)
    overflow_items: list[RoadmapItem] = Field(default_factory=list, description="Items that couldn't fit before deadline")


def generate_roadmap(
    profile: UserProfile,
    priority_report: PriorityReport | None = None,
    data_dir: str | None = None
) -> RoadmapReport:
    """
    Deterministically generates a weekly roadmap fitting user capacity and deadline.
    """
    if data_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

    if priority_report is None:
        priority_report = calculate_priorities(profile, data_dir=data_dir)

    milestones_path = os.path.join(data_dir, "milestones.csv")
    milestone_map = {}
    hours_map = {}
    if os.path.exists(milestones_path):
        df_m = pd.read_csv(milestones_path)
        for _, row in df_m.iterrows():
            s_name = row["skill"].strip().lower()
            milestone_map[s_name] = str(row["milestone"]).strip()
            hours_map[s_name] = int(row["default_hours"])

    # Combine items in priority sequence: NOW -> NEXT -> LATER
    queue: list[PrioritizedSkillItem] = (
        priority_report.now + 
        priority_report.next_skills + 
        priority_report.later
    )

    hours_per_week = profile.hours_per_week
    deadline_weeks = profile.deadline_weeks
    available_capacity = hours_per_week * deadline_weeks
    user_session_pref = profile.session_duration or profile.preferred_session_duration or "1 hour"

    current_week = 1
    scheduled_items: list[RoadmapItem] = []
    overflow_items: list[RoadmapItem] = []
    total_hours_allocated = 0

    for item in queue:
        skill_lower = item.skill.lower()
        default_h = hours_map.get(skill_lower, 15)
        
        # Scale hours based on gap score
        if item.gap_score == 1:
            est_hours = max(6, int(default_h * 0.6))
        else:
            est_hours = default_h

        # Duration in weeks
        duration_weeks = max(1, math.ceil(est_hours / hours_per_week))
        week_start = current_week
        week_end = week_start + duration_weeks - 1

        is_overflow = False
        if week_start > deadline_weeks:
            is_overflow = True

        m_desc = milestone_map.get(
            skill_lower, 
            f"Master core concepts and complete practical exercises in {item.skill}."
        )

        why_now = (
            f"Scheduled in Weeks {week_start}-{week_end} based on '{item.priority_category}' priority "
            f"(Score: {item.priority_score}) and {est_hours}h effort at {hours_per_week}h/week."
        )

        r_item = RoadmapItem(
            skill=item.skill,
            priority_category=item.priority_category,
            priority_score=item.priority_score,
            estimated_hours=est_hours,
            week_start=week_start,
            week_end=week_end,
            prerequisites=item.prerequisites,
            milestone=m_desc,
            why_now=why_now,
            recommended_session_length=user_session_pref,
            is_overflow=is_overflow
        )

        if not is_overflow:
            scheduled_items.append(r_item)
            total_hours_allocated += est_hours
            current_week = week_end + 1
        else:
            overflow_items.append(r_item)

    max_allocated_week = max([i.week_end for i in scheduled_items], default=0)

    # Tradeoff explanation if capacity exceeded
    tradeoff_explanation = ""
    if overflow_items:
        tradeoff_explanation = (
            f"Total estimated learning workload ({total_hours_allocated + sum(i.estimated_hours for i in overflow_items)}h) "
            f"exceeds available capacity ({available_capacity}h over {deadline_weeks} weeks). "
            f"Retained core NOW priorities ({', '.join(i.skill for i in scheduled_items if i.priority_category == 'NOW')}) "
            f"and moved lower-priority electives to overflow to fit your timeframe."
        )
    else:
        tradeoff_explanation = (
            f"Roadmap workload ({total_hours_allocated}h) fits comfortably within your available capacity "
            f"({available_capacity}h over {deadline_weeks} weeks)."
        )

    return RoadmapReport(
        goal=profile.goal,
        total_weeks_allocated=max_allocated_week,
        deadline_weeks=deadline_weeks,
        hours_per_week=hours_per_week,
        total_estimated_hours=total_hours_allocated,
        total_available_capacity_hours=available_capacity,
        capacity_tradeoff_explanation=tradeoff_explanation,
        items=scheduled_items,
        overflow_items=overflow_items
    )
