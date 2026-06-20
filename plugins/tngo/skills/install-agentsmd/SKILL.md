---
name: install-agentsmd
description: Install the AGENTS.md guidance and Codex config.toml bundled with the TNGO Workflow plugin. Use when the user asks to reproduce plugin AGENTS.md behavior, install durable Codex guidance globally or into a repo, or apply the bundled Codex config.
---

# Install Codex Guidance

Use this skill to apply the plugin's recommended `AGENTS.md` guidance and bundled Codex `config.toml` with the installer script.

Plugins do not make `AGENTS.md` active by themselves. This skill intentionally performs a separate, explicit install step:

- Global install writes the bundled templates to `~/.codex/AGENTS.md` and `~/.codex/config.toml`, overwriting any existing files after first backing each existing target up in the same directory as `name.backupYYYYMMDD.ext`. If a same-day backup already exists for either target, the installer fails before changing either file.
- Repository install writes the bundled `AGENTS.md` template to the current git repo root `AGENTS.md` and fails if that file already exists. It does not install `config.toml`, because Codex config is global.

Before installing, ask the user to choose the destination unless they already explicitly chose one. The first prompt should offer these two normal targets:

- global Codex guidance and config: `~/.codex/AGENTS.md` and `~/.codex/config.toml`
- repository guidance: the current repo root `AGENTS.md`

Only `--repo` is supported. With no arguments, the installer performs a global install.

## Procedure

1. Determine whether the user already chose a destination.
   - If the user says global, personal, or config, use the installer with no arguments.
   - If the user says this repo or current project, use `--repo`.
2. If the destination is not explicit, ask whether to install to `~/.codex/AGENTS.md` plus `~/.codex/config.toml`, or to the current repo root `AGENTS.md`, then wait for the user's choice before running commands.
3. Resolve this skill directory from the loaded `SKILL.md` path.
4. Run the skill-local installer with the selected destination arguments.
5. Report the target path or paths and any backup paths emitted by the installer. If a repository install is blocked because `AGENTS.md` already exists, report that path and do not modify it.

## Commands

Install globally, backing up and then overwriting `~/.codex/AGENTS.md` and `~/.codex/config.toml`:

```bash
bash "<skill-dir>/scripts/install-agents-md.sh"
```

Install `AGENTS.md` into the current git repository, only if `AGENTS.md` does not already exist:

```bash
bash "<skill-dir>/scripts/install-agents-md.sh" --repo
```
