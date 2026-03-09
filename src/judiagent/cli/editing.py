"""Editor and file-writing helpers used by JUDIAgent's CLI review loops."""

from __future__ import annotations

import os
import subprocess
import tempfile

from rich.prompt import Prompt

from judiagent.globals import console
from judiagent.state import JuliaCodeBlock


def edit_document_content(original_content: str, edit_julia_file: bool = False) -> str:
    """Open text in the user's editor and return the edited result."""
    file_suffix = ".jl" if edit_julia_file else ".md"

    try:
        with tempfile.NamedTemporaryFile(
            mode="w+",
            suffix=file_suffix,
            delete=False,
        ) as handle:
            handle.write(original_content)
            handle.flush()
            editor = os.environ.get("EDITOR", "vim")

            try:
                subprocess.run([editor, handle.name], check=True)
                with open(handle.name, "r") as edited_file:
                    edited_content = edited_file.read()
                os.unlink(handle.name)
                return edited_content
            except subprocess.CalledProcessError:
                console.print(
                    f"[red]Error opening editor '{editor}'. Using original content.[/red]"
                )
                os.unlink(handle.name)
                return original_content
            except FileNotFoundError:
                console.print(
                    f"[red]Editor '{editor}' not found. Set EDITOR to a valid editor.[/red]"
                )
                os.unlink(handle.name)
                return original_content
    except Exception as exc:
        console.print(f"[red]Error with external editor: {exc}[/red]")
        return original_content


def save_code_to_file(code_block: JuliaCodeBlock) -> None:
    """Save a Julia code block to a user-selected file path."""
    console.print("\n[bold bright_cyan]Save Julia Code[/bold bright_cyan]")
    filename = Prompt.ask("Enter filename", default="generated_code.jl")

    if not filename.endswith(".jl"):
        filename += ".jl"

    try:
        if os.path.exists(filename):
            overwrite = Prompt.ask(
                f"File '{filename}' exists. Overwrite?",
                choices=["y", "n"],
                default="n",
            )
            if overwrite.lower() != "y":
                console.print("[yellow]File save cancelled.[/yellow]")
                return

        with open(filename, "w") as handle:
            if code_block.imports:
                handle.write(code_block.imports + "\n\n")
            handle.write(code_block.body)

        console.print(f"[green]Saved code to '{filename}'.[/green]")
    except Exception as exc:
        console.print(f"[red]Error saving file: {exc}[/red]")
