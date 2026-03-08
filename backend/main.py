"""FastAPI app: CORS, exception handlers, router. Load .env from project root."""
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (parent of backend/)
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings, CORS_ORIGINS
from backend.core.exceptions import AppException
from backend.core.logging_config import request_id_ctx
from backend.api.routes import router


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assign a request_id to each request; set in state, contextvar, and response header."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


app = FastAPI()

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _exception_response(exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": exc.type_name},
    )


@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    return _exception_response(exc)


@app.exception_handler(Exception)
async def generic_handler(_request: Request, exc: Exception) -> JSONResponse:
    import logging
    logging.getLogger("pdf_query").exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "伺服器發生錯誤", "type": "InternalError"},
    )


# Ensure upload directory exists on startup; validate OPENAI_API_KEY to fail fast
@app.on_event("startup")
async def startup() -> None:
    import os
    os.makedirs(settings.upload_folder, exist_ok=True)
    key = (settings.openai_api_key or "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set or empty. Set it in .env or environment before starting the server."
        )


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
