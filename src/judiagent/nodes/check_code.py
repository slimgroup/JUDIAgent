"""Graph node that validates generated Julia code for JUDIAgent."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from judiagent.cli import colorscheme, print_to_console
from judiagent.configuration import BaseConfiguration, cli_mode
from judiagent.core.julia_code import parse_julia_code_block, wrap_julia_fence
from judiagent.nodes.validation_models import ValidationConversation
from judiagent.nodes.validation_quality import run_domain_validation
from judiagent.nodes.validation_review import (
    PreValidationDecision,
    request_post_validation_review,
    request_pre_validation_review,
)
from judiagent.nodes.validation_runtime import (
    prepare_validation_code,
    run_runtime_validation,
    run_static_validation,
)
from judiagent.state import AgentState


def _build_validation_feedback(conversation: ValidationConversation) -> HumanMessage:
    combined = "# Validation issues – please fix the code:\n"
    combined += "\n".join(finding.report for finding in conversation.findings)
    return HumanMessage(content=combined)


def _run_lint_check(code: str, show_code: bool = True) -> tuple[str, bool]:
    """Backward-compatible lint wrapper used by older tool call sites."""
    finding = run_static_validation(code, show_code=show_code)
    if finding is None:
        return "", False
    return finding.report, True


def _run_code_execution(code: str, show_code: bool = True) -> tuple[str, bool]:
    """Backward-compatible runtime wrapper used by older tool call sites."""
    finding = run_runtime_validation(code, show_code=show_code)
    if finding is None:
        return "", False
    return finding.report, True


def _review_generated_code(
    *,
    code: str,
    configuration: BaseConfiguration,
) -> PreValidationDecision | None:
    if not configuration.human_interaction.code_check:
        return None
    return request_pre_validation_review(code, cli_mode=cli_mode)


def _run_validation_stages(
    conversation: ValidationConversation,
    configuration: BaseConfiguration,
) -> None:
    try:
        lint_finding = run_static_validation(conversation.working_code, show_code=False)
    except Exception:
        print_to_console(
            text="Static analysis skipped (normal for JUDI due to slow package loading).",
            title="Lint Skipped",
            border_style=colorscheme.warning,
        )
        lint_finding = None

    runtime_finding = run_runtime_validation(conversation.working_code, show_code=False)
    domain_finding = None
    if runtime_finding is None:
        domain_finding = run_domain_validation(
            conversation.working_code,
            configuration.domain_validation,
        )

    for finding in (lint_finding, runtime_finding, domain_finding):
        if finding is not None:
            conversation.findings.append(finding)


# ---------------------------------------------------------------------------
# Graph node
# ---------------------------------------------------------------------------

def verify_code_output(
    state: AgentState,
    config: RunnableConfig,
):
    """Validate the latest generated Julia code block inside the graph flow."""
    configuration = BaseConfiguration.from_runnable_config(config)
    code_block = state.code_block
    code = code_block.to_string()

    if code_block.is_blank():
        return {"error": False}

    review = _review_generated_code(code=code, configuration=configuration)
    should_validate = True
    user_response = ""
    working_code = code
    if review is not None:
        should_validate = review.should_validate
        user_response = review.user_response
        working_code = review.working_code

    if user_response:
        return {"error": True, "messages": [HumanMessage(content=user_response)]}
    if not should_validate:
        return {"error": False}

    conversation = ValidationConversation(
        original_code=code,
        working_code=working_code,
    )
    if conversation.code_was_edited:
        conversation.messages.append(
            HumanMessage(
                content=(
                    "The code was manually edited to the following. This version will be validated:\n"
                    + wrap_julia_fence(conversation.working_code)
                )
            )
        )

    conversation.working_code = prepare_validation_code(conversation.working_code)
    _run_validation_stages(conversation, configuration)

    if not conversation.has_findings:
        return {"error": False, "messages": conversation.messages}

    conversation.messages.append(_build_validation_feedback(conversation))

    should_fix = True
    user_response = ""
    if configuration.human_interaction.fix_error:
        decision = request_post_validation_review(cli_mode=cli_mode)
        should_fix = decision.should_fix
        user_response = decision.user_response

    if not should_fix:
        conversation.messages.append(
            HumanMessage(content="The code failed, but the user chose to skip fixing it.")
        )
        return {"messages": conversation.messages, "error": False}

    if user_response:
        conversation.messages.append(HumanMessage(content=user_response))

    if conversation.code_was_edited:
        edited_block = parse_julia_code_block(
            conversation.working_code,
            from_markdown=False,
        )
        return {
            "messages": conversation.messages,
            "error": True,
            "code_block": edited_block,
        }
    return {"messages": conversation.messages, "error": True}
