"""Backward-compatible markdown chunking exports for JUDIAgent RAG."""

from judiagent.rag.chunking.docs import (
    format_markdown_chunk as format_doc,
    format_markdown_context as format_docs,
    preprocess_markdown_content as preprocess_content,
    section_path as get_section_path,
    split_markdown_document as split_docs,
)

__all__ = [
    "format_doc",
    "format_docs",
    "get_section_path",
    "preprocess_content",
    "split_docs",
]
