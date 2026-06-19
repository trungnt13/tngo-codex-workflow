---
name: count-loc
description: Count countable executable/source lines of code for Python, Rust, C, and C++ files and directories. Use when Codex needs LOC metrics, countable LOC totals, language breakdowns, or before/after code-size comparisons while excluding blank lines, comments, Python docstrings, and build/cache/vendor directories.
---

# Count LOC

Use this skill to produce deterministic countable LOC metrics for supported source targets.

## Supported Targets

Support only:

```text
Python: .py
Rust:   .rs
C/C++:  .c, .h, .cc, .cpp, .cxx, .c++, .hh, .hpp, .hxx, .inl, .ipp
```

Skip common cache, vendor, and build directories such as `.git`, `.venv`, `target`, `build`, `node_modules`, `dist`, and `cmake-build-*`.

## Count Model

Count source lines that remain after excluding:

```text
- blank lines
- full-line comments
- Python module, class, function, and async function docstrings
```

For Rust and C/C++, preserve string and character literals while stripping `//` and `/* ... */` comments before counting non-empty lines.

## Run

Resolve this skill directory, then run from the repository root or another stable working directory:

```bash
python3 "$SKILL_DIR/scripts/countable_loc.py" <target...>
```

The script emits sorted JSON with:

```text
ok
files[absolute_path].countable_loc
files[absolute_path].language
totals.countable_loc
totals.by_language
```

If the script returns `ok: false`, report the exact `error_code` and `reason`.

## Comparisons

For before/after comparisons:

- run the same target list both times
- compare `totals.countable_loc` and `totals.by_language`
- state that this is a structural LOC metric, not proof of behavior, complexity, or quality
