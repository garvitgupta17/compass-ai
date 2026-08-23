"""
Compass AI - Recommendation Explanation Generator
Generates clear, transparent natural language explanations for recommended resources
answering: Why this resource?, Why now?, and How it fits user constraints.
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
) -> str:
    """
    Generates a grounded natural language explanation using Gemini / OpenAI API,
    or a deterministic template fallback when offline.
    """
    user_level = gap_item.user_level if gap_item else "beginner"
    required_level = gap_item.required_level if gap_item else "intermediate"
    lang_str = ", ".join(profile.language)
    goal_type_str = profile.goal_type or "target role"
    fmt_pref = profile.learning_format or profile.learning_preference or "any format"

    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Tier 1: Gemini API
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
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
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response.text:
                return response.text.strip()
        except (ValueError, RuntimeError, KeyError, AttributeError) as e:
            print(f"[Explanation Warning] Gemini API failed: {e}. Using template fallback.")

    # Tier 2: OpenAI API
    if openai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
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
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            if res.choices and res.choices[0].message.content:
                return res.choices[0].message.content.strip()
        except (ValueError, RuntimeError, KeyError, AttributeError) as e:
            print(f"[Explanation Warning] OpenAI API failed: {e}. Using template fallback.")

    # Tier 3: Deterministic Template Fallback (Offline)
    explanation = (
        f"**Why this resource?** We recommended **\"{resource.title}\"** by {resource.provider} because it directly "
        f"bridges your gap in **{skill_name}** from {user_level} to {required_level} level for your {profile.goal} {goal_type_str}.\n"
        f"**Why now?** Scheduled in **{roadmap_weeks}** under **{priority_category}** priority to establish "
        f"core prerequisites before advancing.\n"
        f"**Constraint & Format Fit:** Aligns with your **{profile.budget}** budget ({resource.cost}), "
        f"format preference ({resource.format}), and preferred language ({resource.language})."
    )
    return explanation
