"""PDF load, Chroma vectorstore, and BM25 retriever. Async wrapper over blocking ops."""
import asyncio
import os
import time
from typing import Any

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever

from backend.core.config import settings
from backend.core.exceptions import PDFParseError, VectorStoreError


VECTOR_DB_PATH = settings.vector_db_path


def _clear_vector_store_sync() -> None:
    """Clear Chroma index files (sync)."""
    if not os.path.isdir(VECTOR_DB_PATH):
        return
    files_to_remove = [
        os.path.join(VECTOR_DB_PATH, "chroma-collections.parquet"),
        os.path.join(VECTOR_DB_PATH, "chroma-embeddings.parquet"),
    ]
    for f in files_to_remove:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass
    time.sleep(0.5)


def _load_and_build_sync(pdf_path: str) -> tuple[Any, Any]:
    """
    Sync: load PDF, build Chroma + BM25. Raises PDFParseError or VectorStoreError.
    Returns (vectorstore, bm25_retriever).
    """
    if not os.path.isfile(pdf_path):
        raise PDFParseError("PDF 檔案不存在。")
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    _clear_vector_store_sync()
    try:
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key or None,
        )
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
    except Exception as e:
        raise PDFParseError(f"PDF 解析失敗：{str(e)}") from e
    if not pages:
        raise PDFParseError("PDF 無有效頁面。")
    try:
        vectorstore = Chroma.from_documents(
            documents=pages,
            embedding=embeddings,
            persist_directory=VECTOR_DB_PATH,
        )
    except Exception as e:
        raise VectorStoreError(f"向量儲存寫入失敗：{str(e)}") from e
    try:
        bm25_retriever = BM25Retriever.from_documents(pages)
        bm25_retriever.k = settings.bm25_retriever_k
    except Exception as e:
        raise VectorStoreError(f"BM25 索引建立失敗：{str(e)}") from e
    return (vectorstore, bm25_retriever)


async def load_pdf_and_build_index(pdf_path: str) -> tuple[Any, Any]:
    """
    Async: run PDF load + Chroma + BM25 in thread pool.
    Returns (vectorstore, bm25_retriever). Raises PDFParseError, VectorStoreError.
    """
    return await asyncio.to_thread(_load_and_build_sync, pdf_path)
