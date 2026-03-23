# Implementation

## 1. Repository-level architecture

The implementation is organized around a small number of stable layers.

### 1.1 Agent layer

`src/judiagent/agents/`

- `agent.py`: iterative agent with validation-centered workflow
- `autonomous_agent.py`: ReAct-style autonomous agent
- `agent_base.py`: shared infrastructure for model calls, tools, retries, streaming, and graph setup

### 1.2 Validation layer

`src/judiagent/nodes/`

- `check_code.py`: orchestration of validation flow
- `validation_runtime.py`: correctness checks such as lint and execution
- `validation_review.py`: human review integration around validation
- `validation_quality.py`: JUDI-specific domain-quality review
- `validation_metrics.py`: task-aware metric recommendation
- `validation_models.py`: structured validation findings

This layer is now one of the strongest differentiators of JUDIAgent.

### 1.3 Retrieval layer

`src/judiagent/tools/retrieve.py` and `src/judiagent/rag/`

This layer handles retrieval over JUDI examples, documentation, and local code context. It supports grounding generation in existing examples rather than relying on unguided model recall.

### 1.4 Julia bridge layer

`src/judiagent/julia/`

The Julia bridge is responsible for:

- launching Julia subprocesses
- lint and execution drivers
- documentation lookup
- runtime error cleanup and formatting
- structured result passing back to Python

The current codebase has a clearer bridge split than earlier monolithic runner designs.

### 1.5 Human-in-the-loop layer

`src/judiagent/human_in_the_loop/`

This layer supports both CLI review paths and interrupt-based UI review. It allows the same system to work in terminal-first and IDE-integrated modes.

### 1.6 Shared core layer

`src/judiagent/core/`

This layer contains pure helpers for history compaction, Julia code handling, message extraction, model creation, and state utilities.

## 2. Configuration

The runtime configuration is defined in `configuration.py` and `settings.py`.

Important configuration axes include:

- model selection for iterative and autonomous agents
- embedding model and retriever configuration
- human-in-the-loop intervention points
- domain-validation mode and score threshold
- optional benchmark task identifier for metric planning

## 3. Current model defaults

At the moment, the default remote model path is configured through `settings.py`, and the repo currently defaults to a DeepSeek chat model for the remote LLM path. This is a practical default, but the architecture is model-agnostic enough to support stronger coding-oriented hosted models later.

## 4. Execution interfaces

The repo preserves multiple entry points:

- `examples/agent.py`
- `examples/autonomous_agent.py`
- `langgraph.json`

These are important because they keep the system runnable after internal refactors and also serve as smoke-test targets.

## 5. Why the current implementation matters for the paper

The implementation now supports a stronger paper story than a simple code-generation agent:

- there are two explicit agent modes
- validation is split into correctness and scientific review
- metric bundles are attached to task families
- human review is integrated into the workflow rather than bolted on afterward
- the repo now contains benchmark prompts that align with validator expectations

That combination is what makes the implementation worth presenting as a scientific coding framework rather than only a prompt-engineering artifact.
