"""Julia code parsing and transformation helpers for JUDIAgent."""

from __future__ import annotations

import re

from judiagent.state import JuliaCodeBlock

_JULIA_FENCE_RE = re.compile(r"```julia\s*([\s\S]*?)```", re.IGNORECASE)
_INDENTED_CODE_LINE_RE = re.compile(
    r"^(?:using\s+|import\s+|#|[A-Za-z_][A-Za-z0-9_]*\s*=|println\(|print\(|for\s+|if\s+|while\s+|function\s+|end\b|[A-Za-z_][A-Za-z0-9_]*\()"
)


def _score_julia_block(block: str) -> tuple[int, int, int, int]:
    """Heuristically score candidate Julia blocks by how script-like they are."""
    lines = [line.rstrip() for line in block.splitlines()]
    non_empty = [line for line in lines if line.strip()]
    non_comment = [line for line in non_empty if not line.lstrip().startswith("#")]
    using_lines = [line for line in non_comment if line.lstrip().startswith("using ")]
    code_like = [line for line in non_empty if _INDENTED_CODE_LINE_RE.match(line.lstrip())]
    executable = [
        line
        for line in code_like
        if not line.lstrip().startswith(("using ", "import ", "#"))
    ]
    return (len(executable), len(code_like), len(non_comment), len(using_lines))


def _extract_indented_julia(response: str) -> str:
    """Fallback parser for markdown-style indented code blocks."""
    blocks: list[str] = []
    current: list[str] = []

    for raw_line in response.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        is_code = False
        if line.startswith("  ") or line.startswith("\t"):
            candidate = line[2:] if line.startswith("  ") else line.lstrip("\t")
            if not stripped or _INDENTED_CODE_LINE_RE.match(candidate.lstrip()):
                is_code = True
                current.append(candidate.rstrip())
        if not is_code:
            if current:
                block = "\n".join(current).strip()
                if block:
                    blocks.append(block)
                current = []
    if current:
        block = "\n".join(current).strip()
        if block:
            blocks.append(block)

    if not blocks:
        return ""

    ranked = [(index, block, _score_julia_block(block)) for index, block in enumerate(blocks)]
    _, best_block, best_score = max(ranked, key=lambda item: (item[2], item[0]))
    if best_score[1] == 0:
        return ""
    return best_block


def extract_fenced_julia(response: str) -> str:
    """Pull Julia source from the most script-like markdown fence.

    Models sometimes emit multiple Julia snippets, for example a debug probe,
    a main solution, and then a tiny follow-up example. Validation should run
    the primary solution block rather than concatenating alternatives or
    blindly picking the final fenced snippet.
    """
    blocks = [match.strip() for match in _JULIA_FENCE_RE.findall(response) if match.strip()]
    if blocks:
        ranked = [
            (index, block, _score_julia_block(block))
            for index, block in enumerate(blocks)
        ]
        _, best_block, _ = max(
            ranked,
            key=lambda item: (item[2], item[0]),
        )
        return best_block
    return _extract_indented_julia(response)


def parse_julia_code_block(
    response: str,
    from_markdown: bool = True,
) -> JuliaCodeBlock:
    """Parse Julia source into a ``JuliaCodeBlock``."""
    raw = extract_fenced_julia(response) if from_markdown else response
    if not raw:
        return JuliaCodeBlock(imports="", body="")

    import_lines: list[str] = []
    code_lines: list[str] = []
    for line in raw.splitlines():
        if line.strip().startswith("using "):
            import_lines.append(line.strip())
        else:
            code_lines.append(line)

    return JuliaCodeBlock(
        imports="\n".join(import_lines),
        body="\n".join(code_lines).strip(),
    )


def render_code_as_markdown(code: JuliaCodeBlock) -> str:
    """Render a ``JuliaCodeBlock`` as a markdown Julia fence."""
    if code.imports == "" and code.body == "":
        return ""
    parts = ["```julia"]
    if code.imports:
        parts.append(code.imports)
        parts.append("")
    if code.body:
        parts.append(code.body)
    parts.append("```")
    return "\n".join(parts)


