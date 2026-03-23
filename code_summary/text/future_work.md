# Future Work

## 1. Reward modeling and RLHF

The current framework is a good candidate for future SFT and RLHF work. The most promising direction is to treat the existing metric vocabulary as **reward primitives** rather than as a single monolithic reward.

A practical reward design could combine:

- correctness reward
  - lint pass
  - runtime pass
  - structured artifact presence
- domain-quality reward
  - workflow completeness
  - correct operator and objective usage
  - geometry and model consistency
- task-aware metric reward
  - image residual norm for migration tasks
  - objective decrease for inversion tasks
  - gradient update norm for FWI stability

This would support both supervised fine-tuning data generation and later preference or reward modeling.

## 2. Benchmark harness

The next natural step is to turn the benchmark prompt catalog into a runnable benchmark suite with:

- benchmark-specific execution drivers
- score aggregation
- reference artifacts where possible
- ablations on retrieval, dual validation, and human-in-the-loop settings

## 3. Persistent Julia execution

A persistent Julia runtime or pooled worker model could reduce validation latency and make iterative repair much more practical for heavier scientific workflows.

## 4. Better metric realization

Some current metric bundles are still conceptual. Future work should connect them to explicit numeric routines, for example:

- illumination maps for imaging tasks
- objective traces for inversion tasks
- geometry coverage diagnostics for acquisition tasks
- artifact-presence checks for workflow completion

## 5. Learning from accepted workflows

Another strong direction is to store validated successful workflows and use them as high-quality supervision data. This could improve both retrieval quality and later model fine-tuning.

## 6. Publication-facing positioning

For the paper, the framework should be positioned as a scientific coding agent with domain-aware validation, not as a claim to have solved autonomous survey optimization or closed-loop acquisition design in the strongest mathematical sense. That narrower positioning is both more accurate and more defensible.
