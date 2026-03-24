"""
Retrieve Julia function docstrings via the Language Server protocol.

The driver script ``judiagent_doc_lookup.jl`` inspects user code
for function references and emits their documentation in a structured format.
This module parses that output back into Python objects.
"""

from __future__ import annotations

from judiagent.cli import colorscheme, print_to_console
from judiagent.julia.execution_bridge import execute_julia_script


def _extract_docstring_sections(raw_output: str) -> tuple[list[str], str]:
    """
    Parse the structured text emitted by ``judiagent_doc_lookup.jl``.

    Expected markers in *raw_output*:
      - ``FUNCTION NAMES:`` followed by a Julia array literal
      - ``DOCUMENTATION`` followed by the docstring body

    Returns ``(function_names, documentation_text)``.
    """
    lines = raw_output.splitlines()
    try:
        fn_header = lines.index("FUNCTION NAMES:") + 1
        doc_header = lines.index("DOCUMENTATION") + 1
    except ValueError:
        return [], ""

    names_blob = "".join(lines[fn_header : doc_header - 1]).strip()
    if names_blob.startswith("[") and names_blob.endswith("]"):
        names_blob = names_blob[1:-1]
    names = [n.strip().strip('"') for n in names_blob.split(",") if n.strip()]

    docstring = "\n".join(lines[doc_header:]).strip()
    return names, docstring


def fetch_julia_docstrings(code: str) -> tuple[list[str], str]:
    """
    Run the documentation-extraction driver on *code* and return
    ``(function_names, documentation_text)``.
    """
    try:
        stdout, _stderr, _return_code = execute_julia_script(
            code=code, driver_script="judiagent_doc_lookup.jl"
        )
        names, docstring = _extract_docstring_sections(stdout)

        if names:
            names = [n for n in names if n != "String[]"]
        else:
            print_to_console(
                text="No function documentation found!",
                title="Docstring Retriever",
                border_style=colorscheme.error,
            )
        return names, docstring

    except Exception as exc:
        print_to_console(
            text=f"Error retrieving function documentation: {exc}",
            title="Docstring Retriever",
            border_style=colorscheme.error,
        )
        return [], ""


def fetch_docstrings_for_functions(
    func_names: list[str],
) -> tuple[list[str], str]:
    """
    Convenience wrapper: build synthetic Julia code that references each
    function in *func_names*, then retrieve their docstrings.
    """
    synthetic_code = "\n".join(f"{fn}();" for fn in func_names)

    print_to_console(
        text="Retrieving documentation for: " + ", ".join(func_names),
        title="Docstring Retriever",
        border_style=colorscheme.message,
    )
    return fetch_julia_docstrings(synthetic_code)
