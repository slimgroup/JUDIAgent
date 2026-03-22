#!/usr/bin/env bash
# Shared local environment settings for JUDIAgent.
# This file is meant to be sourced by the environment-specific helpers.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Source an environment helper such as env/pace-local.sh or env/desktop-local.sh" >&2
  exit 1
fi

_repo_dir="$({ cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd; })"

export JUDIAgent_REPO_DIR="$_repo_dir"
export JULIA_PROJECT="$_repo_dir"
export JULIA_DEPOT_PATH="$_repo_dir/.julia-depot"
export CONDAPKG_ENV="$_repo_dir/.condapkg-env"
export UV_CACHE_DIR="$_repo_dir/.uv-cache"

mkdir -p "$JULIA_DEPOT_PATH" "$CONDAPKG_ENV" "$UV_CACHE_DIR"
