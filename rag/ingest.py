"""
Compass AI - RAG Resource Dataset Ingestion & Preprocessing
Loads curated resources from data/resources.csv and constructs structured, searchable text documents.
"""
import os

import pandas as pd
from pydantic import BaseModel, Field


class ResourceDocument(BaseModel):
    """
    Searchable resource document matching RAG ingestion pipeline.
    """
    id: int
    title: str
    skill: str
    level: str
    language: str
    cost: str
    format: str
    duration: str
    provider: str
    url: str
    prerequisites: str = "none"
    last_verified: str = "2026-08-01"
    text_content: str = Field(..., description="Composite text representation for embedding generation")


def load_and_preprocess_resources(csv_path: str | None = None) -> list[ResourceDocument]:
    """
    Loads data/resources.csv and builds composite text representations for RAG indexing.
    """
    if csv_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "data", "resources.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Resource dataset CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    required_cols = [
        "title", "skill", "level", "language", "cost", 
        "format", "duration", "provider", "url"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in resources.csv")

    documents: list[ResourceDocument] = []

    for idx, row in df.iterrows():
        title = str(row["title"]).strip()
        skill = str(row["skill"]).strip()
        level = str(row["level"]).strip().lower()
        language = str(row["language"]).strip()
        cost = str(row["cost"]).strip().lower()
        fmt = str(row["format"]).strip().lower()
        duration = str(row["duration"]).strip()
        provider = str(row["provider"]).strip()
        url = str(row["url"]).strip()
        prereqs = str(row.get("prerequisites", "none")).strip()
        last_verified = str(row.get("last_verified", "2026-08-01")).strip()

        # Construct rich composite text representation for semantic embedding
        composite_text = (
            f"Title: {title}\n"
            f"Skill: {skill}\n"
            f"Difficulty Level: {level}\n"
            f"Language: {language}\n"
            f"Cost: {cost}\n"
            f"Format: {fmt}\n"
            f"Duration: {duration}\n"
            f"Provider: {provider}\n"
            f"Prerequisites: {prereqs}"
        )

        doc = ResourceDocument(
            id=idx,
            title=title,
            skill=skill,
            level=level,
            language=language,
            cost=cost,
            format=fmt,
            duration=duration,
            provider=provider,
            url=url,
            prerequisites=prereqs,
            last_verified=last_verified,
            text_content=composite_text
        )
        documents.append(doc)

    return documents
