from __future__ import annotations

from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
    HumanResponse,
)
from langgraph.types import interrupt


def response_on_file_write(file_path: str) -> tuple[bool, str]:
    """Ask whether JUDIAgent may overwrite or rename an output file."""
    request = HumanInterrupt(  # type: ignore[arg-type]
        action_request=ActionRequest(
            action=(
                "JUDIAgent wants to write a file, but the path already exists. "
                "Accept to overwrite it, ignore to skip writing, or edit to provide a new path."
            ),
            args={"Filepath": file_path},
        ),
        config=HumanInterruptConfig(
            allow_ignore=True,
            allow_accept=True,
            allow_respond=False,
            allow_edit=True,
        ),
    )

    human_response: HumanResponse = interrupt([request])[0]
    response_type = human_response.get("type")

    if response_type == "accept":
        return True, file_path
    if response_type == "edit":
        args_dict = human_response.get("args", {}) or {}
        args_dict = args_dict.get("args", {}) if isinstance(args_dict, dict) else {}
        return True, args_dict.get("Filepath", file_path)
    if response_type == "ignore":
        return False, file_path
    raise TypeError(f"Interrupt value of type {response_type} is not supported.")
