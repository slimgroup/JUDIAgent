# Developing and testing on shared clusters (e.g. PACE)

This note is for working on **login nodes** or **interactive/batch jobs** without wasting **allocated compute hours** when you only need editing, syncing, or fast tests. Heavy Julia/JUDI initialization should be treated as compute-node work, not login-node work.

Policies differ by site; always follow your cluster’s current usage rules.

## What “git pull + `uv sync` aligned with `uv.lock`” means

- **`git pull`**: bring your clone up to date with the remote branch so you have the same `pyproject.toml` and **`uv.lock`** as the team.
- **`uv sync`**: install Python packages **exactly as pinned in `uv.lock`**. That keeps everyone on the same dependency versions (reproducible builds, fewer “works on my machine” issues).
- **`.venv` in the repo directory**: either keep the virtualenv folder **inside the project** (common, easy for editors), or delete it and recreate with `uv venv && uv sync`—**as long as you always recreate from the same lockfile**, the environment is equivalent.

Never commit `.venv` (it is gitignored). Do commit `uv.lock` when dependencies change.

## Save node hours: what to do where

| Activity | Typical place | Why |
|----------|----------------|-----|
| Edit code, `git`, `ruff`, small refactors | Login node | Light I/O; no allocation needed |
| `uv sync`, `uv run pytest` (unit/integration, no live LLM) | Login node | Short CPU; keeps tests fast and cheap |
| First-time heavy `pip`/`uv` resolve (rare) | Login or job | If it thrashes disk/CPU for a long time, use an interactive job |
| Run `examples/agent.py` / autonomous agent with real API calls | Prefer **`salloc` / `srun --pty`** (interactive job) or batch | Long-running, may need stable session; counts as allocated time, not login abuse |
| Julia `Pkg.instantiate()`, JUDI build, CondaPkg resolution, big precompilation | Interactive job | Heavy CPU, disk, and artifact work; avoid doing the first full pass on the login node |
| GPU or many cores | Batch or interactive partition | Required by policy |

**Practical rule:** treat the **login node** as a **thin workstation**: sync, light tests, commit. Treat **compute nodes** as where you do Julia/JUDI first-time setup, big precompilation, and real agent runs.

## SSH, Cursor/VS Code, and the Python environment

- Open the **repository root** (`JUDIAgent/`) as the workspace folder so `pyproject.toml`, `uv.lock`, and `.venv` line up with editor settings (e.g. `.vscode/settings.json` uses `${workspaceFolder}/.venv`).
- After `uv sync`, pick the interpreter **`./.venv/bin/python`** if the IDE still shows missing imports.
- Use **`tmux`** or **`screen`** on the cluster so disconnects do not kill long interactive sessions.

## Caches and quotas

If home directory quota is tight, point caches to scratch/work (names depend on your site), for example:

- `UV_CACHE` — uv download cache  
- `JULIA_DEPOT_PATH` — Julia artifacts (if you use Julia on the cluster)

For this repository, you can also keep Julia and uv state local to the clone by sourcing `env/pace-local.sh`:

```bash
source env/pace-local.sh
```

That helper uses a dedicated persistent depot at `~/julia-depot-judiagent`, reuses `~/julia-depot` as a fallback layer when it exists, keeps the JUDIAgent CondaPkg environment at `~/condapkg-env-judiagent`, and leaves the uv cache in `.uv-cache/`. This keeps JUDI isolated without throwing away reusable Julia packages you already have.

Recommended split:

```bash
# Login node: cheap setup and smoke checks
source .venv/bin/activate
source env/pace-local.sh
./.venv/bin/python -m pytest tests/integration_tests/test_entrypoints.py

# Interactive compute node: first Julia/JUDI setup
source .venv/bin/activate
source env/pace-local.sh
module load julia/1.11.3
julia --project=. -e 'import Pkg; Pkg.instantiate()'
```

- `UV_CACHE` — uv download cache  
- `JULIA_DEPOT_PATH` — Julia artifacts (if you use Julia on the cluster)

Check your center’s documentation for recommended paths (`$WORK`, `$SCRATCH`, etc.).

## Secrets

- Keep API keys only in **`.env`** (created from `.env.example`).  
- **Do not commit `.env`.** Rotate keys if they are ever pasted into chat, logs, or tickets.

## Quick verification (minimal cost)

On the login node:

```bash
uv sync
./.venv/bin/python -m pytest tests/integration_tests/test_entrypoints.py
```

On an interactive compute node, you can then do the first Julia setup and any real agent run:

```bash
module load julia/1.11.3
julia --project=. -e 'import Pkg; Pkg.instantiate()'
uv run examples/agent.py
```

For a smoke check of entrypoints without a long agent loop, rely on tests under `tests/` first; use full `examples/agent.py` when you intentionally spend time/API quota on an interactive node or approved session.
