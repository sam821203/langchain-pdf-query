"""API routes: upload-pdf, query, root. Delegate to services and log query/sources."""
import asyncio
import os
import shutil
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException

from backend.core.config import settings
from backend.core.exceptions import NoPDFLoadedError
from backend.core.logging_config import log_query_and_sources
from backend.schemas.request_response import QueryRequest, QueryResponse, SourceItem
from backend.services import pdf_service, retrieval_service
from backend.services.state import get_state, set_state


router = APIRouter()

NO_RELEVANT_MSG = "我無法從提供的內容中找到相關資訊"


def _save_upload_sync(file_path: str, file: UploadFile) -> None:
    """Sync: write uploaded file to disk."""
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


@router.get("/")
async def root() -> dict:
    return {"message": "歡迎來到PDF內容查詢系統！請上傳 PDF 來開始分析。"}


@router.post("/upload-pdf", response_model=dict)
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    file_ext = (file.filename or "").split(".")[-1].lower()
    if file_ext != "pdf":
        raise HTTPException(status_code=400, detail="僅支援 PDF 檔案")
    os.makedirs(settings.upload_folder, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_folder, f"{file_id}.pdf")
    await asyncio.to_thread(_save_upload_sync, file_path, file)
    vectorstore, bm25_retriever = await pdf_service.load_pdf_and_build_index(file_path)
    rag_chain = retrieval_service.build_rag_chain(vectorstore, bm25_retriever)
    await set_state(file_path, vectorstore, bm25_retriever, rag_chain)
    return {"message": "PDF 上傳並初始化成功", "pdf_path": file_path}


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    pdf_path, _vs, _bm25, rag_chain = await get_state()
    if rag_chain is None:
        raise NoPDFLoadedError()
    response = await retrieval_service.aquery(request.question, rag_chain)
    answer_text = response.get("answer", "")
    if NO_RELEVANT_MSG in answer_text:
        sources = []
    else:
        seen_pages: set[int] = set()
        sources = []
        for doc in response.get("context", []):
            page_0 = doc.metadata.get("page", 0)
            page_1 = page_0 + 1
            if page_1 in seen_pages:
                continue
            seen_pages.add(page_1)
            content = (doc.page_content or "")[:200].strip()
            sources.append(SourceItem(page=page_1, content=content))
    result = QueryResponse(answer=answer_text, sources=sources)
    log_query_and_sources(
        question=request.question,
        sources=sources,
        answer_preview=answer_text,
    )
    return result
