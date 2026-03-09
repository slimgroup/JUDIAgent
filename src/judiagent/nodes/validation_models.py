"""Validation data models for the JUDIAgent code-checking pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.messages import HumanMessage


@dataclass(frozen=True)
class ValidationFinding:
    """A single lint/runtime finding emitted during validation."""

    stage: str
    report: str


@dataclass
class ValidationConversation:
    """Mutable validation session state used by the orchestrator node."""

    original_code: str
    working_code: str
    messages: list[HumanMessage] = field(default_factory=list)
    findings: list[ValidationFinding] = field(default_factory=list)

    @property
    def code_was_edited(self) -> bool:
        return self.working_code != self.original_code

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)
