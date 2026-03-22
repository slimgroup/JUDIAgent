# Codex Setup for JUDIAgent

This repository now includes two Codex-oriented layers:

- `AGENTS.md`: repo-local default instructions for Codex and similar coding agents
- `.codex/skills/judiagent-dev/`: a reusable skill version of the same workflow

## Recommended usage

If you open this repository directly in Codex, the root `AGENTS.md` is the most important file. It gives the agent the repo-specific workflow, testing, and safety rules that were previously stored in Cursor rules.

## Optional: install the reusable skill globally

If you want the `judiagent-dev` skill available across sessions, copy or symlink it into your Codex home skills directory:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/.codex/skills/judiagent-dev" ~/.codex/skills/judiagent-dev
```

If the symlink already exists, remove or update it first.

Once installed, you can explicitly mention `judiagent-dev` in a prompt, or let Codex trigger it from the task description.
