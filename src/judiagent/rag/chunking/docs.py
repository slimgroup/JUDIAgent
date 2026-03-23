"""Markdown-document chunking and formatting for JUDIAgent RAG."""

from __future__ import annotations

import re
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from judiagent.core.documents import (
    deduplicate_documents as remove_duplicate_chunks,
)
from judiagent.core.documents import (
    get_document_source as get_file_source,
)


def split_markdown_document(
    document: Document,
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    content = preprocess_markdown_content(document.page_content)
    document_metadata = document.metadata.copy()

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=True,
    )
    splits = markdown_splitter.split_text(content)

    processed_docs = []
    for split in splits:
        split.metadata = {**split.metadata, **document_metadata}
        for key in ["Header 1", "Header 2", "Header 3"]:
            if key in split.metadata and split.metadata[key]:
                split.metadata[key] = re.sub(
                    r"\s*\{#[^}]*\}",
                    "",
                    split.metadata[key],
                ).strip()
        processed_docs.append(split)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    final_docs = []
    for doc in text_splitter.split_documents(processed_docs):
        doc.metadata.update(document_metadata)
        final_docs.append(doc)
    return final_docs


def preprocess_markdown_content(content: str) -> str:
    content = re.sub(r"^\s*>+", "", content, flags=re.MULTILINE).strip()
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content).strip()
    content = re.sub(r"```ansi[\s\S]*?```", "", content, flags=re.MULTILINE).strip()
    return content


def format_markdown_chunk(doc: Document) -> str:
    return doc.page_content.strip()


def section_path(doc: Document, for_ui_printing: bool = False) -> str:
    header_keys = ["Header 1", "Header 2", "Header 3"]
    section_path_parts = [
        str(doc.metadata[key])
        for key in header_keys
        if key in doc.metadata and doc.metadata[key] is not None
    ]
    if for_ui_printing:
        return section_path_parts[0] if section_path_parts else "Root"
    return " > ".join(section_path_parts) if section_path_parts else "Root"


def format_markdown_context(docs, remove_duplicates: bool = True):
    if remove_duplicates:
        docs = remove_duplicate_chunks(docs)

    formatted = []
    for doc in docs:
        doc_string = f"# From `{get_file_source(doc)}`: Section `{section_path(doc)}`\n"
        doc_string += format_markdown_chunk(doc)
        formatted.append(doc_string)
    return "\n\n".join(formatted)
