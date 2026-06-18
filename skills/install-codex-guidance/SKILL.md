---
name: install-codex-guidance
description: Install or update the AGENTS.md guidance bundled with the TNGO Codex Workflow plugin. Use when the user asks to reproduce plugin AGENTS.md behavior, merge recommended Codex instructions, or install this plugin's durable guidance globally or into a repo.
---

# Install Codex Guidance

Use this skill to apply the plugin's recommended `AGENTS.md` guidance with the bundled installer script.

Plugins do not make `AGENTS.md` active by themselves. This skill intentionally performs a separate, explicit install step that merges the bundled template into one of:

- global Codex guidance: `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`
- a repository guidance file: `<repo>/AGENTS.md`
- an explicitly provided target file

## Procedure

1. Choose the target from the user's request.
   - If the user says global or personal, use `--global`.
   - If the user says this repo or current project, use `--repo` with the current git root or provided path.
   - If the user gives an exact file, use `--target <path>`.
2. Resolve this skill directory from the loaded `SKILL.md` path.
3. Resolve the plugin root as two directories above this skill directory.
4. Run a dry run first:

```bash
bash "<plugin-root>/scripts/install-agents-md.sh" --global --dry-run
```

5. If the dry run matches the requested target, run the same command without `--dry-run`.
6. Report the target path and backup path, if the script created one.

The installer is idempotent. It writes a managed block bounded by:

```text
<!-- BEGIN tngo-codex-workflow AGENTS.md -->
<!-- END tngo-codex-workflow AGENTS.md -->
```

On later runs, it replaces only that block.

## Commands

Install globally:

```bash
bash "<plugin-root>/scripts/install-agents-md.sh" --global
```

Install into the current git repository:

```bash
bash "<plugin-root>/scripts/install-agents-md.sh" --repo
```

Install into a specific repository:

```bash
bash "<plugin-root>/scripts/install-agents-md.sh" --repo /path/to/repo
```

Install into a specific file:

```bash
bash "<plugin-root>/scripts/install-agents-md.sh" --target /path/to/AGENTS.md
```
