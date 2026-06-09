#!/usr/bin/env bash
# Shared local environment settings for JUDIAgent.
# This file is meant to be sourced by the environment-specific helpers.

if [[ -n "${BASH_VERSION:-}" && "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Source an environment helper such as env/pace-local.sh or env/desktop-local.sh" >&2
  exit 1
elif [[ -n "${ZSH_VERSION:-}" && "$ZSH_EVAL_CONTEXT" != *:file* ]]; then
  echo "Source an environment helper such as env/pace-local.sh or env/desktop-local.sh" >&2
  return 1 2>/dev/null || exit 1
fi

if [[ -n "${BASH_VERSION:-}" ]]; then
  _judiagent_common_script="${BASH_SOURCE[0]}"
elif [[ -n "${ZSH_VERSION:-}" ]]; then
  _judiagent_common_script="${(%):-%x}"
else
  _judiagent_common_script="$0"
fi

_repo_dir="$({ cd "$(dirname "$_judiagent_common_script")/.." && pwd; })"
unset _judiagent_common_script

export JUDIAgent_REPO_DIR="$_repo_dir"
export JULIA_PROJECT="$_repo_dir"
export JULIA_DEPOT_PATH="$_repo_dir/.julia-depot"
export CONDAPKG_ENV="$_repo_dir/.condapkg-env"
export UV_CACHE_DIR="$_repo_dir/.uv-cache"

mkdir -p "$JULIA_DEPOT_PATH" "$CONDAPKG_ENV" "$UV_CACHE_DIR"
