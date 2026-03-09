"""Human-review adapters for the JUDIAgent validation pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PreValidationDecision:
    should_validate: bool
    user_response: str
    working_code: str


@dataclass(frozen=True)
class PostValidationDecision:
    should_fix: bool
    user_response: str


def request_pre_validation_review(code: str, *, cli_mode: bool) -> PreValidationDecision:
    """Ask the user whether and how the generated code should be validated."""
    if cli_mode:
        import judiagent.human_in_the_loop.cli as hitl_cli

        should_validate, user_response, working_code = hitl_cli.response_on_check_code(
            code=code
        )
    else:
        import judiagent.human_in_the_loop.ui as hitl_ui

        should_validate, user_response, working_code = hitl_ui.response_on_check_code(
            code=code
        )

    return PreValidationDecision(
        should_validate=should_validate,
        user_response=user_response,
        working_code=working_code,
    )


def request_post_validation_review(*, cli_mode: bool) -> PostValidationDecision:
    """Ask the user whether the failed code should be fixed or skipped."""
    if cli_mode:
        import judiagent.human_in_the_loop.cli as hitl_cli

        should_fix, user_response = hitl_cli.response_on_error()
    else:
        import judiagent.human_in_the_loop.ui as hitl_ui

        should_fix, user_response = hitl_ui.response_on_error()

    return PostValidationDecision(
        should_fix=should_fix,
        user_response=user_response,
    )
