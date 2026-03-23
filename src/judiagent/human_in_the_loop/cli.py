from __future__ import annotations

from typing import Callable

from langchain_core.documents import Document
from rich.table import Table

import judiagent.cli.cli_utils as utils
from judiagent.cli.cli_colorscheme import colorscheme
from judiagent.core.julia_code import wrap_julia_fence
from judiagent.globals import console
from judiagent.rag.utils import modify_doc_content


def response_on_rag(
    docs: list[Document],
    get_file_source: Callable[[Document], str],
    get_section_path: Callable[[Document], str],
    format_doc: Callable[[Document], str],
    action_name: str = "Review retrieved context",
    edit_julia_file: bool = False,
) -> list[Document]:
    """Interactive CLI review for retrieved RAG context."""
    if not docs:
        console.print("[yellow]No documents retrieved.[/yellow]")
        return docs

    choice = utils.menu_select(
        f"{action_name} - Found {len(docs)} document(s)",
        [
            ("1", "Accept all documents", "+"),
            ("2", "Review and filter documents", "?"),
            ("3", "Reject all documents", "x"),
        ],
        default="1",
    )

    if choice == "1":
        console.print("[green]Accepting all retrieved context[/green]")
        return docs
    if choice == "3":
        console.print("[red]Rejecting all retrieved context[/red]")
        return []

    filtered_docs: list[Document] = []
    console.print("\n[bold]Retrieved Context Review[/bold]")

    for index, doc in enumerate(docs, start=1):
        section_path = get_section_path(doc)
        file_source = get_file_source(doc)
        content = format_doc(doc)
        preview = content if not edit_julia_file else wrap_julia_fence(content.strip())

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        table.add_row("Document", f"{index}/{len(docs)}")
        table.add_row("Source", file_source)
        table.add_row("Section", section_path)
        console.print(f"\n{table}")

        utils.print_to_console(
            text=preview[:500] + "..." if len(preview) > 500 else preview,
            title="Content Preview",
            border_style=colorscheme.human_interaction,
        )

        doc_choice = utils.quick_select(
            [("k", "eep"), ("e", "dit"), ("s", "kip"), ("v", "iew-full")],
            prompt="Action",
            default="k",
        )

        if doc_choice == "v":
            utils.print_to_console(
                text=preview,
                title="Full Context",
                border_style=colorscheme.success,
            )
            doc_choice = utils.quick_select(
                [("k", "eep"), ("e", "dit"), ("s", "kip")],
                prompt="Now",
                default="k",
            )

        if doc_choice == "k":
            filtered_docs.append(doc)
            console.print("[green]Context kept[/green]")
            continue

        if doc_choice == "e":
            new_content = utils.edit_document_content(content, edit_julia_file=edit_julia_file)
            if new_content.strip():
                updated = wrap_julia_fence(new_content.strip()) if edit_julia_file else new_content
                filtered_docs.append(modify_doc_content(doc, updated))
                console.print("[green]Context edited and kept[/green]")
            else:
                console.print("[red]Context removed because it became empty[/red]")
            continue

        console.print("[red]Context skipped[/red]")

    console.print(f"\n[bold]Summary:[/bold] Kept {len(filtered_docs)}/{len(docs)} documents")
    return filtered_docs


def response_on_check_code(code: str) -> tuple[bool, str, str]:
    """Ask how JUDIAgent should handle a generated code block before validation."""
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


def modify_rag_query(query: str, retriever_name: str) -> str:
    """Review or edit a retrieval query before JUDIAgent searches the corpus."""
    utils.print_to_console(
        text=f"**Query:** `{query}`",
        title=f"Review {retriever_name} query",
        border_style=colorscheme.warning,
    )

    choice = utils.menu_select(
        f"Review {retriever_name} query",
        [
            ("1", "Accept query as-is", "+"),
            ("2", "Edit the query", "*"),
            ("3", "Skip retrieval", "-"),
        ],
        default="1",
    )

    if choice == "1":
        console.print(f"[green]Using original query for {retriever_name}[/green]")
        return query
    if choice == "2":
        new_query = utils.edit_document_content(query)
        if new_query.strip():
            console.print(f"[green]Query updated for {retriever_name}[/green]")
            return new_query
        console.print(f"[red]Edited query was empty; keeping the original for {retriever_name}[/red]")
        return query

    console.print(f"[red]Skipping retrieval for {retriever_name}[/red]")
    return ""
