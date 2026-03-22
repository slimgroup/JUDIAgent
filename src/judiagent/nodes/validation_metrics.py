"""Lightweight metric recommendations for paper-friendly JUDI evaluation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricRecommendation:
    name: str
    workflow: str
    rationale: str


METRIC_CATALOG: dict[str, tuple[MetricRecommendation, ...]] = {
    "forward_modeling": (
        MetricRecommendation(
            name="trace_energy_consistency",
            workflow="forward_modeling",
            rationale="Check that generated shot records have non-trivial energy and consistent dimensions across sources and receivers.",
        ),
        MetricRecommendation(
            name="runtime_and_memory_budget",
            workflow="forward_modeling",
            rationale="Track whether simple benchmark scripts stay inside an acceptable runtime and memory envelope.",
        ),
    ),
    "imaging": (
        MetricRecommendation(
            name="image_residual_norm",
            workflow="imaging",
            rationale="Use residual or adjoint-image norms as a first-pass proxy for whether the migration result is numerically meaningful.",
        ),
        MetricRecommendation(
            name="illumination_balance",
            workflow="imaging",
            rationale="Measure whether illumination or amplitude compensation avoids obviously under-illuminated regions.",
        ),
    ),
    "fwi": (
        MetricRecommendation(
            name="objective_decrease",
            workflow="fwi",
            rationale="Track whether the inversion objective decreases across the first few iterations.",
        ),
        MetricRecommendation(
            name="gradient_update_norm",
            workflow="fwi",
            rationale="Measure whether gradient and model updates remain finite and non-degenerate.",
        ),
    ),
}


WORKFLOW_HINTS: dict[str, tuple[str, ...]] = {
    "forward_modeling": ("forward", "wavelet", "synthetic data", "born"),
    "imaging": ("rtm", "lsrtm", "migration", "illumination", "image"),
    "fwi": ("fwi", "inversion", "objective", "gradient descent", "nlopt"),
}


def infer_workflow_family(text: str) -> str | None:
    normalized = text.lower()
    for workflow, hints in WORKFLOW_HINTS.items():
        if any(hint in normalized for hint in hints):
            return workflow
    return None


def recommend_metrics(text: str) -> tuple[MetricRecommendation, ...]:
    workflow = infer_workflow_family(text)
    if workflow is None:
        return ()
    return METRIC_CATALOG.get(workflow, ())
