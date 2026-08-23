"""
Unit & Integration Tests for Google Gemini API (gemini-3.6-flash) Integration
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from core.agent import CompassAgent
from core.evaluator import evaluate_skill_query
from core.profile import UserProfile
from llm.explain import generate_recommendation_explanation
from rag.ingest import ResourceDocument


@pytest.fixture
def dummy_profile():
    return UserProfile(
        name="Test Student",
        goal="Data Engineer",
        deadline_weeks=12,
        hours_per_week=10,
        skills={"Python": "beginner"},
        budget="free",
        language=["English"]
    )


@pytest.fixture
def dummy_resource():
    return ResourceDocument(
        id=1,
        title="SQL for Beginners",
        skill="SQL",
        level="beginner",
        provider="Coursera",
        url="https://example.com/sql",
        format="video",
        cost="free",
        language="English",
        duration="10 hours",
        text_content="SQL course text"
    )


def test_gemini_missing_key_fallback(dummy_profile, dummy_resource):
    """Test 4: Test missing GEMINI_API_KEY triggers deterministic fallback."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
        explanation, provider = generate_recommendation_explanation(
            skill_name="SQL",
            priority_category="NOW",
            roadmap_weeks="Week 1-3",
            resource=dummy_resource,
            profile=dummy_profile
        )
        assert provider == "Deterministic Template Fallback"
        assert "SQL for Beginners" in explanation
        assert "Why this resource?" in explanation


def test_mocked_gemini_generation(dummy_profile, dummy_resource):
    """Test 2, 3 & 8: Successful Gemini generation using mocked Client response."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Gemini: Recommended SQL course is ideal for Data Engineering."
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "mock_gemini_key_123"}), \
         patch("google.genai.Client", return_value=mock_client):
        explanation, provider = generate_recommendation_explanation(
            skill_name="SQL",
            priority_category="NOW",
            roadmap_weeks="Week 1-3",
            resource=dummy_resource,
            profile=dummy_profile
        )
        assert "Gemini" in provider
        assert "Recommended SQL course" in explanation


def test_gemini_api_failure_fallback(dummy_profile, dummy_resource):
    """Test 5: Test Gemini API request failure gracefully triggers template fallback."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("API quota exceeded")

    with patch.dict(os.environ, {"GEMINI_API_KEY": "mock_gemini_key_123"}), \
         patch("google.genai.Client", return_value=mock_client):
        _explanation, provider = generate_recommendation_explanation(
            skill_name="SQL",
            priority_category="NOW",
            roadmap_weeks="Week 1-3",
            resource=dummy_resource,
            profile=dummy_profile
        )
        assert provider == "Deterministic Template Fallback"


def test_empty_gemini_response_fallback(dummy_profile, dummy_resource):
    """Test 6: Test empty Gemini text response triggers template fallback."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = ""
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "mock_gemini_key_123"}), \
         patch("google.genai.Client", return_value=mock_client):
        _explanation, provider = generate_recommendation_explanation(
            skill_name="SQL",
            priority_category="NOW",
            roadmap_weeks="Week 1-3",
            resource=dummy_resource,
            profile=dummy_profile
        )
        assert provider == "Deterministic Template Fallback"


def test_ask_compass_with_mocked_gemini(dummy_profile):
    """Test 9: Ask Compass works with mocked Gemini API."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Gemini Answer: Kafka is a valuable elective."
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"GEMINI_API_KEY": "mock_gemini_key_123"}), \
         patch("google.genai.Client", return_value=mock_client):
        res = evaluate_skill_query("Should I learn Kafka now?", dummy_profile)
        assert res.query_skill == "Kafka"
        assert res.verdict == "YES - VALUABLE ELECTIVE"
        assert res.priority_tier == "LATER"
        assert res.provider_source == "⚡ Gemini + Compass Agent"
        assert res.generative_explanation == "Gemini Answer: Kafka is a valuable elective."


def test_agent_with_mocked_gemini(dummy_profile):
    """Test 7 & 8: Compass Agent tool execution & non-overriding priority using Gemini."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Gemini Agent: Kafka should be learned later."
    mock_client.models.generate_content.return_value = mock_response

    agent = CompassAgent(profile=dummy_profile)
    with patch.dict(os.environ, {"GEMINI_API_KEY": "mock_gemini_key_123"}), \
         patch("google.genai.Client", return_value=mock_client):
        log = agent.run("Should I learn Kafka now?")
        assert len(log.tools_invoked) == 4
        assert log.priority_tier == "LATER"
        assert log.provider_source == "⚡ Gemini + Compass Agent"
        assert log.answer_text == "Gemini Agent: Kafka should be learned later."
