# 🧭 Compass AI

> **Tagline:** *"Too much information. Too many paths. One clear direction."*  
> **Core Philosophy:** *"The user chooses the destination. Compass AI helps find the path."*  
> **Mission:** Developed for the **1M1B Virtual Internship "AI for Sustainability"** aligning with **UN SDG 4: Quality Education**.

---

## 🌟 Overview

**Compass AI** is an intelligent, personalized learning path and skill-gap optimization platform built to eliminate choice overload for students and self-taught developers.

By combining deterministic business logic with Retrieval-Augmented Generation (RAG) and **Google Gemini API (`gemini-3.6-flash`)** generative explanations, Compass AI converts unstructured background text into:
1. **Validated User Profiles** (Pydantic v2 schemas).
2. **Skill Gap Analysis** (Quantified proficiency levels & status classification).
3. **Transparent Priority Matrices** (`NOW`, `NEXT`, `LATER`, `SKIP`).
4. **Capacity-Constrained Weekly Study Roadmaps** (Sequenced milestones & weekly hour budgets).
5. **Grounded Resource Recommendations** (FAISS vector retrieval & multi-factor constraint ranking for free/paid and English/Hindi resources).
6. **"Should I Learn X?" Skill Query Evaluations** (Grounded by Compass Agent & Gemini opportunity cost analysis).
7. **Dynamic Progress Adaptation** (Roadmap re-sequencing on skill completion).

---

## 🏗️ System Architecture

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
                                    | Gemini Generative                 |
                                    | Explanations & Compass Agent      |
                                    | Conversational Decision Support   |
                                    +-----------------------------------+
                                                      |
                                                      v
                                    +-----------------------------------+
                                    | Streamlit Web Application Dashboard|
                                    +-----------------------------------+
```

---

## 🛠️ Project Structure

```
CompassAI Project/
├── app.py                   # Streamlit Web Interface Application
├── requirements.txt         # Core dependencies (including google-genai)
├── README.md                # Project documentation overview
├── core/
│   ├── profile.py           # Pydantic v2 UserProfile schema & validation
│   ├── skill_gap.py         # Skill Gap Engine
│   ├── priority.py          # Priority Engine Matrix
│   ├── roadmap.py           # Weekly Study Roadmap Engine
│   ├── evaluator.py         # "Should I Learn X?" Skill Query Evaluator (Gemini grounded)
│   ├── tools.py             # Agentic Tool Wrappers (get_skill_gap, evaluate_priority, etc.)
│   ├── agent.py             # CompassAgent Orchestrator
│   └── adaptation.py        # Progress Tracking & Dynamic Roadmap Adaptation
├── llm/
│   ├── schemas.py           # LLM extraction schemas
│   ├── prompts.py           # System prompts for Gemini & extraction
│   ├── client.py            # Extraction client (Google Gemini / Heuristic Fallback)
│   └── explain.py           # Recommendation Explanation Generator (Google Gemini)
├── rag/
│   ├── ingest.py            # Resource Dataset Preprocessing & Ingestion
│   ├── embeddings.py        # Embedding Generator (Gemini/Hash fallback)
│   ├── retriever.py         # FAISS Vector Store Index
│   └── ranking.py           # Hard Constraint Filtering & Multi-Factor Ranking
├── data/
│   ├── goals.csv            # Career goal definitions
│   ├── skills.csv           # Skill definitions & prerequisites
│   ├── goal_skills.csv      # Importance weights (1-10)
│   ├── resources.csv        # Curated learning resources database
│   └── milestones.csv       # Skill milestones & estimated study hours
├── docs/
│   ├── architecture.md      # Detailed technical architecture (Gemini + Deterministic)
│   ├── datasets.md          # Dataset schemas & data governance
│   ├── ibm_bob_usage.md     # IBM BOB Development Stage Integration Log
│   ├── responsible_ai.md    # Responsible AI Framework & SDG 4 Alignment
│   └── sdg_impact.md        # UN SDG 4 Quality Education alignment
└── tests/
    ├── test_gemini.py       # Google Gemini API integration test suite (Mocked & Fallback)
    ├── test_agent.py        # Compass Agent & Agentic Tools unit test suite
    ├── test_dataset.py      # Dataset integrity unit tests
    ├── test_profile.py      # UserProfile schema unit tests
    ├── test_llm.py          # LLM profile extraction unit tests
    ├── test_skill_gap.py    # Skill gap engine unit tests
    ├── test_priority.py     # Priority engine unit tests
    ├── test_roadmap.py      # Roadmap engine unit tests
    ├── test_ingest.py       # Resource ingestion unit tests
    ├── test_embeddings.py   # Embedding generator unit tests
    ├── test_retriever.py    # FAISS retrieval unit tests
    ├── test_ranking.py      # Filtering and ranking unit tests
    ├── test_explain.py      # Explanation generator unit tests
    ├── test_evaluator.py    # Evaluation engine unit tests
    ├── test_adaptation.py   # Roadmap adaptation unit tests
    └── test_e2e.py          # End-to-End integration test suite
```

---

## ⚡ Quickstart & Setup

### 1. Environment Setup
```bash
# Create Python 3.10 virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Google Gemini API)
Copy `.env.example` to `.env` and set your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If `GEMINI_API_KEY` is not configured or offline, Compass AI automatically operates using its deterministic decision engines, template explanations, and offline rule-based parser).*

---

## 🧪 Running Automated Tests

Run pytest across all test modules:
```bash
pytest -q
```

---

## 🚀 Running the Streamlit Web App

Launch the application locally:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📜 License & SDG 4 Impact
Developed as an open-source educational platform for the **1M1B Virtual Internship "AI for Sustainability"**, supporting **UN SDG Goal 4: Quality Education & Lifelong Learning**.
