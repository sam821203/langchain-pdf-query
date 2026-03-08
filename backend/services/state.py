"""App state: per-document PDF path, vectorstore, and LCEL runnable. Thread/asyncio-safe updates."""
import asyncio
from typing import Any

_lock = asyncio.Lock()
_state_by_doc_id: dict[str, tuple[str | None, Any, Any, Any]] = {}  # doc_id -> (pdf_path, vectorstore, bm25_retriever, rag_chain)


async def get_state(doc_id: str) -> tuple[str | None, Any, Any, Any]:
    """Return (pdf_path, vectorstore, bm25_retriever, rag_chain) for doc_id, or (None, None, None, None) if missing."""
    async with _lock:
        return _state_by_doc_id.get(doc_id, (None, None, None, None))


async def set_state(
    doc_id: str,
    pdf_path: str | None,
    vectorstore: Any,
    bm25_retriever: Any,
    rag_chain: Any,
) -> None:
    """Update state for doc_id after loading a new PDF."""
    async with _lock:
        _state_by_doc_id[doc_id] = (pdf_path, vectorstore, bm25_retriever, rag_chain)


async def clear_state(doc_id: str) -> None:
    """Clear state for doc_id (e.g. on error or explicit reset)."""
    async with _lock:
        _state_by_doc_id.pop(doc_id, None)
