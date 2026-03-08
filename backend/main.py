"""FastAPI app: CORS, exception handlers, router. Load .env from project root."""
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (parent of backend/)
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.exceptions import (
    AppException,
    NoPDFLoadedError,
    OpenAITimeoutError,
    PDFParseError,
    VectorStoreError,
)
from backend.api.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _exception_response(exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": exc.type_name},
    )


@app.exception_handler(PDFParseError)
async def pdf_parse_handler(_request: Request, exc: PDFParseError) -> JSONResponse:
    return _exception_response(exc)


@app.exception_handler(OpenAITimeoutError)
async def openai_timeout_handler(_request: Request, exc: OpenAITimeoutError) -> JSONResponse:
    return _exception_response(exc)


@app.exception_handler(VectorStoreError)
async def vector_store_handler(_request: Request, exc: VectorStoreError) -> JSONResponse:
    return _exception_response(exc)


@app.exception_handler(NoPDFLoadedError)
async def no_pdf_loaded_handler(_request: Request, exc: NoPDFLoadedError) -> JSONResponse:
    return _exception_response(exc)


@app.exception_handler(Exception)
async def generic_handler(_request: Request, exc: Exception) -> JSONResponse:
    import logging
    logging.getLogger("pdf_query").exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "伺服器發生錯誤", "type": type(exc).__name__},
    )


# Ensure upload directory exists on startup
@app.on_event("startup")
async def startup() -> None:
    import os
    os.makedirs(settings.upload_folder, exist_ok=True)


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
