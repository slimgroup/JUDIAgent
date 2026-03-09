"""Execution and lint stages for JUDIAgent code validation."""

from __future__ import annotations

from judiagent.cli import colorscheme, print_to_console
from judiagent.core.julia_code import normalize_julia_imports, reduce_simulation_steps
from judiagent.julia import execute_and_capture, format_runtime_error, perform_lint_analysis
from judiagent.nodes.validation_models import ValidationFinding


def prepare_validation_code(code: str) -> str:
    """Normalize code before validation so checks stay fast and reproducible."""
    code = normalize_julia_imports(code)
    code = reduce_simulation_steps(code)
    return code


def run_static_validation(code: str, show_code: bool = False) -> ValidationFinding | None:
    """Run Julia linting and return a finding when issues are reported."""
    if show_code:
        preview = f"```julia\n{code}\n```"
        if len(preview) > 500:
            preview = preview[:500] + "..."
        print_to_console(
            text="Running static analysis:\n" + preview,
            title="Static Analysis",
            border_style=colorscheme.warning,
        )
    else:
        print_to_console(
            text="Running static analysis...",
            title="Static Analysis",
            border_style=colorscheme.warning,
        )

    diagnostics = perform_lint_analysis(code)
    if not diagnostics:
        return None

    report = (
        "## Static analysis issues:\n"
        "The linter reported the following:\n"
        f"{diagnostics}"
    )
    return ValidationFinding(stage="lint", report=report)


def run_runtime_validation(code: str, show_code: bool = False) -> ValidationFinding | None:
    """Execute Julia code and return a finding when runtime errors occur."""
    if show_code:
        preview = f"```julia\n{code}\n```"
        if len(preview) > 500:
            preview = preview[:500] + "..."
        print_to_console(
            text="Executing code:\n" + preview,
            title="Runtime Execution",
            border_style=colorscheme.warning,
        )

    result = execute_and_capture(code)
    if result.has_error:
        error_text = format_runtime_error(result)
        print_to_console(
            text=f"Execution failed!\n\n{error_text}",
            title="Runtime Result",
            border_style=colorscheme.error,
        )
        report = (
            "## Runtime error:\n"
            "Executing the generated code produced the following error:\n"
            f"{error_text}"
        )
        return ValidationFinding(stage="runtime", report=report)

    elapsed_str = f"{result.elapsed_seconds:.2f}"
    output = result.stdout.strip()
    if output:
        if len(output) > 500:
            output = output[:500] + "...\n(Output truncated)"
        summary = f"Executed successfully in {elapsed_str}s!\n\nOutput:\n{output}"
    else:
        summary = f"Executed successfully in {elapsed_str}s!"

    print_to_console(
        text=summary,
        title="Runtime Result",
        border_style=colorscheme.success,
    )
    return None
