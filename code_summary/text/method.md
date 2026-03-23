# Method

## 1. Overview

JUDIAgent maps a natural-language seismic task description to validated Julia code through a retrieval, generation, and validation loop. The system is implemented as a LangGraph-based agent stack around JUDI.jl. Its central methodological claim is that scientific code generation for seismic workflows should be evaluated at two levels:

1. **Correctness level**: can the code be parsed, linted, and executed?
2. **Scientific workflow level**: does the code encode the expected ingredients of the requested task?

## 2. Agent Modes

JUDIAgent exposes two complementary agent modes.

### 2.1 Iterative agent

The iterative agent is the stricter path. It is designed for focused coding tasks where the final output should be a validated code artifact. The loop is:

`user request -> retrieval/planning -> code generation -> correctness validation -> domain review -> finalize or refine`

### 2.2 Autonomous ReAct agent

The autonomous agent is more open-ended. It can call retrieval, execution, linting, shell, and file tools in a multi-step reasoning loop. This mode is useful for exploratory assistance and tool-oriented workflows, but it is less tightly centered on producing a single mandatory validated code block.

## 3. Retrieval-grounded code generation

The generation process is grounded in JUDI examples and documentation. The retrieval layer searches example code, API usage patterns, and local code context. This helps reduce hallucinated API use and keeps generation closer to the actual JUDI operator vocabulary.

The operational principle is simple: **retrieve before synthesizing**. In practice, this means the agent is encouraged to inspect JUDI examples and documentation before proposing a seismic workflow.

## 4. Dual validation

### 4.1 Stage 1: correctness validation

Correctness validation checks whether the generated Julia is executable in a practical sense. This stage includes:

- import normalization and lightweight preprocessing
- static checks and lint feedback
- runtime execution checks
- structured error formatting for iterative repair

A candidate that fails here is not yet worth scientific review.

### 4.2 Stage 2: domain-quality review

If runtime validation succeeds, the code is then evaluated as a scientific workflow. The domain validator checks whether the generated script includes the ingredients expected for the task family. Depending on the task, these ingredients may include:

- model definition
- acquisition geometry
- source or wavelet specification
- forward, imaging, or inversion operators
- objective or misfit terms
- output artifacts or quality diagnostics

This second stage is crucial because many weak solutions are executable but scientifically incomplete.

## 5. Task-aware metric guidance

The domain review is coupled to a metric recommendation layer. JUDIAgent associates different task families with lightweight metric bundles. Examples include:

- **forward modeling**: trace energy consistency, runtime and memory budget
- **RTM / imaging**: image residual norm, illumination balance
- **FWI**: objective decrease, gradient update norm
- **geometry tasks**: coverage and spacing checks
- **workflow tasks**: stage completeness and final artifact presence

These metrics are not yet a full numerical benchmark suite, but they provide a structured language for evaluating outputs. They are useful for benchmark design now and can evolve into supervision or reward signals later.

## 6. Human-in-the-loop control

JUDIAgent supports optional human review at several intervention points:

- modifying RAG queries
- filtering retrieved context
- reviewing code before validation
- deciding how to respond to validation failures
- approving file writes or shell actions

This allows the same framework to serve both autonomous and supervised workflows.

## 7. Why this method matters

The methodological point is that seismic coding agents should not stop at “the code runs.” For JUDI workflows, a useful system must distinguish between executable code and scientifically adequate code. JUDIAgent operationalizes that distinction and uses it to drive iterative refinement.
