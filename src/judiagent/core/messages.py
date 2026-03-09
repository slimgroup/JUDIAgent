from __future__ import annotations

"""LangChain message normalization helpers for JUDIAgent."""

from langchain_core.messages import BaseMessage


def get_message_text(message: BaseMessage) -> str:
    """Extract plain-text content from a LangChain message."""
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", "")
    fragments = [
        fragment if isinstance(fragment, str) else (fragment.get("text") or "")
        for fragment in content
    ]
    return "".join(fragments).strip()
