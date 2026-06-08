# Deployment Guide for JUDIAgent Tutorial

This guide is for hosting the tutorial for colleagues on a shared workstation,
cluster login node, or teaching server. Deploy the whole JUDIAgent repository so
the tutorial uses the same source tree, lockfile, retrieval corpus, and
environment helpers as the public codebase.

## Server Setup

Clone the repository and set up the parent environment:

```bash
git clone https://github.com/haoyunl2/JUDIAgent.git
cd JUDIAgent
uv venv
uv sync
cp .env.example .env
julia --project=. -e 'import Pkg; Pkg.instantiate()'
```

Fill only the needed keys in `.env`. Do not commit or share that file.

On PACE or another shared cluster, use the root environment helpers:

```bash
source env/pace-local.sh
```

See `docs/devel-pace.md` for login-node versus compute-node guidance.

## Launch

```bash
cd judiagent_tutorial
./launch.sh
```

If the server uses JupyterHub, register the root environment kernel:

```bash
uv run python -m ipykernel install --user --name judiagent --display-name "Python (JUDIAgent)"
```

For JupyterHub or shared access, see [JupyterHub documentation](https://jupyterhub.readthedocs.io/).

## Reproducibility

The parent `uv.lock` pins Python dependencies. The root Julia `Project.toml`
defines the Julia environment; `Manifest.toml` is intentionally local/runtime
state in this workflow.

## Troubleshooting

- **JUDIAgent not found**: Run `uv sync` from the repository root.
- **Julia packages not found**: Run `julia --project=. -e 'import Pkg; Pkg.instantiate()'` from the root.
- **API key error**: Fill the relevant provider key in the root `.env`.
- **Port conflicts**: Launch Jupyter with a different port, for example `uv run jupyter notebook --port 8889`.
