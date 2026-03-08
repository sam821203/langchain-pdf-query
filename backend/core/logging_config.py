"""Structured logging: query + retrieved sources. Request-scoped request_id via contextvar."""
import contextvars
import json
import logging
from typing import Any

from backend.core.config import settings
from backend.schemas.request_response import SourceItem  # noqa: I001

# Request-scoped ID set by middleware; used by RequestIdFilter and log_query_and_sources.
request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


class RequestIdFilter(logging.Filter):
    """Inject request_id from contextvar into each LogRecord for this request."""

    def filter(self, record: logging.LogRecord) -> bool:
        rid = request_id_ctx.get(None)
        setattr(record, "request_id", f" [req:{rid}]" if rid else "")
        return True


logger = logging.getLogger("pdf_query")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s%(request_id)s: %(message)s"
        )
    )
    _h.addFilter(RequestIdFilter())
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
    payload: dict[str, Any] = {
        "event": "query",
        "question": question,
        "sources": [{"page": s.page, "content": (s.content or "")[:200]} for s in sources],
        "answer_preview": (answer_preview or "")[:300] if answer_preview else None,
    }
    rid = request_id_ctx.get(None)
    if rid is not None:
        payload["request_id"] = rid
    if extra:
        payload["extra"] = extra
    logger.info(json.dumps(payload, ensure_ascii=False))
