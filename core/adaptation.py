"""
Compass AI - Progress Tracking & Dynamic Roadmap Adaptation Engine
Adapts weekly study roadmaps when learning progress deviates or capacity constraints change.
"""
from pydantic import BaseModel, Field

from core.profile import UserProfile
from core.roadmap import RoadmapReport, generate_roadmap


class AdaptationReport(BaseModel):
    """
    Report detailing dynamic roadmap adaptation results.
    """
    status: str = Field(..., description="'ON TRACK', 'BEHIND SCHEDULE - ADAPTED', or 'AHEAD OF SCHEDULE'")
    completed_skills: list[str] = Field(default_factory=list)
    delay_weeks: int = 0
    adaptation_summary: str = Field(..., description="Clear explanation of how roadmap was adjusted")
    updated_profile: UserProfile
    updated_roadmap: RoadmapReport


def adapt_roadmap_progress(
    profile: UserProfile,
    completed_skills: list[str],
    current_week: int,
    new_hours_per_week: int | None = None,
    data_dir: str | None = None
) -> AdaptationReport:
    """
    Dynamically recalculates user skill profile and regenerates an adapted weekly roadmap.
    """
    # 1. Update user skills based on completed items (mark as 'intermediate' or 'advanced')
    updated_skills = dict(profile.skills)
    for skill_name in completed_skills:
        updated_skills[skill_name] = "intermediate"

    # 2. Update weekly capacity if modified
    updated_hours = new_hours_per_week if new_hours_per_week is not None else profile.hours_per_week

    # 3. Calculate remaining deadline weeks
    remaining_weeks = max(1, profile.deadline_weeks - current_week + 1)

    updated_profile = UserProfile(
        education=profile.education,
        experience=profile.experience,
        goal=profile.goal,
        skills=updated_skills,
        deadline_weeks=remaining_weeks,
        hours_per_week=updated_hours,
        budget=profile.budget,
        language=profile.language,
        learning_preference=profile.learning_preference,
        constraints=profile.constraints
    )

    # 4. Generate new adapted roadmap
    new_roadmap = generate_roadmap(updated_profile, data_dir=data_dir)

    # Determine status & summary
    if new_roadmap.total_weeks_allocated <= remaining_weeks and len(new_roadmap.overflow_items) == 0:
        status = "ON TRACK"
        summary = (
            f"Great job! You have completed {len(completed_skills)} skills ({', '.join(completed_skills)}). "
            f"Your remaining roadmap fits comfortably within your {remaining_weeks}-week deadline."
        )
    elif len(new_roadmap.overflow_items) > 0:
        status = "BEHIND SCHEDULE - ADAPTED"
        overflow_names = [i.skill for i in new_roadmap.overflow_items]
        summary = (
            f"Due to timeline constraints, {len(new_roadmap.overflow_items)} lower-priority skills "
            f"({', '.join(overflow_names)}) have been moved to overflow to ensure you master core foundations "
            f"within your {remaining_weeks}-week deadline."
        )
    else:
        status = "AHEAD OF SCHEDULE"
        summary = (
            f"You are ahead of schedule! Completed: {', '.join(completed_skills)}. "
            f"Next priority skills have been moved forward into your upcoming weeks."
        )

    return AdaptationReport(
        status=status,
        completed_skills=completed_skills,
        delay_weeks=max(0, current_week - 1),
        adaptation_summary=summary,
        updated_profile=updated_profile,
        updated_roadmap=new_roadmap
    )
