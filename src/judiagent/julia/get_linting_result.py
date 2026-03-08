"""
Static analysis of Julia code via the ``julia_lint_script.jl`` driver.

The linter driver uses Julia's ``StaticLint`` / ``CSTParser`` to flag
potential issues.  This module invokes the driver, parses the structured
output, and returns the diagnostic text (empty string if clean).
"""

from __future__ import annotations

import subprocess

from judiagent.cli import colorscheme, print_to_console
from judiagent.julia.julia_code_runner import execute_julia_script


def perform_lint_analysis(code: str) -> str:
    """
    Run static analysis on *code* and return a diagnostic string.

    Returns an empty string when no issues are found or the linter
    times out (JUDI package loading can be slow).
    """
    try:
        stdout, stderr = execute_julia_script(
            code=code, driver_script="julia_lint_script.jl"
        )

        if stderr and "timed out" in stderr.lower():
            print_to_console(
                text=(
                    "Linter timed out (JUDI package loading is slow). "
                    "Skipping static analysis; code will still be validated at runtime."
                ),
                title="Lint Timeout – Skipped",
                border_style=colorscheme.warning,
            )
            return ""

        for idx, line in enumerate(stdout.splitlines()):
            if "STARTING LINT:" in line:
                diagnostics = "\n".join(stdout.splitlines()[idx + 1 :])
                if diagnostics:
                    print_to_console(
                        text=diagnostics,
                        title="Lint Diagnostics",
                        border_style=colorscheme.error,
                    )
                else:
                    print_to_console(
                        text="No lint issues found!",
                        title="Lint Diagnostics",
                        border_style=colorscheme.success,
                    )
                return diagnostics

        if stdout and "STARTING LINT:" not in stdout:
            print_to_console(
                text=f"Partial linter output:\n{stdout[:500]}...",
                title="Lint – Partial Output",
                border_style=colorscheme.warning,
            )
        if stderr and "timed out" not in stderr.lower():
            print_to_console(
                text=f"Lint stderr:\n{stderr[:500]}",
                title="Lint Error",
                border_style=colorscheme.error,
            )
        return ""

    except subprocess.TimeoutExpired:
        print_to_console(
            text=(
                "Linter timed out (JUDI package loading is slow). "
                "Skipping; code will still be validated at runtime."
            ),
            title="Lint Timeout – Skipped",
            border_style=colorscheme.warning,
        )
        return ""
    except Exception as exc:
        print_to_console(
            text=f"Lint error: {exc}",
            title="Lint Error",
            border_style=colorscheme.warning,
        )
        return ""
