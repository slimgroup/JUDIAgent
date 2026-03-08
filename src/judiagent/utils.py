"""
Shared utility functions for code parsing, message handling, and Julia code transformations.
"""

from __future__ import annotations

import os
import re
from dataclasses import asdict
from typing import List, Sequence, Union

from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import BaseMessage, trim_messages
from langchain_core.runnables import Runnable

from judiagent.state import JuliaCodeBlock, AgentState


# ---------------------------------------------------------------------------
# Message content extraction
# ---------------------------------------------------------------------------

def get_message_text(msg: BaseMessage) -> str:
    """Extract plain-text content from a LangChain message (handles str, dict, list)."""
    content = msg.content
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", "")
    fragments = [
        c if isinstance(c, str) else (c.get("text") or "")
        for c in content
    ]
    return "".join(fragments).strip()


# ---------------------------------------------------------------------------
# Julia code block extraction
# ---------------------------------------------------------------------------

_JULIA_FENCE_RE = re.compile(r"```julia\s*([\s\S]*?)```", re.IGNORECASE)


def _extract_fenced_julia(response: str) -> str:
    """
    Pull Julia source from one or more markdown fences in *response*.
    Multiple blocks are joined chronologically.
    """
    blocks = [m.strip() for m in _JULIA_FENCE_RE.findall(response) if m.strip()]
    return "\n\n".join(blocks)


def parse_julia_code_block(
    response: str, from_markdown: bool = True
) -> JuliaCodeBlock:
    """
    Parse Julia source from a response string into a :class:`JuliaCodeBlock`.

    When *from_markdown* is ``True`` (default), the response is expected to
    contain markdown-fenced Julia blocks.  When ``False``, the entire
    *response* is treated as raw Julia code.
    """
    raw = _extract_fenced_julia(response) if from_markdown else response
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


def retrieve_latest_code_block(state: AgentState) -> JuliaCodeBlock:
    """Return the :class:`JuliaCodeBlock` from the most recent AI/human message."""
    last = state.messages[-1]
    if last.type in ("ai", "human"):
        text = get_message_text(last)
    else:
        text = ""
    return parse_julia_code_block(text)


# ---------------------------------------------------------------------------
# Code formatting helpers
# ---------------------------------------------------------------------------

def render_code_as_markdown(code: JuliaCodeBlock) -> str:
    """Render a :class:`JuliaCodeBlock` as a markdown Julia fence."""
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


# ---------------------------------------------------------------------------
# Model provider helpers
# ---------------------------------------------------------------------------

def resolve_provider_and_model(fully_qualified: str) -> tuple[str, str]:
    """Split ``'provider:model-name'`` into ``(provider, model_name)``."""
    provider, model = fully_qualified.split(":", maxsplit=1)
    return provider, model


def instantiate_chat_model(fully_qualified: str) -> BaseChatModel:
    """
    Instantiate a LangChain chat model from a ``provider:model`` string.

    Supports openai, anthropic, deepseek, and ollama providers.
    """
    provider, model_name = resolve_provider_and_model(fully_qualified)

    common_kwargs = {"temperature": 0.1}

    if provider == "ollama" and model_name == "qwen3:14b":
        common_kwargs["reasoning"] = True

    try:
        return init_chat_model(model_name, model_provider=provider, **common_kwargs)
    except Exception as exc:
        hints = {
            "openai": "Ensure the model name is correct and OPENAI_API_KEY is set.",
            "anthropic": "Ensure the model name is correct and ANTHROPIC_API_KEY is set.",
            "deepseek": "Ensure the DEEPSEEK_API_KEY is set.",
            "ollama": "Ensure the model is pulled and Ollama is running.",
        }
        raise ValueError(
            f"Failed to load {provider} model '{model_name}': {exc}. "
            f"{hints.get(provider, '')}"
        ) from exc


# ---------------------------------------------------------------------------
# File & document helpers
# ---------------------------------------------------------------------------

