"""
Compass AI - Compass Agent (Agentic Orchestrator)
Autonomous tool-using agent that coordinates tool calls and formats decision explanations.
Uses Google Gemini API (gemini-3.6-flash) when GEMINI_API_KEY is configured,
or falls back to deterministic context assembly.
"""

import os
from typing import Any

from pydantic import BaseModel, Field

from core.profile import UserProfile
from core.tools import (
    tool_evaluate_skill_priority,
    tool_get_roadmap_context,
    tool_get_skill_gap,
    tool_search_learning_resources,
)
from llm.prompts import ASK_COMPASS_GEMINI_PROMPT, GEMINI_SYSTEM_PROMPT


class AgentExecutionLog(BaseModel):
    """
    Log of tool calls and execution trace for the Compass Agent.
    """
    user_query: str
    tools_invoked: list[str] = Field(default_factory=list)
    tool_outputs: dict[str, Any] = Field(default_factory=dict)
    final_verdict: str = ""
    priority_tier: str = ""
    answer_text: str = ""
    provider_source: str = "⚙️ Compass Agent + Deterministic Engine"


class CompassAgent:
    """
    Lightweight Agentic Orchestrator for Compass AI.
    Executes relevant tool calls deterministically and invokes Google Gemini API for synthesis.
    """

    def __init__(self, profile: UserProfile, retriever: Any = None):
        self.profile = profile
        self.retriever = retriever

    def run(self, user_query: str) -> AgentExecutionLog:
        """
        Executes agent tool-use workflow:
        1. Analyzes query to determine target skill.
        2. Invokes Tool 1: get_skill_gap
        3. Invokes Tool 2: evaluate_skill_priority
        4. Invokes Tool 3: search_learning_resources
        5. Invokes Tool 4: get_roadmap_context
        6. Synthesizes context with Google Gemini API (if key present) or template fallback.
        """
        exec_log = AgentExecutionLog(user_query=user_query)

        # 1. Tool 2: Evaluate Skill Priority & Verdict (Authoritative)
        prio_data = tool_evaluate_skill_priority(self.profile, user_query)
        exec_log.tools_invoked.append("evaluate_skill_priority")
        exec_log.tool_outputs["evaluate_skill_priority"] = prio_data

        target_skill = prio_data["query_skill"]
        exec_log.final_verdict = prio_data["verdict"]
        exec_log.priority_tier = prio_data["priority_tier"]

        # 2. Tool 1: Get Skill Gap
        gap_data = tool_get_skill_gap(self.profile, skill_name=target_skill)
        exec_log.tools_invoked.append("get_skill_gap")
        exec_log.tool_outputs["get_skill_gap"] = gap_data

        # 3. Tool 4: Get Roadmap Context
        roadmap_data = tool_get_roadmap_context(self.profile, skill_name=target_skill)
        exec_log.tools_invoked.append("get_roadmap_context")
        exec_log.tool_outputs["get_roadmap_context"] = roadmap_data

        # 4. Tool 3: Search Learning Resources
        resources_data = tool_search_learning_resources(
            self.profile,
            skill_name=target_skill,
            retriever=self.retriever,
            top_k=2
        )
        exec_log.tools_invoked.append("search_learning_resources")
        exec_log.tool_outputs["search_learning_resources"] = resources_data

        # 5. Synthesize Answer via Google Gemini API (gemini-3.6-flash) or Fallback
        answer, provider = self._synthesize_explanation(user_query, prio_data, gap_data, roadmap_data, resources_data)
        exec_log.answer_text = answer
        exec_log.provider_source = provider

        return exec_log

    def _synthesize_explanation(
        self,
        user_query: str,
        prio_data: dict[str, Any],
        gap_data: dict[str, Any],
        roadmap_data: dict[str, Any],
        resources_data: list[dict[str, Any]]
    ) -> tuple[str, str]:
        """
        Synthesizes final natural-language response using Google Gemini API if key is present,
        or structured template fallback if key is missing/unconfigured.
        """
        gemini_key = os.getenv("GEMINI_API_KEY")

        res_str = "None available"
        if resources_data:
            res_str = "\n".join(
                f"- {r['title']} by {r['provider']} ({r['format']}, {r['cost']})"
                for r in resources_data
            )

        if gemini_key and not gemini_key.startswith("your_"):
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)

                prompt = ASK_COMPASS_GEMINI_PROMPT.format(
                    system_prompt=GEMINI_SYSTEM_PROMPT,
                    goal=self.profile.goal,
                    deadline_weeks=self.profile.deadline_weeks,
                    hours_per_week=self.profile.hours_per_week,
                    skills=", ".join(f"{k}:{v}" for k, v in self.profile.skills.items()),
                    query_skill=prio_data["query_skill"],
                    verdict=prio_data["verdict"],
                    priority_tier=prio_data["priority_tier"],
                    relevance_score=prio_data["relevance_score"],
                    recommendation_timing=prio_data["recommendation_timing"],
                    tradeoff_analysis=prio_data["tradeoff_analysis"],
                    resource_context=res_str,
                    user_question=user_query
                )

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
                if response.text:
                    return response.text.strip(), "⚡ Gemini + Compass Agent"
            except Exception as e:  # noqa: BLE001
                print(f"[Agent Warning] Gemini synthesis failed: {e}. Using deterministic synthesis.")

        # Fallback Synthesis
        fallback_text = (
            f"**Agent Decision:** `{prio_data['verdict']}` (Priority Tier: `{prio_data['priority_tier']}`).\n"
            f"**Opportunity Cost Analysis:** {prio_data['tradeoff_analysis']}\n"
            f"**Timing Guidance:** {prio_data['recommendation_timing']}."
        )
        return fallback_text, "⚙️ Compass Agent + Deterministic Engine"
