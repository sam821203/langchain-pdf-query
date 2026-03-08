"""App state: current PDF path, vectorstore, and LCEL runnable. Thread/asyncio-safe updates."""
import asyncio
from typing import Any

_lock = asyncio.Lock()
_current_pdf_path: str | None = None
_vectorstore: Any = None
_bm25_retriever: Any = None
_rag_chain: Any = None  # LCEL runnable (ainvoke)


async def get_state() -> tuple[str | None, Any, Any, Any]:
    """Return (pdf_path, vectorstore, bm25_retriever, rag_chain)."""
    async with _lock:
        return (_current_pdf_path, _vectorstore, _bm25_retriever, _rag_chain)


async def set_state(
    pdf_path: str | None,
    vectorstore: Any,
    bm25_retriever: Any,
    rag_chain: Any,
) -> None:
    """Update state after loading a new PDF."""
    async with _lock:
        global _current_pdf_path, _vectorstore, _bm25_retriever, _rag_chain
        _current_pdf_path = pdf_path
        _vectorstore = vectorstore
        _bm25_retriever = bm25_retriever
        _rag_chain = rag_chain


async def clear_state() -> None:
    """Clear state (e.g. on error or explicit reset)."""
    async with _lock:
        global _current_pdf_path, _vectorstore, _bm25_retriever, _rag_chain
        _current_pdf_path = None
        _vectorstore = None
        _bm25_retriever = None
        _rag_chain = None


def get_state_sync() -> tuple[str | None, Any, Any, Any]:
    """Synchronous get for use from sync code (e.g. inside to_thread)."""
    return (_current_pdf_path, _vectorstore, _bm25_retriever, _rag_chain)
