"""
Compass AI - User Profile Schema (Pydantic v2)
Collects and validates structured user profile parameters across multi-step intake.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

VALID_SKILL_LEVELS = {"none", "beginner", "intermediate", "advanced"}
VALID_BUDGETS = {
    "free", "paid", "any", "limited", 
    "free only", "limited budget", "paid resources allowed"
}
VALID_LEARNING_PREFERENCES = {
    "video", "course", "book", "article", "interactive", 
    "reading", "practice", "projects", "mixed", "any", "mixed / any"
}


class UserProfile(BaseModel):
    """
    Expanded User Profile schema covering multi-step intake sections while maintaining 
    full backward compatibility with existing engines and test suites.
    """
    # SECTION A: ABOUT YOU
    name: str | None = Field(default="Student", description="User name or nickname")
    education: str = Field(default="B.Tech Student", description="Educational background")
    education_level: str | None = Field(default=None, description="Education level alias")
    degree_branch: str | None = Field(default="AI & DS", description="Degree or branch")
    degree_or_branch: str | None = Field(default=None, description="Degree or branch alias")
    graduation_year: int | None = Field(default=2025, description="Graduation year")
    current_status: str | None = Field(default="Student", description="Student, Graduate, or Working Professional")
    experience: str = Field(default="Student", description="Experience summary")

    # SECTION B: DESTINATION
    goal: str = Field(..., description="Target career goal or primary role (REQUIRED)")
    primary_goal: str | None = Field(default=None, description="Primary destination description")
    goal_type: str | None = Field(default="Internship", description="Internship, Full-time Job, Certification, Project, Skill Development")
    target_role: str | None = Field(default=None, description="Specific target role title")
    target_industry: str | None = Field(default=None, description="Target industry sector")
    target_companies: list[str] | None = Field(default_factory=list, description="Target companies")
    deadline_weeks: int = Field(default=12, ge=1, le=104, description="Target timeline deadline in weeks (REQUIRED)")
    goal_importance: int | None = Field(default=8, ge=1, le=10, description="Importance rating (1-10)")
    goal_priority: str | None = Field(default="High", description="Low, Medium, or High priority")

    # SECTION C: CURRENT POSITION
    skills: dict[str, str] = Field(default_factory=dict, description="Current skills dictionary: {skill_name: proficiency}")
    experience_months: dict[str, Any] | int | None = Field(default_factory=dict, description="Experience in months per skill")
    skill_confidence: dict[str, Any] | None = Field(default_factory=dict, description="Confidence rating per skill: Low, Medium, High")
    existing_projects: list[str] | None = Field(default_factory=list, description="Completed projects")
    certifications: list[str] | None = Field(default_factory=list, description="Certifications earned")
    completed_courses: list[str] | None = Field(default_factory=list, description="Courses completed")

    # SECTION D: CONSTRAINTS
    hours_per_day: float | None = Field(default=None, ge=0.5, le=24.0, description="Available study hours per day")
    days_per_week: int | None = Field(default=None, ge=1, le=7, description="Available study days per week")
    hours_per_week: int = Field(default=10, ge=1, le=100, description="Available study time per week in hours (REQUIRED)")
    total_hours_per_week: int | None = Field(default=None, description="Alias for hours_per_week")
    budget: str = Field(default="free", description="Budget preference: 'free', 'paid', 'limited', 'any', 'Free Only', etc.")
    device: str | None = Field(default="Laptop", description="Primary learning device: Laptop, Desktop, Mobile")
    internet_quality: str | None = Field(default="Good", description="Poor, Average, Good")
    internet_reliability: str | None = Field(default="Reliable", description="Internet connection reliability alias")

    # SECTION E: LEARNING PREFERENCES
    language: list[str] = Field(default_factory=lambda: ["English"], description="Preferred learning languages")
    preferred_language: list[str] | str | None = Field(default=None, description="Alias for language")
    learning_preference: str = Field(default="any", description="Preferred resource format")
    learning_format: str | None = Field(default="any", description="Detailed format preference: Video, Reading, Practice, Projects, Mixed")
    theory_practical_pref: str | None = Field(default="Balanced", description="Theory vs practical preference: More Theory, Balanced, More Practical")
    theory_practical_preference: str | None = Field(default=None, description="Alias for theory_practical_pref")
    session_duration: str | None = Field(default="1 hour", description="Preferred study session length: 30 min, 1 hour, 2 hours, Flexible")
    preferred_session_duration: str | None = Field(default=None, description="Alias for session_duration")
    difficulty_pref: str | None = Field(default="Balanced", description="Pacing / difficulty preference")

    # SECTION F: ADDITIONAL CONTEXT
    weakest_areas: list[str] | None = Field(default_factory=list, description="Weakest areas / self-identified weak topics")
    topics_studied: list[str] | None = Field(default_factory=list, description="Topics already studied")
    topics_already_studied: list[str] | None = Field(default_factory=list, description="Alias for topics_studied")
    topics_prioritize: list[str] | None = Field(default_factory=list, description="Topics user wants to prioritize")
    topics_to_prioritize: list[str] | None = Field(default_factory=list, description="Alias for topics_prioritize")
    topics_postpone: list[str] | None = Field(default_factory=list, description="Topics user wants to postpone")
    topics_to_postpone: list[str] | None = Field(default_factory=list, description="Alias for topics_postpone")
    constraints: list[str] | None = Field(default_factory=list, description="Additional constraints")
    additional_constraints: list[str] | None = Field(default_factory=list, description="Alias for constraints")

    def model_post_init(self, context: Any) -> None:
        """Sync alias fields after initialization to ensure full cross-field compatibility."""
        if self.education_level and not self.education:
            self.education = self.education_level
        elif self.education and not self.education_level:
            self.education_level = self.education

        if self.degree_or_branch and not self.degree_branch:
            self.degree_branch = self.degree_or_branch
        elif self.degree_branch and not self.degree_or_branch:
            self.degree_or_branch = self.degree_branch

        if self.total_hours_per_week is not None and self.hours_per_week == 10:
            self.hours_per_week = self.total_hours_per_week

        if self.internet_quality and not self.internet_reliability:
            self.internet_reliability = self.internet_quality
        elif self.internet_reliability and not self.internet_quality:
            self.internet_quality = self.internet_reliability

        if self.preferred_language is not None:
            if isinstance(self.preferred_language, list):
                self.language = self.preferred_language
            elif isinstance(self.preferred_language, str):
                self.language = [self.preferred_language]

        if self.theory_practical_preference and not self.theory_practical_pref:
            self.theory_practical_pref = self.theory_practical_preference

        if self.preferred_session_duration and not self.session_duration:
            self.session_duration = self.preferred_session_duration

        if self.topics_already_studied and not self.topics_studied:
            self.topics_studied = self.topics_already_studied

        if self.topics_to_prioritize and not self.topics_prioritize:
            self.topics_prioritize = self.topics_to_prioritize

        if self.topics_to_postpone and not self.topics_postpone:
            self.topics_postpone = self.topics_to_postpone

        if self.additional_constraints and not self.constraints:
            self.constraints = self.additional_constraints

    @field_validator("skills")
    @classmethod
    def validate_skill_levels(cls, v: dict[str, str]) -> dict[str, str]:
        validated_skills = {}
        for skill_name, level in v.items():
            level_clean = str(level).strip().lower()
            if level_clean not in VALID_SKILL_LEVELS:
                raise ValueError(
                    f"Invalid level '{level}' for skill '{skill_name}'. "
                    f"Must be one of: {sorted(VALID_SKILL_LEVELS)}"
                )
            validated_skills[skill_name.strip()] = level_clean
        return validated_skills

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if "free" in v_clean:
            return "free"
        elif "paid" in v_clean:
            return "paid"
        elif "limited" in v_clean:
            return "limited"
        elif "any" in v_clean:
            return "any"
        if v_clean not in VALID_BUDGETS:
            raise ValueError(f"Invalid budget '{v}'. Must be one of: {sorted(VALID_BUDGETS)}")
        return v_clean

    @field_validator("learning_preference")
    @classmethod
    def validate_learning_preference(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in VALID_LEARNING_PREFERENCES:
            raise ValueError(
                f"Invalid learning preference '{v}'. Must be one of: {sorted(VALID_LEARNING_PREFERENCES)}"
            )
        return v_clean

    def get_skill_level(self, skill_name: str) -> str:
        return self.skills.get(skill_name, "none")
