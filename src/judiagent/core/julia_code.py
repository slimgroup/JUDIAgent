"""Julia code parsing and transformation helpers for JUDIAgent."""

from __future__ import annotations

import re

from judiagent.state import JuliaCodeBlock

_JULIA_FENCE_RE = re.compile(r"```julia\s*([\s\S]*?)```", re.IGNORECASE)


def extract_fenced_julia(response: str) -> str:
    """Pull Julia source from one or more markdown fences."""
    blocks = [match.strip() for match in _JULIA_FENCE_RE.findall(response) if match.strip()]
    return "\n\n".join(blocks)


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
