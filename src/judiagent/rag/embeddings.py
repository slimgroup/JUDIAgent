"""Embedding backend factory for JUDIAgent retrieval."""

from __future__ import annotations

from langchain_core.embeddings import Embeddings

from judiagent.core.models import resolve_provider_and_model


def build_embedding_backend(model_ref: str) -> Embeddings:
    """Create the embedding backend declared in configuration."""
    provider, model_name = resolve_provider_and_model(model_ref)
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=model_name)
    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(model=model_name)
    raise ValueError(f"Unsupported embedding provider: {provider}")
