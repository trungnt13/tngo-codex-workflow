#!/usr/bin/env python3
"""Count executable/source LOC while excluding blanks, comments, and Python docstrings."""

from __future__ import annotations

import argparse
import ast
import io
import json
import os
import sys
import tokenize
from pathlib import Path

SUPPORTED_EXTENSIONS = {".py": "python", ".rs": "rust", **dict.fromkeys((".c", ".h", ".cc", ".cpp", ".cxx", ".c++", ".hh", ".hpp", ".hxx", ".inl", ".ipp"), "c_cpp")}
SKIP_DIRS = {".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".venv", "venv", "__pycache__", "target", "build", "node_modules", "dist"}


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Count executable/source LOC.")
    parser.add_argument("targets", nargs="+", help="Files or directories to count.")
    ns = parser.parse_args()

    targets = [Path(t) for t in ns.targets]
    missing = [str(t) for t in targets if not t.exists()]
    if missing:
        print(json.dumps({"ok": False, "error_code": "MISSING_TARGET", "reason": "target path does not exist", "missing": missing}, indent=2))
        return 2

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
            for walk_root, dirs, names in os.walk(target):
                dirs[:] = [d for d in dirs if not skip_dir(d) and not (Path(walk_root) / d / ".git").exists()]
                for name in names:
                    path = Path(walk_root) / name
                    if language_for(path):
                        files.append(path.resolve())
    files = sorted(set(files))
    if not files:
        print(json.dumps({"ok": False, "error_code": "NO_SUPPORTED_FILES", "reason": "no supported source files found"}, indent=2))
        return 2

    result: dict[str, object] = {"ok": True, "files": {}, "totals": {"countable_loc": 0}}
    totals = result["totals"]  # type: ignore[assignment]
    by_language: dict[str, int] = {}
    for file in files:
        language = language_for(file)
        source = file.read_text(encoding="utf-8", errors="replace")
        physical = source.splitlines()
        if language == "python":
            doc_lines: set[int] = set()
            try:
                tree = ast.parse(source)
            except SyntaxError:
                tree = None
            if tree is not None:
                docstring_nodes = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                for node in ast.walk(tree):
                    if not isinstance(node, docstring_nodes):
                        continue
                    body = getattr(node, "body", None)
                    if not isinstance(body, list) or not body:
                        continue
                    first = body[0]
                    if (
                        isinstance(first, ast.Expr)
                        and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)
                    ):
                        start = getattr(first, "lineno", None)
                        end = getattr(first, "end_lineno", start)
                        start_col = getattr(first, "col_offset", 0)
                        end_col = getattr(first, "end_col_offset", None)
                        if start and end:
                            for lineno in range(start, end + 1):
                                text = physical[lineno - 1]
                                left = start_col if lineno == start else 0
                                right = end_col if lineno == end and end_col is not None else len(text)
                                prefix = text[:left].strip()
                                suffix = text[right:].lstrip()
                                if not prefix and (not suffix or suffix.startswith("#")):
                                    doc_lines.add(lineno)

            comment_lines: set[int] = set()
            try:
                for token in tokenize.generate_tokens(io.StringIO(source).readline):
                    if token.type == tokenize.COMMENT and not physical[token.start[0] - 1][: token.start[1]].strip():
                        comment_lines.add(token.start[0])
            except tokenize.TokenError:
                comment_lines.update(i for i, line in enumerate(physical, start=1) if line.lstrip().startswith("#"))

            blank_lines = {i for i, line in enumerate(physical, start=1) if not line.strip()}
            excluded = doc_lines | comment_lines | blank_lines
            metrics = {
                "language": "python",
                "physical_lines": len(physical),
                "blank_lines": len(blank_lines),
                "comment_lines": len(comment_lines),
                "docstring_lines": len(doc_lines),
                "countable_loc": sum(1 for i in range(1, len(physical) + 1) if i not in excluded),
            }
        elif language in {"rust", "c_cpp"}:
            blank_lines = code_lines = comment_only = 0
            block_depth = 0
            quote: str | None = None
            escape = False
            raw_hashes: int | None = None
            cpp_raw_terminator: str | None = None
            for line in physical:
                original = line.strip()
                i = 0
                kept: list[str] = []
                while i < len(line):
                    if cpp_raw_terminator is not None:
                        terminator = cpp_raw_terminator
                        end = line.find(terminator, i)
                        if end == -1:
                            kept.append(line[i:])
                            i = len(line)
                            continue
                        kept.append(line[i : end + len(terminator)])
                        cpp_raw_terminator = None
                        i = end + len(terminator)
                        continue
                    if raw_hashes is not None:
                        terminator = '"' + ("#" * raw_hashes)
                        end = line.find(terminator, i)
                        if end == -1:
                            kept.append(line[i:])
                            i = len(line)
                            continue
                        kept.append(line[i : end + len(terminator)])
                        raw_hashes = None
                        i = end + len(terminator)
                        continue
                    if quote is not None:
                        char = line[i]
                        kept.append(char)
                        if escape:
                            escape = False
                        elif char == "\\":
                            escape = True
                        elif char == quote:
                            quote = None
                        i += 1
                        continue
                    if block_depth:
                        if language == "rust" and line.startswith("/*", i):
                            block_depth += 1
                            i += 2
                            continue
                        if line.startswith("*/", i):
                            block_depth -= 1
                            i += 2
                            continue
                        i += 1
                        continue
                    if line.startswith("/*", i):
                        block_depth = 1
                        i += 2
                        continue
                    if line.startswith("//", i):
                        break
                    if language == "rust" and line[i] == "'":
                        j = i + 1
                        j = j + 2 if j < len(line) and line[j] == "\\" else j + 1
                        if j < len(line) and line[j] == "'":
                            kept.append(line[i : j + 1])
                            i = j + 1
                            continue
                    if language != "rust" and line[i] == "'":
                        end = None
                        literal_escape = False
                        for j in range(i + 1, len(line)):
                            if literal_escape:
                                literal_escape = False
                            elif line[j] == "\\":
                                literal_escape = True
                            elif line[j] == "'":
                                end = j + 1
                                break
                        if end is None:
                            kept.append(line[i])
                            i += 1
                        else:
                            kept.append(line[i:end])
                            i = end
                        continue
                    if language != "rust" and line.startswith('R"', i):
                        open_paren = line.find("(", i + 2)
                        if open_paren != -1:
                            delimiter = line[i + 2 : open_paren]
                            cpp_raw_terminator = ")" + delimiter + '"'
                            kept.append(line[i : open_paren + 1])
                            i = open_paren + 1
                            continue
                    if line[i] == '"':
                        quote = line[i]
                        kept.append(line[i])
                        i += 1
                        continue
                    if line[i] == "r":
                        j = i + 1
                        while j < len(line) and line[j] == "#":
                            j += 1
                        if j < len(line) and line[j] == '"':
                            raw_hashes = j - i - 1
                            kept.append(line[i : j + 1])
                            i = j + 1
                            continue
                    kept.append(line[i])
                    i += 1
                code = "".join(kept).strip()
                blank_lines += 1 if not original else 0
                code_lines += 1 if code else 0
                comment_only += 1 if original and not code else 0

            metrics = {
                "language": language,
                "physical_lines": len(physical),
                "blank_lines": blank_lines,
                "comment_only_lines": comment_only,
                "docstring_lines": 0,
                "countable_loc": code_lines,
            }
        else:
            raise ValueError(f"unsupported file: {file}")
        result["files"][str(file)] = metrics  # type: ignore[index]
        totals["countable_loc"] += int(metrics["countable_loc"])  # type: ignore[index]
        by_language[language] = by_language.get(language, 0) + int(metrics["countable_loc"])
    totals["by_language"] = by_language  # type: ignore[index]

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
