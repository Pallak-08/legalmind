"""POST /query — ask a question about a previously-uploaded contract."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import Citation, QueryRequest, QueryResponse
from app.services.rag import answer_question
from app.services.vectorstore import get_vector_store


router = APIRouter(tags=["contracts"])


@router.post("/query", response_model=QueryResponse)
async def query_contract(req: QueryRequest) -> QueryResponse:
    if not get_vector_store().has_contract(req.contract_id):
        raise HTTPException(404, f"Unknown contract_id: {req.contract_id}. Upload it first.")

    result = answer_question(req.contract_id, req.question)
    citations = [
        Citation(
            section=c.section,
            title=c.title,
            page=c.page,
            excerpt=c.raw_text[:400] + ("…" if len(c.raw_text) > 400 else ""),
            score=c.score,
        )
        for c in result.citations
    ]
    return QueryResponse(
        answer=result.answer,
        citations=citations,
        contract_id=req.contract_id,
    )
