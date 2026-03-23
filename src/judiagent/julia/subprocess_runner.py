"""Low-level Julia subprocess runners used by the execution bridge."""

from __future__ import annotations

import os
import subprocess
import tempfile

LINT_TIMEOUT_SECS = 120
CODE_TIMEOUT_SECS = 180


def execute_julia_script(
    code: str,
    driver_script: str,
    project_dir: str | None = None,
) -> tuple[str, str]:
    """Write code to a temp file and run a Julia driver script against it."""
    assert driver_script.endswith(".jl"), "driver_script must be a .jl file"

    project_dir = project_dir or os.getcwd()
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".jl",
        delete=False,
        encoding="utf-8",
        dir=project_dir,
    ) as tmp:
        _ = tmp.write(code)
        tmp.flush()
        tmp_path = tmp.name

    driver_path = os.path.join(
        project_dir,
        "src",
        "judiagent",
        "julia",
        driver_script,
    )

    try:
        proc = subprocess.run(
            ["julia", f"--project={project_dir}", driver_path, project_dir, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir,
            timeout=LINT_TIMEOUT_SECS,
        )
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        _try_kill(exc)
        return (
            "",
            f"Error: Julia process timed out after {LINT_TIMEOUT_SECS} seconds. "
            + "This may happen when loading large packages like JUDI. "
            + "The linter check was skipped.",
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def execute_julia_inline(
    code: str,
    project_dir: str | None = None,
) -> tuple[str, str]:
    """Execute a Julia code snippet via ``julia -e``."""
    project_dir = project_dir or os.getcwd()
    try:
        proc = subprocess.run(
            ["julia", f"--project={project_dir}", "-e", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir,
            timeout=CODE_TIMEOUT_SECS,
        )
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        _try_kill(exc)
        return (
            "",
            f"Error: Julia code execution timed out after {CODE_TIMEOUT_SECS} seconds. "
            + "This may happen with complex simulations or when loading large packages.",
        )
    except Exception as exc:
        return "", f"Error running Julia: {exc}"


def _try_kill(timeout_exc: subprocess.TimeoutExpired) -> None:
    proc = getattr(timeout_exc, "process", None)
    if proc is not None:
        try:
            _ = proc.kill()
        except Exception:
            pass
