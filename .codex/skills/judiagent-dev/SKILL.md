---
name: judiagent-dev
description: Use when working on the JUDIAgent repository or a similar Python plus Julia agent stack, especially for code changes, tests, refactors, PACE cluster workflows, Python or Julia environment setup, entry-point preservation, RAG or prompt edits, and safety-sensitive git or secret-handling decisions.
---

# JUDIAgent Dev

Use this skill when the task is inside JUDIAgent or clearly follows the same workflow constraints.

## Quick workflow

1. Read `AGENTS.md` first if it exists in the repo root.
2. Use the project `.venv` and prefer `uv sync` plus `uv run ...`.
3. Keep source edits in `src/judiagent/`; keep `examples/` as thin runnable entry points.
4. Match test scope to change scope:
   - Unit tests for pure helpers, parsing, and config resolution
   - Integration or smoke tests for imports, graph wiring, and app-load checks
   - Mock or gate Julia subprocesses, live LLM calls, and large RAG indexes unless the user explicitly wants live runs
5. Preserve public entry points and compatibility during refactors unless the user requests a breaking change.

## Repo-specific guardrails

- Keep `examples/agent.py`, `examples/autonomous_agent.py`, and `langgraph.json` targets working.
- Preserve the interface between `src/judiagent/julia/*.py` and the Julia driver scripts unless the user is aware of the change.
- Treat changes under `src/judiagent/rag/`, `src/judiagent/prompts.py`, and
  `src/judiagent/rag/judi/` as behavior-sensitive.
- Use `tmp_path` for test filesystem side effects and avoid writing into tracked runtime output directories unless needed.

## Safety and git

- Never commit secrets or write real API keys into tracked files.
- `.env`, `.venv/`, `.CondaPkg/`, and `Manifest.toml` are local/runtime artifacts in this workflow and should generally stay out of git.
- Avoid destructive actions, history rewrites, or cleanup operations without explicit user approval.
- If the user asks for a commit, write a detailed, descriptive commit message.

## PACE and remote development

- For shared-cluster development, read `docs/devel-pace.md` before suggesting workflows.
- Prefer cheap login-node work for git, `uv sync`, linting, and light tests.
- Prefer compute allocations or interactive jobs for heavier runs, long-lived agents, Julia-heavy work, or anything that may consume node hours.

## What to validate before handoff

- Run the narrowest relevant tests first.
- After non-trivial Python edits, prefer `uv run pytest` or a targeted subset when practical.
- If you could not run validation, say exactly what was skipped and why.
