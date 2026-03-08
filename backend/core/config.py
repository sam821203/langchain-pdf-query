"""Central config from environment. Load .env from project root when running as backend.main."""
import os
from pathlib import Path

# When running as backend.main (e.g. uvicorn backend.main:app), cwd is typically project root
def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _load_dotenv_from_root() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(_project_root() / ".env")
    except Exception:
        pass


_load_dotenv_from_root()

# Upload & vector store paths: under backend/ when relative
BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BACKEND_DIR / "uploaded_pdfs"))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(BACKEND_DIR / "vector"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# Retrieval
VECTOR_RETRIEVER_K = int(os.getenv("VECTOR_RETRIEVER_K", "2"))
BM25_RETRIEVER_K = int(os.getenv("BM25_RETRIEVER_K", "2"))
ENSEMBLE_WEIGHT_VECTOR = float(os.getenv("ENSEMBLE_WEIGHT_VECTOR", "0.5"))
ENSEMBLE_WEIGHT_BM25 = float(os.getenv("ENSEMBLE_WEIGHT_BM25", "0.5"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_QUERY_EVENTS = os.getenv("LOG_QUERY_EVENTS", "true").lower() in ("true", "1", "yes")


class Settings:
    """Settings namespace for dependency injection."""
    upload_folder: str = UPLOAD_FOLDER
    vector_db_path: str = VECTOR_DB_PATH
    openai_api_key: str = OPENAI_API_KEY
    embedding_model: str = EMBEDDING_MODEL
    llm_model: str = LLM_MODEL
    llm_temperature: float = LLM_TEMPERATURE
    vector_retriever_k: int = VECTOR_RETRIEVER_K
    bm25_retriever_k: int = BM25_RETRIEVER_K
    ensemble_weight_vector: float = ENSEMBLE_WEIGHT_VECTOR
    ensemble_weight_bm25: float = ENSEMBLE_WEIGHT_BM25
    log_level: str = LOG_LEVEL
    log_query_events: bool = LOG_QUERY_EVENTS


settings = Settings()
