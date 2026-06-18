# TNGO Codex Workflow

Reusable Codex workflow plugin for skills and explicit guidance installation.

## Install From GitHub

Register the GitHub marketplace:

```bash
codex plugin marketplace add <owner>/tngo-codex-workflow --ref main
```

Install the plugin:

```bash
codex plugin add tngo-codex-workflow@tngo-codex-workflow
```

The plugin is published under:

```text
plugins/tngo-codex-workflow/
```

This plugin intentionally does not rely on `AGENTS.md` being loaded from inside the plugin. Codex does not treat plugin-local `AGENTS.md` as active instructions. Instead, the plugin ships a template and an installer that merges the template into the real global or repository `AGENTS.md`.

## Contents

- `skills/ask`: read-only, evidence-backed answering mode.
- `skills/oracle`: independent oracle consultation workflow.
- `skills/deep-clean`: behavior-preserving cleanup workflow.
- `skills/install-codex-guidance`: workflow for applying the bundled guidance.
- `templates/AGENTS.plugin.md`: guidance copied from the local Codex home at packaging time.
- `scripts/install-agents-md.sh`: idempotent installer for global or repo `AGENTS.md`.

## Install Guidance

Preview global guidance install from the plugin directory:

```bash
bash plugins/tngo-codex-workflow/scripts/install-agents-md.sh --global --dry-run
```

Apply global guidance install from the plugin directory:

```bash
bash plugins/tngo-codex-workflow/scripts/install-agents-md.sh --global
```

Preview repository install:

```bash
bash plugins/tngo-codex-workflow/scripts/install-agents-md.sh --repo /path/to/repo --dry-run
```

Apply repository install:

```bash
bash plugins/tngo-codex-workflow/scripts/install-agents-md.sh --repo /path/to/repo
```

The installer writes a managed block:

```text
<!-- BEGIN tngo-codex-workflow AGENTS.md -->
...
<!-- END tngo-codex-workflow AGENTS.md -->
```

Later runs replace only that block. Existing target files are backed up before changes.
If a target file already exactly matches the bundled template, the installer wraps that content in the managed block instead of appending a duplicate copy.
