#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  install-agents-md.sh
  install-agents-md.sh --repo

With no arguments, overwrite ~/.codex/AGENTS.md and ~/.codex/config.toml
with the bundled templates.
Existing files are backed up first as name.backupYYYYMMDD.ext. If a same-day
backup already exists, the install fails before changing either file.
With --repo, create AGENTS.md at the current git repository root and fail if
that file already exists. Repository mode does not install config.toml.
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
skill_dir="$(cd -- "${script_dir}/.." && pwd -P)"
agents_template_file="${skill_dir}/templates/AGENTS.plugin.md"
config_template_file="${skill_dir}/templates/config.plugin.toml"

if [ ! -f "$agents_template_file" ]; then
  echo "error: missing template: $agents_template_file" >&2
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

  cp "$agents_template_file" "$target_file"
  echo "Created: $target_file"
  exit 0
fi

if [ ! -f "$config_template_file" ]; then
  echo "error: missing template: $config_template_file" >&2
  exit 1
fi

target_dir="${HOME}/.codex"
mkdir -p "$target_dir"

tmp_files=()
cleanup() {
  for tmp_file in "${tmp_files[@]}"; do
    rm -f "$tmp_file"
  done
}
trap cleanup EXIT

backup_path_for() {
  local target_file="$1"
  local target_dir
  local target_base
  local stem
  local ext
  local backup_date
  local backup_file

  target_dir="$(dirname -- "$target_file")"
  target_base="$(basename -- "$target_file")"
  if [[ "$target_base" == *.* && "$target_base" != .* ]]; then
    stem="${target_base%.*}"
    ext=".${target_base##*.}"
  else
    stem="$target_base"
    ext=""
  fi

  backup_date="$(date +%Y%m%d)"
  backup_file="${target_dir}/${stem}.backup${backup_date}${ext}"
  if [ -e "$backup_file" ] || [ -L "$backup_file" ]; then
    echo "error: backup already exists: $backup_file" >&2
    return 1
  fi

  printf '%s\n' "$backup_file"
}

backup_existing_target() {
  local target_file="$1"
  local backup_file="$2"

  if [ ! -e "$target_file" ] && [ ! -L "$target_file" ]; then
    return 0
  fi

  if [ -L "$target_file" ]; then
    cp -P "$target_file" "$backup_file"
  else
    cp -p "$target_file" "$backup_file"
  fi
  echo "Backup: $backup_file"
}

install_template() {
  local source_file="$1"
  local target_file="$2"
  local backup_file="$3"
  local tmp_file

  tmp_file="$(mktemp "${target_dir}/.$(basename -- "$target_file").XXXXXX")"
  tmp_files+=("$tmp_file")
  cp "$source_file" "$tmp_file"
  backup_existing_target "$target_file" "$backup_file"
  mv -f "$tmp_file" "$target_file"
  echo "Updated: $target_file"
}

agents_target_file="${target_dir}/AGENTS.md"
config_target_file="${target_dir}/config.toml"
agents_backup_file=""
config_backup_file=""

if [ -e "$agents_target_file" ] || [ -L "$agents_target_file" ]; then
  agents_backup_file="$(backup_path_for "$agents_target_file")"
fi
if [ -e "$config_target_file" ] || [ -L "$config_target_file" ]; then
  config_backup_file="$(backup_path_for "$config_target_file")"
fi

install_template "$agents_template_file" "$agents_target_file" "$agents_backup_file"
install_template "$config_template_file" "$config_target_file" "$config_backup_file"
trap - EXIT
