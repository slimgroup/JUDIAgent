# Limitations

## 1. Validation is stronger than generation, but still heuristic

The domain-quality review is intentionally lightweight. It checks for workflow ingredients and task-specific expectations, but it does not yet compute a full physics-grounded score for every task. Passing the domain review therefore means “scientifically plausible and structured,” not “numerically optimal” or “publication-grade result.”

## 2. Metric bundles are guidance, not yet full reward functions

The current metric bundles are promising because they define structured evaluation targets, but they are still a mixture of:

- measurable quantities, such as objective decrease or runtime budget
- workflow checks, such as artifact presence or stage completeness
- qualitative proxies, such as operator-role clarity

This is useful for benchmark design and future learning, but not yet a complete reward function by itself.

## 3. Runtime cost remains important

Even with lightweight validation, JUDI and Julia runtime overhead still matters. Package loading, runtime validation, and heavier modeling tasks can make iterative repair expensive. This is especially relevant on shared systems such as PACE.

## 4. Retrieval quality bounds generation quality

If the retrieval layer surfaces weak or only loosely related examples, the LLM may still produce suboptimal code. The system is retrieval-grounded, not retrieval-perfect.

## 5. The autonomous agent is more flexible than guaranteed

The autonomous ReAct path is useful for open-ended assistance, but it is intentionally less constrained than the iterative validation path. For paper claims about validated scientific workflows, the iterative path is the safer center of gravity.

## 6. The framework is not yet a full scientific benchmark platform

`benchmarks/prompts.yaml` now gives a stronger benchmark schema, but the repo still does not provide a complete automated evaluation harness with reference outputs, numerical baselines, or end-to-end score aggregation. That would be an important next step.
