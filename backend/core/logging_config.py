"""Structured logging: query + retrieved sources. Controlled by LOG_QUERY_EVENTS."""
import json
import logging
from typing import Any

from backend.core.config import settings
from backend.schemas.request_response import SourceItem  # noqa: I001

logger = logging.getLogger("pdf_query")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(_h)


def log_query_and_sources(
    question: str,
    sources: list[SourceItem],
    answer_preview: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log user question and retrieved source snippets (structured). No-op when LOG_QUERY_EVENTS is false."""
    if not settings.log_query_events:
        return
    payload = {
        "event": "query",
        "question": question,
        "sources": [{"page": s.page, "content": (s.content or "")[:200]} for s in sources],
        "answer_preview": (answer_preview or "")[:300] if answer_preview else None,
    }
    if extra:
        payload["extra"] = extra
    logger.info(json.dumps(payload, ensure_ascii=False))
