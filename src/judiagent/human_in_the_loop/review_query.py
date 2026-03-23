from __future__ import annotations

import judiagent.cli.cli_utils as utils
from judiagent.cli.cli_colorscheme import colorscheme
from judiagent.globals import console


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
        console.print(
            f"[red]Edited query was empty; keeping the original for {retriever_name}[/red]"
        )
        return query

    console.print(f"[red]Skipping retrieval for {retriever_name}[/red]")
    return ""
