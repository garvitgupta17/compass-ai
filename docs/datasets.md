# Compass AI Dataset Architecture & Data Governance

## 1. Overview
Compass AI relies on structured, curated datasets stored in `data/` to ensure deterministic execution, explainable scoring, and **Grounded Resource Recommendations**.

---

## 2. Dataset Schemas

### 2.1 Goals Dataset (`data/goals.csv`)
Defines supported career roles and target job descriptions.
- `goal`: String (Unique identifier: `Data Analyst`, `Data Engineer`, `ML Engineer`)
- `description`: String (Career role summary)

### 2.2 Skills Dataset (`data/skills.csv`)
Defines core technical competencies, default required target levels, and prerequisite dependencies.
- `skill`: String (Unique skill name)
- `level`: String (`beginner`, `intermediate`, `advanced`)
- `prerequisites`: String (Semicolon-separated list of required prerequisite skills or `none`)

### 2.3 Goal-Skill Mapping (`data/goal_skills.csv`)
Maps career goals to required skills along with a quantitative importance score.
- `goal`: String
- `skill`: String
- `importance`: Integer (1-10 numerical weight)

### 2.4 Resources Dataset (`data/resources.csv`)
Curated database of verified, high-quality learning resources.
- `title`: String (Resource title)
- `skill`: String (Associated technical skill)
- `level`: String (`beginner`, `intermediate`, `advanced`)
- `language`: String (`English`, `Hindi`)
- `cost`: String (`free`, `paid`)
- `format`: String (`video`, `course`, `book`, `interactive`, `article`)
- `duration`: String (e.g. `6h`, `15h`)
- `provider`: String (e.g. `FreeCodeCamp`, `Coursera`, `CodeWithHarry`)
- `url`: String (Direct verified web link)
- `prerequisites`: String (Semicolon-separated prerequisite skills or `none`)
- `last_verified`: String (Verification date, e.g. `2026-08-01`)

### 2.5 Milestones Dataset (`data/milestones.csv`)
Defines actionable learning outcomes and default study hours for each skill.
- `skill`: String
- `milestone`: String (Actionable objective)
- `default_hours`: Integer (Estimated study effort)

---

## 3. Grounded Resource Indexing & Data Governance
1. **Source Verification**: All resources are verified from top educational platforms (FreeCodeCamp, Udacity, Coursera, Mode Analytics, PostgreSQL Docs). Resource titles, providers, and URLs are selected exclusively from this curated dataset.
2. **Schema Enforcement**: Pydantic models automatically validate incoming datasets during application startup.
