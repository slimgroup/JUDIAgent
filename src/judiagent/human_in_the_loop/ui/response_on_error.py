from __future__ import annotations

from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
    HumanResponse,
)
from langgraph.types import interrupt


def response_on_error() -> tuple[bool, str]:
    """UI approval step after JUDIAgent validation fails."""
    request = HumanInterrupt(  # type: ignore[arg-type]
        action_request=ActionRequest(
            action=(
                "Validation failed. Accept to let JUDIAgent attempt a repair, "
                "ignore to skip repair, or respond with extra guidance."
            ),
            args={},
        ),
        config=HumanInterruptConfig(
            allow_ignore=True,
            allow_accept=True,
            allow_respond=True,
            allow_edit=False,
        ),
    )

    human_response: HumanResponse = interrupt([request])[0]
    response_type = human_response.get("type")

    if response_type == "accept":
        return True, ""
    if response_type == "respond":
        raise NotImplementedError(
            "UI free-form repair feedback is not yet wired into the validation interrupt."
        )
    if response_type == "ignore":
        return False, ""
    raise TypeError(f"Interrupt value of type {response_type} is not supported.")
