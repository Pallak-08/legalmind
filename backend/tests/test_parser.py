"""Unit tests for the parser. These don't need the LLM or embedder."""
from pathlib import Path

import pytest

from app.services.parser import parse_contract
from sample_contracts.mutual_nda import generate_nda_docx


@pytest.fixture(scope="module")
def nda_path(tmp_path_factory) -> Path:
    out_dir = tmp_path_factory.mktemp("contracts")
    return generate_nda_docx(out_dir / "mutual_nda.docx")


def test_detects_doc_type_as_nda(nda_path):
    parsed = parse_contract(nda_path)
    assert parsed.doc_type == "NDA"


def test_extracts_top_level_sections(nda_path):
    parsed = parse_contract(nda_path)
    sections = {c.section for c in parsed.clauses}
    # All nine numbered top-level sections must be found.
    for n in range(1, 10):
        assert any(s.startswith(str(n)) or s == str(n) for s in sections), f"missing section {n}"


def test_extracts_decimal_subsections(nda_path):
    parsed = parse_contract(nda_path)
    sections = {c.section for c in parsed.clauses}
    # Section 5 has 5.1, 5.2, 5.3 — these are the canonical "term" clauses.
    assert any("5.1" in s for s in sections)
    assert any("5.2" in s for s in sections)
    assert any("5.3" in s for s in sections)


def test_extracts_quoted_defined_terms(nda_path):
    """Section 1.1 starts with `"Confidential Information"` — the title leads
    with a quote, not a capital letter. Regex must accept that."""
    parsed = parse_contract(nda_path)
    sections = {c.section for c in parsed.clauses}
    assert any("1.1" in s for s in sections)
    assert any("1.2" in s for s in sections)


def test_extracts_section_titles(nda_path):
    """Section 1 has 'DEFINITIONS' as its inline title — captured in clause.title,
    not the section number itself."""
    parsed = parse_contract(nda_path)
    titles = [c.title or "" for c in parsed.clauses]
    assert any("DEFINITIONS" in t.upper() for t in titles)
    assert any("TERMINATION" in t.upper() for t in titles)


def test_no_empty_clauses(nda_path):
    parsed = parse_contract(nda_path)
    for c in parsed.clauses:
        assert c.text.strip(), f"empty clause {c.section}"
        assert c.char_end > c.char_start
