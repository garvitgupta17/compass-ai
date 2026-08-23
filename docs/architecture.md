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
                                    | Primary Generative LLM:           |
                                    | Google Gemini API                 |
                                    | (gemini-3.6-flash)                |
                                    | [Fallback: Heuristic Parser]      |
                                    +-----------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    | Pydantic User Profile             |
                                    +-----------------------------------+
                                                      |
                                                      v
      +-----------------------------------------------------------------------------------------------+
      |                                  DETERMINISTIC ENGINES                                        |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      |  | Skill Gap Engine   | ---> | Priority Engine    | ---> | Capacity Roadmap Engine         |  |
      |  | (Numerical Step)   |      | (Grounded Formula) |      | (Sequential Weekly Schedule)    |  |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      +-----------------------------------------------------------------------------------------------+
                                                      |
                                                      v
      +-----------------------------------------------------------------------------------------------+
      |                                   RAG & RETRIEVAL SYSTEM                                      |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      |  | Vector Embeddings  | ---> | FAISS Vector Store | ---> | Hard Constraint Filter &        |  |
      |  | (384-D Space)      |      | (IndexFlatIP)      |      | Multi-Factor Ranking Engine     |  |
      |  +--------------------+      +--------------------+      +---------------------------------+  |
      +-----------------------------------------------------------------------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    | Generative Explanation &          |
                                    | Compass Agent Decision Support    |
                                    | Grounded by Gemini (gemini-3.6-flash) |
                                    +-----------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    | Streamlit Web Application Dashboard|
                                    +-----------------------------------+
```

---

## 3. Component Deep Dive

### 3.1 LLM Generation & Explanation Layer (`llm/client.py`, `llm/explain.py`)
- Uses **Google Gemini API (`gemini-3.6-flash`)** as the primary generative reasoning and explanation model.
- **Fallback Chain**:
  1. Google Gemini API (`gemini-3.6-flash`)
  2. Offline Rule-Based Heuristic Parser / Template Fallback

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
1. **Google Gemini API (`gemini-3.6-flash`) Integration**: Generates grounded explanations and conversational responses via `google-genai` SDK.
2. **IBM BOB**: Incorporated during the development stage for agent ideation, prompt engineering, tool architecture, and test design (documented in `docs/ibm_bob_usage.md`).
3. **Pydantic v2**: Guaranteed runtime data validation and strict type safety.
4. **FAISS (`faiss-cpu`)**: Blazing fast in-memory vector similarity index.
5. **Zero Hallucination Guarantee**: All recommendations originate strictly from curated dataset resources (`data/resources.csv`).
