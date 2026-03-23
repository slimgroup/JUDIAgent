"""Lightweight metric plans for paper-friendly JUDI evaluation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricRecommendation:
    name: str
    workflow: str
    rationale: str


@dataclass(frozen=True)
class TaskMetricPlan:
    task_id: str
    workflow: str
    headline: str
    metrics: tuple[MetricRecommendation, ...]


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


TASK_METRIC_PLANS: dict[str, TaskMetricPlan] = {
    "basic_2d_forward": TaskMetricPlan(
        task_id="basic_2d_forward",
        workflow="forward_modeling",
        headline="Use a cheap sanity-check bundle for simple 2D acoustic forward modeling.",
        metrics=METRIC_CATALOG["forward_modeling"],
    ),
    "rtm_basic": TaskMetricPlan(
        task_id="rtm_basic",
        workflow="imaging",
        headline="Use image-space metrics that quickly indicate whether RTM produced a meaningful migration result.",
        metrics=METRIC_CATALOG["imaging"],
    ),
    "fwi_basic": TaskMetricPlan(
        task_id="fwi_basic",
        workflow="fwi",
        headline="Use optimization-progress metrics that show whether the inversion loop is numerically healthy.",
        metrics=METRIC_CATALOG["fwi"],
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


def get_task_metric_plan(task_id: str) -> TaskMetricPlan | None:
    return TASK_METRIC_PLANS.get(task_id)


def recommend_metrics(text: str, task_id: str = "") -> tuple[MetricRecommendation, ...]:
    if task_id:
        plan = get_task_metric_plan(task_id)
        if plan is not None:
            return plan.metrics

    workflow = infer_workflow_family(text)
    if workflow is None:
        return ()
    return METRIC_CATALOG.get(workflow, ())


def format_metric_plan(task_id: str = "", text_hint: str = "") -> str:
    """Return a compact, paper-friendly description of the metric bundle."""
    plan = get_task_metric_plan(task_id) if task_id else None
    metrics = plan.metrics if plan is not None else recommend_metrics(text_hint, task_id=task_id)
    if not metrics:
        return ""

    headline = plan.headline if plan is not None else "Use lightweight task-aware metrics to assess scientific quality."
    lines = [headline]
    for metric in metrics:
        lines.append(f"- {metric.name}: {metric.rationale}")
    return "\n".join(lines)
