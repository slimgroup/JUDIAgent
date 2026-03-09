"""Corpus catalog for JUDIAgent retrieval datasets."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable

from judiagent.rag.chunking.docs import split_markdown_document
from judiagent.rag.chunking.examples import split_julia_example_document
from judiagent.settings import PROJECT_ROOT


@dataclass(frozen=True)
class CorpusSpec:
    """Describe a retrievable corpus and how JUDIAgent should process it."""

    source_dir: str
    persist_dir: Callable[[str], str]
    cache_file: str
    collection_name: str
    filetypes: tuple[str, ...]
    chunk_document: Callable


RAG_CATALOG = {
    "judi": {
        "docs": CorpusSpec(
            source_dir=str(PROJECT_ROOT / "rag" / "judi" / "docs" / "src"),
            persist_dir=lambda embedding_family: str(
                PROJECT_ROOT
                / "rag"
                / "retriever_store"
                / f"retriever_judi_docs_{embedding_family}"
            ),
            cache_file=str(
                PROJECT_ROOT / "rag" / "loaded_store" / "loaded_judi_docs.pkl"
            ),
            collection_name="judi_docs",
            filetypes=("md",),
            chunk_document=split_markdown_document,
        ),
        "examples": CorpusSpec(
            source_dir=str(PROJECT_ROOT / "rag" / "judi" / "examples"),
            persist_dir=lambda embedding_family: str(
                PROJECT_ROOT
                / "rag"
                / "retriever_store"
                / f"retriever_judi_examples_{embedding_family}"
            ),
            cache_file=str(
                PROJECT_ROOT / "rag" / "loaded_store" / "loaded_judi_examples.pkl"
            ),
            collection_name="judi_examples",
            filetypes=("jl",),
            chunk_document=partial(
                split_julia_example_document,
                header_to_split_on=1,
            ),
        ),
    },
}
