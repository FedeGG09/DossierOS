import hashlib
from abc import ABC, abstractmethod

import numpy as np


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class HashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        if not text:
            return vec.tolist()
        for tok in text.lower().split():
            h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec /= norm
        return vec.tolist()


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        vec = self.model.encode([text], normalize_embeddings=True)[0]
        return vec.tolist()


def get_embedding_provider(dim: int = 384) -> EmbeddingProvider:
    try:
        return SentenceTransformerEmbeddingProvider()
    except Exception:
        return HashEmbeddingProvider(dim=dim)
