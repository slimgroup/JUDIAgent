"""
Configuration Management for JUDIAgent.

This module defines all configurable parameters for the JUDIAgent system,
including LLM model selection, RAG settings, and human-in-the-loop controls.

Configuration Hierarchy:
    1. Environment variables (.env file)
    2. Static module-level settings (cli_mode, LOCAL_MODELS, etc.)
    3. BaseConfiguration dataclass (runtime-adjustable settings)

Usage:
    # Access configuration in code
    from judiagent.configuration import BaseConfiguration, LLM_MODEL_NAME
    
    # Create configuration from LangGraph runtime config
    config = BaseConfiguration.from_runnable_config(runnable_config)
    model_name = config.agent_model

Environment Variables Required:
    - OPENAI_API_KEY: API key for OpenAI models
    - LANGSMITH_API_KEY: API key for LangSmith (optional, for UI/tracing)
    
Module Constants:
    - cli_mode: Enable CLI interface
    - mcp_mode: Enable MCP server for VSCode
    - LOCAL_MODELS: Use local Ollama models instead of OpenAI
    - LLM_MODEL_NAME: Default LLM model
    - EMBEDDING_MODEL_NAME: Default embedding model
    - RECURSION_LIMIT: Max graph recursion steps
"""

from __future__ import annotations

import getpass
import logging
import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Annotated, Any, Literal, Optional, Type, TypeVar

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig, ensure_config
from pydantic import BaseModel, ConfigDict

from judiagent import prompts


# =============================================================================
# Static Mode Configuration
# =============================================================================
# These settings control the overall mode of operation.
# Only one mode should be active at a time.

cli_mode: bool = True   # Interactive terminal interface
mcp_mode: bool = False  # VSCode Copilot integration via MCP protocol

# Validation: modes are mutually exclusive
assert not (cli_mode and mcp_mode), "cli_mode and mcp_mode cannot both be True"


# =============================================================================
# Model Configuration
# =============================================================================
# Control whether to use local (Ollama) or hosted cloud models.
# Local models are free but require local GPU resources.
# Hosted models have stronger performance but require API costs.
#
# ======================== SUPPORTED MODEL PROVIDERS ========================
#
# OpenAI Models (requires OPENAI_API_KEY):
#   - "openai:o1" / "openai:o3-mini"  - Best reasoning, slow, expensive
#   - "openai:gpt-4o"                  - Best overall, multimodal, fast (RECOMMENDED)
#   - "openai:gpt-4.1"                 - Good coding, slightly cheaper
#   - "openai:gpt-4o-mini"             - Fast & cheap, good for most tasks
#
# Anthropic Claude Models (requires ANTHROPIC_API_KEY):
#   - "anthropic:claude-3-7-sonnet-20250219"  - Latest Sonnet, best coding (RECOMMENDED)
#   - "anthropic:claude-3-5-sonnet-20241022"  - Claude 3.5 Sonnet, excellent coding
#   - "anthropic:claude-3-opus-20240229"      - Most capable, slower, expensive
#
# DeepSeek Models (requires DEEPSEEK_API_KEY):
#   - "deepseek:deepseek-chat"       - General purpose, very cost-effective
#   - "deepseek:deepseek-reasoner"   - Best reasoning (R1), great for complex tasks
#
# Local Ollama Models (requires Ollama installed):
#   - "ollama:qwen2.5:7b"            - Good balance of quality and speed
#   - "ollama:llama3.1:8b"           - Meta's latest open model
#   - "ollama:codellama:13b"         - Specialized for code
#
# Embedding Model Options:
#   - "openai:text-embedding-3-large"  - Best quality, higher cost
#   - "openai:text-embedding-3-small"  - Good balance (recommended)
#
# ======================== HOW TO CHANGE MODELS ========================
# Option 1: Change LLM_MODEL_NAME below
# Option 2: Set in .env file: LLM_MODEL_NAME=anthropic:claude-3-7-sonnet-20250219
# Option 3: Pass at runtime: config = {"configurable": {"agent_model": "deepseek:deepseek-reasoner"}}
#
# ======================== API KEYS ========================
# Add to your .env file:
#   OPENAI_API_KEY=sk-...
#   ANTHROPIC_API_KEY=sk-ant-...
#   DEEPSEEK_API_KEY=sk-...

LOCAL_MODELS = False

