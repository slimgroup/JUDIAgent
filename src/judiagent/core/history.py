"""Conversation history helpers for JUDIAgent runtime safety."""

from __future__ import annotations

from typing import Callable, List, Sequence, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, trim_messages
from langchain_core.runnables import Runnable


MESSAGE_TOKEN_BUDGET = 40_000


def estimate_messages_as_tokens(messages: Sequence[BaseMessage]) -> int:
    """
    Approximate token count for message trimming when the provider
    cannot supply an exact tokenizer.
    """
    return max(1, sum(len(str(message.content)) for message in messages) // 4)


def _trim_with_counter(
    messages: Sequence[BaseMessage],
    *,
    token_counter: Union[
        BaseChatModel,
        Runnable[LanguageModelInput, BaseMessage],
        Callable[[Sequence[BaseMessage]], int],
    ],
    max_tokens: int = MESSAGE_TOKEN_BUDGET,
    include_system: bool = False,
) -> Sequence[BaseMessage]:
    return trim_messages(
        messages,
        max_tokens=max_tokens,
        strategy="last",
        token_counter=token_counter,
        include_system=include_system,
        allow_partial=True,
    )


def strip_orphaned_tool_messages(
    messages: Sequence[BaseMessage],
) -> List[BaseMessage]:
    """
    Drop leading ``ToolMessage`` objects whose parent AI tool call
    has been trimmed away.
    """
    msgs = list(messages)
    first_valid = 0

    for i, message in enumerate(msgs):
        if isinstance(message, ToolMessage):
            tool_call_id = getattr(message, "tool_call_id", None)
            has_parent = False
            for j in range(i - 1, -1, -1):
                previous = msgs[j]
                if isinstance(previous, AIMessage) and previous.tool_calls:
                    if any(
                        tool_call.get("id") == tool_call_id
                        for tool_call in previous.tool_calls
                    ):
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
    model: Union[BaseChatModel, Runnable[LanguageModelInput, BaseMessage]],
    *,
    max_tokens: int = MESSAGE_TOKEN_BUDGET,
    include_system: bool = False,
    drop_orphaned_tool_messages: bool = True,
) -> Sequence[BaseMessage]:
    """
    Trim message history to fit within the configured budget.

    Some LangChain backends cannot provide a token counter for
    ``trim_messages(...)``. In that case, fall back to a rough
    character-based estimate so the agent can still proceed.
    """
    try:
        trimmed = _trim_with_counter(
            messages,
            token_counter=model,
            max_tokens=max_tokens,
            include_system=include_system,
        )
    except Exception:
        trimmed = _trim_with_counter(
            messages,
            token_counter=estimate_messages_as_tokens,
            max_tokens=max_tokens,
            include_system=include_system,
        )

    if drop_orphaned_tool_messages:
        return strip_orphaned_tool_messages(trimmed)
    return trimmed
