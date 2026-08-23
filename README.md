# 🧭 Compass AI

> **Tagline:** *"Too much information. Too many paths. One clear direction."*  
> **Core Philosophy:** *"The user chooses the destination. Compass AI helps find the path."*  
> **Mission:** Developed for the **1M1B Virtual Internship "AI for Sustainability"** aligning with **UN SDG 4: Quality Education**.

---

## 🌟 Overview

**Compass AI** is an intelligent, personalized learning path and skill-gap optimization platform built to eliminate choice overload for students and self-taught developers.

By combining deterministic business logic with Retrieval-Augmented Generation (RAG) and LLM-powered profile extraction, Compass AI converts unstructured background text into:
1. **Validated User Profiles** (Pydantic v2 schemas).
2. **Skill Gap Analysis** (Quantified proficiency levels & status classification).
3. **Transparent Priority Matrices** (`NOW`, `NEXT`, `LATER`, `SKIP`).
4. **Capacity-Constrained Weekly Study Roadmaps** (Sequenced milestones & weekly hour budgets).
5. **Grounded Resource Recommendations** (FAISS vector retrieval & multi-factor constraint ranking for free/paid and English/Hindi resources).
6. **"Should I Learn X?" Skill Query Evaluations** (Deterministic opportunity cost analysis).
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

## 🛠️ Project Structure

```
CompassAI Project/
├── app.py                   # Streamlit Web Interface Application
├── requirements.txt         # Core dependencies
├── README.md                # Project documentation overview
├── core/
│   ├── profile.py           # Pydantic v2 UserProfile schema & validation
│   ├── skill_gap.py         # Skill Gap Engine
│   ├── priority.py          # Priority Engine Matrix
│   ├── roadmap.py           # Weekly Study Roadmap Engine
│   ├── evaluator.py         # "Should I Learn X?" Skill Query Evaluator
│   └── adaptation.py        # Progress Tracking & Dynamic Roadmap Adaptation
├── llm/
│   ├── schemas.py           # LLM extraction schemas
│   ├── prompts.py           # System prompts
│   ├── client.py            # Extraction client (Gemini/OpenAI/Heuristic)
│   └── explain.py           # Recommendation Explanation Generator
├── rag/
│   ├── ingest.py            # Resource Dataset Preprocessing & Ingestion
│   ├── embeddings.py        # Embedding Generator (Gemini/OpenAI/Hash fallback)
│   ├── retriever.py         # FAISS Vector Store Index
│   └── ranking.py           # Hard Constraint Filtering & Multi-Factor Ranking
├── data/
│   ├── goals.csv            # Career goal definitions
│   ├── skills.csv           # Skill definitions & prerequisites
│   ├── goal_skills.csv      # Importance weights (1-10)
│   ├── resources.csv        # Curated learning resources database
│   └── milestones.csv       # Skill milestones & estimated study hours
├── docs/
│   ├── architecture.md      # Detailed technical architecture
│   ├── datasets.md          # Dataset schemas & data governance
│   └── sdg_impact.md        # UN SDG 4 Quality Education alignment
└── tests/
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
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional for Offline Testing)
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Edit `.env` to add your optional API keys:
```env
GEMINI_API_KEY="your-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
```
*(Note: If no API keys are provided, Compass AI uses its built-in offline fallbacks where supported, including a deterministic hash-based embedding vectorizer and heuristic profile extraction.).*

---

## 🧪 Running Automated Tests

Run the complete End-to-End Integration test suite:
```bash
pytest -q
```

Run individual unit test modules:
```bash
python tests/test_dataset.py
python tests/test_profile.py
python tests/test_llm.py
python tests/test_skill_gap.py
python tests/test_priority.py
python tests/test_roadmap.py
python tests/test_retriever.py
python tests/test_ranking.py
python tests/test_explain.py
python tests/test_evaluator.py
python tests/test_adaptation.py
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
