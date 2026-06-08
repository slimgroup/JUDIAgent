"""Utilities for loading the JUDIAgent benchmark prompt catalog."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = REPOSITORY_ROOT / "benchmarks" / "prompts.yaml"


@dataclass(frozen=True)
class BenchmarkTask:
    """A single prompt-catalog entry used for agent evaluation."""

    id: str
    category: str
    difficulty: str
    prompt: str
    required_components: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    metric_bundle: tuple[str, ...]


def _require_sequence(raw: dict[str, Any], key: str) -> tuple[str, ...]:
    value = raw.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Benchmark task {raw.get('id', '<unknown>')!r} has invalid {key!r}")
    return tuple(value)


def _task_from_mapping(raw: dict[str, Any]) -> BenchmarkTask:
    required_strings = ("id", "category", "difficulty", "prompt")
    missing = [key for key in required_strings if not isinstance(raw.get(key), str)]
    if missing:
        raise ValueError(f"Benchmark task is missing string fields: {', '.join(missing)}")

    return BenchmarkTask(
        id=raw["id"],
        category=raw["category"],
        difficulty=raw["difficulty"],
        prompt=raw["prompt"],
        required_components=_require_sequence(raw, "required_components"),
        acceptance_criteria=_require_sequence(raw, "acceptance_criteria"),
        metric_bundle=_require_sequence(raw, "metric_bundle"),
    )


def load_benchmark_tasks(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, BenchmarkTask]:
    """Load and validate benchmark tasks from the YAML prompt catalog."""
    with path.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)

    if not isinstance(catalog, dict):
        raise ValueError(f"Benchmark catalog must be a mapping: {path}")

    tasks: dict[str, BenchmarkTask] = {}
    for group_name, group_tasks in catalog.items():
        if not isinstance(group_tasks, list):
            raise ValueError(f"Benchmark group {group_name!r} must contain a task list")
        for raw_task in group_tasks:
            if not isinstance(raw_task, dict):
                raise ValueError(f"Benchmark group {group_name!r} contains a non-mapping task")
            task = _task_from_mapping(raw_task)
            if task.id in tasks:
                raise ValueError(f"Duplicate benchmark task id: {task.id}")
            tasks[task.id] = task
    return tasks


def get_benchmark_task(task_id: str, path: Path = DEFAULT_CATALOG_PATH) -> BenchmarkTask:
    """Return one benchmark task by id."""
    tasks = load_benchmark_tasks(path)
    try:
        return tasks[task_id]
    except KeyError as exc:
        raise KeyError(f"Unknown benchmark task id: {task_id}") from exc
