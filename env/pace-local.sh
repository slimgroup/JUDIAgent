#!/usr/bin/env bash
# Source this on PACE or another shared cluster login / interactive node.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Source this file instead of executing it: source env/pace-local.sh" >&2
  exit 1
fi

source "$(dirname "${BASH_SOURCE[0]}")/common-local.sh"

_judiagent_pace_depot="${JUDIAgent_PACE_DEPOT_ROOT:-$HOME/julia-depot-judiagent}"
_judiagent_pace_conda="${JUDIAgent_PACE_CONDAPKG_ENV:-$HOME/condapkg-env-judiagent}"

if [[ -z "${JUDIAgent_PACE_SHARED_DEPOT+x}" ]]; then
  _judiagent_shared_depot="$HOME/julia-depot"
elif [[ "$JUDIAgent_PACE_SHARED_DEPOT" == "off" || "$JUDIAgent_PACE_SHARED_DEPOT" == "none" ]]; then
  _judiagent_shared_depot=""
else
  _judiagent_shared_depot="$JUDIAgent_PACE_SHARED_DEPOT"
fi

mkdir -p "$_judiagent_pace_depot" "$_judiagent_pace_conda"

if [[ -n "$_judiagent_shared_depot" && -d "$_judiagent_shared_depot" && "$_judiagent_shared_depot" != "$_judiagent_pace_depot" ]]; then
  export JULIA_DEPOT_PATH="$_judiagent_pace_depot:$_judiagent_shared_depot"
else
  export JULIA_DEPOT_PATH="$_judiagent_pace_depot"
fi

export CONDAPKG_ENV="$_judiagent_pace_conda"

cat <<MSG
Configured JUDIAgent environment for PACE/shared-cluster use:
  JUDIAgent_REPO_DIR=$JUDIAgent_REPO_DIR
  JULIA_PROJECT=$JULIA_PROJECT
  JULIA_DEPOT_PATH=$JULIA_DEPOT_PATH
  CONDAPKG_ENV=$CONDAPKG_ENV
  UV_CACHE_DIR=$UV_CACHE_DIR

Behavior:
  - Uses a dedicated persistent JUDIAgent depot at $_judiagent_pace_depot
  - Reuses $_judiagent_shared_depot as a fallback layer when configured and present
  - Keeps the JUDIAgent CondaPkg environment at $_judiagent_pace_conda
  - Set JUDIAgent_PACE_SHARED_DEPOT=off to disable shared-depot fallback entirely

Recommended next steps:
  uv sync
  module load julia/1.11.3
  uv run pytest tests/integration_tests/test_entrypoints.py
  julia --project=. -e 'import Pkg; Pkg.instantiate()'
  uv run python examples/agent.py
MSG
