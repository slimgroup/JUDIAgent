from typing import Callable, List

from langchain_core.documents import Document
from rich.table import Table

import judiagent.cli.cli_utils as utils
from judiagent.cli.cli_colorscheme import colorscheme
from judiagent.globals import console
from judiagent.rag.utils import modify_doc_content
from judiagent.utils import wrap_julia_fence as add_julia_context


def response_on_rag(
    docs: List[Document],
    get_file_source: Callable,
    get_section_path: Callable,
    format_doc: Callable,
    action_name: str = "Modify retrieved documents",
    edit_julia_file: bool = False,
) -> List[Document]:
    """
    CLI version of response_on_rag that allows interactive document filtering/editing.

    Args:
       console: Rich console for display
        docs: List of retrieved documents
        get_file_source: Function to get the file source of a document
        get_section_path: Function to get the section path of a document
        format_doc: Function to format a document for display
        action_name: Name of the action for display

    Returns:
        List of documents after user interaction
    """
    if not docs:
        console.print("[yellow]No documents retrieved.[/yellow]")
        return docs

    choice = utils.menu_select(
        f"{action_name} — Found {len(docs)} document(s)",
        [
            ("1", "Accept all documents", "✓"),
            ("2", "Review and filter documents", "📋"),
            ("3", "Reject all documents", "✗"),
        ],
        default="1",
    )

    if choice == "1":
        console.print("[green]✓ Accepting all documents[/green]")
        return docs
    elif choice == "3":
        console.print("[red]✗ Rejecting all documents[/red]")
        return []

    # Interactive review mode
    console.print("\n[bold]Document Review Mode[/bold]")
    filtered_docs = []

    for i, doc in enumerate(docs):
        section_path = get_section_path(doc)
        file_source = get_file_source(doc)
        content = format_doc(doc)
        content_within_julia = (
            content if not edit_julia_file else f"```julia\n{content.strip()}\n```"
        )

        # Create a table to show document info
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        table.add_row("Document", f"{i + 1}/{len(docs)}")
        table.add_row("Source", file_source)
        table.add_row("Section", section_path)

        console.print(f"\n{table}")
        utils.print_to_console(
            text=content_within_julia[:500] + "..."
            if len(content_within_julia) > 500
            else content_within_julia,
            title="Content",
            border_style=colorscheme.human_interaction,
        )

        doc_choice = utils.quick_select(
            [("k", "eep"), ("e", "dit"), ("s", "kip"), ("v", "iew-full")],
            prompt="Action",
            default="k",
        )

        if doc_choice == "k":
            filtered_docs.append(doc)
            console.print("[green]✓ Document kept[/green]")

        elif doc_choice == "s":
            console.print("[red]✗ Document skipped[/red]")

        elif doc_choice == "v":
            utils.print_to_console(
                text=content_within_julia,
                title="Full Document Content",
                border_style=colorscheme.success,
            )

            # Ask again after viewing
            doc_choice = utils.quick_select(
                [("k", "eep"), ("e", "dit"), ("s", "kip")],
                prompt="Now",
                default="k",
            )
            if doc_choice == "k":
                filtered_docs.append(doc)
                console.print("[green]✓ Document kept[/green]")
            elif doc_choice == "e":
                new_content = utils.edit_document_content(
                    content, edit_julia_file=edit_julia_file
                )
                if new_content.strip():
                    if edit_julia_file:
                        new_content = f"```julia\n{new_content.strip()}\n```"
                    filtered_docs.append(modify_doc_content(doc, new_content))
                    console.print("[green]✓ Document edited and kept[/green]")
                else:
                    console.print("[red]✗ Document removed (empty content)[/red]")
            else:  # doc_choice == "s"
                console.print("[red]✗ Document skipped[/red]")

        elif doc_choice == "e":
            new_content = utils.edit_document_content(
                content, edit_julia_file=edit_julia_file
            )
            if new_content.strip():
                if edit_julia_file:
                    new_content = f"```julia\n{new_content.strip()}\n```"
                filtered_docs.append(modify_doc_content(doc, new_content))
                console.print("[green]✓ Document edited and kept[/green]")
            else:
                console.print("[red]✗ Document removed (empty content)[/red]")

    console.print(
        f"\n[bold]Summary:[/bold] Kept {len(filtered_docs)}/{len(docs)} documents"
    )
    return filtered_docs


