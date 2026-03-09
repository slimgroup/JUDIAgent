"""Raw-document loading and cache helpers for JUDIAgent RAG corpora."""

from __future__ import annotations

import pickle
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document

from judiagent.rag.catalog import CorpusSpec


def _make_directory_loaders(spec: CorpusSpec) -> list[DirectoryLoader]:
    return [
        DirectoryLoader(
            path=spec.source_dir,
            glob=f"**/*.{filetype}",
            show_progress=True,
            loader_cls=TextLoader,
        )
        for filetype in spec.filetypes
    ]


def load_raw_documents(spec: CorpusSpec) -> list[Document]:
    """Load raw source documents for a corpus, using a pickle cache when present."""
    cache_path = Path(spec.cache_file)
    if cache_path.exists():
        with open(cache_path, "rb") as handle:
            return pickle.load(handle)

    documents: list[Document] = []
    for loader in _make_directory_loaders(spec):
        documents.extend(loader.load())

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "wb") as handle:
        pickle.dump(documents, handle)
    return documents


def load_chunked_documents(spec: CorpusSpec) -> list[Document]:
    """Load raw corpus files, then transform each one into retrieval chunks."""
    chunks: list[Document] = []
    for document in load_raw_documents(spec):
        chunks.extend(spec.chunk_document(document))
    return chunks
