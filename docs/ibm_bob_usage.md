# IBM BOB Incorporation & Agentic AI Development Log

## 1. Overview & Development Scope
In accordance with the **1M1B Virtual Internship "AI for Sustainability"** requirements, **IBM BOB** was incorporated during the **DEVELOPMENT & ARCHITECTURE DESIGN STAGE** of Compass AI.

> **Important Disclosure**: IBM BOB was used as an agentic ideation, prompt engineering, tool architecture assistant, and test design partner during system development. It is **not** part of runtime web application execution. Runtime LLM execution is handled by Google Gemini API (`gemini-3.6-flash`).

---

## 2. Incorporating IBM BOB Across Development Stages

### Stage 1: Agent & Tool Architecture Ideation
- **Task**: Designing a lightweight Agentic AI layer that orchestrates decision engines without overriding deterministic rules.
- **IBM BOB Role**: Assisted in defining tool boundaries (`get_skill_gap`, `evaluate_skill_priority`, `search_learning_resources`, `get_roadmap_context`) to wrap existing functions cleanly while enforcing strict decision authority rules.

### Stage 2: Prompt Refinement & System Instructions
- **Task**: Creating system prompts for Google Gemini API (`gemini-3.6-flash`) that enforce zero-hallucination policies and strict adherence to deterministic evaluation outcomes.
- **IBM BOB Role**: Iterated on `GEMINI_SYSTEM_PROMPT` and `ASK_COMPASS_GEMINI_PROMPT` to mandate grounded explanations and prevent resource or URL inventions.

### Stage 3: Test Design & Safety Guardrails
- **Task**: Designing unit test suites covering fallback paths, mocked Gemini API responses, credential safety, and non-overriding constraints.
- **IBM BOB Role**: Guided the structure of `tests/test_gemini.py` and `tests/test_agent.py` ensuring 100% test coverage without requiring active external API keys during testing.

---

## 3. Compass Agent Architecture

```
USER QUESTION
      │
      ▼
COMPASS AGENT (core/agent.py)
      │
      ├── Tool 1: get_skill_gap (core/skill_gap.py)
      ├── Tool 2: evaluate_skill_priority (core/evaluator.py)
      ├── Tool 3: search_learning_resources (rag/ranking.py via FAISS)
      └── Tool 4: get_roadmap_context (core/roadmap.py)
      │
      ▼
DETERMINISTIC CONTEXT ASSEMBLY
      │
      ▼
GOOGLE GEMINI API LAYER (gemini-3.6-flash) [or Fallback]
      │
      ▼
GROUNDED CONVERSATIONAL EXPLANATION
```

---

## 4. Key Security & Sustainability Principles
1. **Authoritative Determinism**: Deterministic engines retain absolute authority over numerical gap scores, priority matrices, prerequisite protections, and capacity limits.
2. **Offline Fallback Safety**: If Gemini API keys are absent or unconfigured, the Compass Agent operates seamlessly using deterministic context synthesis.
3. **SDG 4 Alignment**: Helps learners minimize wasted hours by recommending targeted learning resources fitting real-world time availability.
