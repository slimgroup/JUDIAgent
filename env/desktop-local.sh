#!/usr/bin/env bash
# Source this on a desktop or workstation where Julia is installed directly.

if [[ -n "${BASH_VERSION:-}" && "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Source this file instead of executing it: source env/desktop-local.sh" >&2
  exit 1
elif [[ -n "${ZSH_VERSION:-}" && "$ZSH_EVAL_CONTEXT" != *:file* ]]; then
  echo "Source this file instead of executing it: source env/desktop-local.sh" >&2
  return 1 2>/dev/null || exit 1
fi

if [[ -n "${BASH_VERSION:-}" ]]; then
  _judiagent_script="${BASH_SOURCE[0]}"
elif [[ -n "${ZSH_VERSION:-}" ]]; then
  _judiagent_script="${(%):-%x}"
else
  _judiagent_script="$0"
fi
_judiagent_script_dir="$({ cd "$(dirname "$_judiagent_script")" && pwd; })"

source "$_judiagent_script_dir/common-local.sh"
unset _judiagent_script _judiagent_script_dir

cat <<MSG
Configured JUDIAgent local environment for a desktop/workstation:
  JUDIAgent_REPO_DIR=$JUDIAgent_REPO_DIR
  JULIA_PROJECT=$JULIA_PROJECT
  JULIA_DEPOT_PATH=$JULIA_DEPOT_PATH
  CONDAPKG_ENV=$CONDAPKG_ENV
  UV_CACHE_DIR=$UV_CACHE_DIR

Recommended next steps:
  uv sync
  julia --project=. -e 'import Pkg; Pkg.instantiate()'
  uv run pytest tests/integration_tests/test_entrypoints.py
MSG
