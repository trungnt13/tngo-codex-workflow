#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ID="tngo-codex-workflow"
BEGIN_MARKER="<!-- BEGIN ${PLUGIN_ID} AGENTS.md -->"
END_MARKER="<!-- END ${PLUGIN_ID} AGENTS.md -->"

usage() {
  cat <<'USAGE'
Usage:
  install-agents-md.sh --global [--dry-run]
  install-agents-md.sh --repo [REPO_ROOT] [--dry-run]
  install-agents-md.sh --target PATH [--dry-run]

Merges the bundled AGENTS.md template into the selected target using a managed
marker block. Existing files are backed up before they are changed.
USAGE
}

scope="global"
repo_root=""
target_file=""
dry_run=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --global)
      scope="global"
      shift
      ;;
    --repo)
      scope="repo"
      shift
      if [ "$#" -gt 0 ] && [ "${1#--}" = "$1" ]; then
        repo_root="$1"
        shift
      fi
      ;;
    --target)
      scope="target"
      shift
      if [ "$#" -eq 0 ]; then
        echo "error: --target requires a path" >&2
        usage >&2
        exit 2
      fi
      target_file="$1"
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
plugin_root="$(cd -- "${script_dir}/.." && pwd -P)"
template_file="${plugin_root}/templates/AGENTS.plugin.md"

if [ ! -f "$template_file" ]; then
  echo "error: missing template: $template_file" >&2
  exit 1
fi

case "$scope" in
  global)
    codex_home="${CODEX_HOME:-${HOME}/.codex}"
    target_file="${codex_home}/AGENTS.md"
    ;;
  repo)
    if [ -z "$repo_root" ]; then
      repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"
    fi
    target_file="${repo_root%/}/AGENTS.md"
    ;;
  target)
    ;;
esac

target_dir="$(dirname -- "$target_file")"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-agents-install.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

block_file="${tmp_dir}/managed-block.md"
output_file="${tmp_dir}/AGENTS.md"

{
  printf '%s\n' "$BEGIN_MARKER"
  cat "$template_file"
  printf '%s\n' "$END_MARKER"
} > "$block_file"

if [ -f "$target_file" ]; then
  if cmp -s "$target_file" "$template_file"; then
    cat "$block_file" > "$output_file"
    printf '\n' >> "$output_file"
  elif grep -Fqx "$BEGIN_MARKER" "$target_file" && grep -Fqx "$END_MARKER" "$target_file"; then
    awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" -v block="$block_file" '
      BEGIN {
        while ((getline line < block) > 0) {
          replacement = replacement line ORS
        }
        close(block)
        in_block = 0
        replaced = 0
      }
      $0 == begin {
        printf "%s", replacement
        in_block = 1
        replaced = 1
        next
      }
      in_block && $0 == end {
        in_block = 0
        next
      }
      !in_block {
        print
      }
      END {
        if (in_block) {
          exit 2
        }
        if (!replaced) {
          exit 3
        }
      }
    ' "$target_file" > "$output_file"
  else
    cp "$target_file" "$output_file"
    if [ -s "$output_file" ]; then
      printf '\n\n' >> "$output_file"
    fi
    cat "$block_file" >> "$output_file"
    printf '\n' >> "$output_file"
  fi
else
  cat "$block_file" > "$output_file"
  printf '\n' >> "$output_file"
fi

if [ "$dry_run" -eq 1 ]; then
  echo "Dry run target: $target_file"
  if [ -f "$target_file" ]; then
    diff -u "$target_file" "$output_file" || true
  else
    diff -u /dev/null "$output_file" || true
  fi
  exit 0
fi

mkdir -p "$target_dir"

if [ -f "$target_file" ] && cmp -s "$target_file" "$output_file"; then
  echo "No changes: $target_file"
  exit 0
fi

backup_file=""
if [ -f "$target_file" ]; then
  backup_file="${target_file}.bak.$(date -u +%Y%m%dT%H%M%SZ)"
  cp "$target_file" "$backup_file"
fi

mv "$output_file" "$target_file"
echo "Updated: $target_file"
if [ -n "$backup_file" ]; then
  echo "Backup: $backup_file"
fi
