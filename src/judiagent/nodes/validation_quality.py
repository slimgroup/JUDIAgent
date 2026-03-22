"""JUDI-specific scientific evaluation for generated Julia workflows."""

from __future__ import annotations

import re

from judiagent.configuration import DomainValidation
from judiagent.nodes.validation_metrics import recommend_metrics
from judiagent.nodes.validation_models import ValidationFinding


IMAGING_HINTS = (
    "rtm",
    "lsrtm",
    "fwi",
    "migration",
    "imaging",
    "adjoint",
    "gradient",
    "objective",
    "misfit",
)

QUALITY_CATEGORIES: dict[str, tuple[str, ...]] = {
    "model setup": (
        "model(",
        "velocity",
        "slowness",
        "n =",
        "d =",
        "o =",
    ),
    "acquisition geometry": (
        "geometry(",
        "src",
        "rec",
        "shot",
        "receiver",
    ),
    "wave physics or operator": (
        "judimodeling",
        "forward",
        "born",
        "modeling",
    ),
    "imaging or inversion objective": (
        "rtm",
        "lsrtm",
        "fwi",
        "gradient",
        "misfit",
        "objective",
        "image",
    ),
    "quality diagnostics": (
        "snr",
        "semblance",
        "coherence",
        "illumination",
        "artifact",
        "residual",
        "norm(",
        "plot(",
        "imshow",
        "heatmap",
        "savefig",
    ),
}


def _normalize_code(code: str) -> str:
    return re.sub(r"\s+", " ", code.strip().lower())


def should_run_domain_validation(code: str, settings: DomainValidation) -> bool:
    """Decide whether the JUDI-specific evaluator should run."""
    if settings.mode == "off":
        return False
    if settings.mode == "strict":
        return True

    normalized = _normalize_code(code)
    return any(token in normalized for token in IMAGING_HINTS)


def run_domain_validation(
    code: str,
    settings: DomainValidation,
) -> ValidationFinding | None:
    """
    Score whether generated code looks scientifically complete for imaging tasks.

    This evaluator does not replace numerical image-quality metrics. Instead, it
    enforces a JUDI-specific workflow contract: imaging/inversion code should
    include model setup, geometry, wave-physics operators, the imaging objective,
    and at least one quality-diagnostic hook.
    """
    if not should_run_domain_validation(code, settings):
        return None

    normalized = _normalize_code(code)
    matched_categories: list[str] = []
    missing_categories: list[str] = []
    for category, markers in QUALITY_CATEGORIES.items():
        if any(marker in normalized for marker in markers):
            matched_categories.append(category)
        else:
            missing_categories.append(category)

    score = len(matched_categories) / len(QUALITY_CATEGORIES)
    if score >= settings.minimum_score:
        return None

    matched_text = ", ".join(matched_categories) if matched_categories else "none"
    missing_text = ", ".join(missing_categories)
    recommended_metrics = recommend_metrics(code)
    metric_lines = ""
    if recommended_metrics:
        metric_lines = "\n- Recommended lightweight metrics: " + ", ".join(
            metric.name for metric in recommended_metrics
        )
    report = (
        "## JUDI domain-quality review:\n"
        "The code passes syntax/runtime checks but does not yet look like a complete "
        "seismic imaging or inversion workflow.\n"
        f"- Scientific readiness score: {score:.2f}\n"
        f"- Present categories: {matched_text}\n"
        f"- Missing categories: {missing_text}\n"
        f"{metric_lines}\n"
        "Please revise the solution so it includes the missing scientific pieces "
        "or explicitly explains why they are intentionally omitted."
    )
    return ValidationFinding(
        stage="domain_quality",
        report=report,
        metadata={
            "score": score,
            "minimum_score": settings.minimum_score,
            "matched_categories": matched_categories,
            "missing_categories": missing_categories,
            "recommended_metrics": [metric.name for metric in recommended_metrics],
        },
    )
