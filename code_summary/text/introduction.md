# Introduction

## 1. Scientific Motivation

Wave-equation-based seismic computing requires more than syntactically correct code. A usable script must usually encode a coherent scientific workflow: a physical model, an acquisition geometry, a source description, one or more wave-equation operators, and diagnostics or outputs appropriate to the task. This makes seismic coding assistance different from generic software engineering assistance. In practice, many failure cases are not mere parser or runtime failures. Instead, code may execute while still being scientifically incomplete, misleading, or misaligned with the intended modeling, imaging, or inversion objective.

JUDI.jl provides a powerful abstraction layer for seismic modeling and inversion, but it still expects users to know how to compose the right operators, data structures, and workflow stages. Large language models can help with code generation, but naive prompting is not enough. Domain-specific APIs are easy to misuse, Julia syntax can be confused with Python, and apparently valid code can omit important scientific ingredients such as the imaging objective, the starting model, or quality-control diagnostics.

## 2. Problem Statement

The goal of JUDIAgent is not simply to autocomplete Julia. The goal is to map a user request such as “write a basic RTM example” or “set up a simple FWI workflow” into a workflow that is both:

1. **Executable**: the code should lint, run, and produce a meaningful artifact.
2. **Scientifically adequate**: the workflow should contain the ingredients expected for the requested seismic task.

This motivates a scientific coding agent rather than a generic coding assistant.

## 3. Main Idea

JUDIAgent addresses this problem with three design choices.

1. **Retrieval-grounded generation**. The agent is encouraged to retrieve JUDI examples and documentation before generating task-specific Julia.
2. **Dual validation**. Generated code is checked first for correctness and then for domain quality.
3. **Task-aware metric guidance**. When the workflow corresponds to RTM, FWI, or related tasks, the validation system proposes lightweight metric bundles that can guide debugging, benchmark design, and future learning-based optimization.

## 4. Contributions

A concise way to state the contributions is:

1. **JUDI-specific scientific coding agent**. JUDIAgent is specialized for seismic modeling, imaging, and inversion workflows rather than generic programming tasks.
2. **Dual validation architecture**. The system separates correctness validation from scientific workflow validation.
3. **Domain-quality review**. The validator explicitly checks whether generated code contains the expected ingredients of a credible seismic workflow.
4. **Task-aware metric guidance**. The framework attaches benchmark-style metric bundles to different task families such as forward modeling, migration, and inversion.
5. **Practical foundation for supervision and reward design**. The same metric vocabulary can support future benchmark scoring, structured SFT data, and reward models for RLHF.

## 5. Positioning

The most accurate positioning is that JUDIAgent is a **scientific coding agent for JUDI workflows**. The novelty does not come from merely instantiating a generic evaluator-optimizer loop. The novelty comes from adding domain-aware validation, scientific workflow checks, and metric-guided refinement in a geophysical setting where executable code alone is not sufficient.
