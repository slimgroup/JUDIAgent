"""Backward-compatible CLI exports for JUDIAgent human review flows."""

from __future__ import annotations

import judiagent.cli.cli_utils as utils
from judiagent.cli.cli_colorscheme import colorscheme
from judiagent.globals import console
from judiagent.human_in_the_loop.review_query import modify_rag_query
from judiagent.human_in_the_loop.review_rag import response_on_rag
from judiagent.human_in_the_loop.review_validation import (
    response_on_check_code,
    response_on_error,
)


def modify_terminal_run(command: str) -> tuple[bool, str]:
    """Review a shell command before JUDIAgent executes it from the CLI path."""
    utils.print_to_console(
        text=f"**Command:** `{command}`",
        title="Review terminal command",
        border_style=colorscheme.warning,
    )

    choice = utils.menu_select(
        "Choose how to handle this command",
        [
            ("1", "Run the command as-is", ">"),
            ("2", "Edit the command first", "*"),
            ("3", "Skip this command", "-"),
        ],
        default="1",
    )

    if choice == "1":
        console.print("[green]Running the original command[/green]")
        return True, command
    if choice == "2":
        new_command = utils.edit_document_content(command)
        if new_command.strip():
            console.print("[green]Running the edited command[/green]")
            return True, new_command.strip()
        console.print("[red]Edited command was empty; skipping execution[/red]")
        return False, command

    console.print("[red]Skipping command execution[/red]")
    return False, command


__all__ = [
    "modify_terminal_run",
    "modify_rag_query",
    "response_on_check_code",
    "response_on_error",
    "response_on_rag",
]
