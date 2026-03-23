"""Conversation history helpers for JUDIAgent runtime safety."""

from __future__ import annotations

from typing import Any, Callable, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, trim_messages
from langchain_core.runnables import Runnable

MESSAGE_TOKEN_BUDGET = 40_000
TokenCounter = BaseChatModel | Callable[[list[BaseMessage]], int]
ModelLike = BaseChatModel | Runnable[Any, BaseMessage]


def estimate_messages_as_tokens(messages: list[BaseMessage]) -> int:
    """Approximate token count when the provider cannot count tokens directly."""
    return max(1, sum(len(str(message.content)) for message in messages) // 4)


def _trim_with_counter(
    messages: Sequence[BaseMessage],
    *,
    token_counter: TokenCounter,
    max_tokens: int = MESSAGE_TOKEN_BUDGET,
    include_system: bool = False,
) -> list[BaseMessage]:
    return list(
        trim_messages(
            list(messages),
            max_tokens=max_tokens,
            strategy="last",
            token_counter=token_counter,
            include_system=include_system,
            allow_partial=True,
        )
    )


def _trim_with_model_counter(
    messages: Sequence[BaseMessage],
    model: BaseChatModel,
    *,
    max_tokens: int,
    include_system: bool,
) -> list[BaseMessage]:
    """Attempt token-aware trimming using the backend model itself."""
    return _trim_with_counter(
        messages,
        token_counter=model,
        max_tokens=max_tokens,
        include_system=include_system,
    )


def _trim_with_estimated_counter(
    messages: Sequence[BaseMessage],
    *,
    max_tokens: int,
    include_system: bool,
) -> list[BaseMessage]:
    """Fallback trim path when the backend cannot count tokens directly."""
    return _trim_with_counter(
        messages,
        token_counter=estimate_messages_as_tokens,
        max_tokens=max_tokens,
        include_system=include_system,
    )


def strip_orphaned_tool_messages(messages: Sequence[BaseMessage]) -> list[BaseMessage]:
    """Drop leading ``ToolMessage`` objects whose parent AI tool call was trimmed."""
    msgs = list(messages)
    first_valid = 0

    for i, message in enumerate(msgs):
        if isinstance(message, ToolMessage):
            tool_call_id = getattr(message, "tool_call_id", None)
            has_parent = False
            for j in range(i - 1, -1, -1):
                previous = msgs[j]
                if isinstance(previous, AIMessage) and previous.tool_calls:
                    if any(tool_call.get("id") == tool_call_id for tool_call in previous.tool_calls):
                        has_parent = True
                        break
            if not has_parent:
                first_valid = i + 1
            else:
                break
        else:
            break

    return msgs[first_valid:]


def compact_message_history(
    messages: Sequence[BaseMessage],
    model: ModelLike,
    *,
    max_tokens: int = MESSAGE_TOKEN_BUDGET,
    include_system: bool = False,
    drop_orphaned_tool_messages: bool = True,
) -> list[BaseMessage]:
    """Trim message history to fit within the configured runtime budget."""
    try:
        if not isinstance(model, BaseChatModel):
            raise TypeError("Model does not expose LangChain token counting")
        trimmed = _trim_with_model_counter(
            messages,
            max_tokens=max_tokens,
            include_system=include_system,
            model=model,
        )
    except Exception:
        trimmed = _trim_with_estimated_counter(
            messages,
            max_tokens=max_tokens,
            include_system=include_system,
        )

    if drop_orphaned_tool_messages:
        return strip_orphaned_tool_messages(trimmed)
    return trimmed
