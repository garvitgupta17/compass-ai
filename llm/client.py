"""
Compass AI - LLM Extraction Client
Parses natural language text into a validated Pydantic UserProfile object.
Supports Gemini / OpenAI APIs with a robust offline heuristic fallback.
"""
import json
import os
import re

from dotenv import load_dotenv

from core.profile import UserProfile
from llm.prompts import PROFILE_EXTRACTION_PROMPT
from llm.schemas import ExtractedProfileData

load_dotenv()

def extract_profile_from_text(user_input: str) -> tuple[UserProfile, str]:
    """
    Extracts structured UserProfile from natural language user input.
    Returns: Tuple of (UserProfile, extraction_source_description)
    """
    if not user_input or not user_input.strip():
        raise ValueError("Input text cannot be empty.")

    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # 1. Try Gemini API if key exists and is not placeholder
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        try:
            profile = _call_gemini_extraction(user_input, gemini_key)
            return profile, "Gemini API (Structured Extraction)"
        except (ValueError, RuntimeError, KeyError, AttributeError) as e:
            print(f"[Warning] Gemini API extraction failed ({e}). Falling back to heuristic parser.")

    # 2. Try OpenAI API if key exists and is not placeholder
    if openai_key and openai_key != "your_openai_api_key_here":
        try:
            profile = _call_openai_extraction(user_input, openai_key)
            return profile, "OpenAI API (Structured Extraction)"
        except (ValueError, RuntimeError, KeyError, AttributeError) as e:
            print(f"[Warning] OpenAI API extraction failed ({e}). Falling back to heuristic parser.")

    # 3. Offline Heuristic Rule-Based Fallback
    profile = _heuristic_profile_extraction(user_input)
    return profile, "Rule-based Heuristic Parser (Offline Fallback)"


def _call_gemini_extraction(user_input: str, api_key: str) -> UserProfile:
    """Calls Google Gemini API to extract structured JSON profile."""
    from google import genai
    client = genai.Client(api_key=api_key)
    
    prompt = f"{PROFILE_EXTRACTION_PROMPT}\n\nUser Input:\n{user_input}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    raw_text = response.text
    json_str = _clean_json_output(raw_text)
    data_dict = json.loads(json_str)
    extracted = ExtractedProfileData(**data_dict)
    return extracted.to_user_profile()


def _call_openai_extraction(user_input: str, api_key: str) -> UserProfile:
    """Calls OpenAI API to extract structured JSON profile."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": PROFILE_EXTRACTION_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.0
    )
    
    raw_text = response.choices[0].message.content
    json_str = _clean_json_output(raw_text)
    data_dict = json.loads(json_str)
    extracted = ExtractedProfileData(**data_dict)
    return extracted.to_user_profile()


def _heuristic_profile_extraction(user_input: str) -> UserProfile:
    """
    Deterministic rule-based parser for offline profile extraction.
    """
    text_lower = user_input.lower()

    # Goal Detection
    goal = "Data Engineer"  # default
    if "data analyst" in text_lower or "analytics" in text_lower:
        goal = "Data Analyst"
    elif "ml engineer" in text_lower or "machine learning" in text_lower or "ai engineer" in text_lower:
        goal = "ML Engineer"
    elif "data engineer" in text_lower or "data engineering" in text_lower:
        goal = "Data Engineer"

    # Education / Experience
    education = "B.Tech Student" if "student" in text_lower or "b.tech" in text_lower or "college" in text_lower else "Graduate"
    experience = "Student" if "student" in text_lower or "fresher" in text_lower else "Entry level"

    # Skill Detection
    skills = {}
    skill_keywords = {
        "Python": "python",
        "SQL": "sql",
        "Cloud Fundamentals": "cloud",
        "Spark & Big Data": "spark",
        "ETL": "etl",
        "Data Modeling": "data modeling",
        "Data Warehousing": "warehouse",
        "Machine Learning": "machine learning",
        "Statistics & Probability": "statistics"
    }

    for skill_name, keyword in skill_keywords.items():
        if keyword in text_lower:
            # Check level pre-modifiers
            idx = text_lower.find(keyword)
            snippet = text_lower[max(0, idx - 20): idx + len(keyword) + 15]
            if "intermediate" in snippet or "medium" in snippet:
                level = "intermediate"
            elif "advanced" in snippet or "expert" in snippet or "master" in snippet:
                level = "advanced"
            elif "basic" in snippet or "beginner" in snippet or "fundamental" in snippet or "knows" in snippet:
                level = "beginner"
            else:
                level = "beginner"
            skills[skill_name] = level

    # Deadline Weeks Extraction
    deadline_weeks = 12
    weeks_match = re.search(r'(\d+)\s*(?:month|months|week|weeks)', text_lower)
    if weeks_match:
        val = int(weeks_match.group(1))
        if "month" in weeks_match.group(0):
            deadline_weeks = val * 4
        else:
            deadline_weeks = val

    # Hours Per Week Extraction
    hours_per_week = 10
    hours_match = re.search(r'(\d+)\s*(?:hrs|hours|hr|hour)', text_lower)
    if hours_match:
        hours_per_week = int(hours_match.group(1))

    # Budget Extraction
    budget = "free"
    if "paid" in text_lower or "buy" in text_lower or "subscription" in text_lower:
        budget = "paid"

    # Language Extraction
    language = ["English"]
    if "hindi" in text_lower:
        language.append("Hindi")

    # Format Preference Extraction
    learning_pref = "video" if "video" in text_lower or "youtube" in text_lower else "any"

    extracted = ExtractedProfileData(
        education=education,
        experience=experience,
        goal=goal,
        skills=skills,
        deadline_weeks=deadline_weeks,
        hours_per_week=hours_per_week,
        budget=budget,
        language=language,
        learning_preference=learning_pref
    )

    return extracted.to_user_profile()


def _clean_json_output(raw_text: str) -> str:
    """Removes markdown code fences from LLM text responses."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    text = text.removesuffix("```")
    return text.strip()
