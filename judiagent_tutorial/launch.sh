#!/usr/bin/env bash
# Launch the tutorial notebook from the parent JUDIAgent environment.

set -euo pipefail

SCRIPT_DIR="$({ cd "$(dirname "${BASH_SOURCE[0]}")" && pwd; })"
REPO_ROOT="$({ cd "$SCRIPT_DIR/.." && pwd; })"

cd "$REPO_ROOT"

if command -v uv >/dev/null 2>&1; then
    exec uv run jupyter notebook judiagent_tutorial/judiagent_tutorial.ipynb
fi

if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
    exec jupyter notebook judiagent_tutorial/judiagent_tutorial.ipynb
fi

echo "ERROR: JUDIAgent environment not found. Run judiagent_tutorial/setup.sh first." >&2
exit 1

