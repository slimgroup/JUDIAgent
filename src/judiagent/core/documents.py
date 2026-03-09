"""Document and file helpers shared across JUDIAgent retrieval code."""

from __future__ import annotations

import os

from langchain_core.documents import Document


def read_text_lines(file_path: str) -> list[str]:
    """Load non-empty, stripped lines from a text file."""
    if not file_path:
        raise ValueError("File path cannot be empty.")
    file_path = str(file_path)
    try:
        with open(file_path, "r") as handle:
            return [line.strip() for line in handle if line.strip()]
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"File not found: {file_path}  (cwd={os.getcwd()})"
        ) from exc
    except IOError as exc:
        raise IOError(f"Could not read {file_path}: {exc}") from exc


def get_document_source(doc: Document) -> str:
    """Return the ``source`` metadata field from a LangChain document."""
    return doc.metadata.get("source", "Unknown Document")


def deduplicate_documents(chunks: list[Document]) -> list[Document]:
    """Remove duplicate documents by page-content hash."""
    seen: set[str] = set()
    unique: list[Document] = []
    for doc in chunks:
        key = doc.page_content.strip()
        if key not in seen:
            seen.add(key)
            unique.append(doc)
    return unique


def trim_document_source(source: str, anchor: str = "rag") -> str:
    """Strip the path prefix up to and including ``/<anchor>/``."""
    index = source.find(f"/{anchor}/")
    if index != -1:
        return source[index + len(f"/{anchor}/"):]
    return source
