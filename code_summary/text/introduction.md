# Introduction

## 1. Scientific Motivation

Wave-equation-based seismic computing is an unusually demanding target for coding assistance. A script that is merely syntactically valid is often still unusable in practice if it omits the model parameterization, acquisition geometry, source description, or operator composition required by the intended scientific task. In seismic workflows, many important failure cases are therefore not parser failures or import errors. Instead, code may execute while still being scientifically incomplete, misleading, or insufficient for modeling, migration, or inversion.

JUDI.jl is a powerful abstraction layer for seismic computing in Julia, but effective use of JUDI still requires familiarity with task-specific workflow structure. Users must know how to construct models, define source and receiver geometries, assemble modeling and Jacobian operators, manage physical units, and produce quality-control artifacts that make the result interpretable. Large language models can help with this process, but naive prompting is not enough. Domain-specific APIs are easy to misuse, Julia syntax can be confused with Python syntax, and superficially plausible code can still omit essential workflow ingredients such as the migration model, the inversion objective, or appropriate diagnostics.

## 2. Problem Statement

The goal of JUDIAgent is not simply to autocomplete Julia code. The goal is to map natural-language requests such as “write a basic RTM example” or “set up a small FWI workflow” into code that is both:

1. **Executable**: the script should import correctly, run in the target JUDI environment, and produce a meaningful artifact.
2. **Scientifically adequate**: the script should include the ingredients expected for the requested seismic task.

This distinction matters because generic code-generation benchmarks rarely test for scientific completeness. A generated workflow can pass syntax and runtime checks while still failing the underlying domain task. In computational geophysics, that gap is large enough that correctness-only evaluation gives an overly optimistic picture of agent quality.

## 3. Main Idea

JUDIAgent addresses this problem through three linked design choices.

1. **Retrieval-grounded generation.** The agent is encouraged to retrieve JUDI examples and documentation before synthesizing task-specific Julia code, reducing hallucinated API usage and helping generation follow the operator vocabulary and coding patterns of the underlying library.
2. **Dual validation.** Generated code is first checked for executable correctness and then passed to a domain-quality reviewer that evaluates whether the workflow is scientifically complete for the inferred task family.
3. **Task-aware metric guidance.** The validation system associates lightweight metric bundles with different task families, such as trace-energy consistency for forward modeling, image residual norm and illumination balance for migration, and objective decrease for inversion.

Together, these choices shift the system from “LLM writes code” toward “LLM generates a candidate scientific workflow that must survive both software and domain checks.”

## 4. Why A Scientific Coding Agent Instead Of A Generic Assistant

JUDIAgent is best understood as a **scientific coding agent for JUDI workflows** rather than a generic programming assistant. The novelty is not simply the presence of a repair loop or evaluator. The novelty lies in introducing domain-aware validation criteria that are meaningful in seismic computing. For example, an RTM prompt should not only yield a migrated image array. It should also expose a true or observed data path, a migration model, an imaging operator, and image-oriented artifacts that can be inspected after runtime success.

This framing also helps position the system experimentally. The key question is not whether the agent directly produces the best possible subsurface image. The more grounded question is whether it produces executable, scientifically structured, and inspectable JUDI workflows under realistic interactive constraints.

## 5. Contributions

A concise statement of contributions is:

1. **JUDI-specific scientific coding agent.** JUDIAgent is specialized for seismic modeling, imaging, and inversion workflows rather than generic programming tasks.
2. **Dual validation architecture.** The framework separates executable correctness from scientific workflow adequacy.
3. **Domain-quality review.** The reviewer explicitly checks whether generated code contains the expected ingredients of credible forward-modeling, migration, and inversion workflows.
4. **Task-aware metric guidance.** The system attaches benchmark-style metrics and evaluation hooks to task families, enabling more structured repair and evaluation.
5. **Practical benchmark and paper artifacts.** The current repo already demonstrates validated forward-modeling and compact RTM case studies with saved data products and publication-style figures.

## 6. Scope Of The Present Paper

This paper focuses on the iterative validated agent because it provides the clearest scientific guarantee: code is not only generated, but executed and reviewed for domain adequacy. We do not claim that JUDIAgent solves seismic imaging or inversion better than specialized numerical methods. Instead, we claim that it improves the reliability of code generation for scientific workflows in a domain where executable correctness alone is insufficient.

## 7. Paper Roadmap

The remainder of the paper can be organized as follows. Section 2 presents the agent architecture, including retrieval, correctness validation, and domain-quality review. Section 3 describes the benchmark prompt catalog and evaluation framing. Section 4 reports qualitative and quantitative findings, including validated case studies in forward modeling and RTM. Section 5 discusses limitations, especially the gap between validation-scale success and high-end scientific image quality, and outlines future directions for benchmark-driven training and reward modeling.
