"""Menu-style terminal interactions for JUDIAgent's human-in-the-loop flows."""

from __future__ import annotations

from rich.panel import Panel
from rich.text import Text

from judiagent.globals import console


def quick_select(
    options: list[tuple[str, str]],
    prompt: str = "Choice",
    default: str = "",
) -> str:
    """Compact inline selector used in human-in-the-loop prompts."""
    valid_keys = [key for key, _ in options]
    option_line = " [dim]•[/dim] ".join(
        f"[bold bright_cyan]{key}[/bold bright_cyan] [bright_white]{label}[/bright_white]"
        for key, label in options
    )
    console.print(f"\n[bold slate_blue1]{prompt}[/bold slate_blue1]")
    console.print(option_line)

    while True:
        choice = console.input("[bold bright_cyan]>[/bold bright_cyan] ").strip().lower()
        if not choice and default:
            return default
        if choice in valid_keys:
            return choice
        console.print(
            "[bold orange1]Invalid choice.[/bold orange1] "
            f"[bright_white]Expected one of: {', '.join(valid_keys)}[/bright_white]"
        )


def menu_select(
    title: str,
    options: list[tuple[str, str, str]],
    default: str = "1",
) -> str:
    """Render a focused selection panel and return the chosen key."""
    menu_lines: list[str] = []
    valid_choices: list[str] = []

    for key, label, icon in options:
        valid_choices.append(key)
        glyph = icon or ">"
        menu_lines.append(
            f"[bright_cyan]{glyph}[/bright_cyan] "
            f"[bold bright_white][{key}][/bold bright_white] {label}"
        )

    panel = Panel(
        Text.from_markup("\n".join(menu_lines)),
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="deep_sky_blue4",
        padding=(0, 2),
    )
    console.print(panel)

    while True:
        choice = console.input("[bold bright_cyan]>[/bold bright_cyan] ").strip()
        if not choice:
            return default
        if choice in valid_choices:
            return choice
        console.print(
            "[bold orange1]Invalid choice.[/bold orange1] "
            f"[bright_white]Expected one of: {', '.join(valid_choices)}[/bright_white]"
        )
