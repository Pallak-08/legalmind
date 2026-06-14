"""Cross-encoder reranker (BGE).

A cross-encoder reads the (query, passage) pair jointly and scores relevance —
much more accurate than the bi-encoder used for first-stage retrieval, but too
slow to run on every chunk. So: retrieve broadly with embeddings+BM25, then
rerank the top ~30 with this.
"""
from __future__ import annotations

from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.config import get_settings
from app.services.vectorstore import SearchResult


@lru_cache(maxsize=1)
def _model() -> CrossEncoder:
    return CrossEncoder(get_settings().reranker_model, max_length=512)


def rerank(query: str, candidates: list[SearchResult], top_k: int) -> list[SearchResult]:
    if not candidates:
        return []
    pairs = [(query, c.raw_text) for c in candidates]
    scores = _model().predict(pairs, show_progress_bar=False)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    out: list[SearchResult] = []
    for cand, score in ranked[:top_k]:
        # Replace score with the reranker's confidence — the value the user sees.
        out.append(
            SearchResult(
                chunk_id=cand.chunk_id,
                section=cand.section,
                title=cand.title,
                raw_text=cand.raw_text,
                page=cand.page,
                score=float(score),
            )
        )
    return out
