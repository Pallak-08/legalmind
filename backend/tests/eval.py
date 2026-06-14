"""End-to-end retrieval evaluation.

Measures how often the *correct* clause appears in the top-k reranked results
for a set of held-out questions. This is the metric to track when you tune
chunk size, retrieval k, or the rerank model.

Run:  python -m tests.eval

Doesn't require a Groq key — only retrieval is measured.
"""
from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

# Allow `python -m tests.eval` from the backend dir.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.bm25 import get_bm25_store  # noqa: E402
from app.services.chunker import chunk_clauses  # noqa: E402
from app.services.embedder import embed_query, embed_texts  # noqa: E402
from app.services.parser import parse_contract  # noqa: E402
from app.services.reranker import rerank  # noqa: E402
from app.services.rag import _reciprocal_rank_fusion  # noqa: E402
from app.services.vectorstore import get_vector_store  # noqa: E402
from sample_contracts.mutual_nda import generate_nda_docx  # noqa: E402


@dataclass
class EvalCase:
    question: str
    expected_sections: list[str]  # any one of these counts as a hit


CASES: list[EvalCase] = [
    EvalCase("How long does this agreement last?", ["5.1", "5"]),
    EvalCase("Can either party terminate early?", ["5.2"]),
    EvalCase("What happens to confidentiality obligations after the agreement ends?", ["5.3"]),
    EvalCase("What if a court orders us to disclose confidential information?", ["4"]),
    EvalCase("What counts as confidential information?", ["1.1"]),
    EvalCase("Are there exceptions to the confidentiality obligation?", ["3"]),
    EvalCase("Can I share confidential info with my employees?", ["1.2", "2.1"]),
    EvalCase("Where will disputes be resolved?", ["9.2"]),
    EvalCase("What law governs this contract?", ["9.1"]),
    EvalCase("Do I have to return the documents at the end?", ["6"]),
]


def _section_matches(actual: str, expected: list[str]) -> bool:
    """Loose match: 'Section 5.1' contains '5.1', 'Article III' contains 'III'."""
    return any(exp in actual for exp in expected)


def run() -> int:
    contract_path = generate_nda_docx(Path(__file__).parent.parent / "sample_contracts" / "sample_mutual_nda.docx")
    print(f"[setup] generated {contract_path}")

    parsed = parse_contract(contract_path)
    print(f"[setup] parsed {len(parsed.clauses)} clauses, doc_type={parsed.doc_type}")

    contract_id = uuid.uuid4().hex
    chunks = chunk_clauses(parsed.clauses, contract_id)
    print(f"[setup] produced {len(chunks)} chunks")

    embeddings = embed_texts([c.text for c in chunks])
    vstore = get_vector_store()
    vstore.add_chunks(contract_id, chunks, embeddings)
    bm25 = get_bm25_store()
    bm25.invalidate(contract_id)

    hits_at_5 = 0
    rerank_hits = 0
    print("\n--- evaluation ---")
    for case in CASES:
        q_vec = embed_query(case.question)
        dense = vstore.search(contract_id, q_vec, 15)
        sparse = bm25.search(contract_id, case.question, 15)
        fused = _reciprocal_rank_fusion([dense, sparse])
        top5 = fused[:5]
        ranked = rerank(case.question, fused[:15], 5)

        top5_hit = any(_section_matches(c.section, case.expected_sections) for c in top5)
        rerank_hit = any(_section_matches(c.section, case.expected_sections) for c in ranked)
        hits_at_5 += int(top5_hit)
        rerank_hits += int(rerank_hit)

        top_section = ranked[0].section if ranked else "—"
        flag = "PASS" if rerank_hit else "MISS"
        print(f"  [{flag}] expected={case.expected_sections}  top1={top_section}  Q='{case.question[:60]}'")

    total = len(CASES)
    print("\n--- results ---")
    print(f"  Hybrid recall@5:   {hits_at_5}/{total}  ({hits_at_5/total:.0%})")
    print(f"  Reranker recall@5: {rerank_hits}/{total}  ({rerank_hits/total:.0%})")

    # Clean up so reruns are clean.
    vstore.delete_contract(contract_id)
    return 0 if rerank_hits == total else 1


if __name__ == "__main__":
    raise SystemExit(run())
