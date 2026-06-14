"""RAG pipeline: hybrid retrieval + rerank + Groq answer with citation enforcement."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from groq import Groq

from app.config import get_settings
from app.services.bm25 import get_bm25_store
from app.services.embedder import embed_query
from app.services.reranker import rerank
from app.services.vectorstore import SearchResult, get_vector_store


_SYSTEM_PROMPT = """You are LegalMind, a careful assistant answering questions about ONE specific legal contract.

You will be given a question and a list of CLAUSES from that contract. Each clause
starts with a bracketed header like [Section 5.3 - Termination] or [Article III].

Hard rules:
1. Answer ONLY using the clauses provided. Do NOT use outside legal knowledge or
   make assumptions about what a typical contract would say.
2. If the clauses do not answer the question, reply exactly:
   "The contract does not appear to address this."
3. Every factual claim MUST cite the source clause using the EXACT bracketed
   header. Example: "Either party may terminate with 30 days notice [Section 5.3]."
4. If multiple clauses are relevant, cite each one.
5. Quote short phrases from the contract when it adds precision. Do not invent
   text that isn't in the clauses.
6. Be concise. Lawyers and non-lawyers will read this. Favor plain English,
   but never sacrifice precision for friendliness.
"""


@dataclass
class AnswerResult:
    answer: str
    citations: list[SearchResult]


def _reciprocal_rank_fusion(
    rankings: list[list[SearchResult]], k: int = 60
) -> list[SearchResult]:
    """Merge ranked lists by reciprocal rank. Robust to score-scale mismatch."""
    fused: dict[str, tuple[float, SearchResult]] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking):
            prior = fused.get(item.chunk_id)
            increment = 1.0 / (k + rank + 1)
            if prior is None:
                fused[item.chunk_id] = (increment, item)
            else:
                fused[item.chunk_id] = (prior[0] + increment, prior[1])
    return [item for _, item in sorted(fused.values(), key=lambda x: x[0], reverse=True)]


@lru_cache(maxsize=1)
def _groq() -> Groq:
    return Groq(api_key=get_settings().groq_api_key)


def _build_user_prompt(question: str, clauses: list[SearchResult]) -> str:
    lines = ["CLAUSES:\n"]
    for c in clauses:
        header = c.section if not c.title else f"{c.section} - {c.title}"
        page_str = f" (p. {c.page})" if c.page else ""
        lines.append(f"[{header}]{page_str}\n{c.raw_text}\n")
    lines.append(f"\nQUESTION: {question}\n")
    lines.append("ANSWER (with citations):")
    return "\n".join(lines)


def answer_question(contract_id: str, question: str) -> AnswerResult:
    settings = get_settings()
    vstore = get_vector_store()
    bm25 = get_bm25_store()

    # Stage 1: hybrid retrieval
    q_vec = embed_query(question)
    dense_hits = vstore.search(contract_id, q_vec, settings.top_k_dense)
    sparse_hits = bm25.search(contract_id, question, settings.top_k_bm25)
    fused = _reciprocal_rank_fusion([dense_hits, sparse_hits])

    if not fused:
        return AnswerResult(
            answer="No clauses indexed for this contract. Please upload it first.",
            citations=[],
        )

    # Stage 2: cross-encoder rerank, keep top_k_rerank
    top_clauses = rerank(question, fused[: max(settings.top_k_dense, settings.top_k_bm25)], settings.top_k_rerank)

    # Stage 3: Groq generation with strict citation prompt
    user_prompt = _build_user_prompt(question, top_clauses)
    response = _groq().chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=800,
    )
    answer = response.choices[0].message.content or ""

    # Only return citations actually referenced in the answer text. Keeps the
    # UI clean. If the model cited none (e.g. refused), return all candidates
    # so the user can see what we searched.
    cited = [c for c in top_clauses if c.section in answer or (c.title and c.title in answer)]
    return AnswerResult(answer=answer.strip(), citations=cited or top_clauses)
