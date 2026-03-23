"""Backward-compatible markdown chunking exports for JUDIAgent RAG."""

from judiagent.rag.markdown_chunking import (
    format_markdown_chunk as format_doc,
)
from judiagent.rag.markdown_chunking import (
    format_markdown_context as format_docs,
)
from judiagent.rag.markdown_chunking import (
    preprocess_markdown_content as preprocess_content,
)
from judiagent.rag.markdown_chunking import (
    section_path as get_section_path,
)
from judiagent.rag.markdown_chunking import (
    split_markdown_document as split_docs,
)

__all__ = [
    "format_doc",
    "format_docs",
    "get_section_path",
    "preprocess_content",
    "split_docs",
]
