from __future__ import annotations

import judiagent.cli.cli_utils as utils
from judiagent.cli.cli_colorscheme import colorscheme
from judiagent.core.julia_code import wrap_julia_fence
from judiagent.globals import console


def response_on_check_code(code: str) -> tuple[bool, str, str]:
    """Ask how JUDIAgent should handle generated Julia before validation."""
    choice = utils.menu_select(
        "Generated Julia code detected - choose the next step",
        [
            ("1", "Run validation checks", ">"),
            ("2", "Give feedback and regenerate", "?"),
            ("3", "Edit the code manually", "*"),
            ("4", "Skip validation", "-"),
        ],
        default="1",
    )

    if choice == "1":
        console.print("[green]Running validation checks[/green]")
        return True, "", code
    if choice == "2":
        user_input = console.input("[dim]feedback[/dim] [bold gold1]>[/bold gold1] ")
        if not user_input.strip():
            console.print("[red]Feedback was empty[/red]")
            return False, "", code
        console.print("[green]Feedback received[/green]")
        return False, user_input, code
    if choice == "3":
        console.print("\n[bold]Edit Generated Code[/bold]")
        new_code = utils.edit_document_content(code, edit_julia_file=True)
        if new_code.strip():
            utils.print_to_console(
                text=wrap_julia_fence(new_code),
                title="Updated Code",
                border_style=colorscheme.message,
            )
            console.print("[green]Code updated[/green]")
            return True, "", new_code
        console.print("[red]Edited code was empty; keeping the original[/red]")
        return True, "", code

    console.print("[red]Skipping validation[/red]")
    return False, "", code


def response_on_error() -> tuple[bool, str]:
    """Ask how JUDIAgent should react after validation fails."""
    choice = utils.menu_select(
        "Validation failed - choose the next step",
        [
            ("1", "Let JUDIAgent try to repair it", ">"),
            ("2", "Provide extra feedback", "?"),
            ("3", "Skip automatic repair", "-"),
        ],
        default="1",
    )

    if choice == "1":
        console.print("[green]Retrying with automated repair[/green]")
        return True, ""
    if choice == "2":
        user_input = console.input("[dim]feedback[/dim] [bold gold1]>[/bold gold1] ")
        if not user_input.strip():
            console.print("[red]Feedback was empty[/red]")
            return True, ""
        console.print("[green]Feedback received[/green]")
        return True, user_input

    console.print("[red]Skipping automatic repair[/red]")
    return False, ""
