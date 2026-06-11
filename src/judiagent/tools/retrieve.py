"""RAG retrieval and documentation lookup tools."""

from __future__ import annotations

import subprocess
from functools import partial
from typing import Annotated, cast

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, InjectedToolArg, tool
from pydantic import BaseModel, Field

import judiagent.rag.retrieval as retrieval
from judiagent.cli import colorscheme, print_to_console
from judiagent.configuration import PROJECT_ROOT, BaseConfiguration, cli_mode
from judiagent.core.documents import get_document_source
from judiagent.julia import fetch_docstrings_for_functions
from judiagent.rag.catalog import RAG_CATALOG
from judiagent.rag.chunking.examples import format_example_chunk, format_example_context

# -----------------------------------------------------------------------
# Generic RAG tool factory
# -----------------------------------------------------------------------

def _build_retrieval_tool(
    tool_name: str,
    doc_key: str,
    doc_label: str,
    input_schema: type[BaseModel],
) -> BaseTool:
    """
    Factory that creates a domain-specific RAG retrieval tool.
    """

    @tool(
        tool_name,
        args_schema=input_schema,
        description=(
            f"Search for full examples from the {doc_label} documentation. "
            f"Use this when answering Julia code questions about {doc_label}."
        ),
    )
    def _retrieval_tool(
        query: str, config: Annotated[RunnableConfig, InjectedToolArg]
    ) -> str:
        configuration = BaseConfiguration.from_runnable_config(config)

        if configuration.human_interaction.rag_query:
            if cli_mode:
                from judiagent.human_in_the_loop.cli import modify_rag_query
            else:
                from judiagent.human_in_the_loop.ui import modify_rag_query
            query = modify_rag_query(query, doc_label)
        else:
            print_to_console(
                text=f"**Query:** `{query}`",
                title=f"Searching {doc_label} examples",
                border_style=colorscheme.message,
            )

        if not query.strip():
            return "The query is empty."

        with retrieval.make_retriever(
            config=config,
            spec=RAG_CATALOG[doc_key]["examples"],
            retrieval_params=retrieval.RetrievalPlan(
                search_type=configuration.examples_search_type,
                search_kwargs=configuration.examples_search_kwargs,
            ),
        ) as rag_retriever:
            retrieved = cast(list[Document], rag_retriever.invoke(query))

        if configuration.human_interaction.retrieved_examples:
            def _section_path(doc: Document) -> str:
                heading = doc.metadata.get("heading", "")
                return heading if heading else get_document_source(doc)

            if cli_mode:
                from judiagent.human_in_the_loop.cli import response_on_rag
                retrieved = response_on_rag(
                    docs=retrieved,
                    get_file_source=get_document_source,
                    get_section_path=_section_path,
                    format_doc=partial(format_example_chunk, within_julia_context=False),
                    action_name=f"Filter {doc_label} examples",
                    edit_julia_file=True,
                )
            else:
                from judiagent.human_in_the_loop.ui import response_on_rag
                retrieved = response_on_rag(
                    retrieved,
                    get_file_source=get_document_source,
                    get_section_path=_section_path,
                    format_doc=format_example_chunk,
                    action_name=f"Filter {doc_label} examples",
                )

        formatted = format_example_context(retrieved)
        return formatted if formatted else "(empty)"

    return _retrieval_tool


# -----------------------------------------------------------------------
# Concrete retrieval tools
# -----------------------------------------------------------------------

class JudiQueryInput(BaseModel):
    query: str = Field(description="Semantic query for JUDI.jl examples and docs.")


search_judi_examples = _build_retrieval_tool(
    tool_name="search_judi_examples",
    doc_key="judi",
    doc_label="JUDI.jl",
    input_schema=JudiQueryInput,
)


class ImageGatherQueryInput(BaseModel):
    query: str = Field(description="Semantic query for ImageGather.jl examples and docs.")


search_imagegather_examples = _build_retrieval_tool(
    tool_name="search_imagegather_examples",
    doc_key="imagegather",
    doc_label="ImageGather.jl",
    input_schema=ImageGatherQueryInput,
)

# -----------------------------------------------------------------------
# Function documentation lookup
# -----------------------------------------------------------------------

class FunctionDocInput(BaseModel):
    function_names: list[str] = Field(
        description="Julia function names whose docstrings should be retrieved."
    )


@tool(
    "lookup_function_docs",
    description="Retrieve Julia function documentation (signatures, usage, docstrings).",
    args_schema=FunctionDocInput,
)
def lookup_function_docs(
    function_names: list[str],
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> str:
    _ = config
    _, docstrings = fetch_docstrings_for_functions(func_names=function_names)
    return docstrings or "No documentation found for the given function names."


# -----------------------------------------------------------------------
# Codebase search (grep)
# -----------------------------------------------------------------------

class CodeSearchInput(BaseModel):
    query: str = Field(
        description="Keyword or regex pattern to search for in files."
    )
    file_pattern: str | None = Field(
        default=None,
        description="Optional glob pattern to restrict the search (e.g. '*.jl').",
    )
    use_regex: bool | None = Field(
        default=False,
        description="Treat the query as a regex pattern.",
    )


@tool(
    "search_codebase",
    description=(
        "Keyword search across JUDI.jl and ImageGather.jl docs and examples. "
        "Returns up to 20 matches with file paths and line numbers."
    ),
    args_schema=CodeSearchInput,
)
def search_codebase(
    query: str,
    file_pattern: str | None = None,
    use_regex: bool | None = False,
) -> str:
    try:
        search_roots = [
            str(PROJECT_ROOT / "rag" / "judi"),
            str(PROJECT_ROOT / "rag" / "imagegather"),
        ]
        cmd = ["grep", "-r", "-n"]
        cmd.append("-E" if use_regex else "-F")

        if file_pattern:
            cmd.extend(["--include", file_pattern])
        else:
            cmd.extend(["--include=*.jl", "--include=*.md"])

        cmd.append(query)
        cmd.extend(search_roots)
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if proc.stdout:
            raw_lines = proc.stdout.strip().split("\n")[:20]
            results: list[str] = []
            for line in raw_lines:
                parts = line.split(":", 2)
                if len(parts) == 3:
                    results.append(f"File: {parts[0]}, Line {parts[1]}: {parts[2]}")
                else:
                    results.append(line)

            display = f"Found {len(results)} matches:\n\n" + "```text\n" + "\n\n".join(results) + "\n```"
            print_to_console(
                text=display[:500] + "...",
                title=f"Search: {query}",
                border_style=colorscheme.message,
            )
            return f"Found {len(results)} matches:\n" + "\n\n".join(results)

        return f"No matches for: {query}"
    except Exception as exc:
        return f"Search error: {exc}"
