# Responsible AI Framework - Compass AI

## 1. Core Principles
- **Fairness:** Career guidance is tailored strictly based on objective user parameters (skills, budget, time, deadline).
- **Transparency & Explainability:** All priority scoring and resource filtering algorithms are open and explainable. Google Gemini API (`gemini-3.6-flash`) provides natural language context grounded strictly by deterministic calculations.
- **Safety & Non-Overriding AI:** Generative LLMs (Gemini) are restricted to explanation and conversational support. They cannot independently alter skill gap scores, priority matrices, prerequisite protections, or capacity allocations.
- **Ethics:** Compass AI does not promise employment or guaranteed salaries.
- **Privacy:** Minimal data collection; API credentials are kept securely in local `.env` configuration.
- **Grounded Resource Recommendations:** Resource titles, providers, and URLs are selected exclusively from the curated resource dataset (`data/resources.csv`), while Gemini is restricted to generating explanations from deterministic context.

## 2. Development Assistant vs. Runtime LLM
- **IBM BOB**: Incorporated during the **development stage** for agent architecture ideation, tool design, prompt engineering, and test design (see `docs/ibm_bob_usage.md`).
- **Google Gemini API (`gemini-3.6-flash`)**: Serves as the **runtime LLM** for generating natural-language explanations and decision support responses.

## 3. Sustainable Learning Alignment (UN SDG 4)
Compass AI promotes sustainable learning by:
- Reducing redundant learning effort and duplicate course recommendations.
- Prioritizing core prerequisites before advanced topics.
- Fitting learning plans strictly to real-world available weekly study hours.
- Providing targeted rather than generic resource recommendations.

## 4. Standard Disclaimer
> "Compass AI provides guidance based on the current user profile and curated knowledge base. It does not guarantee employment or any specific outcome."
