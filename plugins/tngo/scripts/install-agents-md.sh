#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  install-agents-md.sh
  install-agents-md.sh --repo

With no arguments, overwrite ~/.codex/AGENTS.md with the bundled template.
With --repo, create AGENTS.md at the current git repository root and fail if
that file already exists.
USAGE
}

repo_mode=0
if [ "$#" -eq 1 ] && [ "$1" = "--repo" ]; then
  repo_mode=1
elif [ "$#" -ne 0 ]; then
  echo "error: only --repo is supported" >&2
  usage >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
plugin_root="$(cd -- "${script_dir}/.." && pwd -P)"
template_file="${plugin_root}/templates/AGENTS.plugin.md"

if [ ! -f "$template_file" ]; then
  echo "error: missing template: $template_file" >&2
  exit 1
fi

if [ "$repo_mode" -eq 1 ]; then
  if ! repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    echo "error: --repo requires running inside a git repository" >&2
    exit 1
  fi

  target_file="${repo_root%/}/AGENTS.md"
  if [ -e "$target_file" ] || [ -L "$target_file" ]; then
    echo "error: repo AGENTS.md already exists: $target_file" >&2
    exit 1
  fi

  cp "$template_file" "$target_file"
  echo "Created: $target_file"
  exit 0
fi

target_dir="${HOME}/.codex"
target_file="${target_dir}/AGENTS.md"
mkdir -p "$target_dir"

tmp_file="$(mktemp "${target_dir}/.AGENTS.md.XXXXXX")"
trap 'rm -f "$tmp_file"' EXIT
cp "$template_file" "$tmp_file"
mv -f "$tmp_file" "$target_file"
trap - EXIT
echo "Updated: $target_file"
