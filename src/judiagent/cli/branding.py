"""Terminal branding views for the JUDIAgent CLI."""

from __future__ import annotations

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from judiagent.globals import console


def show_startup_screen():
    """Display the JUDIAgent startup panel with a distinct visual identity."""
    wordmark = Text(
        "JUDIAgent",
        style="bold bright_cyan",
        justify="center",
    )
    wordmark.stylize("bold", 0, len("JUDIAgent"))
    subtitle = Text(
        "Seismic coding copilot for JUDI.jl",
        style="italic bright_white",
        justify="center",
    )
    horizon = Text.from_markup(
        "[steel_blue3]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[/steel_blue3]\n"
        "[cyan]====[/cyan] "
        "[bright_black]layered velocity model / acquisition workspace[/bright_black] "
        "[cyan]====[/cyan]"
    )
    prompt = Text.from_markup(
        "[bright_cyan]>[/bright_cyan] [bright_white]Ask about JUDI.jl, geometry, modeling, inversion, or debugging.[/bright_white]\n"
        "[dim]Type q to quit.[/dim]"
    )

    panel = Panel(
        Group(
            Align.center(wordmark),
            Align.center(subtitle),
            Align.center(horizon),
            Align.center(prompt),
        ),
        title="[bold cyan]JUDIAgent Console[/bold cyan]",
        border_style="deep_sky_blue4",
        padding=(1, 2),
        expand=True,
    )
    console.print(panel)
    console.print()
