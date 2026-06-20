# Agentic Workflow

## Rules

- Whenever finish a features review with independent subagent and refine for at least 1 iteration
- Commit the code when finished a feature, PUSH ONLY ALLOWED WITH EXPLICITE USER CONFIRMATION


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

## Contents

- `skills/ask`: read-only, evidence-backped answering mode.
- `skills/oracle`: independent oracle consultation workflow.
- `skills/count-loc`: countable executable LOC metrics for supported code targets.
- `skills/deep-research`: phase-tuned, source-grounded research workflow.
- `skills/deep-clean`: behavior-preserving cleanup workflow.
