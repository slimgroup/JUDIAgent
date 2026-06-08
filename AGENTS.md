# JUDIAgent Agent Guide

This repository contains a Python + Julia agent stack. When working here with Codex or another coding agent, follow these repo-specific rules first.

## Environment

- Use the project virtual environment at `.venv/`.
- Prefer `uv sync` to align with `pyproject.toml` and `uv.lock`.
- Prefer `uv run ...` for Python commands so the project environment is used consistently.
- Keep secrets in local `.env` only. Never write real keys into tracked files.

## Repository layout

- `src/judiagent/`: library code only.
- `examples/`: thin entry scripts that should stay runnable after refactors.
- `tests/`: pytest coverage for Python behavior, imports, graph wiring, and smoke tests.
- `docs/devel-pace.md`: PACE / SSH / cluster development workflow and cost-saving guidance.
- `docs/reproducibility.md`: public-release setup and reproducibility checklist.
- `src/judiagent/rag/THIRD_PARTY.md`: provenance notes for vendored JUDI retrieval material.

## Testing expectations

- Prefer unit tests for pure helpers and config/parsing logic.
- Use integration or smoke tests for imports, graph wiring, and app-load checks.
- If a change touches Julia subprocesses, live LLM calls, or large RAG indexes, keep tests mocked or optional unless the user explicitly asks for live runs.
- Use `tmp_path` for filesystem side effects in tests.
- Do not write test artifacts into real `outputs/` or `scripts/` unless the task explicitly needs that.

## Cluster cost control

- On PACE or similar shared clusters, prefer login-node work for git, linting, file inspection, and narrow smoke tests.
- If heavier tests or Julia-heavy runs are needed, request the smallest practical `salloc` allocation first.
- End the allocation immediately after the task completes to save node hours.

## Refactor guardrails

- Preserve public entry points such as `examples/agent.py`, `examples/autonomous_agent.py`, and `langgraph.json` targets unless the user requests a breaking change.
- When splitting modules, prefer compatibility shims or re-exports so imports stay stable.
- Preserve the Python/Julia boundary in `src/judiagent/julia/` and the `.jl` driver scripts unless the user is aware of the interface change.
- Treat `src/judiagent/rag/`, `src/judiagent/prompts.py`, and
  `src/judiagent/rag/judi/` as behavior-sensitive areas. Prefer additive or
  clearly scoped edits.

## Safety

- Do not delete tracked files or perform other destructive actions without explicit permission in the current conversation.
- Do not rewrite git history, run aggressive cleanup, or touch recovery-impacting git operations without explicit permission.
- Do not modify local-only runtime state such as `.env`, `.venv/`, `.CondaPkg/`, `outputs/`, or user-generated `scripts/` content unless the user asks.
- Prefer reversible changes and explain intentional breakage clearly.
- Before public-release edits, preserve attribution in `NOTICE`, `CITATION.cff`,
  and third-party corpus notes. Do not remove upstream JutulGPT or JUDI credits.

## Commit workflow

- Do not create commits unless the user explicitly asks.
- If the user wants a commit, use a descriptive message that explains why the change was made and the main scope.
