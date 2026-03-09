from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
    HumanResponse,
)
from langgraph.types import interrupt

from judiagent.core.julia_code import (
    unwrap_julia_fence as remove_julia_context,
    wrap_julia_fence as add_julia_context,
)


def response_on_check_code(code: str) -> tuple[bool, str, str]:
    """
    Returns:
        bool: Whether the user wants to check the code or not
        str: Additional feedback to the model
    """

    # Prepare the human-in-the-loop UI request
    request = HumanInterrupt(  # type: ignore
        action_request=ActionRequest(
            action="Accept or modify the generated code to check it. Ignore to not check it. Respond to provide feedback and regenerate response",
            args={"Code": add_julia_context(code)},
        ),
        config=HumanInterruptConfig(
            allow_ignore=True,
            allow_accept=True,
            allow_respond=True,
            allow_edit=True,
        ),
    )

    # Wait for the user's response from the UI
    human_response: HumanResponse = interrupt([request])[0]
    response_type = human_response.get("type")

    if response_type == "accept":
        return True, "", code
    elif response_type == "edit":
        args_dics = human_response.get("args", {}) or {}  # type: ignore[union-attr]
        args_dics = args_dics.get("args", {}) if isinstance(args_dics, dict) else {}

        # Get the updated code
        new_code = args_dics.get("Code", code)
        new_code = remove_julia_context(new_code)
        if new_code.strip():
            code = new_code
        return True, "", code
    elif response_type == "respond":
        raise NotImplementedError(
            f"Interrupt value of type {response_type} is not yet implemented."
        )
    elif response_type == "ignore":
        return False, "", code
    else:
        raise TypeError(f"Interrupt value of type {response_type} is not supported.")
