"""
Compass AI - Priority Engine
Calculates transparent priority scores (NOW, NEXT, LATER, SKIP) for skills based on
goal importance, skill gap distance, prerequisite satisfaction, user preferences, and constraints.
"""

import os

import pandas as pd
from pydantic import BaseModel, Field

from core.profile import UserProfile
from core.skill_gap import (
    LEVEL_SCORES,
    SkillGapItem,
    SkillGapReport,
    calculate_skill_gap,
)

# Centralized Scoring Constants
WEAK_AREA_BOOST: float = 1.5
USER_PRIORITY_BOOST: float = 2.0
POSTPONE_PENALTY: float = 2.0


class PriorityScoreBreakdown(BaseModel):
    """
    Detailed, transparent breakdown of numerical components contributing to final priority score.
    """
    base_score: float = Field(..., description="Raw base score (importance * gap_score)")
    goal_contribution: float = Field(..., description="Goal importance weight component")
    gap_contribution: float = Field(..., description="Skill gap step distance component")
    prerequisite_contribution: float = Field(..., description="Prerequisite factor multiplier (1.0, 0.5, 0.2)")
    urgency_contribution: float = Field(default=0.0, description="Timeline urgency factor adjustment")
    weak_area_adjustment: float = Field(default=0.0, description="Weak area boost (+1.5)")
    user_priority_adjustment: float = Field(default=0.0, description="Explicit user priority boost (+2.0)")
    postpone_adjustment: float = Field(default=0.0, description="User postponement penalty (-2.0)")
    final_score: float = Field(..., description="Final combined priority score")


class PrioritizedSkillItem(BaseModel):
    """
    Skill item with computed priority category, score, structured breakdown, and transparent reasoning.
    """
    skill: str
    priority_category: str = Field(..., description="'NOW', 'NEXT', 'LATER', or 'SKIP'")
    priority_score: float = Field(..., description="Explainable numerical priority score")
    importance: int
    gap_score: int
    user_level: str
    required_level: str
    confidence: str = Field(default="Medium")
    prerequisites: list[str] = Field(default_factory=list)
    unsatisfied_prerequisites: list[str] = Field(default_factory=list)
    score_breakdown: PriorityScoreBreakdown | None = Field(default=None, description="Detailed numerical score breakdown")
    structured_reasons: list[str] = Field(default_factory=list, description="Fact-based deterministic reasons")
    reasoning: str = Field(..., description="Grounded explanation of why this priority was assigned")


class PriorityReport(BaseModel):
    """
    Categorized priority report for all skills.
    """
    goal: str
    now: list[PrioritizedSkillItem] = Field(default_factory=list)
    next_skills: list[PrioritizedSkillItem] = Field(default_factory=list)
    later: list[PrioritizedSkillItem] = Field(default_factory=list)
    skip: list[PrioritizedSkillItem] = Field(default_factory=list)


