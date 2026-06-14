from app.services.chunker import MAX_CHARS, chunk_clauses
from app.services.parser import RawClause


def _clause(section: str, text: str, title: str | None = None) -> RawClause:
    return RawClause(
        section=section, title=title, text=text, page=1, char_start=0, char_end=len(text)
    )


def test_short_clause_makes_one_chunk():
    chunks = chunk_clauses([_clause("5.1", "Term begins on the Effective Date.")], "c1")
    assert len(chunks) == 1
    assert chunks[0].section == "5.1"
    assert "[5.1]" in chunks[0].text


def test_long_clause_splits_with_overlap():
    big = "Lorem ipsum dolor sit amet. " * 500  # ~14k chars
    chunks = chunk_clauses([_clause("2.1", big)], "c1")
    assert len(chunks) > 1
    # All chunks must carry the same section so citations stay correct.
    assert all(c.section == "2.1" for c in chunks)
    assert all(len(c.raw_text) <= MAX_CHARS for c in chunks)


def test_chunk_ids_are_unique_and_sequential():
    clauses = [_clause(f"{i}", f"Clause {i} content here that is long enough to keep." * 3) for i in range(5)]
    chunks = chunk_clauses(clauses, "abc")
    ids = [c.chunk_id for c in chunks]
    assert len(set(ids)) == len(ids)
    assert ids == [f"abc:{i}" for i in range(len(ids))]


def test_tiny_clauses_dropped():
    chunks = chunk_clauses([_clause("9.9", "ok")], "c1")
    assert chunks == []  # 2 chars < MIN_CHUNK_CHARS
