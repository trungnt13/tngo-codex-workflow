#!/usr/bin/env bash
set -u

usage() {
  cat <<'USAGE'
Usage: run-oracle.sh [xhigh|max] [PROMPT_FILE]

Effort defaults to xhigh. Reads the prompt packet from PROMPT_FILE, or stdin when omitted.
Uses claude when available, otherwise cursor-agent.
USAGE
}

cleanup() {
  [ -z "$cleanup_file" ] || rm -f "$cleanup_file"
}

effort=xhigh
prompt_file=
cleanup_file=

[ "$#" -le 2 ] || { usage >&2; exit 64; }
[ "$#" -ge 1 ] && effort="$1"
[ "$#" -ge 2 ] && prompt_file="$2"

case "$effort" in
  xhigh|max) ;;
  *) echo "unsupported effort: $effort (expected xhigh or max)" >&2; exit 64 ;;
esac

if [ -z "$prompt_file" ]; then
  prompt_file="$(mktemp "${TMPDIR:-/tmp}/oracle-prompt.XXXXXX")"
  cleanup_file="$prompt_file"
  trap cleanup EXIT HUP INT TERM
  cat >"$prompt_file"
fi

if [ ! -r "$prompt_file" ]; then
  echo "prompt file is not readable: $prompt_file" >&2
  [ -z "$cleanup_file" ] || rm -f "$cleanup_file"
  exit 66
fi

if command -v claude >/dev/null 2>&1; then
  claude --settings '{"autoMemoryEnabled":false}' --strict-mcp-config --mcp-config '{"mcpServers":{}}' --tools "" --no-session-persistence --model opus --effort "$effort" -p <"$prompt_file"
  status=$?
elif command -v cursor-agent >/dev/null 2>&1; then
  cursor_model=claude-opus-4-8-xhigh
  [ "$effort" = max ] && cursor_model=claude-opus-4-8-max
  cursor-agent -p --mode ask --output-format text --model "$cursor_model" "$(<"$prompt_file")"
  status=$?
else
  echo "oracle unavailable: neither claude nor cursor-agent found in PATH" >&2
  status=127
fi

exit "$status"