def calculate_priorities(
    profile: UserProfile,
    gap_report: SkillGapReport | None = None,
    data_dir: str | None = None
) -> PriorityReport:
    """
    Deterministically computes priority category and score for every skill in target goal.
    """
    if data_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

    if gap_report is None:
        gap_report = calculate_skill_gap(profile, data_dir=data_dir)

    skills_path = os.path.join(data_dir, "skills.csv")
    df_skills = pd.read_csv(skills_path)
    
    # Map prerequisite definitions: skill -> list of prereq skill names
    prereq_map: dict[str, list[str]] = {}
    for _, row in df_skills.iterrows():
        s_name = row["skill"].strip()
        raw_prereqs = str(row["prerequisites"]).strip()
        if raw_prereqs and raw_prereqs.lower() != "none":
            prereq_map[s_name.lower()] = [p.strip() for p in raw_prereqs.split(";")]
        else:
            prereq_map[s_name.lower()] = []

    # Map user's current skill levels
    user_levels = {k.lower(): v.lower() for k, v in profile.skills.items()}

    # Combine all items from gap_report
    all_gap_items: list[SkillGapItem] = (
        gap_report.existing_skills + 
        gap_report.needs_improvement_skills + 
        gap_report.missing_skills
    )

    # Gather user context signals
    weak_areas = [w.strip().lower() for w in (profile.weakest_areas or [])]
    prioritize_topics = [t.strip().lower() for t in (profile.topics_prioritize or profile.topics_to_prioritize or [])]
    postpone_topics = [t.strip().lower() for t in (profile.topics_postpone or profile.topics_to_postpone or [])]

    now_items = []
    next_items = []
    later_items = []
    skip_items = []

    for item in all_gap_items:
        skill_lower = item.skill.lower()
        prereqs = prereq_map.get(skill_lower, [])
        reasons = []

        # Determine unsatisfied prerequisites
        unsatisfied = []
        for p in prereqs:
            p_level = user_levels.get(p.lower(), "none")
            p_score = LEVEL_SCORES.get(p_level, 0)
            if p_score < 1:
                unsatisfied.append(p)

        # 1. Existing Skills -> SKIP
        if item.status == "Existing":
            reasons.append(f"✓ Current level ({item.user_level.capitalize()}) meets required standard for {item.skill}.")
            breakdown_skip = PriorityScoreBreakdown(
                base_score=0.0,
                goal_contribution=float(item.importance),
                gap_contribution=0.0,
                prerequisite_contribution=1.0,
                urgency_contribution=0.0,
                weak_area_adjustment=0.0,
                user_priority_adjustment=0.0,
                postpone_adjustment=0.0,
                final_score=0.0
            )
            p_item = PrioritizedSkillItem(
                skill=item.skill,
                priority_category="SKIP",
                priority_score=0.0,
                importance=item.importance,
                gap_score=0,
                user_level=item.user_level,
                required_level=item.required_level,
                confidence=item.confidence,
                prerequisites=prereqs,
                unsatisfied_prerequisites=unsatisfied,
                score_breakdown=breakdown_skip,
                structured_reasons=reasons,
                reasoning=f"You already possess {item.user_level} proficiency in {item.skill}, which meets the required goal standard."
            )
            skip_items.append(p_item)
            continue

        # 2. Compute Prerequisite Factor
        if len(unsatisfied) == 0:
            prereq_factor = 1.0
            reasons.append("✓ Prerequisites satisfied.")
        elif len(unsatisfied) == 1:
            prereq_factor = 0.5
            reasons.append(f"⚠️ Depends on prerequisite: {', '.join(unsatisfied)}.")
        else:
            prereq_factor = 0.2
            reasons.append(f"⚠️ Depends on multiple prerequisites: {', '.join(unsatisfied)}.")

        # Goal relevance & gap score contribution
        reasons.append(f"✓ High relevance to {profile.goal} (Importance: {item.importance}/10).")
        reasons.append(f"✓ Current gap: {item.gap_score} level step(s).")

        base_raw = float(item.importance * item.gap_score)
        raw_score = base_raw * prereq_factor

        # Signal A: Weak Areas Adjustment
        is_weak_area = any(w in skill_lower or skill_lower in w for w in weak_areas)
        weak_adj = 0.0
        if is_weak_area:
            weak_adj = WEAK_AREA_BOOST
            raw_score += weak_adj
            reasons.append("✓ Identified by user as a weak area needing attention.")

        # Signal B: Topics to Prioritize
        is_user_prioritized = any(p in skill_lower or skill_lower in p for p in prioritize_topics)
        prio_adj = 0.0
        if is_user_prioritized:
            prio_adj = USER_PRIORITY_BOOST
            raw_score += prio_adj
            reasons.append("✓ Explicitly prioritized by user.")

        # Signal C: Topics to Postpone (Guarding Critical Prerequisites)
        is_user_postponed = any(p in skill_lower or skill_lower in p for p in postpone_topics)
        is_critical_prereq = (prereq_factor == 1.0 and item.importance >= 8)
        postpone_adj = 0.0

        if is_user_postponed:
            if is_critical_prereq:
                reasons.append(
                    f"⚠️ {item.skill} is a foundational requirement for {profile.goal}, "
                    f"so it cannot be safely postponed from the early roadmap."
                )
            else:
                postpone_adj = -POSTPONE_PENALTY
                raw_score += postpone_adj
                reasons.append("ℹ️ Postponed per user request (non-critical elective).")

        urgency_adj = 0.0
        if profile.deadline_weeks <= 8:
            reasons.append("⏳ Accelerated timeline (<=8 weeks).")

        priority_score = round(raw_score, 2)

        score_breakdown = PriorityScoreBreakdown(
            base_score=base_raw,
            goal_contribution=float(item.importance),
            gap_contribution=float(item.gap_score),
            prerequisite_contribution=float(prereq_factor),
            urgency_contribution=urgency_adj,
            weak_area_adjustment=weak_adj,
            user_priority_adjustment=prio_adj,
            postpone_adjustment=postpone_adj,
            final_score=priority_score
        )

        # Categorization logic
        if len(unsatisfied) == 0 and not (is_user_postponed and not is_critical_prereq):
            category = "NOW"
            reason_text = (
                f"{item.skill} is a high-priority foundation (Importance: {item.importance}/10, Gap: {item.gap_score}) "
                f"with all prerequisites satisfied."
            )
        elif item.status == "Needs Improvement" or len(unsatisfied) == 1:
            category = "NEXT"
            reason_text = (
                f"{item.skill} is important for your goal, but relies on completing/strengthening prerequisite ({', '.join(unsatisfied)}) first."
            )
        else:
            category = "LATER"
            reason_text = (
                f"{item.skill} can wait because it depends on multiple prerequisites ({', '.join(unsatisfied)}) that are currently missing."
            )

        if is_user_postponed and not is_critical_prereq:
            category = "LATER"
            reason_text = f"{item.skill} has been shifted to LATER per user request."

        p_item = PrioritizedSkillItem(
            skill=item.skill,
            priority_category=category,
            priority_score=priority_score,
            importance=item.importance,
            gap_score=item.gap_score,
            user_level=item.user_level,
            required_level=item.required_level,
            confidence=item.confidence,
            prerequisites=prereqs,
            unsatisfied_prerequisites=unsatisfied,
            score_breakdown=score_breakdown,
            structured_reasons=reasons,
            reasoning=reason_text
        )

        if category == "NOW":
            now_items.append(p_item)
        elif category == "NEXT":
            next_items.append(p_item)
        else:
            later_items.append(p_item)

    # Sort each category by priority score descending
    now_items.sort(key=lambda x: x.priority_score, reverse=True)
    next_items.sort(key=lambda x: x.priority_score, reverse=True)
    later_items.sort(key=lambda x: x.priority_score, reverse=True)
    skip_items.sort(key=lambda x: x.importance, reverse=True)

    return PriorityReport(
        goal=gap_report.goal,
        now=now_items,
        next_skills=next_items,
        later=later_items,
        skip=skip_items
    )
