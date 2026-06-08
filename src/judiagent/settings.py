"""Static settings and environment bootstrap for JUDIAgent."""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent

# Runtime mode selection.
cli_mode: bool = True
mcp_mode: bool = False
assert not (cli_mode and mcp_mode), "cli_mode and mcp_mode cannot both be True"

# Model defaults.
LOCAL_MODELS = False
DEFAULT_REMOTE_LLM = "deepseek:deepseek-chat"
DEFAULT_REMOTE_EMBEDDING = "openai:text-embedding-3-small"
DEFAULT_LOCAL_LLM = "ollama:qwen2.5:7b"
DEFAULT_LOCAL_EMBEDDING = "ollama:nomic-embed-text"

if LOCAL_MODELS:
    LLM_MODEL_NAME = DEFAULT_LOCAL_LLM
    EMBEDDING_MODEL_NAME = DEFAULT_LOCAL_EMBEDDING
else:
    LLM_MODEL_NAME = DEFAULT_REMOTE_LLM
    EMBEDDING_MODEL_NAME = DEFAULT_REMOTE_EMBEDDING

RECURSION_LIMIT = 200
LLM_TEMPERATURE = 0

load_dotenv()

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("faiss").setLevel(logging.WARNING)
