"""
Compass AI - Recommendation Explanation Generator
Generates clear, transparent natural language explanations for recommended resources
answering: Why this resource?, Why now?, and How it fits user constraints.
Supports Google Gemini API (gemini-3.6-flash) as primary provider.
"""
import os

from core.profile import UserProfile
from core.skill_gap import SkillGapItem
from rag.ingest import ResourceDocument

EXPLANATION_PROMPT = """You are Compass AI, a technical mentor guiding a student toward their career goal.
Explain why the following resource was recommended to the student in 3-4 concise, encouraging sentences.

Context:
- Target Goal: {goal} ({goal_type})
- Target Skill: {skill} (Priority: {priority_category}, Scheduled: {roadmap_weeks})
- Current User Skill Level: {user_level} -> Required Level: {required_level}
- User Constraints: Budget: {budget}, Preferred Language: {language}, Format Preference: {learning_format}
- Recommended Resource: "{title}" by {provider} (Format: {format}, Cost: {cost}, Language: {res_lang})
- Direct Link: {url}

Structure the explanation clearly answering:
1. Why this specific resource is recommended for closing the skill gap.
2. Why it is scheduled right now in their roadmap.
3. How it perfectly aligns with their budget, format, and language preferences.
"""


def generate_recommendation_explanation(
    skill_name: str,
    priority_category: str,
    roadmap_weeks: str,
    resource: ResourceDocument,
    profile: UserProfile,
    gap_item: SkillGapItem | None = None
) -> tuple[str, str]:
    """
    Generates a grounded natural language explanation using Google Gemini API (gemini-3.6-flash)
    or a deterministic template fallback when offline or unconfigured.
    Returns: Tuple of (explanation_text, provider_label)
    """
    user_level = gap_item.user_level if gap_item else "beginner"
    required_level = gap_item.required_level if gap_item else "intermediate"
    lang_str = ", ".join(profile.language)
    goal_type_str = profile.goal_type or "target role"
    fmt_pref = profile.learning_format or profile.learning_preference or "any format"

    prompt = EXPLANATION_PROMPT.format(
        goal=profile.goal,
        goal_type=goal_type_str,
        skill=skill_name,
        priority_category=priority_category,
        roadmap_weeks=roadmap_weeks,
        user_level=user_level,
        required_level=required_level,
        budget=profile.budget,
        language=lang_str,
        learning_format=fmt_pref,
        title=resource.title,
        provider=resource.provider,
        format=resource.format,
        cost=resource.cost,
        res_lang=resource.language,
        url=resource.url
    )

    gemini_key = os.getenv("GEMINI_API_KEY")

    # Primary Provider: Google Gemini API (gemini-3.6-flash)
    if gemini_key and not gemini_key.startswith("your_"):
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            if response.text:
                return response.text.strip(), "⚡ Gemini (gemini-3.6-flash)"
        except Exception as e:  # noqa: BLE001
            print(f"[Explanation Warning] Gemini API failed: {e}. Using template fallback.")

    # Deterministic Template Fallback (Offline / Key Unconfigured)
    explanation = (
        f"**Why this resource?** We recommended **\"{resource.title}\"** by {resource.provider} because it directly "
        f"bridges your gap in **{skill_name}** from {user_level} to {required_level} level for your {profile.goal} {goal_type_str}.\n"
        f"**Why now?** Scheduled in **{roadmap_weeks}** under **{priority_category}** priority to establish "
        f"core prerequisites before advancing.\n"
        f"**Constraint & Format Fit:** Aligns with your **{profile.budget}** budget ({resource.cost}), "
        f"format preference ({resource.format}), and preferred language ({resource.language})."
    )
    return explanation, "Deterministic Template Fallback"