if LOCAL_MODELS:
    # Local model defaults (requires Ollama installation)
    # qwen2.5:7b is a good balance of quality and resource usage
    LLM_MODEL_NAME = "ollama:qwen2.5:7b"
    EMBEDDING_MODEL_NAME = "ollama:nomic-embed-text"
else:
    # Hosted model defaults
    # Change this to use different providers:
    # - "openai:gpt-4o"                          - Good overall
    # - "anthropic:claude-sonnet-4-20250514"     - Latest Claude Sonnet 4
    # - "anthropic:claude-3-5-sonnet-20241022"   - Claude 3.5 Sonnet
    # - "deepseek:deepseek-chat"                 - DeepSeek V3.2 (latest, cost-effective)
    # - "deepseek:deepseek-reasoner"             - DeepSeek R1 (best reasoning)
    LLM_MODEL_NAME = "deepseek:deepseek-chat"  # Using DeepSeek V3.2
    EMBEDDING_MODEL_NAME = "openai:text-embedding-3-small"

# Graph execution limits
RECURSION_LIMIT = 200  # Maximum recursion depth before error
LLM_TEMPERATURE = 0    # Deterministic outputs for reproducibility


# =============================================================================
# Environment Setup
# =============================================================================

def _set_env(var: str) -> None:
    """
    Prompt for an environment variable if not set.
    
    Used during initialization to ensure required API keys are available.
    
    Args:
        var: Name of the environment variable to check/set
    """
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv()

# Ensure required API keys are available
_set_env("OPENAI_API_KEY")
_set_env("LANGSMITH_API_KEY")

# Reduce logging noise from HTTP clients
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("faiss").setLevel(logging.WARNING)


# =============================================================================
# Human-in-the-Loop Configuration
# =============================================================================

class HumanInteraction(BaseModel):
    """
    Configuration for human-in-the-loop intervention points.
    
    Controls when the agent should pause for human review or input.
    Each flag enables/disables a specific intervention point.
    
    Attributes:
        rag_query: Pause to review/modify RAG search queries
        retrieved_examples: Pause to filter retrieved examples
        code_check: Pause to review generated code before execution
        fix_error: Pause to decide on error handling strategy
        
    Example:
        >>> human_config = HumanInteraction(code_check=True, fix_error=True)
        >>> # Agent will pause before running code and when errors occur
    """
    model_config = ConfigDict(extra="forbid")  # Strict validation
    
    rag_query: bool = field(
        default=False,
        metadata={"description": "Allow modification of RAG search queries"},
    )
    retrieved_examples: bool = field(
        default=False,
        metadata={"description": "Allow filtering of retrieved examples"},
    )
    code_check: bool = field(
        default=True,
        metadata={"description": "Require approval before code execution"},
    )
    fix_error: bool = field(
        default=True,
        metadata={"description": "Allow user decision on error handling"},
    )


# =============================================================================
# Main Configuration Class
# =============================================================================

