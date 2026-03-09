"""Panel-based console rendering helpers for JUDIAgent output."""

from __future__ import annotations

from rich.markdown import Markdown
from rich.panel import Panel

from judiagent.globals import console


def print_to_console(
    text: str,
    title: str = "JUDIAgent",
    border_style: str = "steel_blue3",
    panel_kwargs: dict | None = None,
    with_markdown: bool = True,
):
    """Display content inside a consistently styled Rich panel."""
    panel_kwargs = (panel_kwargs or {}).copy()
    panel_kwargs.setdefault("border_style", border_style)
    panel_kwargs.setdefault("title", f"[bold bright_cyan]{title}[/bold bright_cyan]")
    content = Markdown(text) if with_markdown else text
    console.print(Panel.fit(content, **panel_kwargs))
