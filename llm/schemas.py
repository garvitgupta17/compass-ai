"""
Compass AI - LLM Extraction Schemas
Defines structured output models for LLM responses.
"""

from pydantic import BaseModel, Field

from core.profile import UserProfile


class ExtractedProfileData(BaseModel):
    """
    Raw extracted fields from LLM natural language parsing.
    """
    education: str | None = Field(default="Student", description="Extracted education details")
    experience: str | None = Field(default="Student", description="Extracted experience details")
    goal: str | None = Field(default="Data Engineer", description="Target role (Data Analyst, Data Engineer, ML Engineer)")
    skills: dict[str, str] = Field(default_factory=dict, description="Skills dict with levels")
    deadline_weeks: int | None = Field(default=12, description="Target timeline in weeks")
    hours_per_week: int | None = Field(default=10, description="Available study hours per week")
    budget: str | None = Field(default="free", description="Budget constraint")
    language: list[str] | None = Field(default_factory=lambda: ["English"], description="Preferred language(s)")
    learning_preference: str | None = Field(default="any", description="Preferred learning format")
    constraints: list[str] | None = Field(default_factory=list, description="Additional constraints")

    def to_user_profile(self) -> UserProfile:
        """Converts raw extracted data into a validated UserProfile instance."""
        return UserProfile(
            education=self.education or "Student",
            experience=self.experience or "Student",
            goal=self.goal or "Data Engineer",
            skills=self.skills or {},
            deadline_weeks=self.deadline_weeks or 12,
            hours_per_week=self.hours_per_week or 10,
            budget=self.budget or "free",
            language=self.language or ["English"],
            learning_preference=self.learning_preference or "any",
            constraints=self.constraints or []
        )
