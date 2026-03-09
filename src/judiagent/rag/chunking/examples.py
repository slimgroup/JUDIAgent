"""Julia-example chunking and formatting for JUDIAgent RAG."""

from __future__ import annotations

import re
from typing import List

from langchain_core.documents import Document

from judiagent.core.documents import (
    deduplicate_documents as remove_duplicate_chunks,
    get_document_source as get_file_source,
)


def split_julia_example_document(
    document: Document,
    header_to_split_on: int = 2,
) -> List[Document]:
    """
    Split Julia example files at commented markdown-style headings such as `# #`.
    """
    lines = document.page_content.splitlines()
    chunks = []
    current_chunk_lines = []
    current_heading = None
    current_metadata = document.metadata.copy()

    def finalize_chunk():
        if current_chunk_lines:
            chunk_text = "\n".join(line for line in current_chunk_lines if line.strip())
            if chunk_text:
                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata={**current_metadata, "heading": current_heading},
                    )
                )

    for line in lines:
        heading_match = re.match(
            rf"^#\s+(#{{1,{header_to_split_on}}})\s+(.*)",
            line.strip(),
        )
        if heading_match:
            finalize_chunk()
            current_chunk_lines = [line]
            current_heading = heading_match.group(2)
        else:
            current_chunk_lines.append(line)

    finalize_chunk()
    return chunks


def format_example_chunk(doc: Document, within_julia_context: bool = True) -> str:
    if within_julia_context:
        return f"```julia\n{doc.page_content.strip()}\n```"
    return doc.page_content.strip()


def format_example_context(docs: List[Document], remove_duplicates: bool = True) -> str:
    if remove_duplicates:
        docs = remove_duplicate_chunks(docs)

    formatted = []
    for doc in docs:
        example_string = f"# From `{get_file_source(doc)}`:\n"
        example_string += format_example_chunk(doc, within_julia_context=True)
        formatted.append(example_string)

    return "\n\n".join(formatted)
