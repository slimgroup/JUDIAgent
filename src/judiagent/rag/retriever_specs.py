"""Backward-compatible corpus registry exports for JUDIAgent RAG."""

from judiagent.rag.catalog import CorpusSpec as RetrieverSpec
from judiagent.rag.catalog import RAG_CATALOG as RETRIEVER_SPECS

__all__ = ["RETRIEVER_SPECS", "RetrieverSpec"]
