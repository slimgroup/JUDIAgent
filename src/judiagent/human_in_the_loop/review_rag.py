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
            new_content = utils.edit_document_content(
                content,
                edit_julia_file=edit_julia_file,
            )
            if new_content.strip():
                updated = (
                    wrap_julia_fence(new_content.strip())
                    if edit_julia_file
                    else new_content
                )
                filtered_docs.append(modify_doc_content(doc, updated))
                console.print("[green]Context edited and kept[/green]")
            else:
                console.print("[red]Context removed because it became empty[/red]")
            continue

        console.print("[red]Context skipped[/red]")

    console.print(
        f"\n[bold]Summary:[/bold] Kept {len(filtered_docs)}/{len(docs)} documents"
    )
    return filtered_docs
