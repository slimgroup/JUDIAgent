"""State-oriented helper functions for JUDIAgent graph state objects."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from judiagent.core.julia_code import parse_julia_code_block
from judiagent.core.messages import get_message_text
from judiagent.state import AgentState, JuliaCodeBlock


def retrieve_latest_code_block(state: AgentState) -> JuliaCodeBlock:
    """Return the Julia code block from the latest AI or human message."""
    last = state.messages[-1]
    text = get_message_text(last) if last.type in ("ai", "human") else ""
    return parse_julia_code_block(text)


def state_as_dict(
    state: AgentState,
    exclude: list[str] | None = None,
) -> dict[str, Any]:
    """Serialize an ``AgentState`` to a dict, optionally dropping keys."""
    data = asdict(state)
    for key in exclude or []:
        data.pop(key, None)
    return data


def recent_tool_message(
    messages: list[Any],
    lookback: int = 2,
    verbose: bool = False,
) -> Any | None:
    """Return the most recent ToolMessage within the last ``lookback`` messages."""
    for message in messages[-lookback:]:
        if message.type == "tool":
            if verbose:
                message.pretty_print()
            return message
    return None
