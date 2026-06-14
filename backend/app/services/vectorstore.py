"""ChromaDB-backed vector store with a thin interface.

Why the interface: every method goes through `VectorStore` so swapping to
Pinecone is a single class addition + an env switch — no caller changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

import chromadb
import numpy as np
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.services.chunker import Chunk


@dataclass
class SearchResult:
    chunk_id: str
    section: str
    title: str | None
    raw_text: str
    page: int | None
    score: float


class VectorStore(Protocol):
    def add_chunks(self, contract_id: str, chunks: list[Chunk], embeddings: np.ndarray) -> None: ...
    def search(self, contract_id: str, query_embedding: np.ndarray, top_k: int) -> list[SearchResult]: ...
    def delete_contract(self, contract_id: str) -> None: ...
    def has_contract(self, contract_id: str) -> bool: ...


class ChromaVectorStore:
    _COLLECTION = "legalmind_clauses"

    def __init__(self) -> None:
        settings = get_settings()
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self._COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, contract_id: str, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        if not chunks:
            return
        self._collection.add(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings.tolist(),
            documents=[c.raw_text for c in chunks],
            metadatas=[
                {
                    "contract_id": contract_id,
                    "section": c.section,
                    "title": c.title or "",
                    "page": c.page if c.page is not None else -1,
                    "char_start": c.char_start,
                    "char_end": c.char_end,
                }
                for c in chunks
            ],
        )

    def search(self, contract_id: str, query_embedding: np.ndarray, top_k: int) -> list[SearchResult]:
        result = self._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where={"contract_id": contract_id},
        )
        ids = result["ids"][0]
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        # Chroma cosine 'distance' is 1 - similarity. Convert back to similarity.
        distances = result["distances"][0]
        return [
            SearchResult(
                chunk_id=cid,
                section=meta["section"],
                title=meta["title"] or None,
                raw_text=doc,
                page=meta["page"] if meta["page"] != -1 else None,
                score=float(1.0 - dist),
            )
            for cid, doc, meta, dist in zip(ids, docs, metas, distances)
        ]

    def delete_contract(self, contract_id: str) -> None:
        self._collection.delete(where={"contract_id": contract_id})

    def has_contract(self, contract_id: str) -> bool:
        result = self._collection.get(where={"contract_id": contract_id}, limit=1)
        return len(result["ids"]) > 0


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    return ChromaVectorStore()
