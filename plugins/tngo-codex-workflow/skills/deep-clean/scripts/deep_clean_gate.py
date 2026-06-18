#!/usr/bin/env python3
"""Fail-fast start gate for $deep-clean."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import in_skipped_dir, iter_source_files, language_for, rel, repo_root, skip_dir


UNFINISHED_MARKERS = (
    ".deep-clean",
    ".deep-clean-state.json",
    ".codex/deep-clean-state.json",
    ".codex/deep-clean",
)


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def fail(error_code: str, reason: str, **extra: object) -> int:
    payload = {"ok": False, "error_code": error_code, "reason": reason, **extra}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate a repository before $deep-clean edits.")
    parser.add_argument("targets", nargs="+", help="Files or directories to clean.")
    ns = parser.parse_args()

    targets = [Path(t).resolve() for t in ns.targets]
    missing = [str(t) for t in targets if not t.exists()]
    if missing:
        return fail("MISSING_TARGET", "target path does not exist", missing=missing)

    root = repo_root(targets[0])
    if root is None:
        return fail("NOT_GIT_WORKTREE", "target is not inside a git worktree")
    outside = [str(t) for t in targets if repo_root(t) != root]
    if outside:
        return fail("MULTIPLE_WORKTREES", "targets span multiple git worktrees", repo=str(root), outside=outside)

    status = run_git(root, ["status", "--porcelain=v1"])
    if status.returncode != 0:
        return fail("GIT_STATUS_FAILED", "git status failed", stderr=status.stderr.strip())
    if status.stdout.strip():
        return fail(
            "DIRTY_WORKTREE",
            "git worktree is dirty; commit or clear local changes before $deep-clean",
            repo=str(root),
            status=status.stdout.splitlines(),
        )

    diff_check = run_git(root, ["diff", "--check"])
    if diff_check.returncode != 0:
        return fail("DIFF_CHECK_FAILED", "git diff --check failed", stdout=diff_check.stdout, stderr=diff_check.stderr)

    markers = [m for m in UNFINISHED_MARKERS if (root / m).exists()]
    if markers:
        return fail("UNFINISHED_STATE", "unfinished deep-clean marker exists", repo=str(root), markers=markers)

    files = iter_source_files(targets)
    unsupported_direct = [
        str(t)
        for t in targets
        if t.is_file() and language_for(t) is None
    ]
    skipped_direct = [
        str(t)
        for t in targets
        if (t.is_file() and in_skipped_dir(t))
        or (t.is_dir() and t.resolve() != root.resolve() and (skip_dir(t.name) or in_skipped_dir(t)))
    ]
    if unsupported_direct:
        return fail("UNSUPPORTED_LANGUAGE", "unsupported target file language", unsupported=unsupported_direct)
    if skipped_direct:
        return fail("SKIPPED_TARGET", "target file is under a skipped build/cache/vendor directory", skipped=skipped_direct)
    if not files:
        return fail("NO_SUPPORTED_FILES", "no supported Python/Rust/C/C++ source files found")

    languages: dict[str, int] = {}
    for file in files:
        lang = language_for(file)
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    print(
        json.dumps(
            {
                "ok": True,
                "repo": str(root),
                "targets": [rel(t, root) for t in targets],
                "supported_files": len(files),
                "languages": languages,
                "files": [rel(f, root) for f in files],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
