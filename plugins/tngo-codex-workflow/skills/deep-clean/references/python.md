# Python Cleanup Rules

Prefer explicit, boring Python.

Good cleanup targets:

```text
- unused imports, variables, params, returns, branches
- redundant wrappers around pathlib, contextlib, itertools, functools, dataclasses
- copy-paste literal configuration that is truly tabular
- single-use helpers whose body is clearer inline and lowers net executable LOC
- repeated runtime checks that can move to a narrow validated object or parser boundary
```

Reject:

```text
- dense nested comprehensions that require rereading
- clever walrus/operator tricks just to remove lines
- deleting comments, docstrings, typing, tests, or diagnostics to reduce LOC
- dynamic dispatch, callbacks, or registries only to save local lines
- helpers with boolean flags for unrelated behavior
```

Validation hints:

```text
pytest
python -m pytest
ruff check .
ruff format --check .
mypy .
```

Use only commands that exist or are configured in the project.
