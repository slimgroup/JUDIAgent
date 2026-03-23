"""Tools for Julia code execution, linting, and shell commands."""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from judiagent.cli import colorscheme, print_to_console
from judiagent.core.julia_code import normalize_julia_imports, reduce_simulation_steps
from judiagent.nodes.check_code import _run_code_execution, _run_lint_check

# -----------------------------------------------------------------------
# Julia code execution
# -----------------------------------------------------------------------

class JuliaCodeInput(BaseModel):
    code: str = Field(description="Julia source code to execute")


@tool(
    "execute_julia_snippet",
    args_schema=JuliaCodeInput,
    description="Execute a Julia code snippet. Returns output on success or the error message.",
)
def execute_julia_snippet(code: str):
    code = normalize_julia_imports(code)
    code = reduce_simulation_steps(code)
    report, failed = _run_code_execution(code, show_code=True)
    if failed:
        return report
    return "Code executed successfully!"


# -----------------------------------------------------------------------
# Julia linter
# -----------------------------------------------------------------------

class JuliaLintInput(BaseModel):
    code: str = Field(description="Julia source code to lint (static analysis)")


@tool(
    "lint_julia_code",
    args_schema=JuliaLintInput,
    description="Run static analysis on Julia code. Returns diagnostics or a clean-bill message.",
)
def lint_julia_code(code: str):
    report, has_issues = _run_lint_check(code)
    if not has_issues:
        return "Linter found no issues!"
    return report


# -----------------------------------------------------------------------
# Shell command execution
# -----------------------------------------------------------------------

@tool("execute_shell_command", parse_docstring=True)
def execute_shell_command(command: str) -> str:
    """
    Run a terminal command and return its output.  When running Julia be sure
    to include ``--project=.`` (e.g. ``julia --project=. my_script.jl``).

    Args:
        command: Shell command to execute.  Remember to include ``--project=.`` for Julia commands.

    Returns:
        str: Combined stdout / stderr output.
    """
    from judiagent.human_in_the_loop import cli as hitl

    approved, command = hitl.modify_terminal_run(command)
    if not approved:
        return "User did not approve this command."

    cwd = os.getcwd()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        parts: list[str] = []
        if proc.stdout:
            parts.append(f"# STDOUT:\n\n```text\n{proc.stdout}\n```\n\n")
        if proc.stderr:
            parts.append(f"# STDERR:\n\n```text\n{proc.stderr}\n```\n\n")
        if proc.returncode != 0:
            parts.append(f"EXIT CODE: {proc.returncode}\n")

        output = "".join(parts)
        print_to_console(
            text=output,
            title="Shell Result",
            border_style=colorscheme.success if not proc.stderr else colorscheme.message,
        )
        return output.strip() or "Command completed with no output."

    except subprocess.TimeoutExpired:
        msg = "ERROR: Command timed out after 60 seconds."
        print_to_console(text=msg, title="Shell Error", border_style=colorscheme.error)
        return msg
    except Exception as exc:
        msg = f"ERROR: {exc}"
        print_to_console(text=msg, title="Shell Error", border_style=colorscheme.error)
        return msg


# -----------------------------------------------------------------------
# Directory / workspace tools
# -----------------------------------------------------------------------

def _prepare_project_output_dirs(base_directory: str) -> dict[str, Path]:
    """Ensure the standard JUDIAgent output folders exist."""
    root = Path(base_directory)
    layout = {
        "scripts": root / "scripts",
        "outputs": root / "outputs",
        "figures": root / "outputs" / "figures",
        "data": root / "outputs" / "data",
    }
    for directory in layout.values():
        directory.mkdir(parents=True, exist_ok=True)
    return layout

