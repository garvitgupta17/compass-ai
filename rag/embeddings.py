"""
Compass AI - Embeddings Generator Wrapper
Vector embedding generator supporting Google Gemini embeddings
with a deterministic hash-based vectorizer offline fallback.

Note:
The application uses Gemini embeddings when API access is available.
A deterministic hash-based vector representation is provided as an offline/testing
fallback so that core workflows remain testable without external API access.
"""
import hashlib
import os

import numpy as np

EMBEDDING_DIM = 384

def _normalize(vec: np.ndarray) -> np.ndarray:
    """
    Normalizes vector to unit length (L2 norm) for cosine similarity.
    """
    norm = np.linalg.norm(vec, axis=-1, keepdims=True)
    norm = np.where(norm == 0, 1.0, norm)
    return (vec / norm).astype(np.float32)

def _fallback_hash_embedding(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """
    Deterministic pseudo-embedding generated via text hash features.
    Enables full offline index generation and semantic search testing without API keys.
    """
    words = text.lower().split()
    vec = np.zeros(dim, dtype=np.float32)
    
    if not words:
        return vec
        
    for w in words:
        # Create deterministic feature hash bucket
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
        bucket = h % dim
        sign = 1.0 if (h % 2 == 0) else -1.0
        vec[bucket] += sign

    return _normalize(vec)


class EmbeddingGenerator:
    """
    Gemini embedding generator with seamless offline fallback.
    """
    def __init__(self):
        self.provider = "offline"
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        if self.gemini_key and not self.gemini_key.startswith("your_"):
            self.provider = "gemini"
        else:
            self.provider = "offline"

    def embed_text(self, text: str | list[str]) -> np.ndarray:
        """
        Embeds a single string or list of strings into normalized float32 vectors.
        Returns: np.ndarray of shape (N, EMBEDDING_DIM)
        """
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        if not texts:
            return np.empty((0, EMBEDDING_DIM), dtype=np.float32)

        # Primary: Gemini API Embeddings
        if self.provider == "gemini":
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=self.gemini_key)
                res = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=texts,
                    config=types.EmbedContentConfig(
                        output_dimensionality=EMBEDDING_DIM
                    )
                )
                if not res.embeddings or not isinstance(res.embeddings, list):
                    raise ValueError("Gemini returned no valid embeddings list")

                vectors = []
                for item in res.embeddings:
                    emb = np.array(item.values, dtype=np.float32)
                    if emb.shape != (EMBEDDING_DIM,):
                        raise ValueError(f"Gemini returned invalid embedding shape {emb.shape}")
                    vectors.append(_normalize(emb))
                return np.vstack(vectors)
            except Exception as e:  # noqa: BLE001
                print(f"[EmbeddingGenerator Warning] Gemini API embedding failed: {e}. Falling back to offline vectorizer.")

        # Secondary: Deterministic Hash-Based Fallback Vectorizer
        vectors = [_fallback_hash_embedding(t, EMBEDDING_DIM) for t in texts]
        return np.vstack(vectors)
