# Deep Clean Policy

Optimize semantic executable size, not textual shortness.

```text
goal:
  minimize countable executable LOC while preserving exact behavior and improving or preserving readability

count:
  include executable/source lines
  exclude blank lines, comments, docstrings, documentation, generated reference outputs
```

## Reduction Ladder

Prefer reductions in this order:

```text
1. delete unreachable/dead code
2. remove unused imports, variables, parameters, outputs, branches, flags
3. replace hand-written boilerplate with standard-library or project-native helpers
4. collapse duplicated boilerplate only when variation is tabular
5. inline short single-use logic when it lowers net executable LOC and remains obvious
6. extract helpers only when they reduce net LOC across call sites or name a real domain concept
7. narrow function/class/API surface without breaking callers
8. apply common language idioms already used by the project
```

## Inline vs Helper

```text
prefer inline when:
  inline_total < helper_total
  and the expression remains obvious at the source location

prefer helper when:
  helper_total <= inline_total across all call sites
  or the helper name captures a real domain concept
  or the logic needs independent testing/debugging
  or inline logic stops being locally parseable
```

## Acceptance Checklist

```text
behavior:
  outputs, warnings, ordering, filenames, side effects, stdout/stderr, exceptions, ABI/API contracts unchanged

readability:
  main path remains top-to-bottom
  names stay domain-level
  nesting, branching, and hidden state do not increase

abstraction:
  abstraction removes knowledge duplication, not just text duplication
  no new boolean-flag helper for unrelated behaviors
  likely future changes do not fight through one generic helper

docs:
  comments/docstrings/docs remain accurate or improve
  comments explaining why, invariants, units, and constraints are preserved

metrics:
  countable executable LOC decreases
  complexity is flat or lower
  public surface does not grow without explicit payoff
```

## Stop Conditions

Stop instead of editing unless the user explicitly authorizes a named unsafe bypass after seeing the risk:

```text
- the validation pipeline cannot capture or verify the baseline
- no reference behavior can be established
- git worktree is dirty
- cleanup requires speculative redesign
- repeated candidate rejection shows the target is already near a local minimum
```

Always stop for non-bypassable hard-scope failures:

```text
- target language is unsupported
- no supported Python/Rust/C/C++ source files are found
- target paths are missing
```
