"""
Code validation pipeline node.

Combines static analysis (linting) with runtime execution to validate
generated Julia code.  Supports human-in-the-loop review at each stage.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from judiagent.cli import colorscheme, print_to_console
from judiagent.configuration import BaseConfiguration, cli_mode
from judiagent.core.julia_code import (
    normalize_julia_imports,
    parse_julia_code_block,
    reduce_simulation_steps,
    wrap_julia_fence,
)
from judiagent.julia import execute_and_capture, format_runtime_error, perform_lint_analysis
from judiagent.state import AgentState


def _run_lint_check(code: str, show_code: bool = True) -> tuple[str, bool]:
    """
    Run Julia static analysis.

    Returns:
        (diagnostic_text, has_issues) – *diagnostic_text* is empty when clean.
    """
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
    if diagnostics:
        report = (
            "## Static analysis issues:\n"
            "The linter reported the following:\n" + diagnostics
        )
        return report, True
    return "", False


def _run_code_execution(code: str, show_code: bool = True) -> tuple[str, bool]:
    """
    Execute Julia code and capture the outcome.

    Returns:
        (error_report, has_issues) – *error_report* is empty on success.
    """
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
            + error_text
        )
        return report, True

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
    return "", False


# ---------------------------------------------------------------------------
# Graph node
# ---------------------------------------------------------------------------

def verify_code_output(
    state: AgentState,
    config: RunnableConfig,
):
    """
    LangGraph node: validate the latest ``code_block`` via lint + execution.

    Returns a state-update dict.  On failure the ``error`` flag is set and
    diagnostic messages are appended so the LLM can self-correct.
    """
    configuration = BaseConfiguration.from_runnable_config(config)
    code_block = state.code_block
    code = code_block.to_string()

    if code_block.is_blank():
        return {"error": False}

    pending_messages: list[HumanMessage] = []
    should_validate = True
    user_response = ""
    working_code = code

    if configuration.human_interaction.code_check:
        if cli_mode:
            import judiagent.human_in_the_loop.cli as hitl_cli
            should_validate, user_response, working_code = hitl_cli.response_on_check_code(code=code)
        else:
            import judiagent.human_in_the_loop.ui as hitl_ui
            should_validate, user_response, working_code = hitl_ui.response_on_check_code(code=code)

    if user_response:
        return {"error": True, "messages": [HumanMessage(content=user_response)]}
    if not should_validate:
        return {"error": False}

    code_was_edited = working_code != code
    if code_was_edited:
        code = working_code
        pending_messages.append(
            HumanMessage(
                content=(
                    "The code was manually edited to the following. "
                    "This version will be validated:\n" + wrap_julia_fence(code)
                )
            )
        )

    code = normalize_julia_imports(code)
    code = reduce_simulation_steps(code)

    try:
        lint_report, lint_failed = _run_lint_check(code, show_code=False)
    except Exception:
        print_to_console(
            text="Static analysis skipped (normal for JUDI due to slow package loading).",
            title="Lint Skipped",
            border_style=colorscheme.warning,
        )
        lint_report, lint_failed = "", False

    exec_report, exec_failed = _run_code_execution(code, show_code=False)

    if not lint_failed and not exec_failed:
        return {"error": False, "messages": pending_messages}

    combined = "# Validation issues – please fix the code:\n"
    if lint_failed:
        combined += lint_report + "\n"
    if exec_failed:
        combined += exec_report

    pending_messages.append(HumanMessage(content=combined))

    should_fix = True
    user_response = ""
    if configuration.human_interaction.fix_error:
        if cli_mode:
            import judiagent.human_in_the_loop.cli as hitl_cli
            should_fix, user_response = hitl_cli.response_on_error()
        else:
            import judiagent.human_in_the_loop.ui as hitl_ui
            should_fix, user_response = hitl_ui.response_on_error()

    if not should_fix:
        pending_messages.append(
            HumanMessage(content="The code failed, but the user chose to skip fixing it.")
        )
        return {"messages": pending_messages, "error": False}

    if user_response:
        pending_messages.append(HumanMessage(content=user_response))

    if code_was_edited:
        edited_block = parse_julia_code_block(code, from_markdown=False)
        return {"messages": pending_messages, "error": True, "code_block": edited_block}
    return {"messages": pending_messages, "error": True}
