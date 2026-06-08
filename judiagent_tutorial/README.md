# JUDIAgent Tutorial

This notebook demonstrates how JUDIAgent retrieves JUDI.jl examples, generates
Julia workflow code, and validates seismic modeling tasks.

The tutorial is part of the main repository and should use the parent
JUDIAgent environment, not a separate Python environment inside this directory.

## Quick Setup

From the repository root:

```bash
uv venv
uv sync
cp .env.example .env
julia --project=. -e 'import Pkg; Pkg.instantiate()'
```

Then launch the tutorial:

```bash
cd judiagent_tutorial
./launch.sh
```

If `uv` is unavailable, run `./setup.sh`; it will fall back to a standard
`.venv` and editable install from the parent repository.

## Credentials

Edit the root `.env` file and fill only the providers you use:

- `DEEPSEEK_API_KEY` for the default chat model
- `OPENAI_API_KEY` for the default embedding model
- `LANGSMITH_API_KEY` only for tracing or GUI workflows

Never commit `.env`.

## Notebook Structure

1. **Core JUDI design**: basic JUDI.jl concepts and retrieved examples.
2. **JUDIAgent framework**: programmatic retrieval and agent generation.
3. **Adaptive configuration**: examples of iterative workflow refinement.

## Troubleshooting

- If imports fail, run `uv sync` from the repository root.
- If Jupyter cannot find the kernel, run `./setup.sh` from this directory.
- If Julia packages are missing, run `julia --project=. -e 'import Pkg; Pkg.instantiate()'` from the repository root.
- The first retrieval call may build local RAG indexes and require `OPENAI_API_KEY`.

See the root [README](../README.md) and
[reproducibility guide](../docs/reproducibility.md) for the full public-release
setup path.

