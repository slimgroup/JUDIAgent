#!/usr/bin/env bash
# Source this on PACE or another shared cluster login / interactive node.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Source this file instead of executing it: source env/pace-local.sh" >&2
  exit 1
fi

source "$(dirname "${BASH_SOURCE[0]}")/common-local.sh"

cat <<MSG
Configured JUDIAgent local environment for PACE/shared-cluster use:
  JUDIAgent_REPO_DIR=$JUDIAgent_REPO_DIR
  JULIA_PROJECT=$JULIA_PROJECT
  JULIA_DEPOT_PATH=$JULIA_DEPOT_PATH
  CONDAPKG_ENV=$CONDAPKG_ENV
  UV_CACHE_DIR=$UV_CACHE_DIR

Recommended next steps:
  source .venv/bin/activate
  module load julia/1.11.3
  julia --project=. -e 'import Pkg; Pkg.instantiate()'
  ./.venv/bin/python -m pytest tests/integration_tests/test_entrypoints.py
MSG
