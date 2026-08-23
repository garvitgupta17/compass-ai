"""
Compass AI - FAISS Vector Store & Retriever
Builds and queries an in-memory FAISS vector index over curated learning resources.
"""
import os

import faiss
import numpy as np

from rag.embeddings import EMBEDDING_DIM, EmbeddingGenerator
from rag.ingest import ResourceDocument, load_and_preprocess_resources


class FAISSRetriever:
    """
    FAISS vector store index for semantic resource retrieval.
    """
    def __init__(self, data_dir: str | None = None):
        self.embedding_generator = EmbeddingGenerator()
        self.dim = EMBEDDING_DIM
        self.index = faiss.IndexFlatIP(self.dim)
        self.doc_map: dict[int, ResourceDocument] = {}
        self.is_indexed = False

        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")

        self.data_dir = data_dir

    def build_index(self, csv_path: str | None = None):
        """
        Loads resources, generates embeddings, and constructs the FAISS index.
        """
        if csv_path is None:
            csv_path = os.path.join(self.data_dir, "resources.csv")

        documents = load_and_preprocess_resources(csv_path)
        if not documents:
            raise ValueError("No resource documents loaded for vector indexing.")

        texts = [doc.text_content for doc in documents]
        embeddings = self.embedding_generator.embed_text(texts)
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)

        if embeddings.ndim != 2 or embeddings.shape[1] != EMBEDDING_DIM:
            raise ValueError(f"Embeddings array must have shape (N, {EMBEDDING_DIM}), got {embeddings.shape}")

        # Reset index and build
        self.index.reset()
        self.index.add(embeddings)

        self.doc_map = {i: doc for i, doc in enumerate(documents)}
        self.is_indexed = True
        print(f"[FAISSRetriever] Successfully indexed {self.index.ntotal} resource documents.")

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> list[tuple[ResourceDocument, float]]:
        """
        Searches the FAISS vector index for top_k most relevant resource documents.
        Returns: List of (ResourceDocument, similarity_score) tuples.
        """
        if not self.is_indexed:
            self.build_index()

        if self.index.ntotal == 0:
            return []

        query_vec = self.embedding_generator.embed_text(query)
        query_vec = np.ascontiguousarray(query_vec, dtype=np.float32)

        if query_vec.ndim != 2 or query_vec.shape != (1, EMBEDDING_DIM):
            raise ValueError(f"Query vector must have shape (1, {EMBEDDING_DIM}), got {query_vec.shape}")

        scores, indices = self.index.search(query_vec, top_k)

        results: list[tuple[ResourceDocument, float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx in self.doc_map and idx != -1:
                doc = self.doc_map[idx]
                results.append((doc, float(score)))

        return results
