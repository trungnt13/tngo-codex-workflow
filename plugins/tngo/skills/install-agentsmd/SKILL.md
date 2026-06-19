---
name: install-agentsmd
description: Install the AGENTS.md guidance bundled with the TNGO Workflow plugin. Use when the user asks to reproduce plugin AGENTS.md behavior or install this plugin's durable guidance globally or into a repo.
---

# Install Codex Guidance

Use this skill to apply the plugin's recommended `AGENTS.md` guidance with the bundled installer script.

Plugins do not make `AGENTS.md` active by themselves. This skill intentionally performs a separate, explicit install step:

- Global install writes the bundled template to `~/.codex/AGENTS.md` and overwrites any existing file.
- Repository install writes the bundled template to the current git repo root `AGENTS.md` and fails if that file already exists.

Before installing, ask the user to choose the destination unless they already explicitly chose one. The first prompt should offer these two normal targets:

- global Codex guidance: `~/.codex/AGENTS.md`
- repository guidance: the current repo root `AGENTS.md`

Only `--repo` is supported. With no arguments, the installer performs a global install.

## Procedure

1. Determine whether the user already chose a destination.
   - If the user says global or personal, use the installer with no arguments.
   - If the user says this repo or current project, use `--repo`.
2. If the destination is not explicit, ask whether to install to `~/.codex/AGENTS.md` or the current repo root `AGENTS.md`, then wait for the user's choice before running commands.
3. Resolve this skill directory from the loaded `SKILL.md` path.
4. Run the skill-local installer with the selected destination arguments.
5. Report the target path. If a repository install is blocked because `AGENTS.md` already exists, report that path and do not modify it.

## Commands

Install globally, overwriting `~/.codex/AGENTS.md`:

```bash
bash "<skill-dir>/scripts/install-agents-md.sh"
```

Install into the current git repository, only if `AGENTS.md` does not already exist:

```bash
bash "<skill-dir>/scripts/install-agents-md.sh" --repo
```
