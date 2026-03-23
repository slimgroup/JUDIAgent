from __future__ import annotations

from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
    HumanResponse,
)
from langgraph.types import interrupt


def modify_rag_query(query: str, retriever_name: str) -> str:
    """Allow the UI to approve or edit a retrieval query before execution."""
    request = HumanInterrupt(  # type: ignore[arg-type]
        action_request=ActionRequest(
            action=f"Review the {retriever_name} retrieval query",
            args={"Query": query},
        ),
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
        new_query = args_dict.get("Query", query)
        return new_query if new_query.strip() else query
    if response_type == "ignore":
        return ""
    if response_type == "accept":
        return query
    raise TypeError(f"Interrupt value of type {response_type} is not supported.")
