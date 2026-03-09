"""Backward-compatible Julia-example chunking exports for JUDIAgent RAG."""

from judiagent.rag.chunking.examples import (
    format_example_chunk as format_doc,
    format_example_context as format_examples,
    split_julia_example_document as split_examples,
)

__all__ = ["format_doc", "format_examples", "split_examples"]
