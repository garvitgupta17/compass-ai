# Compass AI System Architecture & Technical Design

## 1. Executive Summary
Compass AI is a personalized learning path and skill-gap optimization platform engineered for students and early-career professionals facing choice overload. Built as part of the 1M1B Virtual Internship "AI for Sustainability", the system transforms underspecified user background descriptions into realistic, weekly study roadmaps and verified learning resource recommendations.

---

## 2. Core Architectural Design Philosophy

Compass AI adheres to a **Hybrid Architecture** separating deterministic business logic from probabilistic AI capabilities:

```
                                    +-----------------------------------+
                                    |    User Input (Text / Form)      |
                                    +-----------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    |   Phase 4: LLM Profile Extractor  |
                                    |   (Gemini / OpenAI / Heuristic)   |
                                    +-----------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    | Phase 3: Pydantic User Profile    |
                                    +-----------------------------------+
                                                      |
                                                      v
      +-----------------------------------------------------------------------------------------------+
      |                                  DETERMINISTIC ENGINES                                        |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      |  | Phase 5: Skill Gap | ---> | Phase 6: Priority  | ---> | Phase 7: Capacity Roadmap Engine|  |
      |  | Engine (Numerical) |      | Engine (Formula)   |      | (Sequential Weekly Schedule)    |  |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      +-----------------------------------------------------------------------------------------------+
                                                      |
                                                      v
      +-----------------------------------------------------------------------------------------------+
      |                                   RAG & RETRIEVAL SYSTEM                                      |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      |  | Phase 8 & 9: Vector| ---> | Phase 10: FAISS    | ---> | Phase 11: Hard Constraint Filter|  |
      |  | Embeddings (384-D) |      | Store (IndexFlatIP)|      | & Multi-Factor Ranking Engine   |  |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      +-----------------------------------------------------------------------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    | Phase 12: Grounded Explanations   |
                                    | & Phase 13: "Should I Learn X?"   |
                                    +-----------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    | Phase 14: Streamlit Web UI App    |
                                    +-----------------------------------+
```

---

## 3. Component Deep Dive

### 3.1 Profile Extractor (`llm/client.py`)
- Extracts structured profile data from natural language text.
- Uses a **3-tier fallback chain**:
  1. Google Gemini API (`gemini-2.5-flash`) structured JSON output.
  2. OpenAI API (`gpt-3.5-turbo`) JSON mode.
  3. Offline Heuristic Rule-Based Parser (regex and keyword matching).

### 3.2 Deterministic Engines (`core/`)
- **Skill Gap Engine (`core/skill_gap.py`)**: Quantifies proficiency levels (`none` = 0, `beginner` = 1, `intermediate` = 2, `advanced` = 3) and computes gap distances ($\max(0, \text{Required} - \text{User})$).
- **Priority Engine (`core/priority.py`)**: Applies transparent formula:
  $$\text{Priority Score} = \text{Goal Importance} \times \text{Gap Score} \times \text{Prerequisite Factor}$$
- **Roadmap Engine (`core/roadmap.py`)**: Schedules skills into weekly blocks respecting available study hours (`hours_per_week`) and overall target deadline (`deadline_weeks`).
- **Adaptation Engine (`core/adaptation.py`)**: Recalculates remaining weeks and re-sequences upcoming tasks when progress is ahead or behind schedule.

### 3.3 RAG Retrieval Pipeline (`rag/`)
- **FAISS Vector Store (`rag/retriever.py`)**: Uses `faiss.IndexFlatIP` over 384-dimensional unit-normalized float32 embeddings for exact cosine similarity searches.
- **Filtering & Ranking Engine (`rag/ranking.py`)**: Enforces hard constraint filters (budget: free/paid, language: English/Hindi) and applies multi-factor hybrid scoring:
  $$\text{Final Score} = 0.40 \cdot \text{Vector Sim} + 0.30 \cdot \text{Skill Match} + 0.15 \cdot \text{Budget Fit} + 0.15 \cdot \text{Language Fit}$$

---

## 4. Key Technical Decisions
1. **Pydantic v2**: Guaranteed runtime data validation and strict type safety.
2. **FAISS (`faiss-cpu==1.8.0`)**: Blazing fast in-memory vector similarity index.
3. **Zero Hallucination Guarantee**: All recommendations originate strictly from curated dataset resources (`data/resources.csv`).
