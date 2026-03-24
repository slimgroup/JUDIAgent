"""Helpers for persisting validated JUDIAgent runs to disk."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Sequence

from langchain_core.messages import BaseMessage, HumanMessage

from judiagent.core.messages import get_message_text

_SKIP_PREFIXES = (
    "# Validation issues",
    "The code was manually edited",
)

_OUTPUT_PATH_RE = re.compile(r'["\'](outputs/(?:figures|data)/[^"\']+)["\']')


def _prepare_output_layout(base_directory: str | Path) -> dict[str, Path]:
    root = Path(base_directory)
    layout = {
        "root": root,
        "scripts": root / "scripts",
        "figures": root / "outputs" / "figures",
        "data": root / "outputs" / "data",
    }
    for path in (layout["scripts"], layout["figures"], layout["data"]):
        path.mkdir(parents=True, exist_ok=True)
    return layout


def extract_output_paths(code: str) -> list[str]:
    """Return output file paths referenced in Julia code."""
    return sorted({match.group(1) for match in _OUTPUT_PATH_RE.finditer(code)})


def infer_primary_user_prompt(messages: Sequence[BaseMessage]) -> str:
    """Pick the most informative human-authored task prompt from the turn history."""
    candidates: list[str] = []
    for message in messages:
        if not isinstance(message, HumanMessage):
            continue
        text = get_message_text(message).strip()
        if not text or text.startswith(_SKIP_PREFIXES):
            continue
        candidates.append(text)

    if not candidates:
        return "validated_judiagent_run"

    return max(candidates, key=len)


def build_task_slug(prompt: str, code: str) -> str:
    """Derive a compact task slug from outputs, code, or the user prompt."""
    output_paths = extract_output_paths(code)
    if output_paths:
        figure_paths = [p for p in output_paths if "/figures/" in p]
        preferred = figure_paths[0] if figure_paths else output_paths[0]
        stem = Path(preferred).stem.lower()
        for suffix in ("_shot", "_figure", "_plot", "_data"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        return stem or Path(preferred).stem.lower()

    if "ricker_wavelet" in code:
        return "ricker_wavelet"
    if "judiModeling" in code and "plot" in code.lower():
        return "forward_modeling"

    tokens = re.findall(r"[A-Za-z0-9]+", prompt.lower())
    if not tokens:
        return "validated_judiagent_run"
    return "_".join(tokens[:8])[:80].strip("_") or "validated_judiagent_run"


def persist_validated_run(
    *,
    base_directory: str | Path,
    messages: Sequence[BaseMessage],
    code: str,
    agent_mode: str,
    model_name: str,
) -> tuple[Path, Path]:
    """Persist the validated Julia script and a metadata sidecar to disk."""
    layout = _prepare_output_layout(base_directory)
    prompt = infer_primary_user_prompt(messages)
    task_slug = build_task_slug(prompt, code)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    script_path = layout["scripts"] / f"{task_slug}_{timestamp}.jl"
    metadata_path = layout["data"] / f"{task_slug}_{timestamp}_run.json"

    script_path.write_text(code.rstrip() + "\n", encoding="utf-8")

    metadata = {
        "task_slug": task_slug,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "agent_mode": agent_mode,
        "model_name": model_name,
        "workspace": str(layout["root"]),
        "user_prompt": prompt,
        "script_path": str(script_path.relative_to(layout["root"])),
        "metadata_path": str(metadata_path.relative_to(layout["root"])),
        "declared_output_paths": extract_output_paths(code),
        "code_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
    }

    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return script_path, metadata_path
