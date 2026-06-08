#!/usr/bin/env bash
# Source this on a desktop or workstation where Julia is installed directly.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Source this file instead of executing it: source env/desktop-local.sh" >&2
  exit 1
fi

source "$(dirname "${BASH_SOURCE[0]}")/common-local.sh"

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
