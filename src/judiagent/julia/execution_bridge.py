"""High-level Julia execution bridge for JUDIAgent."""

from __future__ import annotations

import time

from judiagent.julia.bridge_types import JuliaExecutionResult
from judiagent.julia.error_formatting import (
    CONDAPKG_NOISE,
    format_runtime_error,
    parse_error_and_trace,
)
from judiagent.julia.subprocess_runner import (
    execute_julia_inline,
    execute_julia_script,
)

__all__ = [
    "JuliaExecutionResult",
    "execute_and_capture",
    "execute_julia_inline",
    "execute_julia_script",
    "format_runtime_error",
]

SUCCESS_HINTS = ["ran in", "Operator"]
REAL_ERROR_TOKENS = [
    "error:",
    "exception:",
    "methoderror",
    "typeerror",
    "argumenterror",
    "loaderror",
    "stacktrace:",
]


def execute_and_capture(code: str) -> JuliaExecutionResult:
    """Run Julia code inline and return a structured execution result."""
    t0 = time.time()
    stdout, stderr = execute_julia_inline(code=code)
    elapsed = time.time() - t0

    if stderr:
        stderr_lc = stderr.lower()
        has_condapkg = any(
            token.lower() in stderr_lc for token in CONDAPKG_NOISE + SUCCESS_HINTS
        )
        has_real_error = any(token in stderr_lc for token in REAL_ERROR_TOKENS)

        if has_condapkg and not has_real_error:
            if any(hint in stderr for hint in SUCCESS_HINTS):
                return JuliaExecutionResult(
                    stdout=stdout,
                    has_error=False,
                    elapsed_seconds=elapsed,
                )

        err_msg, err_trace = parse_error_and_trace(stderr)
        return JuliaExecutionResult(
            stdout=stdout,
            has_error=True,
            error_summary=err_msg,
            error_trace=err_trace,
            elapsed_seconds=elapsed,
        )

    return JuliaExecutionResult(
        stdout=stdout,
        has_error=False,
        elapsed_seconds=elapsed,
    )
