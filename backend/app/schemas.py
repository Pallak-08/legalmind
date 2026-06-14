from pydantic import BaseModel, Field


class Clause(BaseModel):
    """A single clause extracted from a contract, with citation metadata."""
    section: str = Field(..., description="Clause number like '5.3' or 'Article III' or '(a)'")
    title: str | None = Field(None, description="Heading text, if detected")
    text: str
    page: int | None = None
    char_start: int
    char_end: int


class UploadResponse(BaseModel):
    contract_id: str
    filename: str
    num_clauses: int
    num_pages: int | None
    detected_doc_type: str


class Citation(BaseModel):
    section: str
    title: str | None
    page: int | None
    excerpt: str = Field(..., description="The clause text the answer is grounded in")
    score: float


class QueryRequest(BaseModel):
    contract_id: str
    question: str = Field(..., min_length=3, max_length=1000)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    contract_id: str
