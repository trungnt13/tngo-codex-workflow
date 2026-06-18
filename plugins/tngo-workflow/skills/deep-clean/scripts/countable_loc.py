#!/usr/bin/env python3
"""Count executable/source LOC while excluding blanks, comments, and Python docstrings."""

from __future__ import annotations

import argparse
import ast
import io
import json
import sys
import tokenize
from pathlib import Path

from common import iter_source_files, language_for


def python_docstring_only_lines(source: str) -> set[int]:
    lines: set[int] = set()
    physical = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return lines

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
                    if not (text[:left] + text[right:]).strip():
                        lines.add(lineno)
    return lines


def count_python(path: Path) -> dict[str, int | str]:
    source = path.read_text(encoding="utf-8", errors="replace")
    physical = source.splitlines()
    doc_lines = python_docstring_only_lines(source)
    comment_lines: set[int] = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT and not physical[token.start[0] - 1][: token.start[1]].strip():
                comment_lines.add(token.start[0])
    except tokenize.TokenError:
        pass

    blank_lines = {i for i, line in enumerate(physical, start=1) if not line.strip()}
    excluded = doc_lines | comment_lines | blank_lines
    return {
        "language": "python",
        "physical_lines": len(physical),
        "blank_lines": len(blank_lines),
        "comment_lines": len(comment_lines),
        "docstring_lines": len(doc_lines),
        "countable_loc": sum(1 for i in range(1, len(physical) + 1) if i not in excluded),
    }


def c_char_literal_end(line: str, start: int) -> int | None:
    escape = False
    for i in range(start + 1, len(line)):
        if escape:
            escape = False
        elif line[i] == "\\":
            escape = True
        elif line[i] == "'":
            return i + 1
    return None


def strip_comments_line_aware(source: str, language: str = "c_cpp") -> list[str]:
    output: list[str] = []
    block_depth = 0
    quote: str | None = None
    escape = False
    raw_hashes: int | None = None
    cpp_raw_terminator: str | None = None
    for line in source.splitlines():
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
                end = c_char_literal_end(line, i)
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
        output.append("".join(kept))
    return output


def count_c_like(path: Path, language: str) -> dict[str, int | str]:
    source = path.read_text(encoding="utf-8", errors="replace")
    physical = source.splitlines()
    stripped = strip_comments_line_aware(source, language)
    blank_lines = sum(1 for line in physical if not line.strip())
    code_lines = sum(1 for line in stripped if line.strip())
    comment_only = sum(1 for original, code in zip(physical, stripped) if original.strip() and not code.strip())
    return {
        "language": language,
        "physical_lines": len(physical),
        "blank_lines": blank_lines,
        "comment_only_lines": comment_only,
        "docstring_lines": 0,
        "countable_loc": code_lines,
    }


def count_file(path: Path) -> dict[str, int | str]:
    language = language_for(path)
    if language == "python":
        return count_python(path)
    if language in {"rust", "c_cpp"}:
        return count_c_like(path, language)
    raise ValueError(f"unsupported file: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Count deep-clean executable LOC.")
    parser.add_argument("targets", nargs="+", help="Files or directories to count.")
    ns = parser.parse_args()

    files = iter_source_files([Path(t) for t in ns.targets])
    if not files:
        print(json.dumps({"ok": False, "error_code": "NO_SUPPORTED_FILES", "reason": "no supported source files found"}, indent=2))
        return 2

    result: dict[str, object] = {"ok": True, "files": {}, "totals": {"countable_loc": 0}}
    totals = result["totals"]  # type: ignore[assignment]
    by_language: dict[str, int] = {}
    for file in files:
        metrics = count_file(file)
        result["files"][str(file)] = metrics  # type: ignore[index]
        totals["countable_loc"] += int(metrics["countable_loc"])  # type: ignore[index]
        lang = str(metrics["language"])
        by_language[lang] = by_language.get(lang, 0) + int(metrics["countable_loc"])
    totals["by_language"] = by_language  # type: ignore[index]

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
