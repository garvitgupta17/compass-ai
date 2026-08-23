"""
Compass AI - Embeddings Generator Wrapper
Multi-tiered vector embedding generator supporting Google Gemini, OpenAI,
and a deterministic offline hash vectorizer fallback.
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
    Multi-provider embedding generator with seamless offline fallback.
    """
    def __init__(self):
        self.provider = "offline"
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if self.gemini_key:
            self.provider = "gemini"
        elif self.openai_key:
            self.provider = "openai"

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

        # Tier 1: Gemini API
        if self.provider == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                vectors = []
                for t in texts:
                    res = client.models.embed_content(
                        model="text-embedding-004",
                        contents=t
                    )
                    if not res.embeddings:
                        raise ValueError("Gemini returned no embeddings")
                    emb = np.array(res.embeddings[0].values, dtype=np.float32)
                    # Project or truncate to 384 dim if needed
                    emb_384 = emb[:EMBEDDING_DIM] if len(emb) >= EMBEDDING_DIM else np.pad(emb, (0, EMBEDDING_DIM - len(emb)))
                    vectors.append(_normalize(emb_384))
                return np.vstack(vectors)
            except (ValueError, RuntimeError, KeyError, AttributeError) as e:
                print(f"[EmbeddingGenerator Warning] Gemini API embedding failed: {e}. Falling back to offline vectorizer.")

        # Tier 2: OpenAI API
        if self.provider == "openai":
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                res = client.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                vectors = []
                for item in res.data:
                    emb = np.array(item.embedding, dtype=np.float32)[:EMBEDDING_DIM]
                    vectors.append(_normalize(emb))
                return np.vstack(vectors)
            except (ValueError, RuntimeError, KeyError, AttributeError) as e:
                print(f"[EmbeddingGenerator Warning] OpenAI API embedding failed: {e}. Falling back to offline vectorizer.")

        # Tier 3: Offline Fallback Vectorizer
        vectors = [_fallback_hash_embedding(t, EMBEDDING_DIM) for t in texts]
        return np.vstack(vectors)
