"""In-memory BM25 keyword index, one per contract.

Built lazily on first query by replaying chunks from the vector store. Keeps
Chroma as the single source of truth for persistence; no second on-disk index.
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable

import chromadb
from chromadb.config import Settings as ChromaSettings
from rank_bm25 import BM25Okapi

from app.config import get_settings
from app.services.vectorstore import SearchResult


_TOKEN = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


class _ContractIndex:
    __slots__ = ("bm25", "chunk_ids", "raw_texts", "sections", "titles", "pages")

    def __init__(self, chunks: list[dict]) -> None:
        self.chunk_ids = [c["id"] for c in chunks]
        self.raw_texts = [c["text"] for c in chunks]
        self.sections = [c["section"] for c in chunks]
        self.titles = [c["title"] for c in chunks]
        self.pages = [c["page"] for c in chunks]
        tokenized = [_tokenize(t) for t in self.raw_texts]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        tokens = _tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        # Take top_k indices
        idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        max_score = scores[idx[0]] if idx and scores[idx[0]] > 0 else 1.0
        out: list[SearchResult] = []
        for i in idx:
            if scores[i] <= 0:
                continue
            out.append(
                SearchResult(
                    chunk_id=self.chunk_ids[i],
                    section=self.sections[i],
                    title=self.titles[i] or None,
                    raw_text=self.raw_texts[i],
                    page=self.pages[i] if self.pages[i] != -1 else None,
                    score=float(scores[i] / max_score),  # normalize for RRF later
                )
            )
        return out


class BM25Store:
    _COLLECTION = "legalmind_clauses"

    def __init__(self) -> None:
        self._cache: dict[str, _ContractIndex] = {}
        settings = get_settings()
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    def _load(self, contract_id: str) -> _ContractIndex | None:
        col = self._client.get_or_create_collection(name=self._COLLECTION)
        result = col.get(where={"contract_id": contract_id})
        if not result["ids"]:
            return None
        chunks = [
            {
                "id": cid,
                "text": doc,
                "section": meta["section"],
                "title": meta["title"] or None,
                "page": meta["page"],
            }
            for cid, doc, meta in zip(result["ids"], result["documents"], result["metadatas"])
        ]
        return _ContractIndex(chunks)

    def search(self, contract_id: str, query: str, top_k: int) -> list[SearchResult]:
        if contract_id not in self._cache:
            idx = self._load(contract_id)
            if idx is None:
                return []
            self._cache[contract_id] = idx
        return self._cache[contract_id].search(query, top_k)

    def invalidate(self, contract_id: str) -> None:
        self._cache.pop(contract_id, None)


@lru_cache(maxsize=1)
def get_bm25_store() -> BM25Store:
    return BM25Store()
