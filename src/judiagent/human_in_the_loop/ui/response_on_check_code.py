from __future__ import annotations

from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
    HumanResponse,
)
from langgraph.types import interrupt

from judiagent.core.julia_code import unwrap_julia_fence, wrap_julia_fence


def response_on_check_code(code: str) -> tuple[bool, str, str]:
    """UI approval step before JUDIAgent validates generated Julia code."""
    request = HumanInterrupt(  # type: ignore[arg-type]
        action_request=ActionRequest(
            action=(
                "Review the generated Julia code. Accept to validate it, edit to "
                "adjust it, or ignore to skip validation."
            ),
            args={"Code": wrap_julia_fence(code)},
        ),
        config=HumanInterruptConfig(
            allow_ignore=True,
            allow_accept=True,
            allow_respond=True,
            allow_edit=True,
        ),
    )

    human_response: HumanResponse = interrupt([request])[0]
    response_type = human_response.get("type")

    if response_type == "accept":
        return True, "", code
    if response_type == "edit":
        args_dict = human_response.get("args", {}) or {}
        args_dict = args_dict.get("args", {}) if isinstance(args_dict, dict) else {}
        new_code = unwrap_julia_fence(args_dict.get("Code", code))
        return True, "", new_code if new_code.strip() else code
    if response_type == "respond":
        raise NotImplementedError(
            "UI free-form feedback is not yet wired into the validation interrupt."
        )
    if response_type == "ignore":
        return False, "", code
    raise TypeError(f"Interrupt value of type {response_type} is not supported.")