def response_on_check_code(code: str) -> tuple[bool, str, str]:
    """
    Returns:
        bool: Whether the user wants to check the code or not
        str: Additional feedback to the model
    """
    choice = utils.menu_select(
        "Code detected — what would you like to do?",
        [
            ("1", "Check the code for errors", "▶"),
            ("2", "Give feedback and regenerate", "💬"),
            ("3", "Edit the code manually", "✏"),
            ("4", "Skip code check", "⏭"),
        ],
        default="1",
    )

    if choice == "1":
        console.print("[green]✓ Running code checks[/green]")
        return True, "", code
    elif choice == "2":
        user_input = console.input("[dim]feedback[/dim] [bold gold1]❯[/bold gold1] ")
        if not user_input.strip():  # If the user input is empty
            console.print("[red]✗ User feedback empty[/red]")
            return False, "", code
        console.print("[green]✓ Feedback recieved[/green]")
        return False, user_input, code
    elif choice == "3":
        console.print("\n[bold]Edit Code[/bold]")
        new_code = utils.edit_document_content(code, edit_julia_file=True)

        if new_code.strip():
            utils.print_to_console(
                text=add_julia_context(new_code),
                title="Code update",
                border_style=colorscheme.message,
            )
            console.print("[green]✓ Code updated[/green]")
            return True, "", new_code
        console.print("[red]✓ Code empty. Not updating![/red]")
        return True, "", code

    else:  # choice == "4"
        console.print("[red]✗ Skipping code checks[/red]")
        return False, "", code


def response_on_error() -> tuple[bool, str]:
    """
    Returns:
        bool: Whether the user wants to check the code or not
        str: Additional feedback to the model
    """
    choice = utils.menu_select(
        "⚠ Code check failed — what would you like to do?",
        [
            ("1", "Try to fix the code automatically", "🔧"),
            ("2", "Provide feedback to help fix", "💬"),
            ("3", "Skip code fixing", "⏭"),
        ],
        default="1",
    )

    if choice == "1":
        console.print("[green]✓ Trying to fix code[/green]")
        return True, ""
    elif choice == "2":
        user_input = console.input("[dim]feedback[/dim] [bold gold1]❯[/bold gold1] ")
        if not user_input.strip():  # If the user input is empty
            console.print("[red]✗ User feedback empty[/red]")
            return True, ""
        console.print("[green]✓ Feedback received[/green]")
        return True, user_input
    else:  # choice == "3"
        console.print("[red]✗ Skipping code fix[/red]")
        return False, ""


def modify_rag_query(query: str, retriever_name: str) -> str:
    """
    CLI version of modify_rag_query that allows interactive query modification.

    Args:
        console: Rich console for display
        query: The original query string
        retriever_name: Name of the retriever (e.g., "JUDI.jl", "Fimbul")

    Returns:
        str: The potentially modified query
    """
    utils.print_to_console(
        text=f"**Query:** `{query}`",
        title=f"🔍 Retrieving from {retriever_name}",
        border_style=colorscheme.warning,
    )

    choice = utils.menu_select(
        f"Review {retriever_name} query",
        [
            ("1", "Accept query as-is", "✓"),
            ("2", "Edit the query", "✏"),
            ("3", "Skip retrieval", "⏭"),
        ],
        default="1",
    )

    if choice == "1":
        console.print(f"[green]✓ Using original query for {retriever_name}[/green]")
        return query

    elif choice == "2":
        new_query = utils.edit_document_content(query)

        if new_query.strip():
            console.print(f"[green]✓ Query updated for {retriever_name}[/green]")
            utils.print_to_console(
                text=f"**New Query:** `{new_query.strip()}`",
                title="Updated Query",
                border_style=colorscheme.success,
            )

            return new_query.strip()
        else:
            console.print("[yellow]⚠ Empty query, using original[/yellow]")
            return query
    else:  # choice == "3"
        console.print(f"[red]✗ Skipping {retriever_name} retrieval[/red]")
        return ""  # Return empty string to indicate no query


def modify_terminal_run(command: str) -> tuple[bool, str]:
    """
    Accept, modify, or skip a terminal command.

    Args:
        command: The original terminal command string

    Returns:
        bool: Whether the command is allowed to run
        str: The potentially modified query

    """
    utils.print_to_console(
        text=f"**Command:** `{command}`",
        title="⚡ Terminal Command",
        border_style=colorscheme.warning,
    )

    choice = utils.menu_select(
        "Review terminal command",
        [
            ("1", "Accept and run", "▶"),
            ("2", "Edit command first", "✏"),
            ("3", "Don't run", "✗"),
        ],
        default="3",
    )

    if choice == "1":
        console.print("[green]✓ Running original command[/green]")
        return True, command

    elif choice == "2":
        new_command = utils.edit_document_content(command)

        if new_command.strip():
            console.print("[green]✓ Running updated command[/green]")

            return True, new_command
        else:
            console.print("[yellow]⚠ Empty command. Not running[/yellow]")
            return False, command
    else:  # choice == "3"
        console.print("[red]✗ Skipping running command[/red]")
        return False, command
