"""Central config from environment. .env is loaded in main.py before this module is imported."""
import os
from pathlib import Path
from typing import Any

# .env is loaded in main.py (entry point). Project root for resolving relative paths (e.g. RAG_PROMPTS_FILE).
def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


# Upload & vector store paths: under backend/ when relative
BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BACKEND_DIR / "uploaded_pdfs"))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(BACKEND_DIR / "vector"))
MAX_UPLOAD_SIZE_MB = float(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# Retrieval（可透過環境變數調整，建議 k 約 4～8 以平衡上下文與噪音）
VECTOR_RETRIEVER_K = int(os.getenv("VECTOR_RETRIEVER_K", "6"))
BM25_RETRIEVER_K = int(os.getenv("BM25_RETRIEVER_K", "6"))
ENSEMBLE_WEIGHT_VECTOR = float(os.getenv("ENSEMBLE_WEIGHT_VECTOR", "0.5"))
ENSEMBLE_WEIGHT_BM25 = float(os.getenv("ENSEMBLE_WEIGHT_BM25", "0.5"))

# RAG prompts: built-in defaults (overridden by RAG_PROMPTS_FILE then env)
_DEFAULT_RAG_SYSTEM = "你是根據提供文件內容回答問題的助手。僅根據檢索到的內容回答，不要臆測或編造。"
_DEFAULT_RAG_NO_MATCH = "若提供的內容中沒有與問題相關的資訊，請明確回答「找不到相關內容」，不要猜測或編造。"
_DEFAULT_RAG_USER_TEMPLATE = """以下為檢索到的內容：
{context}

問題：{input}
請僅根據上述內容回答。"""


def _load_rag_prompts_from_file(path: Path) -> dict[str, Any]:
    """Load RAG prompt keys from YAML. Returns dict with system, user_template, no_match_instruction; missing keys are absent."""
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        out: dict[str, Any] = {}
        if "system" in data and isinstance(data["system"], str):
            out["system"] = data["system"].strip()
        if "user_template" in data and isinstance(data["user_template"], str):
            out["user_template"] = data["user_template"].strip()
        if "no_match_instruction" in data and isinstance(data["no_match_instruction"], str):
            out["no_match_instruction"] = data["no_match_instruction"].strip()
        return out
    except Exception:
        return {}


def _resolve_rag_prompts() -> tuple[str, str, str]:
    """Resolve RAG system, user_template, no_match_instruction: defaults -> file (if set) -> env."""
    system = _DEFAULT_RAG_SYSTEM
    user_template = _DEFAULT_RAG_USER_TEMPLATE
    no_match = _DEFAULT_RAG_NO_MATCH

    rag_file = os.getenv("RAG_PROMPTS_FILE", "").strip()
    if rag_file:
        path = Path(rag_file)
        if not path.is_absolute():
            path = _project_root() / path
        if path.exists():
            file_prompts = _load_rag_prompts_from_file(path)
            if file_prompts.get("system"):
                system = file_prompts["system"]
            if file_prompts.get("user_template"):
                user_template = file_prompts["user_template"]
            if file_prompts.get("no_match_instruction"):
                no_match = file_prompts["no_match_instruction"]

    if os.getenv("RAG_SYSTEM_PROMPT", "").strip():
        system = os.getenv("RAG_SYSTEM_PROMPT", "").strip()
    if os.getenv("RAG_USER_TEMPLATE", "").strip():
        user_template = os.getenv("RAG_USER_TEMPLATE", "").strip()
    if os.getenv("RAG_NO_MATCH_INSTRUCTION", "").strip():
        no_match = os.getenv("RAG_NO_MATCH_INSTRUCTION", "").strip()

    return system, user_template, no_match


_RAG_SYSTEM_PROMPT, _RAG_USER_TEMPLATE, _RAG_NO_MATCH_INSTRUCTION = _resolve_rag_prompts()

# CORS: explicit origins when allow_credentials=True (production: set to frontend URL(s))
_DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
_cors_raw = os.getenv("CORS_ORIGINS", _DEFAULT_CORS_ORIGINS).strip()
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_QUERY_EVENTS = os.getenv("LOG_QUERY_EVENTS", "true").lower() in ("true", "1", "yes")


class Settings:
    """Settings namespace for dependency injection."""
    upload_folder: str = UPLOAD_FOLDER
    vector_db_path: str = VECTOR_DB_PATH
    max_upload_size_mb: float = MAX_UPLOAD_SIZE_MB

    @property
    def max_upload_bytes(self) -> int:
        """Max upload size in bytes (read-only, from max_upload_size_mb)."""
        return int(self.max_upload_size_mb * 1024 * 1024)
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
    # RAG prompts (configurable via RAG_PROMPTS_FILE or env)
    rag_system_prompt: str = _RAG_SYSTEM_PROMPT
    rag_user_template: str = _RAG_USER_TEMPLATE
    rag_no_match_instruction: str = _RAG_NO_MATCH_INSTRUCTION


settings = Settings()
