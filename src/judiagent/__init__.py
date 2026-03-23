"""Top-level exports for JUDIAgent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["iterative_agent", "react_agent"]

if TYPE_CHECKING:
    from judiagent.agents.agent import iterative_agent
    from judiagent.agents.autonomous_agent import react_agent


def __getattr__(name: str) -> Any:
    if name == "iterative_agent":
        from judiagent.agents.agent import iterative_agent

        return iterative_agent
    if name == "react_agent":
        from judiagent.agents.autonomous_agent import react_agent

        return react_agent
    raise AttributeError(f"module 'judiagent' has no attribute {name!r}")
