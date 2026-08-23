"""
Unit & Integration Tests for Compass Agent and Agentic Tools
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from core.agent import CompassAgent
from core.profile import UserProfile
from core.tools import (
    tool_evaluate_skill_priority,
    tool_get_roadmap_context,
    tool_get_skill_gap,
    tool_search_learning_resources,
)


@pytest.fixture
def dummy_profile():
    return UserProfile(
        name="Agent Tester",
        goal="Data Engineer",
        deadline_weeks=12,
        hours_per_week=10,
        skills={"Python": "intermediate", "SQL": "beginner"},
        budget="free",
        language=["English"]
    )


def test_agent_initialization(dummy_profile):
    """Test 1 & 2: Agent initializes cleanly and tool wrappers function."""
    agent = CompassAgent(profile=dummy_profile)
    assert agent.profile.goal == "Data Engineer"


def test_tool_get_skill_gap(dummy_profile):
    """Test 3: Skill gap tool calls existing engine correctly."""
    gap_all = tool_get_skill_gap(dummy_profile)
    assert "missing_skills" in gap_all

    gap_single = tool_get_skill_gap(dummy_profile, skill_name="ETL")
    assert gap_single["skill"].lower() == "etl"
    assert "gap_score" in gap_single


def test_tool_evaluate_skill_priority(dummy_profile):
    """Test 4: Priority tool calls existing evaluator logic."""
    prio_res = tool_evaluate_skill_priority(dummy_profile, "Kafka")
    assert prio_res["query_skill"] == "Kafka"
    assert prio_res["priority_tier"] == "LATER"
    assert prio_res["relevance_score"] == 6


def test_tool_search_learning_resources(dummy_profile):
    """Test 5: Resource search tool calls FAISS/RAG system."""
    res_list = tool_search_learning_resources(dummy_profile, skill_name="SQL", top_k=2)
    assert isinstance(res_list, list)
    assert len(res_list) > 0
    assert "title" in res_list[0]


def test_tool_get_roadmap_context(dummy_profile):
    """Test 6: Roadmap tool calls existing roadmap engine."""
    rd_all = tool_get_roadmap_context(dummy_profile)
    assert "total_weeks_allocated" in rd_all

    rd_single = tool_get_roadmap_context(dummy_profile, skill_name="SQL")
    assert rd_single["skill"].lower() == "sql"
    assert "estimated_hours" in rd_single


def test_agent_run_mocked_gemini(dummy_profile):
    """Test 7: Agent answers question with mocked Google Gemini synthesis."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Gemini Agent Response: SQL is high priority."
    mock_client.models.generate_content.return_value = mock_response

    agent = CompassAgent(profile=dummy_profile)
    with patch.dict(os.environ, {"GEMINI_API_KEY": "mock_gemini_key_123"}), \
         patch("google.genai.Client", return_value=mock_client):
        log = agent.run("Should I learn SQL now?")
        assert len(log.tools_invoked) == 4
        assert log.final_verdict != ""
        assert "Gemini" in log.provider_source
        assert "Gemini Agent Response" in log.answer_text


def test_agent_run_gemini_unavailable_fallback(dummy_profile):
    """Test 8: Agent seamlessly falls back when Gemini API key is missing."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
        agent = CompassAgent(profile=dummy_profile)
        log = agent.run("Should I learn Kafka now?")
        assert len(log.tools_invoked) == 4
        assert "Deterministic Engine" in log.provider_source
        assert log.priority_tier == "LATER"
        assert "Agent Decision:" in log.answer_text


def test_deterministic_priority_cannot_be_overridden(dummy_profile):
    """Test 9: Agent cannot alter underlying deterministic priority score or verdict."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
        agent = CompassAgent(profile=dummy_profile)
        log = agent.run("Can I skip SQL?")
        assert log.final_verdict == "NO - DO NOT SKIP"
        assert log.priority_tier in ["NOW", "NEXT"]
