"""Sentence-transformers wrapper. Loaded lazily so the server boots fast."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


def embed_texts(texts: list[str]) -> np.ndarray:
    """L2-normalized embeddings, shape (n, dim). Cosine-similarity-ready."""
    if not texts:
        return np.zeros((0, 1024), dtype=np.float32)
    vecs = _model().encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=16,
    )
    return vecs.astype(np.float32)


def embed_query(text: str) -> np.ndarray:
    """BGE recommends a query prefix for retrieval. Slight quality bump."""
    prefixed = f"Represent this sentence for searching relevant passages: {text}"
    return embed_texts([prefixed])[0]
