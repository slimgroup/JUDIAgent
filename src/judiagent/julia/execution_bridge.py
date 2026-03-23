"""
Julia subprocess execution layer.

Provides two execution strategies for running Julia code from Python:
  1. Script-based: writes code to a temp file, then invokes a driver ``.jl`` script.
  2. Inline: passes the code directly via ``julia -e``.

Both capture stdout/stderr and enforce configurable timeouts.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class JuliaExecutionResult:
    """Structured outcome of a Julia subprocess run."""

    stdout: str = ""
    has_error: bool = False
    error_summary: str = ""
    error_trace: str | None = None
    elapsed_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Low-level runners
# ---------------------------------------------------------------------------

_LINT_TIMEOUT_SECS = 120
_CODE_TIMEOUT_SECS = 180


def execute_julia_script(
    code: str, driver_script: str, project_dir: str | None = None
) -> tuple[str, str]:
    """
    Write *code* to a temporary ``.jl`` file, then run *driver_script* which
    receives the project directory and temp-file path as positional arguments.

    Returns ``(stdout, stderr)``; on timeout returns an explanatory message
    in *stderr*.
    """
    assert driver_script.endswith(".jl"), "driver_script must be a .jl file"

    project_dir = project_dir or os.getcwd()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jl", delete=False, encoding="utf-8", dir=project_dir
    ) as tmp:
        _ = tmp.write(code)
        tmp.flush()
        tmp_path = tmp.name

    driver_path = os.path.join(
        project_dir, "src", "judiagent", "julia", driver_script
    )

    try:
        proc = subprocess.run(
            ["julia", f"--project={project_dir}", driver_path, project_dir, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir,
            timeout=_LINT_TIMEOUT_SECS,
        )
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        _try_kill(exc)
        return (
            "",
            f"Error: Julia process timed out after {_LINT_TIMEOUT_SECS} seconds. "
            + "This may happen when loading large packages like JUDI. "
            + "The linter check was skipped.",
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def execute_julia_inline(code: str, project_dir: str | None = None) -> tuple[str, str]:
    """
    Execute a Julia code snippet via ``julia -e <code>``.

    Returns ``(stdout, stderr)``; on timeout returns an explanatory message
    in *stderr*.
    """
    project_dir = project_dir or os.getcwd()
    try:
        proc = subprocess.run(
            ["julia", f"--project={project_dir}", "-e", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir,
            timeout=_CODE_TIMEOUT_SECS,
        )
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        _try_kill(exc)
        return (
            "",
            f"Error: Julia code execution timed out after {_CODE_TIMEOUT_SECS} seconds. "
            + "This may happen with complex simulations or when loading large packages.",
        )
    except Exception as exc:
        return "", f"Error running Julia: {exc}"


# ---------------------------------------------------------------------------
# Error / stacktrace helpers
# ---------------------------------------------------------------------------

_STACKTRACE_MARKER = "\nStacktrace:\n"

_INTERNAL_TRACE_PATTERNS = [
    r"PythonCall", r"JlWrap", r"juliacall", r"pyjlmodule_seval",
]


def _parse_error_and_trace(raw: str) -> tuple[str, str | None]:
    """
    Separate a Julia error blob into (message, stacktrace-or-None).
    """
    if _STACKTRACE_MARKER in raw:
        msg, trace = raw.split(_STACKTRACE_MARKER, 1)
        return msg.strip(), trace.strip()

    m = re.search(r"(.*?)(\nStacktrace:\n.*)", raw, re.DOTALL)
    if m:
        return m.group(1).strip(), m.group(2).replace("Stacktrace:\n", "").strip()
    return raw.strip(), None


def _sanitize_stacktrace(
    trace: str, exclude: list[str] | None = None
) -> str | None:
    """Remove lines referencing internal PythonCall / JlWrap frames."""
    patterns = exclude or _INTERNAL_TRACE_PATTERNS
    kept = [
        line for line in trace.splitlines()
        if not any(re.search(p, line) for p in patterns)
    ]
    return "\n".join(kept) if kept else None


_CONDAPKG_NOISE = [
    "CondaPkg Found dependencies",
    "CondaPkg Initialising",
    "CondaPkg Installing packages",
    "CondaPkg Wrote",
    "pixi.toml",
    "The default environment has been installed",
    "[dependencies]",
    "[project]",
    "[pypi-dependencies]",
    "channel-priority",
    "conda-forge",
    "automatically generated by CondaPkg",
]


def _strip_condapkg_noise(text: str) -> str:
    """Remove verbose CondaPkg initialisation chatter from output."""
    if not text:
        return text
    filtered: list[str] = []
    suppressing = False
    for line in text.split("\n"):
        if any(tok.lower() in line.lower() for tok in _CONDAPKG_NOISE):
            suppressing = True
            continue
        if not line.strip():
            suppressing = False
            continue
        if not suppressing:
            filtered.append(line)
    return "\n".join(filtered)


def format_runtime_error(result: JuliaExecutionResult) -> str:
    """Render a human-readable error string from a :class:`JuliaExecutionResult`."""
    msg = _strip_condapkg_noise(result.error_summary)
    parts = [msg] if msg else []
    if result.error_trace is not None:
        trace = _strip_condapkg_noise(result.error_trace)
        if trace:
            parts.append(f"\nStacktrace:\n{trace}")
    return "".join(parts)


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------

_SUCCESS_HINTS = ["ran in", "Operator"]

_REAL_ERROR_TOKENS = [
    "error:", "exception:", "methoderror", "typeerror",
    "argumenterror", "loaderror", "stacktrace:",
]


def execute_and_capture(code: str) -> JuliaExecutionResult:
    """
    Run *code* inline and return a structured :class:`JuliaExecutionResult`.

    Distinguishes genuine errors from benign CondaPkg initialisation noise
    that Julia may emit on stderr.
    """
    t0 = time.time()
    stdout, stderr = execute_julia_inline(code=code)
    elapsed = time.time() - t0

    if stderr:
        stderr_lc = stderr.lower()
        has_condapkg = any(tok.lower() in stderr_lc for tok in _CONDAPKG_NOISE + _SUCCESS_HINTS)
        has_real_error = any(tok in stderr_lc for tok in _REAL_ERROR_TOKENS)

        if has_condapkg and not has_real_error:
            if any(hint in stderr for hint in _SUCCESS_HINTS):
                return JuliaExecutionResult(
                    stdout=stdout, has_error=False, elapsed_seconds=elapsed
                )

        err_msg, err_trace = _parse_error_and_trace(stderr)
        return JuliaExecutionResult(
            stdout=stdout,
            has_error=True,
            error_summary=err_msg,
            error_trace=err_trace,
            elapsed_seconds=elapsed,
        )

    return JuliaExecutionResult(stdout=stdout, has_error=False, elapsed_seconds=elapsed)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _try_kill(timeout_exc: subprocess.TimeoutExpired) -> None:
    proc = getattr(timeout_exc, "process", None)
    if proc is not None:
        try:
            _ = proc.kill()
        except Exception:
            pass
