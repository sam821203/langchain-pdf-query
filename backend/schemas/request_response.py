"""Request/response schemas for API (keep contract for frontend)."""
from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    page: int
    content: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem] = []


class PDFUpdateRequest(BaseModel):
    pdf_path: str
