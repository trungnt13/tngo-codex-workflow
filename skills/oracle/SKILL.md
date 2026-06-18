---
name: oracle
description: Consult an independent oracle for hard ambiguous problems that need diverse perspectives, critical or major review, complex planning, architecture review, unresolved tradeoffs, or final high-risk judgment. Skip routine work where local inspection is faster.
---

# Oracle

Use `claude` when available; otherwise use `cursor-agent`. Treat oracle output as evidence to verify, not authority.
Always review oracle returns and reasoning from first principles to integrate the feedbacks.

## Command

Use `xhigh` for hard review or planning. Use `max` only for explicit max requests, ultra-hard problems, or final high-risk judgment. Cursor fallback uses exact Opus 4.8 model ids.
Resolve `scripts/...` paths relative to this skill directory.
`scripts/run-oracle.sh` checks providers on every run and uses `claude` first, otherwise `cursor-agent`.

```bash
prompt_file="$(mktemp "${TMPDIR:-/tmp}/oracle-prompt.XXXXXX")"
trap 'rm -f "$prompt_file"' EXIT
cat >"$prompt_file" <<'ORACLE_PROMPT'
ROLE: ...
QUESTION: ...
CONTEXT: ...
PERSPECTIVES: security reviewer, implementation maintainer, skeptical architect.
BOUNDARIES: ...
OUTPUT: ...
ORACLE_PROMPT

scripts/run-oracle.sh xhigh "$prompt_file"
```

For `max`, reuse the same prompt-file setup and change only `xhigh` to `max`. Do not store multi-line packets in `prompt='...'`; use the heredoc file so quotes and code snippets cannot break the shell.

Scripts:

- `scripts/run-oracle.sh [xhigh|max] [PROMPT_FILE]`: read `PROMPT_FILE` or stdin, use `claude` first, otherwise `cursor-agent`, and map Cursor `xhigh|max` to Opus 4.8 model ids.

## Prompt Packet

- Role: the exact reviewer or planner role the oracle should play.
- Question: the decision, review, or plan needed.
- Context: repo paths, diffs, constraints, prior findings, and uncertainty.
- Perspectives: ask for 2-4 named viewpoints and require separate viewpoints before synthesis.
- Boundaries: forbidden edits, assumptions, scope creep, or non-goals.
- Output format: ask for findings, confidence, gaps, and recommended next checks.

Do not send secrets, credentials, private keys, or irrelevant large dumps. Prefer selected diffs, file excerpts, commands, and error text.

## Failure Handling

Treat non-zero exit, timeout, empty output, or refusal as failure. Try at most two total oracle calls: one normal call and one recoverable retry with a shorter or clearer packet.

For the retry, rewrite the same `$prompt_file` and rerun `scripts/run-oracle.sh xhigh "$prompt_file"`; do not create a second temp prompt unless it has its own cleanup. If both attempts fail, report the exact failure and continue with Codex's own analysis labeled as not oracle-backed. Never imply an oracle judgment when no oracle produced one.

## Review Discipline

- Keep Codex responsible for the final answer, implementation, and verification.
- Compare Claude's claims against local source, tests, logs, or docs before relying on them.
- State where Claude was uncertain, speculative, or contradicted local evidence.
- Reject advice that conflicts with user constraints, AGENTS.md, security boundaries, or observed code behavior.
- Summarize only the useful conclusions to the user; do not paste long oracle output unless requested.

## Examples

Use the command above with packets like these.

Critical review:

```text
ROLE: Senior reviewer for Rust async runtime changes.
QUESTION: Identify critical and major correctness risks in this diff.
CONTEXT: [paste git diff and relevant tests]
PERSPECTIVES: correctness reviewer, security reviewer, implementation maintainer.
BOUNDARIES: Do not suggest unrelated refactors.
OUTPUT: Separate findings by perspective, then synthesize critical and major risks ordered by severity, each with evidence and confidence.
```

Hard architecture planning:

```text
ROLE: Principal engineer reviewing a migration plan.
QUESTION: Stress-test this plan and propose a safer sequencing.
CONTEXT: [paste current architecture, constraints, candidate plan]
PERSPECTIVES: skeptical architect, migration owner, operations owner, API compatibility maintainer.
BOUNDARIES: Preserve public API compatibility.
OUTPUT: Separate each perspective, highlight disagreements, then provide a decision matrix, hidden risks, and validation milestones.
```
