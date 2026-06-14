"""Contract parser: extracts text and clause-level structure from PDF/DOCX files.

The whole point of this module is that legal documents are *structured* — they
have Articles, Sections, numbered clauses, and lettered subclauses. A naive
text-splitter will shred that structure, which means citations later will be
fake ("see section 5" when there's no section 5). We detect structure here so
the chunker and the LLM can both cite real clause numbers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from docx import Document


# Patterns are ordered most-specific first. The first match on a line wins.
# Each pattern has two capture groups: (marker, body_on_same_line).
# The body group is just used to confirm this is a real clause (not a stray
# numeric line); the actual short "title" is extracted from it separately.
_CLAUSE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # ARTICLE III - TERMINATION  /  Article 5: Confidentiality
    ("article", re.compile(r"^\s*ARTICLE\s+([IVXLCDM]+|\d+)\b\.?\s*[-:.]?\s*(.*)$", re.IGNORECASE)),
    # SECTION 5.3 Title  /  Section 12: Indemnification
    ("section", re.compile(r"^\s*SECTION\s+(\d+(?:\.\d+)*)\b\.?\s*[-:.]?\s*(.*)$", re.IGNORECASE)),
    # Multi-part decimal: 5.3 Title, 1.1 "Defined Term"..., 7.2.1 Subclause...
    # No upper bound on body length — DOCX paragraphs put full clause text on one line.
    ("decimal_sub", re.compile(r"^\s*(\d+(?:\.\d+){1,4})\s+(.+)$")),
    # Top-level decimal: 1. Title, 12. Indemnification. Period required to avoid
    # matching stray numeric lines like "1 of 2" in a page footer.
    ("decimal_top", re.compile(r"^\s*(\d+)\.\s+(.+)$")),
    # (a) text...  /  (i) text...
    ("lettered", re.compile(r"^\s*\(([a-z]{1,3}|[ivx]{1,5}|\d{1,3})\)\s+(.+)$")),
    # ALL CAPS HEADING (>=5 chars, no lowercase). Catches standalone "CONFIDENTIALITY".
    ("caps_heading", re.compile(r"^\s*([A-Z][A-Z0-9 &/\-,]{4,80})\s*$")),
]

# Words that often appear in ALL-CAPS but aren't real clause headings.
_CAPS_BLOCKLIST = {"WHEREAS", "NOW THEREFORE", "WITNESSETH", "IN WITNESS WHEREOF"}


@dataclass
class RawClause:
    section: str
    title: str | None
    text: str
    page: int | None
    char_start: int
    char_end: int


@dataclass
class ParsedContract:
    full_text: str
    clauses: list[RawClause]
    num_pages: int | None
    doc_type: str  # "NDA" | "Employment" | "MSA" | "Lease" | "Contract"


# ---------- text extraction ----------

def _extract_pdf(path: Path) -> tuple[str, list[tuple[int, int, int]], int]:
    """Returns (full_text, page_ranges, num_pages).

    page_ranges is a list of (page_number, char_start, char_end) so we can map
    any character offset back to a page number.
    """
    full = []
    page_ranges = []
    offset = 0
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.rstrip() + "\n\n"
            full.append(text)
            page_ranges.append((i, offset, offset + len(text)))
            offset += len(text)
        num_pages = len(pdf.pages)
    return "".join(full), page_ranges, num_pages


def _extract_docx(path: Path) -> tuple[str, list[tuple[int, int, int]], int]:
    """DOCX has no real page concept until rendered; we treat the whole doc as page 1."""
    doc = Document(path)
    parts = []
    for para in doc.paragraphs:
        # Promote heading styles to ALL CAPS so our caps_heading pattern catches them.
        text = para.text
        if para.style and para.style.name.lower().startswith("heading") and text:
            text = text.upper() if not text.isupper() else text
        parts.append(text)
    full = "\n".join(parts) + "\n"
    return full, [(1, 0, len(full))], 1


def _page_for_offset(offset: int, page_ranges: list[tuple[int, int, int]]) -> int | None:
    for page, start, end in page_ranges:
        if start <= offset < end:
            return page
    return page_ranges[-1][0] if page_ranges else None


# ---------- doc type sniffing ----------

_DOC_TYPE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("NDA", ["non-disclosure", "nondisclosure", "confidentiality agreement", "mutual nda"]),
    ("Employment", ["employment agreement", "offer letter", "employee handbook", "at-will employment"]),
    ("MSA", ["master services agreement", "statement of work", "services agreement"]),
    ("Lease", ["lease agreement", "rental agreement", "landlord", "tenant"]),
]


def _detect_doc_type(text: str) -> str:
    head = text[:4000].lower()
    for label, keywords in _DOC_TYPE_KEYWORDS:
        if any(k in head for k in keywords):
            return label
    return "Contract"


# ---------- clause segmentation ----------

def _match_clause_marker(line: str) -> tuple[str, str, str] | None:
    """Returns (kind, marker, inline_title) if line starts a new clause, else None."""
    stripped = line.strip()
    if not stripped:
        return None
    for kind, pattern in _CLAUSE_PATTERNS:
        m = pattern.match(line)
        if not m:
            continue
        marker = m.group(1).strip()
        title = (m.group(2) or "").strip() if m.lastindex and m.lastindex >= 2 else ""
        if kind == "caps_heading":
            if marker.upper() in _CAPS_BLOCKLIST:
                return None
            # Treat the whole heading as the marker AND title, no body yet.
            return kind, marker, marker
        return kind, marker, _extract_title(title) or ""
    return None


def _normalize_section(kind: str, marker: str) -> str:
    if kind == "article":
        return f"Article {marker.upper()}"
    if kind == "section":
        return f"Section {marker}"
    if kind == "lettered":
        return f"({marker})"
    if kind == "caps_heading":
        return marker.strip().title()
    return marker  # decimal_sub / decimal_top: "5.3", "12"


_TITLE_SPLIT = re.compile(r"(?<=[.!?])\s")


def _extract_title(body: str, max_len: int = 80) -> str | None:
    """First sentence (or quoted phrase) of the body, used as a display title."""
    body = body.strip()
    if not body:
        return None
    # If body opens with a quoted defined term, use that.
    if body[0] in ('"', "'"):
        end_quote = body.find(body[0], 1)
        if 2 < end_quote < max_len:
            return body[: end_quote + 1]
    # Otherwise first sentence, capped at max_len.
    parts = _TITLE_SPLIT.split(body, maxsplit=1)
    first = parts[0].strip()
    if len(first) > max_len:
        first = first[:max_len].rstrip() + "…"
    return first or None


def _segment_clauses(
    full_text: str, page_ranges: list[tuple[int, int, int]]
) -> list[RawClause]:
    """Walk line-by-line, opening a new clause every time we see a marker."""
    clauses: list[RawClause] = []
    current: dict | None = None
    offset = 0

    for line in full_text.splitlines(keepends=True):
        marker = _match_clause_marker(line)
        if marker:
            kind, raw_marker, inline_title = marker
            # Close out the previous clause.
            if current:
                current["char_end"] = offset
                current["text"] = current["text"].strip()
                if current["text"]:
                    clauses.append(RawClause(**current))
            section = _normalize_section(kind, raw_marker)
            current = {
                "section": section,
                "title": inline_title if inline_title and inline_title != section else None,
                "text": line,
                "page": _page_for_offset(offset, page_ranges),
                "char_start": offset,
                "char_end": offset + len(line),
            }
        elif current:
            current["text"] += line
        # Pre-amble (text before the first marker) is dropped — it's usually
        # recitals, parties, and date, which we capture as the "Preamble" clause:
        elif line.strip():
            current = {
                "section": "Preamble",
                "title": None,
                "text": line,
                "page": _page_for_offset(offset, page_ranges),
                "char_start": offset,
                "char_end": offset + len(line),
            }
        offset += len(line)

    if current:
        current["char_end"] = offset
        current["text"] = current["text"].strip()
        if current["text"]:
            clauses.append(RawClause(**current))

    return clauses


# ---------- public entry point ----------

def parse_contract(path: str | Path) -> ParsedContract:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        full_text, page_ranges, num_pages = _extract_pdf(path)
    elif suffix in (".docx", ".doc"):
        full_text, page_ranges, num_pages = _extract_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use PDF or DOCX.")

    if not full_text.strip():
        raise ValueError("Could not extract any text from the document.")

    clauses = _segment_clauses(full_text, page_ranges)
    doc_type = _detect_doc_type(full_text)

    return ParsedContract(
        full_text=full_text,
        clauses=clauses,
        num_pages=num_pages,
        doc_type=doc_type,
    )