@tool
def list_directory_contents(directory_path: str) -> str:
    """List items in a directory (files and subdirectories)."""
    try:
        if not os.path.isdir(directory_path):
            return f"ERROR: {directory_path} is not a valid directory."
        items = sorted(os.listdir(directory_path))
        if not items:
            return f"Directory {directory_path} is empty."
        lines = []
        for name in items:
            full = os.path.join(directory_path, name)
            prefix = "[DIR] " if os.path.isdir(full) else "[FILE]"
            lines.append(f"{prefix} {name}")
        return f"Contents of {directory_path}:\n" + "\n".join(lines)
    except Exception as exc:
        return f"ERROR: {exc}"


@tool
def fetch_working_directory() -> str:
    """Return the current working directory path."""
    return os.getcwd()


@tool
def switch_working_directory(directory_path: str) -> str:
    """
    Change the process working directory.

    Args:
        directory_path: Target directory.
    """
    try:
        if not os.path.isdir(directory_path):
            return f"ERROR: {directory_path} is not a valid directory."
        os.chdir(directory_path)
        return f"Working directory changed to: {os.getcwd()}"
    except Exception as exc:
        return f"ERROR: {exc}"


@tool
def scaffold_julia_workspace(task_name: str, base_directory: str | None = None) -> str:
    """
    Create a timestamped ``.jl`` file inside the project ``scripts/`` folder.

    Args:
        task_name: Short descriptor used in the filename.
        base_directory: Where to create the workspace (defaults to cwd).
    """
    base_directory = base_directory or os.getcwd()
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", task_name.lower())
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    layout = _prepare_project_output_dirs(base_directory)
    jl = layout["scripts"] / f"{safe}_{ts}.jl"

    print_to_console(
        text=f"Scaffolding Julia script: {jl}",
        title="Tool: Scaffold Script",
        border_style=colorscheme.message,
    )
    try:
        jl.write_text(
            f"# {task_name}\n"
            f"# Created: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
            f"for dir in [\"scripts\", \"outputs/figures\", \"outputs/data\"]\n"
            f"    isdir(dir) || mkpath(dir)\n"
            f"end\n\n"
        )
        return str(jl)
    except Exception as exc:
        return f"ERROR: {exc}"


@tool
def save_julia_code(code: str, file_path: str, append: bool = False) -> str:
    """
    Write Julia code to a file (overwrite or append).

    Args:
        code: Julia source code.
        file_path: Target ``.jl`` file.
        append: Append instead of overwrite.
    """
    print_to_console(
        text=f"{'Appending' if append else 'Writing'} code → {file_path}",
        title="Tool: Save Julia Code",
        border_style=colorscheme.message,
    )
    try:
        destination = Path(file_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "a" if append else "w") as fh:
            if append:
                fh.write("\n")
            fh.write(code)
            if not code.endswith("\n"):
                fh.write("\n")
        verb = "appended to" if append else "written to"
        return f"Successfully {verb} {destination}"
    except Exception as exc:
        return f"ERROR: {exc}"


@tool
def run_julia_file(file_path: str) -> str:
    """
    Execute a Julia file and return its output.

    Args:
        file_path: Path to the ``.jl`` file.
    """
    print_to_console(
        text=f"Running {file_path}",
        title="Tool: Run Julia File",
        border_style=colorscheme.warning,
    )
    try:
        if not os.path.exists(file_path):
            return f"ERROR: File not found: {file_path}"
        proc = subprocess.run(
            ["julia", file_path], capture_output=True, text=True, timeout=30,
        )
        parts = [f"=== {file_path} ==="]
        if proc.stdout:
            parts.append(f"STDOUT:\n{proc.stdout}")
        if proc.stderr:
            parts.append(f"STDERR:\n{proc.stderr}")
        parts.append(f"EXIT CODE: {proc.returncode}")
        output = "\n".join(parts)
        print_to_console(
            text=output.strip(),
            title="Execution Result",
            border_style=colorscheme.success if proc.returncode == 0 else colorscheme.error,
        )
        return output
    except subprocess.TimeoutExpired:
        return f"ERROR: {file_path} timed out after 30 seconds."
    except Exception as exc:
        return f"ERROR: {exc}"