def read_text_lines(file_path: str) -> List[str]:
    """Load non-empty, stripped lines from a text file."""
    if not file_path:
        raise ValueError("File path cannot be empty.")
    file_path = str(file_path)
    try:
        with open(file_path, "r") as fh:
            return [line.strip() for line in fh if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(
            f"File not found: {file_path}  (cwd={os.getcwd()})"
        )
    except IOError as exc:
        raise IOError(f"Could not read {file_path}: {exc}") from exc


def get_document_source(doc: Document) -> str:
    """Return the 'source' metadata field from a LangChain Document."""
    return doc.metadata.get("source", "Unknown Document")


def deduplicate_documents(chunks: List[Document]) -> List[Document]:
    """Remove duplicate Documents by content hash."""
    seen: set[str] = set()
    unique: list[Document] = []
    for doc in chunks:
        key = doc.page_content.strip()
        if key not in seen:
            seen.add(key)
            unique.append(doc)
    return unique


def trim_document_source(source: str, anchor: str = "rag") -> str:
    """Strip the path prefix up to and including ``/<anchor>/``."""
    idx = source.find(f"/{anchor}/")
    if idx != -1:
        return source[idx + len(f"/{anchor}/"):]
    return source


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def state_as_dict(state: AgentState, exclude: List[str] | None = None) -> dict:
    """Serialise an :class:`AgentState` to dict, optionally dropping keys."""
    d = asdict(state)
    for key in (exclude or []):
        d.pop(key, None)
    return d


def recent_tool_message(messages: List, lookback: int = 2, verbose: bool = False):
    """Return the most recent ToolMessage within the last *lookback* messages."""
    for msg in messages[-lookback:]:
        if msg.type == "tool":
            if verbose:
                msg.pretty_print()
            return msg
    return None


# ---------------------------------------------------------------------------
# Julia code transformations
# ---------------------------------------------------------------------------

def compact_message_history(
    messages: Sequence[BaseMessage],
    model: Union[BaseChatModel, Runnable[LanguageModelInput, BaseMessage]],
) -> Sequence[BaseMessage]:
    """Trim a message list to fit within a 40 000-token budget."""
    return trim_messages(
        messages,
        max_tokens=40000,
        strategy="last",
        token_counter=model,
        include_system=False,
        allow_partial=True,
    )


def _split_by_bracket_balance(code: str) -> list[str]:
    """
    Split Julia source into logical blocks based on bracket balance.
    Multi-line expressions are kept together.
    """
    blocks: list[str] = []
    current: list[str] = []
    depth = {"(": 0, "[": 0, "{": 0}
    openers = set("([{")
    closers = {")": "(", "]": "[", "}": "{"}

    for line in code.splitlines():
        if not line.strip() and not current:
            continue
        for ch in line:
            if ch in openers:
                depth[ch] += 1
            elif ch in closers:
                depth[closers[ch]] -= 1
        current.append(line)

        if all(v == 0 for v in depth.values()):
            blocks.append("\n".join(current))
            current = []

    if current:
        blocks.append("\n".join(current))
    return blocks


def strip_plotting_code(code: str) -> str:
    """
    Remove GLMakie imports and plotting-related statements from Julia code.
    """
    plot_tokens = [
        "fig", "plt", "ax", "scatter", "Colorbar", "Axis", "lines",
        "plot_reservoir", "plot_well_results", "plot_reservoir_measurables",
        "plot_reservoir_simulation_result", "plot_well!", "myplot",
        "plot_cell_data", "plot_mesh_edges", "plot_mesh", "plot_co2_inventory",
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
        if any(tok in stripped for tok in plot_tokens):
            continue
        cleaned.append(block)
    return "\n".join(cleaned)


def _shorten_first_positional(code: str, target_fns: List[str]) -> str:
    """Append ``[1:1]`` to the first argument of each *target_fn* call."""
    for fn in target_fns:
        pattern = rf"({fn}\s*\()\s*([^,)\s]+)(.*?\))"

        def _repl(m: re.Match) -> str:
            return f"{m.group(1)}{m.group(2)}[1:1]{m.group(3)}"

        code = re.sub(pattern, _repl, code, flags=re.DOTALL)
    return code


def _narrow_named_arg(code: str, arg_name: str, target_fns: List[str]) -> str:
    """Replace ``arg_name`` with ``arg_name[1:1]`` inside *target_fn* calls."""
    for fn in target_fns:
        pattern = rf"({fn}\s*\(.*?)(\b{arg_name}\b)(.*?\))"

        def _repl(m: re.Match) -> str:
            return f"{m.group(1)}{arg_name}[1:1]{m.group(3)}"

        code = re.sub(pattern, _repl, code, flags=re.DOTALL)
    return code


def reduce_simulation_steps(code: str) -> str:
    """
    Rewrite simulation calls to use a single timestep for faster validation.
    """
    sim_fns = ["simulate_reservoir"]
    original = code

    for label in ("case", "dt", "timesteps"):
        code = _narrow_named_arg(code, label, sim_fns)

    if code == original:
        code = _shorten_first_positional(code, sim_fns)
    return code


def normalize_julia_imports(code: str) -> str:
    """Prepend ``Pkg.activate(\".\")`` when Fimbul + GLMakie are both imported."""
    if "Fimbul" not in code or "GLMakie" not in code:
        return code
    return 'using Pkg; Pkg.activate(".");\n' + code


def detect_package_install_attempt(block: JuliaCodeBlock) -> bool:
    """Return ``True`` if the code block tries to install or modify packages."""
    forbidden = ["using Pkg", "Pkg.add", "Pkg.update", "Pkg.instantiate"]
    combined = block.imports + "\n" + block.body
    return any(tok in combined for tok in forbidden)
