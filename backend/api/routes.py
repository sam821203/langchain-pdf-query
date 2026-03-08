"""API routes: upload-pdf, query, root. Delegate to services and log query/sources."""
import asyncio
import logging
import os
import shutil
import uuid

from fastapi import APIRouter, File, Request, UploadFile, HTTPException

from backend.core.config import settings
from backend.core.exceptions import AppException
from backend.core.logging_config import log_query_and_sources
from backend.schemas.request_response import QueryRequest, QueryResponse, ResetRequest, SourceItem
from backend.services import pdf_service, retrieval_service
from backend.services.state import clear_state, get_state, set_state


router = APIRouter()

NO_RELEVANT_MSG = "我無法從提供的內容中找到相關資訊"

# PDF 檔頭魔術位元組（降低偽造副檔名/MIME 的風險）
PDF_MAGIC = b"%PDF"


def _is_pdf_by_header(header: bytes) -> bool:
    """依檔頭判斷是否為 PDF（至少 4 位元組）。"""
    return len(header) >= 4 and header[:4] == PDF_MAGIC


def _save_upload_sync(file_path: str, file: UploadFile, header: bytes) -> None:
    """Sync: 將已驗證檔頭的檔案寫入磁碟（先寫檔頭再寫剩餘內容）。"""
    with open(file_path, "wb") as buffer:
        buffer.write(header)
        shutil.copyfileobj(file.file, buffer)


@router.get("/")
async def root() -> dict:
    return {"message": "歡迎來到PDF內容查詢系統！請上傳 PDF 來開始分析。"}


@router.get("/config", response_model=dict)
async def get_config() -> dict:
    """Return client-relevant config (e.g. max upload size) so frontend limits stay in sync with backend."""
    return {"max_upload_size_mb": settings.max_upload_size_mb}


@router.post("/upload-pdf", response_model=dict)
async def upload_pdf(request: Request, file: UploadFile = File(...)) -> dict:
    # 1) 副檔名
    file_ext = (file.filename or "").split(".")[-1].lower()
    if file_ext != "pdf":
        raise HTTPException(status_code=400, detail="僅支援 PDF 檔案")
    # 2) Content-Type（若有提供則須為 application/pdf，降低偽造風險）
    content_type = (file.content_type or "").strip().lower()
    if content_type and not content_type.startswith("application/pdf"):
        raise HTTPException(
            status_code=400,
            detail="僅接受 application/pdf 類型，請確認上傳檔案",
        )
    content_length = request.headers.get("content-length")
    if content_length is None:
        raise HTTPException(
            status_code=400,
            detail="請使用帶 Content-Length 的請求上傳檔案",
        )
    try:
        size = int(content_length)
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的 Content-Length")
    if size > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"檔案過大，最大允許 {settings.max_upload_size_mb:.0f} MB",
        )
    # 3) 檔頭魔術位元組：先讀前 4 位元組，未通過則不寫入磁碟
    header = b""
    try:
        header = (await file.read(4)) or b""
    except Exception:
        raise HTTPException(status_code=400, detail="無法讀取上傳檔案內容")
    if not _is_pdf_by_header(header):
        raise HTTPException(
            status_code=400,
            detail="檔案內容並非有效的 PDF（檔頭檢查失敗），請確認檔案格式",
        )
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_folder, f"{file_id}.pdf")
    await asyncio.to_thread(_save_upload_sync, file_path, file, header)
    try:
        vectorstore, bm25_retriever = await pdf_service.load_pdf_and_build_index(file_path)
        rag_chain = retrieval_service.build_rag_chain(vectorstore, bm25_retriever)
        document_id = file_id
        await set_state(document_id, file_path, vectorstore, bm25_retriever, rag_chain)
        return {"message": "PDF 上傳並初始化成功", "document_id": document_id}
    except Exception as e:
        if os.path.isfile(file_path):
            await asyncio.to_thread(os.remove, file_path)
        if isinstance(e, AppException):
            raise
        logging.getLogger(__name__).exception("PDF 上傳或索引建立時發生未預期錯誤")
        raise HTTPException(status_code=500, detail="伺服器發生錯誤")


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    pdf_path, _vs, _bm25, rag_chain = await get_state(str(request.document_id))
    if rag_chain is None:
        raise HTTPException(status_code=404, detail="無效的 document_id 或文件已過期")
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


@router.post("/reset", response_model=dict)
async def reset(request: ResetRequest) -> dict:
    """Clear state and delete uploaded PDF for document_id (idempotent)."""
    doc_id_str = str(request.document_id)
    pdf_path, _vs, _bm25, _rag = await get_state(doc_id_str)
    if pdf_path and os.path.isfile(pdf_path):
        await asyncio.to_thread(os.remove, pdf_path)
    await clear_state(doc_id_str)
    return {"message": "已重置"}
