# Compass AI Dataset Architecture & Data Governance

## 1. Overview
Compass AI relies on structured, curated datasets stored in `data/` to ensure deterministic execution, explainable scoring, and a **Zero-Hallucination Guarantee**.

---

## 2. Dataset Schemas

### 2.1 Goals Dataset (`data/goals.csv`)
Defines supported career roles, target job descriptions, and domain descriptions.
- `goal`: String (Unique identifier: `Data Analyst`, `Data Engineer`, `ML Engineer`)
- `description`: String (Career role summary)
- `domain`: String (Industry domain classification)

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
- `title`: String
- `skill`: String
- `level`: String
- `language`: String (`English`, `Hindi`)
- `cost`: String (`free`, `paid`)
- `format`: String (`video`, `course`, `book`, `interactive`, `documentation`)
- `duration`: String (e.g. `6h`, `15h`)
- `provider`: String (e.g. `FreeCodeCamp`, `Coursera`, `CodeWithHarry`)
- `url`: String (Direct verified web link)

### 2.5 Milestones Dataset (`data/milestones.csv`)
Defines actionable learning outcomes and default study hours for each skill.
- `skill`: String
- `milestone`: String (Actionable objective)
- `default_hours`: Integer (Estimated study effort)

---

## 3. Data Governance & Anti-Hallucination Controls
1. **Source Verification**: All resources are verified from top educational platforms (FreeCodeCamp, Udacity, Coursera, Mode Analytics, PostgreSQL Docs).
2. **Schema Enforcement**: Pydantic models automatically validate incoming datasets during application startup.
