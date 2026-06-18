#!/usr/bin/env python3
"""Shared helpers for the deep-clean skill scripts."""

from __future__ import annotations

import os
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".rs": "rust",
    ".c": "c_cpp",
    ".h": "c_cpp",
    ".cc": "c_cpp",
    ".cpp": "c_cpp",
    ".cxx": "c_cpp",
    ".c++": "c_cpp",
    ".hh": "c_cpp",
    ".hpp": "c_cpp",
    ".hxx": "c_cpp",
    ".inl": "c_cpp",
    ".ipp": "c_cpp",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "__pycache__",
    "target",
    "build",
    "node_modules",
    "dist",
}


def repo_root(path: Path) -> Path | None:
    current = path.resolve()
    if current.is_file():
        current = current.parent
    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            return None
        current = current.parent


def language_for(path: Path) -> str | None:
    return SUPPORTED_EXTENSIONS.get(path.suffix.lower())


def skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or name.startswith("cmake-build-")


def in_skipped_dir(path: Path) -> bool:
    resolved = path.resolve()
    root = repo_root(resolved)
    try:
        parts = resolved.relative_to(root).parts[:-1] if root else resolved.parts[:-1]
    except ValueError:
        parts = resolved.parts[:-1]
    return any(skip_dir(part) for part in parts)


def iter_source_files(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        root = repo_root(target)
        is_root = root is not None and target.resolve() == root.resolve()
        if target.is_file():
            if language_for(target) and not in_skipped_dir(target):
                files.append(target.resolve())
            continue
        if target.is_dir():
            if (not is_root and skip_dir(target.name)) or in_skipped_dir(target):
                continue
            for root, dirs, names in os.walk(target):
                dirs[:] = [
                    d
                    for d in dirs
                    if not skip_dir(d) and not (Path(root) / d / ".git").exists()
                ]
                for name in names:
                    path = Path(root) / name
                    if language_for(path):
                        files.append(path.resolve())
    return sorted(set(files))


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())
