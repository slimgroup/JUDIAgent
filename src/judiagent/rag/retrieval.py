"""Retriever orchestration for JUDIAgent RAG corpora."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator

from langchain_core.runnables import RunnableConfig
from langchain_core.vectorstores import VectorStoreRetriever

from judiagent.configuration import BaseConfiguration
from judiagent.rag.catalog import CorpusSpec
from judiagent.rag.embeddings import build_embedding_backend
from judiagent.rag.vector_index import open_vector_retriever


@dataclass(frozen=True)
class RetrievalPlan:
    """Search controls for a single retrieval request."""

    search_type: str = "mmr"
    search_kwargs: dict[str, Any] = field(
        default_factory=lambda: {"k": 3, "fetch_k": 15, "lambda_mult": 0.5}
    )


RetrievalParams = RetrievalPlan


@contextmanager
def make_retriever(
    config: RunnableConfig,
    spec: CorpusSpec,
    retrieval_params: RetrievalPlan | None = None,
) -> Generator[VectorStoreRetriever, None, None]:
    """Open a retriever for the requested corpus under the active runtime config."""
    configuration = BaseConfiguration.from_runnable_config(config)
    retrieval_plan = retrieval_params or RetrievalPlan()
    embedding_backend = build_embedding_backend(configuration.embedding_model)

    with open_vector_retriever(
        provider=configuration.retriever_provider,
        spec=spec,
        embedding_model_ref=configuration.embedding_model,
        embedding_backend=embedding_backend,
        search_type=retrieval_plan.search_type,
        search_kwargs=retrieval_plan.search_kwargs,
    ) as retriever:
        if configuration.rerank_provider == "None":
            yield retriever
            return

    raise ValueError(
        "Unrecognized rerank_provider in configuration. "
        f"Expected one of: {', '.join(BaseConfiguration.__annotations__['rerank_provider'].__args__)}\n"
        f"Got: {configuration.rerank_provider}"
    )
