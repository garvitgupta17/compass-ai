# 🧭 Compass AI - B.Tech Project & Internship Presentation Script

## 🎙️ Project Presentation Walkthrough

### Slide 1: Introduction & SDG 4 Impact
- **Greeting**: "Good morning everyone. I am presenting **Compass AI**, a personalized learning path and skill-gap optimization platform created for my 1M1B Virtual Internship *AI for Sustainability*."
- **Tagline**: *"Too much information. Too many paths. One clear direction."*
- **UN SDG 4 Alignment**: "Our project directly aligns with UN Sustainable Development Goal 4 (Quality Education) by eliminating choice overload for students, enabling free-resource filtering, and regional language support (English & Hindi)."

---

### Slide 2: The Problem Statement
- "Students face conflicting recommendations (e.g. should I learn LeetCode, Rust, Docker, or PySpark?)."
- "GenAI tools like ChatGPT often hallucinate non-existent courses or recommend unrealistic study timelines that exceed a student's available weekly hours."

---

### Slide 3: Architecture & System Design
- "Compass AI uses a **Hybrid Architecture** separating deterministic business logic from probabilistic AI:"
  1. **Structured Extraction**: Converts natural language prompts into validated Pydantic `UserProfile` instances via Gemini API with offline fallback.
  2. **Deterministic Skill Gap & Priority Engine**: Computes exact gap scores and transparent priority matrices (`NOW`, `NEXT`, `LATER`, `SKIP`).
  3. **Capacity-Constrained Roadmap Engine**: Schedules study blocks into realistic weekly schedules matching the user's weekly study budget (e.g. 10 hours/week over 12 weeks).
  4. **FAISS Vector Store RAG Retrieval**: Uses 384-dimensional inner-product embeddings to search curated resources.
  5. **Multi-Factor Ranking Engine**: Filters out paid resources for free-budget users and non-preferred languages.
  6. **Grounded AI Mentorship Explanations**: Answers *Why this resource?*, *Why now?*, and *How it fits your budget*.

---

### Slide 4: Live Demo Highlights
1. **Natural Language Input**: Show how a student types *"I know basic SQL and intermediate Python. I want a Data Engineering internship in 3 months with 10 hours/week free English resources."*
2. **Skill Gap Cards**: Highlight existing skills (`Python`), skills needing improvement (`SQL`), and missing skills (`ETL`, `Data Modeling`, `Spark`).
3. **Weekly Roadmap**: Demonstrate sequential week-by-week study milestones.
4. **"Should I Learn X?" Evaluator**: Type `Docker` or `Rust` to show instant deterministic opportunity cost analysis.

---

### Slide 5: Key Technical Accomplishments & Conclusion
- 51 automated tests across 18 test modules covering core decision engines, RAG retrieval, LLM fallback behavior, agent orchestration, datasets, and end-to-end workflows.
- Grounded resource recommendations strictly selected from curated, verified resource dataset indexing.
- Fully operational Streamlit web interface (`app.py`).
