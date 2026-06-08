#!/usr/bin/env bash
# Set up the JUDIAgent tutorial using the parent repository environment.

set -euo pipefail

SCRIPT_DIR="$({ cd "$(dirname "${BASH_SOURCE[0]}")" && pwd; })"
REPO_ROOT="$({ cd "$SCRIPT_DIR/.." && pwd; })"

echo "=========================================="
echo "JUDIAgent Tutorial Setup"
echo "=========================================="
echo "Repository root: $REPO_ROOT"

if ! command -v julia >/dev/null 2>&1; then
    echo "ERROR: Julia 1.11+ is required and was not found on PATH." >&2
    exit 1
fi

cd "$REPO_ROOT"

if command -v uv >/dev/null 2>&1; then
    uv venv
    uv sync
    PYTHON_CMD=(uv run python)
else
    echo "uv not found; falling back to python -m venv + pip." >&2
    python3 -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]" jupyter notebook
    PYTHON_CMD=(python)
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from .env.example; fill in only the providers you use."
fi

julia --project=. -e 'import Pkg; Pkg.instantiate(); println("Julia project ready")'

"${PYTHON_CMD[@]}" -m ipykernel install \
    --user \
    --name judiagent \
    --display-name "Python (JUDIAgent)" || true

echo ""
echo "Setup complete."
echo "Launch the tutorial with:"
echo "  cd judiagent_tutorial"
echo "  ./launch.sh"

