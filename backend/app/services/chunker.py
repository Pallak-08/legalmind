"""Clause-aware chunker.

Each output chunk carries the *exact* clause metadata from the parser, so when
the LLM cites "Section 5.3" we know it's a real section number — not invented.

Strategy:
  - One short clause -> one chunk.
  - Long clauses -> overlapping windows, all carrying the same section metadata.
  - We do NOT merge across clauses. Merging would muddy citations: the model
    could grab text from clause A while citing clause B.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.services.parser import RawClause


# BGE-large has a 512-token limit. ~4 chars per token => ~2000 char budget.
# We leave headroom for the section/title prefix we prepend.
MAX_CHARS = 1800
OVERLAP_CHARS = 200
MIN_CHUNK_CHARS = 20  # drop dead-tiny fragments but keep short legit clauses


@dataclass
class Chunk:
    chunk_id: str           # "<contract_id>:<seq>"
    section: str
    title: str | None
    text: str               # what gets embedded — includes the section prefix
    raw_text: str           # original clause body, used in citations
    page: int | None
    char_start: int
    char_end: int


def _slide(text: str, max_chars: int, overlap: int) -> list[tuple[int, int, str]]:
    """Yield (start, end, slice) windows. start/end are offsets within `text`."""
    if len(text) <= max_chars:
        return [(0, len(text), text)]
    out = []
    step = max_chars - overlap
    i = 0
    while i < len(text):
        end = min(i + max_chars, len(text))
        out.append((i, end, text[i:end]))
        if end == len(text):
            break
        i += step
    return out


def chunk_clauses(clauses: list[RawClause], contract_id: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    seq = 0
    for clause in clauses:
        body = clause.text.strip()
        if len(body) < MIN_CHUNK_CHARS:
            continue
        windows = _slide(body, MAX_CHARS, OVERLAP_CHARS)
        for (local_start, local_end, slice_text) in windows:
            # Prefix the embedded text with the citation marker so retrieval
            # matches questions like "what does section 5.3 say".
            header = clause.section
            if clause.title:
                header = f"{clause.section} - {clause.title}"
            embed_text = f"[{header}]\n{slice_text}"
            chunks.append(
                Chunk(
                    chunk_id=f"{contract_id}:{seq}",
                    section=clause.section,
                    title=clause.title,
                    text=embed_text,
                    raw_text=slice_text,
                    page=clause.page,
                    char_start=clause.char_start + local_start,
                    char_end=clause.char_start + local_end,
                )
            )
            seq += 1
    return chunks
