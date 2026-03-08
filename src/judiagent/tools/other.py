"""General-purpose file I/O and workspace tools."""

from __future__ import annotations

import os

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from rich.panel import Panel

from judiagent.cli import colorscheme, print_to_console
from judiagent.configuration import cli_mode
from judiagent.globals import console


# -----------------------------------------------------------------------
# Read file
# -----------------------------------------------------------------------

class ReadFileInput(BaseModel):
    file_path: str = Field(description="Absolute path of the file to read.")
    read_full_file: bool = Field(description="If True, ignore line range and read everything.")
    start_line: int = Field(description="0-based start line (inclusive).")
    end_line: int = Field(description="0-based end line (inclusive).")


@tool(
    "read_from_file",
    description="Read file contents, optionally within a line range.",
    args_schema=ReadFileInput,
)
def read_from_file(
    file_path: str,
    read_full_file: bool,
    start_line: int,
    end_line: int,
) -> str:
    try:
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        with open(file_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()

        if read_full_file:
            lo, hi = 0, len(lines)
        else:
            lo = max(0, start_line)
            hi = min(len(lines), end_line + 1)

        if lo >= len(lines):
            return f"Start line {start_line} exceeds file length ({len(lines)} lines)."

        numbered = [f"{i:4d}: {line.rstrip()}" for i, line in enumerate(lines[lo:hi], start=lo)]
        preview = "\n".join(numbered)

        print_to_console(
            text=f"```text\n{preview[:500]}...\n```",
            title=f"Read: {file_path}",
            border_style=colorscheme.message,
        )
        return (
            f"File: {file_path} (lines {lo}–{hi - 1} of {len(lines)} total)\n"
            + "\n".join(numbered)
        )
    except Exception as exc:
        return f"Error reading file: {exc}"


# -----------------------------------------------------------------------
# Write file
# -----------------------------------------------------------------------

class WriteFileInput(BaseModel):
    file_path: str = Field(description="Absolute path of the file to write.")
    content: str = Field(description="Content to write.")


@tool(
    "write_to_file",
    description="Write text content to a file (with overwrite confirmation in CLI).",
    args_schema=WriteFileInput,
)
def write_to_file(file_path: str, content: str) -> str:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                existing = fh.read()

            if cli_mode:
                old_preview = existing[:300] + ("..." if len(existing) > 300 else "")
                new_preview = content[:300] + ("..." if len(content) > 300 else "")
                console.print(
                    Panel.fit(
                        f"[bold yellow]File exists: {file_path}[/bold yellow]\n\n"
                        f"[bold]Current ({len(existing)} chars):[/bold]\n[dim]{old_preview}[/dim]\n\n"
                        f"[bold]New ({len(content)} chars):[/bold]\n[dim]{new_preview}[/dim]",
                        title="Overwrite Confirmation",
                        border_style="yellow",
                    )
                )
                answer = console.input(
                    "\n[bold red]Overwrite? (y/n): [/bold red]"
                ).strip().lower()
                if answer not in ("y", "yes"):
                    print_to_console(
                        text=f"Write cancelled: {file_path}",
                        title="File Writer",
                        border_style=colorscheme.warning,
                    )
                    return f"Write cancelled by user: {file_path}"
            else:
                from judiagent.human_in_the_loop.ui import response_on_file_write
                approved, file_path = response_on_file_write(file_path)
                if not approved:
                    return f"Write cancelled by user: {file_path}"
        except Exception as exc:
            print_to_console(
                text=f"Warning reading existing file: {exc}",
                title="File Writer",
                border_style=colorscheme.warning,
            )

    try:
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        msg = f"Written to {file_path}"
        print_to_console(text=msg, title="File Writer", border_style=colorscheme.success)
        return msg
    except Exception as exc:
        msg = f"Error writing {file_path}: {exc}"
        print_to_console(text=msg, title="File Writer", border_style=colorscheme.error)
        return msg


# -----------------------------------------------------------------------
# CWD / directory listing
# -----------------------------------------------------------------------

@tool("fetch_working_directory", description="Return the current working directory.")
def fetch_working_directory() -> str:
    return os.getcwd()


class DirectoryListingInput(BaseModel):
    directory_path: str = Field(description="Absolute path of the directory to list.")
    recursive: bool = Field(description="True for recursive listing, False for top-level only.")


@tool(
    "list_files_in_directory",
    description="List files and subdirectories. Supports recursive and top-level modes.",
    args_schema=DirectoryListingInput,
)
def list_files_in_directory(directory_path: str, recursive: bool) -> str:
    try:
        if not os.path.isdir(directory_path):
            return f"ERROR: {directory_path} is not a valid directory."

        entries: list[str] = []
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                for f in files:
                    entries.append(f"[FILE] {os.path.join(root, f)}")
                for d in dirs:
                    entries.append(f"[DIR]  {os.path.join(root, d)}/")
        else:
            for item in os.listdir(directory_path):
                full = os.path.join(directory_path, item)
                tag = "[DIR] " if os.path.isdir(full) else "[FILE]"
                entries.append(f"{tag} {full}")

        if not entries:
            return f"No files in {directory_path}"

        entries.sort()
        mode = "recursive" if recursive else "top-level"
        return f"Contents of {directory_path} ({mode}):\n" + "\n".join(entries)
    except Exception as exc:
        return f"ERROR: {exc}"