@dataclass(kw_only=True)
class BaseConfiguration:
    """
    Main configuration class for JUDIAgent runtime settings.
    
    This dataclass defines all configurable parameters that can be
    adjusted at runtime through the LangGraph configuration system.
    Settings can be passed when invoking the agent graph.
    
    Categories:
        - Human Interaction: Control intervention points
        - RAG: Retrieval-augmented generation settings
        - Models: LLM and embedding model selection
        - Prompts: System prompts for agent behavior
        
    Example:
        >>> from langchain_core.runnables import RunnableConfig
        >>> config = RunnableConfig(
        ...     configurable={
        ...         "agent_model": "openai:gpt-4o",
        ...         "examples_search_kwargs": {"k": 5}
        ...     }
        ... )
        >>> react_agent_graph.invoke(state, config=config)
        
    Attributes:
        human_interaction: Human-in-the-loop settings
        embedding_model: Model for text embeddings
        retriever_provider: Vector store backend (chroma/faiss)
        examples_search_type: Search algorithm (similarity/mmr)
        examples_search_kwargs: Search parameters
        rerank_provider: Optional reranking model
        rerank_kwargs: Reranking parameters
        agent_model: LLM for code generation
        autonomous_agent_model: LLM for autonomous agent
        agent_prompt: System prompt for standard agent
        autonomous_agent_prompt: System prompt for autonomous agent
    """

    # =========================================================================
    # Human-in-the-Loop Settings
    # =========================================================================
    human_interaction: HumanInteraction = field(
        default_factory=HumanInteraction,
        metadata={
            "description": (
                "Controls human intervention points during agent execution. "
                "Includes options for RAG query review, code approval, and error handling."
            )
        },
    )

    # =========================================================================
    # RAG (Retrieval-Augmented Generation) Settings
    # =========================================================================
    embedding_model: Annotated[
        str,
        {"__template_metadata__": {"kind": "embeddings"}},
    ] = field(
        default_factory=lambda: EMBEDDING_MODEL_NAME,
        metadata={
            "description": (
                "Embedding model for semantic search. "
                "Format: 'provider:model-name' (e.g., 'openai:text-embedding-3-small')"
            )
        },
    )

    retriever_provider: Annotated[
        Literal["faiss", "chroma"],
        {"__template_metadata__": {"kind": "retriever"}},
    ] = field(
        default="chroma",
        metadata={
            "description": (
                "Vector store backend for RAG retrieval. "
                "Options: 'chroma' (persistent), 'faiss' (in-memory)"
            )
        },
    )

    examples_search_type: Annotated[
        Literal["similarity", "mmr", "similarity_score_threshold"],
        {"__template_metadata__": {"kind": "reranker"}},
    ] = field(
        default="mmr",
        metadata={
            "description": (
                "Search algorithm for example retrieval. "
                "'mmr' (Maximal Marginal Relevance) balances relevance and diversity. "
                "'similarity' returns most similar results. "
                "'similarity_score_threshold' filters by minimum score."
            )
        },
    )

    examples_search_kwargs: dict[str, Any] = field(
        default_factory=lambda: {"k": 2, "fetch_k": 10, "lambda_mult": 0.5},
        metadata={
            "description": (
                "Parameters for the retriever search function. "
                "k: number of results to return. "
                "fetch_k: candidates to fetch before MMR filtering. "
                "lambda_mult: diversity vs relevance trade-off (0=diverse, 1=relevant)."
            )
        },
    )

    rerank_provider: Annotated[
        Literal["None", "flash"],
        {"__template_metadata__": {"kind": "reranker"}},
    ] = field(
        default="None",
        metadata={
            "description": (
                "Optional reranking model to improve retrieval quality. "
                "'flash' uses FlashRank for fast CPU-based reranking."
            )
        },
    )

    rerank_kwargs: dict[str, Any] = field(
        default_factory=lambda: {},
        metadata={"description": "Additional parameters for the reranking model"},
    )

    # =========================================================================
    # LLM Model Settings
    # =========================================================================
    agent_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: LLM_MODEL_NAME,
        metadata={
            "description": (
                "Language model for the standard agent. "
                "Format: 'provider:model-name' (e.g., 'openai:gpt-4.1', 'ollama:qwen2.5:7b')"
            )
        },
    )
    
    autonomous_agent_model: Annotated[
        str, {"__template_metadata__": {"kind": "llm"}}
    ] = field(
        default_factory=lambda: LLM_MODEL_NAME,
        metadata={
            "description": (
                "Language model for the autonomous agent. "
                "Can be the same or different from the standard agent model."
            )
        },
    )

    # =========================================================================
    # Prompt Settings
    # =========================================================================
    agent_prompt: str = field(
        default=prompts.AGENT_PROMPT,
        metadata={
            "description": (
                "System prompt defining the standard agent's behavior, "
                "including role, capabilities, and coding guidelines."
            )
        },
    )
    
    autonomous_agent_prompt: str = field(
        default=prompts.AUTONOMOUS_AGENT_PROMPT,
        metadata={
            "description": (
                "System prompt for the autonomous agent, which has "
                "extended capabilities and more tool access."
            )
        },
    )

    # =========================================================================
    # Factory Method
    # =========================================================================
    @classmethod
    def from_runnable_config(
        cls: Type[T], config: Optional[RunnableConfig] = None
    ) -> T:
        """
        Create configuration instance from LangGraph RunnableConfig.
        
        Extracts the 'configurable' dict from the runtime config and
        maps matching keys to configuration fields.
        
        Args:
            config: LangGraph runtime configuration object
            
        Returns:
            BaseConfiguration instance with values from config
            
        Example:
            >>> config = RunnableConfig(configurable={"agent_model": "gpt-4o"})
            >>> base_config = BaseConfiguration.from_runnable_config(config)
            >>> print(base_config.agent_model)
            'gpt-4o'
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})


# Type variable for generic typing
T = TypeVar("T", bound=BaseConfiguration)
