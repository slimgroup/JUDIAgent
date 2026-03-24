"""Low-level Julia subprocess runners used by the execution bridge."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

LINT_TIMEOUT_SECS = 120
DEFAULT_CODE_TIMEOUT_SECS = 180
HEAVY_CODE_TIMEOUT_SECS = 600
HEAVY_RUNTIME_MARKERS = (
    "judijacobian",
    "adjoint(j",
    "lsrtm",
    "rtm",
    "illumination",
    "fwi",
    "twri",
    "nlopt",
    "gradient descent",
)


def resolve_julia_executable() -> str:
    """Return the Julia executable path from env or the current PATH."""
    for env_name in ("JUDIAgent_JULIA_BIN", "JULIA_BIN"):
        configured = os.environ.get(env_name, "").strip()
        if configured:
            return configured

    resolved = shutil.which("julia")
    if resolved:
        return resolved

    return "julia"

def _parse_timeout_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def determine_code_timeout_secs(code: str) -> int:
    """Choose a Julia runtime timeout from env and simple task heuristics."""
    base_timeout = _parse_timeout_env("JUDIAgent_JULIA_CODE_TIMEOUT_SECS", DEFAULT_CODE_TIMEOUT_SECS)
    heavy_timeout = _parse_timeout_env("JUDIAgent_JULIA_HEAVY_CODE_TIMEOUT_SECS", HEAVY_CODE_TIMEOUT_SECS)

    code_lc = code.lower()
    is_heavy = any(marker in code_lc for marker in HEAVY_RUNTIME_MARKERS)
    return max(base_timeout, heavy_timeout) if is_heavy else base_timeout



def execute_julia_script(
    code: str,
    driver_script: str,
    project_dir: str | None = None,
) -> tuple[str, str, int | None]:
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
        julia_bin = resolve_julia_executable()
        proc = subprocess.run(
            [julia_bin, f"--project={project_dir}", driver_path, project_dir, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir,
            timeout=LINT_TIMEOUT_SECS,
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        _try_kill(exc)
        return (
            "",
            f"Error: Julia process timed out after {LINT_TIMEOUT_SECS} seconds. "
            + "This may happen when loading large packages like JUDI. "
            + "The linter check was skipped.",
            None,
        )
    except FileNotFoundError as exc:
        return "", f"Error running Julia: {exc}", None
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def execute_julia_inline(
    code: str,
    project_dir: str | None = None,
    timeout_secs: int | None = None,
) -> tuple[str, str, int | None, str]:
    """Execute a Julia code snippet via ``julia -e``."""
    project_dir = project_dir or os.getcwd()
    julia_bin = resolve_julia_executable()
    timeout_secs = timeout_secs or determine_code_timeout_secs(code)
    try:
        proc = subprocess.run(
            [julia_bin, f"--project={project_dir}", "-e", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir,
            timeout=timeout_secs,
        )
        return proc.stdout, proc.stderr, proc.returncode, julia_bin
    except subprocess.TimeoutExpired as exc:
        _try_kill(exc)
        return (
            "",
            f"Error: Julia code execution timed out after {timeout_secs} seconds. "
            + "This may happen with complex simulations or when loading large packages.",
            None,
            julia_bin,
        )
    except FileNotFoundError as exc:
        return "", f"Error running Julia: {exc}", None, julia_bin
    except Exception as exc:
        return "", f"Error running Julia: {exc}", None, julia_bin


def _try_kill(timeout_exc: subprocess.TimeoutExpired) -> None:
    proc = getattr(timeout_exc, "process", None)
    if proc is not None:
        try:
            _ = proc.kill()
        except Exception:
            pass
