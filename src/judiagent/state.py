"""
Agent workflow state definitions.

Defines the data structures that flow through the LangGraph pipeline:
- JuliaCodeBlock: Parsed code container with import/body separation
- AgentState: Core mutable state for conversation tracking and code validation
- MCPInputState / MCPOutputState: Schemas for VSCode Copilot integration
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Sequence


class JuliaCodeBlock(BaseModel):
    """
    Structured container for Julia code, separating import directives from the body.

    Attributes:
        imports: Package import statements (e.g., ``using JUDI``)
        body: Main code excluding imports
    """

    imports: str = Field(default="", description="Julia import/using statements")
    body: str = Field(default="", description="Main code body excluding imports")

    def is_blank(self) -> bool:
        return not self.imports and not self.body

    def to_string(
        self, wrap_as_markdown: bool = False, omit_if_empty: bool = False
    ) -> str:
        """
        Serialize the code block, optionally wrapped in a Julia markdown fence.

        Args:
            wrap_as_markdown: Surround with triple-backtick julia fence.
            omit_if_empty: Return ``""`` when both fields are blank.
        """
        if omit_if_empty and self.is_blank():
            return ""

        parts: list[str] = []
        if wrap_as_markdown:
            parts.append("```julia")
        if self.imports:
            parts.append(self.imports)
        if self.body:
            parts.append(self.body)
        if wrap_as_markdown:
            parts.append("```")
        return "\n".join(parts)


@dataclass
class MCPInputState:
    """Input schema for the MCP endpoint (VSCode Copilot integration)."""

    question: str
    current_filepath: str


@dataclass
class MCPOutputState:
    """Output schema returned from the MCP endpoint."""

    answer: str
    code_block: JuliaCodeBlock


@dataclass
class AgentState:
    """
    Mutable state threaded through the LangGraph pipeline.

    Tracks the evolving conversation, code artefacts, error flags, and
    execution metadata.  The ``add_messages`` reducer merges new messages
    by ID so the history is append-only.
    """

    mcp_question: str = ""
    mcp_current_filepath: str = ""
    mcp_answer: str = ""
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    error: bool = field(default=False)
    error_message: str = field(default="")
    iteration_count: int = field(default=0)
    should_regenerate: bool = field(default=False)
    retrieved_context: str = field(default="")
    code_block: JuliaCodeBlock = field(default_factory=JuliaCodeBlock)
    is_last_step: bool = field(default=False)
    remaining_steps: int = field(default=50)
