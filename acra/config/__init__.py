"""acra configuration package."""

from .defaults import *
from .profile_manager import ProfileManager

__all__ = [
    "ProfileManager",
    "PROJECT_ROOT",
    "USER_DATA_DIR",
    "GENERATED_PROJECT_DIR",
    "MEMORY_STORAGE_DIR",
    "CHROMA_DB_PATH",
    "CHECKPOINT_DIR",
    "SQLITE_DB_PATH",
    "LLM_PROVIDER",
    "LLM_TEMPERATURE",
    "GEMINI_MODEL",
    "GEMINI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_API_KEY",
    "GROQ_MODEL",
    "GROQ_API_KEY",
    "OLLAMA_MODEL",
    "OLLAMA_BASE_URL",
    "HF_MODEL",
    "HF_API_KEY",
    "HF_DEVICE",
    "HF_LOCAL_REPO",
    "MAX_RETRIES",
    "EXECUTION_TIMEOUT",
    "CHECKPOINT_BACKEND",
    "MEMORY_MAX_ENTRIES",
    "SHORT_TERM_MEM_LIMIT",
    "MEMORY_LOG_TRUNCATE",
    "EMBEDDING_MODEL",
]