def wrap_julia_fence(code: str) -> str:
    """Wrap raw Julia code in a markdown fence."""
    return f"```julia\n{code}\n```"


def unwrap_julia_fence(code: str) -> str:
    """Strip markdown fence markers from Julia code."""
    return code.replace("```julia\n", "").replace("\n```", "")


def _split_by_bracket_balance(code: str) -> list[str]:
    """Split Julia source into logical blocks based on bracket balance."""
    blocks: list[str] = []
    current: list[str] = []
    depth = {"(": 0, "[": 0, "{": 0}
    openers = set("([{")
    closers = {")": "(", "]": "[", "}": "{"}

    for line in code.splitlines():
        if not line.strip() and not current:
            continue
        for char in line:
            if char in openers:
                depth[char] += 1
            elif char in closers:
                depth[closers[char]] -= 1
        current.append(line)

        if all(value == 0 for value in depth.values()):
            blocks.append("\n".join(current))
            current = []

    if current:
        blocks.append("\n".join(current))
    return blocks


def strip_plotting_code(code: str) -> str:
    """Remove GLMakie imports and plotting-related statements."""
    plot_tokens = [
        "fig",
        "plt",
        "ax",
        "scatter",
        "Colorbar",
        "Axis",
        "lines",
        "plot_reservoir",
        "plot_well_results",
        "plot_reservoir_measurables",
        "plot_reservoir_simulation_result",
        "plot_well!",
        "myplot",
        "plot_cell_data",
        "plot_mesh_edges",
        "plot_mesh",
        "plot_co2_inventory",
        "println",
    ]

    cleaned: list[str] = []
    for block in _split_by_bracket_balance(code):
        stripped = block.strip()
        if stripped.startswith("using"):
            block = re.sub(r",?\s*GLMakie,?", "", block)
            block = re.sub(r"using\s*,", "using ", block)
            block = re.sub(r",\s*;", ";", block)
            if re.match(r"^\s*using\s*;?\s*$", block):
                continue
            if not block.strip():
                continue
        if stripped == "fig":
            continue
        if any(token in stripped for token in plot_tokens):
            continue
        cleaned.append(block)
    return "\n".join(cleaned)


def _shorten_first_positional(code: str, target_fns: list[str]) -> str:
    """Append ``[1:1]`` to the first argument of each target call."""
    for function_name in target_fns:
        pattern = rf"({function_name}\s*\()\s*([^,)\s]+)(.*?\))"

        def _replace(match: re.Match[str]) -> str:
            return f"{match.group(1)}{match.group(2)}[1:1]{match.group(3)}"

        code = re.sub(pattern, _replace, code, flags=re.DOTALL)
    return code


def _narrow_named_arg(code: str, arg_name: str, target_fns: list[str]) -> str:
    """Replace a named argument with its first slice inside target calls."""
    for function_name in target_fns:
        pattern = rf"({function_name}\s*\(.*?)(\b{arg_name}\b)(.*?\))"

        def _replace(match: re.Match[str]) -> str:
            return f"{match.group(1)}{arg_name}[1:1]{match.group(3)}"

        code = re.sub(pattern, _replace, code, flags=re.DOTALL)
    return code


def reduce_simulation_steps(code: str) -> str:
    """Rewrite simulation calls to use a single timestep for faster validation."""
    sim_fns = ["simulate_reservoir"]
    original = code

    for label in ("case", "dt", "timesteps"):
        code = _narrow_named_arg(code, label, sim_fns)

    if code == original:
        code = _shorten_first_positional(code, sim_fns)
    return code


def normalize_julia_imports(code: str) -> str:
    """Prepend ``Pkg.activate`` when Fimbul and GLMakie are both imported."""
    if "Fimbul" not in code or "GLMakie" not in code:
        return code
    return 'using Pkg; Pkg.activate(".");\n' + code


def detect_package_install_attempt(block: JuliaCodeBlock) -> bool:
    """Return ``True`` if the code block tries to modify packages."""
    forbidden = ["using Pkg", "Pkg.add", "Pkg.update", "Pkg.instantiate"]
    combined = block.imports + "\n" + block.body
    return any(token in combined for token in forbidden)
