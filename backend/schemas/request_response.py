"""Request/response schemas for API (keep contract for frontend)."""
import uuid

from pydantic import BaseModel, Field, field_validator


# 單次查詢問題長度上限，避免過長或惡意輸入
QUESTION_MAX_LENGTH = 4000


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=QUESTION_MAX_LENGTH,
        description="User question (1–4000 characters).",
    )
    document_id: uuid.UUID

    @field_validator("question", mode="before")
    @classmethod
    def normalize_question(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
        return v


class ResetRequest(BaseModel):
    document_id: uuid.UUID


class SourceItem(BaseModel):
    page: int
    content: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem] = []
