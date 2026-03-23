"""Shared result types for the JUDIAgent Julia execution bridge."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JuliaExecutionResult:
    """Structured outcome of a Julia subprocess run."""

    stdout: str = ""
    has_error: bool = False
    error_summary: str = ""
    error_trace: str | None = None
    elapsed_seconds: float = 0.0
