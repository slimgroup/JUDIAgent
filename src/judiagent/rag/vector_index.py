"""Vector-store creation and loading for JUDIAgent retrieval."""

from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from typing import Generator

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever

from judiagent.core.models import resolve_provider_and_model
from judiagent.rag.cache import load_chunked_documents
from judiagent.rag.catalog import CorpusSpec


def _embedding_family(model_ref: str) -> str:
    return resolve_provider_and_model(model_ref)[0]


def _corruption_error(error: Exception) -> bool:
    error_text = str(error)
    error_type = type(error).__name__
    return (
        "PanicException" in error_type
        or "range start index" in error_text
        or "out of range for slice" in error_text
    )


@contextmanager
def _open_faiss_retriever(
    *,
    spec: CorpusSpec,
    embedding_model_ref: str,
    embedding_backend: Embeddings,
    search_type: str,
    search_kwargs: dict,
) -> Generator[VectorStoreRetriever, None, None]:
    from langchain_community.vectorstores import FAISS

    persist_dir = spec.persist_dir(_embedding_family(embedding_model_ref))
    if os.path.exists(persist_dir):
        vectorstore = FAISS.load_local(
            persist_dir,
            embedding_backend,
            allow_dangerous_deserialization=True,
        )
    else:
        vectorstore = FAISS.from_documents(
            documents=load_chunked_documents(spec),
            embedding=embedding_backend,
        )
        vectorstore.save_local(persist_dir)

    yield vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs={**search_kwargs},
    )


@contextmanager
def _open_chroma_retriever(
    *,
    spec: CorpusSpec,
    embedding_model_ref: str,
    embedding_backend: Embeddings,
    search_type: str,
    search_kwargs: dict,
) -> Generator[VectorStoreRetriever, None, None]:
    from langchain_chroma import Chroma

    persist_dir = spec.persist_dir(_embedding_family(embedding_model_ref))
    vectorstore = None

    if os.path.exists(persist_dir):
        try:
            vectorstore = Chroma(
                embedding_function=embedding_backend,
                persist_directory=persist_dir,
                collection_name=spec.collection_name,
            )
            _ = vectorstore._collection
        except Exception as exc:
            if not _corruption_error(exc):
                raise
            if os.path.isdir(persist_dir):
                shutil.rmtree(persist_dir)
            elif os.path.exists(persist_dir):
                os.remove(persist_dir)
            vectorstore = None

    if vectorstore is None:
        vectorstore = Chroma.from_documents(
            documents=load_chunked_documents(spec),
            embedding=embedding_backend,
            persist_directory=persist_dir,
            collection_name=spec.collection_name,
        )

    yield vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs={**search_kwargs},
    )


@contextmanager
def open_vector_retriever(
    *,
    provider: str,
    spec: CorpusSpec,
    embedding_model_ref: str,
    embedding_backend: Embeddings,
    search_type: str,
    search_kwargs: dict,
) -> Generator[VectorStoreRetriever, None, None]:
    """Open the configured vector retriever implementation."""
    if provider == "faiss":
        with _open_faiss_retriever(
            spec=spec,
            embedding_model_ref=embedding_model_ref,
            embedding_backend=embedding_backend,
            search_type=search_type,
            search_kwargs=search_kwargs,
        ) as retriever:
            yield retriever
        return

    if provider == "chroma":
        with _open_chroma_retriever(
            spec=spec,
            embedding_model_ref=embedding_model_ref,
            embedding_backend=embedding_backend,
            search_type=search_type,
            search_kwargs=search_kwargs,
        ) as retriever:
            yield retriever
        return

    raise ValueError(f"Unsupported retriever provider: {provider}")
