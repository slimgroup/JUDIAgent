"""Backward-compatible Julia-example chunking exports for JUDIAgent RAG."""

from judiagent.rag.julia_example_chunking import (
    format_example_chunk as format_doc,
)
from judiagent.rag.julia_example_chunking import (
    format_example_context as format_examples,
)
from judiagent.rag.julia_example_chunking import (
    split_julia_example_document as split_examples,
)

__all__ = ["format_doc", "format_examples", "split_examples"]
