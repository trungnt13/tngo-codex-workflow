# C/C++ Cleanup Rules

Preserve evaluation order, ABI, headers, and defensive checks unless the reference/validation pipeline proves they are unnecessary.

Good cleanup targets:

```text
- unused includes, locals, static helpers, branches
- repeated boilerplate where variation is tabular
- local scope narrowing, `const`, `static`, and anonymous namespace use when project style supports it
- standard algorithms only when clearer than the loop they replace
- duplicate error-handling plumbing when behavior stays identical
```

Reject:

```text
- macro cleverness for line reduction
- hidden side effects inside expressions
- changed evaluation order, lifetime, ownership, alignment, volatile, atomic, or aliasing behavior
- public header/ABI churn without explicit target scope
- deleting defensive checks in memory, concurrency, IO, GPU, or hardware-bound code without strong proof
```

Validation hints:

```text
cmake --build build
ctest --test-dir build --output-on-failure
make test
ninja test
clang-tidy
clang-format --dry-run --Werror
```

Use commands configured by the repository; do not introduce new build systems during cleanup.
