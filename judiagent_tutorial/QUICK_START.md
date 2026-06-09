# JUDIAgent Tutorial Quick Start

## First-Time Setup

From the repository root:

```bash
uv venv
uv sync
cp .env.example .env
julia --project=. -e 'import Pkg; Pkg.instantiate()'
```

This installs Julia requirements from the root `Project.toml`, including
`JUDI`; the root `Manifest.toml` pins the exact Julia package versions.

Then launch:

```bash
cd judiagent_tutorial
./launch.sh
```

In Jupyter, select the **Python (JUDIAgent)** kernel if prompted.

## Returning Users

From `judiagent_tutorial/`:

```bash
./launch.sh
```

## Requirements

- Python 3.12+
- Julia 1.11+
- The parent repository environment created with `uv sync`
- API keys in the root `.env` for whichever providers you use

## Troubleshooting

- **`uv` not found**: Run `./setup.sh`; it falls back to `.venv` + `pip`.
- **Module not found**: Run `uv sync` from the repository root.
- **Kernel not found**: Run `./setup.sh` from this directory.
- **Julia error**: Run `julia --project=. -e 'import Pkg; Pkg.instantiate()'` from the repository root.

See [README.md](README.md) for details.
