"""
Runtime configuration schema for JUDIAgent.

This module exposes the configurable dataclasses used by the agent graph.
Static defaults and environment bootstrap now live in `judiagent.settings`
and are re-exported here for backwards compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Any, Literal, Type, TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config
from pydantic import BaseModel, ConfigDict

import judiagent.prompts as prompts
from judiagent.settings import (
    EMBEDDING_MODEL_NAME,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    LOCAL_MODELS,
    PROJECT_ROOT,
    RECURSION_LIMIT,
    cli_mode,
    mcp_mode,
)

__all__ = [
    "BaseConfiguration",
    "DomainValidation",
    "HumanInteraction",
    "EMBEDDING_MODEL_NAME",
    "LLM_MODEL_NAME",
    "LLM_TEMPERATURE",
    "LOCAL_MODELS",
    "PROJECT_ROOT",
    "RECURSION_LIMIT",
    "cli_mode",
    "mcp_mode",
]

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


class DomainValidation(BaseModel):
    """
    Configuration for JUDI-specific scientific evaluation.

    The domain evaluator complements lint/runtime checks by assessing whether
    generated Julia code contains the expected ingredients for seismic imaging
    or inversion workflows.
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["off", "auto", "strict"] = field(
        default="auto",
        metadata={
            "description": (
                "'off' disables the JUDI domain evaluator, 'auto' enables it for "
                "imaging/inversion-style code, and 'strict' requires it every time."
            )
        },
    )
    minimum_score: float = field(
        default=0.6,
        metadata={
            "description": (
                "Minimum scientific-readiness score required when the domain "
                "evaluator is active."
            )
        },
    )
    benchmark_task_id: str = field(
        default="",
        metadata={
            "description": (
                "Optional benchmark task identifier such as basic_2d_forward, "
                "rtm_basic, or fwi_basic. When set, task-specific metric guidance is used."
            )
        },
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
    domain_validation: DomainValidation = field(
        default_factory=DomainValidation,
        metadata={
            "description": (
                "Settings for the JUDI-specific evaluator that checks whether "
                "generated code reflects a sound seismic imaging or inversion workflow."
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
        cls: Type[T], config: RunnableConfig | None = None
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
