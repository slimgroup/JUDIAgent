from __future__ import annotations

from typing import Callable

from langchain_core.documents import Document
from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
    HumanResponse,
)
from langgraph.types import interrupt

from judiagent.rag.utils import modify_doc_content


def response_on_rag(
    docs: list[Document],
    get_file_source: Callable,
    get_section_path: Callable,
    format_doc: Callable,
    action_name: str = "Review retrieved context",
) -> list[Document]:
    """Allow the UI to review, edit, or reject retrieved RAG context."""
    if not docs:
        return docs

    action_request_args: dict[str, str] = {}
    arg_names: list[str] = []

    for doc in docs:
        section_path = get_section_path(doc)
        file_source = get_file_source(doc)
        arg_name = f"{file_source} - {section_path}"
        original_arg_name = arg_name
        suffix = 1
        while arg_name in action_request_args:
            arg_name = f"{original_arg_name} ({suffix})"
            suffix += 1
        arg_names.append(arg_name)
        action_request_args[arg_name] = format_doc(doc)

    request = HumanInterrupt(  # type: ignore[arg-type]
        action_request=ActionRequest(action=action_name, args=action_request_args),
        config=HumanInterruptConfig(
            allow_ignore=True,
            allow_accept=True,
            allow_respond=False,
            allow_edit=True,
        ),
    )

    human_response: HumanResponse = interrupt([request])[0]
    response_type = human_response.get("type")

    if response_type == "edit":
        args_dict = human_response.get("args", {}) or {}
        args_dict = args_dict.get("args", {}) if isinstance(args_dict, dict) else {}
        new_docs: list[Document] = []
        for arg_name, doc in zip(arg_names, docs):
            new_content = args_dict.get(arg_name)
            if new_content and new_content.strip():
                new_docs.append(modify_doc_content(doc, new_content))
        return new_docs
    if response_type == "accept":
        return docs
    if response_type == "ignore":
        return []
    raise TypeError(f"Interrupt value of type {response_type} is not supported.")
