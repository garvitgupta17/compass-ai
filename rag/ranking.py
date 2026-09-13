"""
Compass AI - Resource Filtering & Ranking Engine
Applies strict hard constraint filtering (budget, language, skill level, format)
and multi-factor hybrid scoring to rank retrieved learning resources.
"""

from pydantic import BaseModel, Field

from core.profile import UserProfile
from rag.ingest import ResourceDocument
from rag.retriever import FAISSRetriever


class RankedResource(BaseModel):
    """
    Final ranked resource recommendation with transparent fit breakdown.
    """
    resource: ResourceDocument
    final_score: float
    vector_similarity: float
    skill_match_score: float
    budget_fit_score: float
    language_fit_score: float
    format_fit_score: float = 1.0
    matched_preferences: list[str] = Field(default_factory=list, description="List of matched user preferences")
    fit_explanation: str
    why_recommended: str = Field(default="", description="Fact-based deterministic recommendation reason")


def filter_and_rank_resources(
    skill_name: str,
    required_level: str,
    profile: UserProfile,
    retriever: FAISSRetriever,
    top_k: int = 3
) -> list[RankedResource]:
    """
    Filters and ranks curated resources for a specific target skill based on user preferences.
    """
    fmt_pref = (profile.learning_format or profile.learning_preference or "any").strip().lower()
    query_text = f"Learning course for {skill_name} difficulty {required_level} {fmt_pref}"
    raw_candidates: list[tuple[ResourceDocument, float]] = retriever.search(query_text, top_k=20)

    user_budget_raw = (profile.budget or "free").strip().lower()
    user_languages = [l.strip().lower() for l in (profile.language or profile.preferred_language or ["English"])]

    # Normalize user budget category
    if "free" in user_budget_raw:
        budget_mode = "free_only"
    elif "paid" in user_budget_raw:
        budget_mode = "paid_allowed"
    else:
        budget_mode = "limited"

    # User exposure lists to prevent duplicate beginner recommendations
    user_exposure = [
        str(x).strip().lower() for x in (
            (profile.completed_courses or []) + 
            (profile.topics_studied or []) + 
            (profile.topics_already_studied or [])
        )
    ]

    ranked_results: list[RankedResource] = []
    language_mismatch_fallback = False

    for doc, sim in raw_candidates:
        doc_skill_lower = doc.skill.strip().lower()
        target_skill_lower = skill_name.strip().lower()

        # HARD CONSTRAINT 1: Skill Match
        if target_skill_lower not in doc_skill_lower and doc_skill_lower not in target_skill_lower:
            continue

        # HARD CONSTRAINT 2: Budget Constraint
        doc_cost = doc.cost.strip().lower()
        if budget_mode == "free_only" and doc_cost != "free":
            continue  # Hard drop paid resources if user budget is Free Only

        # HARD CONSTRAINT 3: Language Constraint
        doc_lang = doc.language.strip().lower()
        lang_matched = False
        if not user_languages or "any" in user_languages or "all" in user_languages or "both" in user_languages or doc_lang in user_languages:
            lang_matched = True

        if not lang_matched and not language_mismatch_fallback:
            # Check if any candidate matches preferred language
            has_preferred_lang = any(
                d.language.strip().lower() in user_languages 
                for d, _ in raw_candidates 
                if target_skill_lower in d.skill.strip().lower()
            )
            if not has_preferred_lang:
                language_mismatch_fallback = True  # Allow fallback if no resource exists in preferred language

        if not lang_matched and not language_mismatch_fallback:
            continue  # Drop non-preferred language resources when preferred language resource exists

        matched_prefs = []

        # SCORING FACTOR 1: Vector Similarity (Weight: 0.30)
        vec_score = max(0.0, sim)
        matched_prefs.append("Vector Similarity Match")

        # SCORING FACTOR 2: Skill & Level Fit (Weight: 0.25)
        if doc_skill_lower == target_skill_lower:
            skill_score = 1.0
            matched_prefs.append("Exact Skill Match")
        else:
            skill_score = 0.7
            matched_prefs.append("Related Skill Match")

        if doc.level.strip().lower() == required_level.strip().lower():
            skill_score += 0.2
            matched_prefs.append(f"Level Match ({doc.level.capitalize()})")
        skill_score = min(1.0, skill_score)

        # SCORING FACTOR 3: Budget Fit (Weight: 0.15)
        if doc_cost == "free":
            budget_score = 1.0
            matched_prefs.append("Free Resource")
        elif budget_mode == "paid_allowed":
            budget_score = 1.0
            matched_prefs.append("Budget Allowed")
        else:
            budget_score = 0.6

        # SCORING FACTOR 4: Language Fit (Weight: 0.15)
        if lang_matched:
            lang_score = 1.0
            matched_prefs.append(f"Language ({doc.language})")
        else:
            lang_score = 0.4

        # SCORING FACTOR 5: Format Fit (Weight: 0.10)
        doc_fmt = doc.format.strip().lower()
        if fmt_pref in ["any", "mixed", "mixed / any"] or doc_fmt == fmt_pref or fmt_pref in doc_fmt:
            fmt_score = 1.0
            matched_prefs.append(f"Format Match ({doc.format.capitalize()})")
        else:
            fmt_score = 0.6

        # SCORING FACTOR 6: Exposure & Redundancy Adjustment (Weight: 0.05)
        is_exposure_match = any(exp in doc.title.lower() or exp in doc_fmt for exp in user_exposure)
        if is_exposure_match and doc.level.lower() == "beginner":
            exposure_bonus = 0.2  # Penalize duplicate beginner course if user already completed topic
        else:
            exposure_bonus = 1.0

        # Hybrid Composite Formula
        final_score = round(
            (vec_score * 0.30) +
            (skill_score * 0.25) +
            (budget_score * 0.15) +
            (lang_score * 0.15) +
            (fmt_score * 0.10) +
            (exposure_bonus * 0.05),
            3
        )

        why_recs = [f"Matches {doc.skill} at {doc.level} level"]
        if "free" in doc_cost:
            why_recs.append("Free resource")
        if lang_matched:
            why_recs.append(f"{doc.language} language")
        if fmt_score == 1.0:
            why_recs.append(f"Preferred {doc.format} format")

        if not lang_matched and language_mismatch_fallback:
            fit_explanation = (
                f"No matching resource was found in your preferred language ({', '.join(user_languages)}). "
                f"Showing closest available alternative in {doc.language}: {doc.title} by {doc.provider}."
            )
        else:
            fit_explanation = (
                f"{doc.title} by {doc.provider} ({doc.format.capitalize()}, {doc.cost.capitalize()}, {doc.language}): "
                f"Matches {doc.skill} at {doc.level} level."
            )

        ranked_results.append(
            RankedResource(
                resource=doc,
                final_score=final_score,
                vector_similarity=vec_score,
                skill_match_score=skill_score,
                budget_fit_score=budget_score,
                language_fit_score=lang_score,
                format_fit_score=fmt_score,
                matched_preferences=matched_prefs,
                fit_explanation=fit_explanation,
                why_recommended=", ".join(why_recs)
            )
        )

    # Sort descending by final hybrid score
    ranked_results.sort(key=lambda x: x.final_score, reverse=True)

    return ranked_results[:top_k]
