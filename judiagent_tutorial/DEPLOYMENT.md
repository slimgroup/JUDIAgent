# Deployment Guide for JUDIAgent Tutorial

This guide is for hosting the tutorial for colleagues on a shared workstation,
cluster login node, or teaching server. Deploy the whole JUDIAgent repository so
the tutorial uses the same source tree, lockfile, retrieval corpus, and
environment helpers as the public codebase.

## Server Setup

Clone the repository and set up the parent environment:

```bash
git clone https://github.com/slimgroup/JUDIAgent.git
cd JUDIAgent
uv venv
uv sync
cp .env.example .env
julia --project=. -e 'import Pkg; Pkg.instantiate()'
```

The Julia instantiate step installs the root `Project.toml` requirements,
including `JUDI`, with exact versions pinned by `Manifest.toml`.

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
declares Julia dependencies, including `JUDI`, and `Manifest.toml` pins their
exact resolved versions.

## Troubleshooting

- **JUDIAgent not found**: Run `uv sync` from the repository root.
- **Julia packages not found**: Run `julia --project=. -e 'import Pkg; Pkg.instantiate()'` from the root.
- **API key error**: Fill the relevant provider key in the root `.env`.
- **Port conflicts**: Launch Jupyter with a different port, for example `uv run jupyter notebook --port 8889`.
