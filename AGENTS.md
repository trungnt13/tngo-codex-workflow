# Agentic Workflow

## Install From GitHub

Register the GitHub marketplace:

```bash
codex plugin marketplace add trungnt13/tngo-workflow --ref main
```

Install the plugin:

```bash
codex plugin add tngo@tngo-workflow
```

The plugin is published under:

```text
plugins/tngo/
```

This plugin intentionally does not rely on `AGENTS.md` being loaded from inside the plugin. Codex does not treat plugin-local `AGENTS.md` as active instructions. Instead, the plugin ships a template and an installer that writes the template into the real global or repository `AGENTS.md`.

## Contents

- `skills/ask`: read-only, evidence-backped answering mode.
- `skills/oracle`: independent oracle consultation workflow.
- `skills/count-loc`: countable executable LOC metrics for supported code targets.
- `skills/deep-research`: phase-tuned, source-grounded research workflow.
- `skills/deep-clean`: behavior-preserving cleanup workflow.
- `skills/install-agentsmd`: workflow, template, and installer for applying the bundled guidance.

## Install Guidance

Apply global guidance install from the repository root. This overwrites `~/.codex/AGENTS.md`:

```bash
bash plugins/tngo/skills/install-agentsmd/scripts/install-agents-md.sh
```

Apply repository guidance install from the repository root. This creates `AGENTS.md` at the current git repo root and fails if that file already exists:

```bash
bash plugins/tngo/skills/install-agentsmd/scripts/install-agents-md.sh --repo
```
