"""POST /upload — accept PDF/DOCX, parse → chunk → embed → index."""
from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.schemas import UploadResponse
from app.services.bm25 import get_bm25_store
from app.services.chunker import chunk_clauses
from app.services.embedder import embed_texts
from app.services.parser import parse_contract
from app.services.vectorstore import get_vector_store


router = APIRouter(tags=["contracts"])


_ALLOWED_SUFFIXES = {".pdf", ".docx", ".doc"}


@router.post("/upload", response_model=UploadResponse)
async def upload_contract(file: UploadFile = File(...)) -> UploadResponse:
    settings = get_settings()

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_SUFFIXES:
        raise HTTPException(400, f"Unsupported file type {suffix}. Use PDF or DOCX.")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        raise HTTPException(413, f"File too large ({size_mb:.1f} MB). Max {settings.max_upload_mb} MB.")

    # Write to a temp file so pdfplumber/docx can open it by path.
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        parsed = parse_contract(tmp_path)
    except ValueError as e:
        raise HTTPException(422, str(e))
    finally:
        tmp_path.unlink(missing_ok=True)

    if not parsed.clauses:
        raise HTTPException(422, "No clauses could be detected in this document.")

    contract_id = uuid.uuid4().hex
    chunks = chunk_clauses(parsed.clauses, contract_id=contract_id)
    if not chunks:
        raise HTTPException(422, "Document parsed but produced no chunks above the minimum size.")

    embeddings = embed_texts([c.text for c in chunks])
    get_vector_store().add_chunks(contract_id, chunks, embeddings)
    # New contract — make sure BM25 won't serve a stale cached index for this id.
    get_bm25_store().invalidate(contract_id)

    return UploadResponse(
        contract_id=contract_id,
        filename=file.filename or "contract",
        num_clauses=len(chunks),
        num_pages=parsed.num_pages,
        detected_doc_type=parsed.doc_type,
    )
