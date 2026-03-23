# Figure: Domain-Guided Seismic Workflow Loop

**Suggested use:** secondary conceptual figure, not necessarily a main figure

The old experimental-design loop should be reframed. The current codebase is better described as a **domain-guided seismic workflow loop** than as a strict survey-optimization loop.

## What the figure should emphasize now

- user intent or benchmark task
- JUDI workflow construction
- correctness validation
- domain-quality evaluation
- task-aware metric guidance
- iterative repair

## Recommended caption

**Figure Z.** Domain-guided seismic workflow loop. JUDIAgent does not merely execute generated Julia. It evaluates whether the workflow contains the scientific ingredients expected for modeling, migration, or inversion, and returns metric-aware guidance for iterative refinement.
