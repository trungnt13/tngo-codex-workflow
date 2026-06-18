---
name: deep-clean
description: Apply behavior-preserving code cleanup for Python, Rust, C, and C++ repositories. Use when the user invokes $deep-clean or asks Codex to reduce executable LOC, remove bloat, simplify code, clean up abstractions, or make code more elegant while preserving behavior, tests, comments, docstrings, documentation, and readability.
---

# Deep Clean

Use this skill to apply safe cleanup, not to produce a dry-run. Invocation means: gate the repository, build a project-specific reference/validation pipeline, apply only validated cleanup, and reject any change that weakens behavior evidence.

Priority order:

```text
1. correctness against baseline/reference behavior
2. countable executable LOC reduction
3. elegance and readability
```

## Hard Scope

Support only first-class Python, Rust, C, and C++ targets:

```text
Python: .py
Rust:   .rs
C/C++:  .c, .h, .cc, .cpp, .cxx, .c++, .hh, .hpp, .hxx, .inl, .ipp
```

Decline or narrow the task when target files are outside this set.

## Start Gate

Before spawning cleanup-candidate subagents or editing source files, resolve this skill directory, then run the gate from the repository root:

```bash
python3 "$SKILL_DIR/scripts/deep_clean_gate.py" <target...>
python3 "$SKILL_DIR/scripts/countable_loc.py" <target...>
```

Block by default when:

```text
- the target is not inside a git worktree
- `git status --porcelain=v1` is non-empty
- `git diff --check` fails
- an unfinished deep-clean marker exists
- no supported Python/Rust/C/C++ source files are found
- the validation pipeline cannot capture and verify the baseline before edits
```

Unsafe bypass: if the user explicitly authorizes a named blocker after seeing the risk, the main agent may continue past that blocker. Record each bypass in the final summary and compensate with stronger reference checks where possible. Never silently bypass, stash, reset, delete files, or hide dirty worktree state. Hard-scope failures remain non-bypassable: missing targets, unsupported target languages, and no supported source files.

## Reference and Validation Pipeline

Before any cleanup edit, deploy a validation-pipeline subagent to create a project-specific verification script at the repository root:

```text
./_tmp_deep_clean_validation.<ext>
```

The filename stem is mandatory so the main agent can always find it with `./_tmp_deep_clean_validation.*`. Choose the extension for the most reliable local runtime, usually `.py` or `.sh`.

The script must be self-contained and tested before source edits:

```text
- `./_tmp_deep_clean_validation.<ext> --capture` saves baseline references under `./_tmp_deep_clean_references/`
- `./_tmp_deep_clean_validation.<ext> --verify` reruns the same checks and exits nonzero on behavior drift
- the script owns all project-specific commands, golden-output capture, comparison logic, environment setup checks, and stable path handling
- the script must be runnable by another agent from the repository root without hidden context
```

Run `--capture` once before edits, then run `--verify` after every accepted candidate and at final validation. The only allowed new dirty paths from validation setup are `./_tmp_deep_clean_validation.<ext>` and `./_tmp_deep_clean_references/`. If validation creates any other untracked or modified files, stop unless the user explicitly authorizes that unsafe bypass. If no meaningful validation pipeline can be created, stop and report that applying cleanup is unsafe unless the user explicitly authorizes proceeding without it.

Reference behavior can be tests, golden outputs, CLI stdout/stderr, API snapshots, generated artifacts, screenshots, or benchmark JSON, depending on the project.

## Four-Agent Schedule

Use at most four child agents at any time. Do not spawn nested subagents.

Discovery phase, in parallel when relevant:

```text
1. Validation-pipeline/reference and metrics agent
2. Python cleanup candidate agent
3. Rust cleanup candidate agent
4. C/C++ cleanup candidate agent
```

Editing phase:

```text
- select up to four non-overlapping candidates
- never assign two agents to the same file, module, public API boundary, or generated artifact set
- each worker owns exact files and one cleanup hypothesis
- each worker validates its focused change before returning
```

Integration is sequential even when workers edit in parallel:

```text
for each candidate patch:
  inspect the diff
  run focused validation
  compare countable LOC
  run the readability/abstraction gate
  keep only if all gates pass
  otherwise revert only that candidate's patch
```

## Iteration Budget

Run three cleanup iterations by default unless the user specifies another count. One iteration means:

```text
1. refresh countable LOC and current validation status
2. discover cleanup candidates against the current accepted code
3. select up to four non-overlapping candidates
4. apply and integrate candidates one at a time
5. keep only candidates passing validation, LOC, readability, and public-surface gates
```

Stop early when no acceptable candidates remain, when the validation pipeline fails without an authorized bypass, or when repeated candidate rejection shows the target is already near a local minimum.

## Acceptance Gate

Accept a cleanup only when all are true:

```text
- baseline/reference behavior is unchanged
- countable executable LOC decreases
- comments, docstrings, docs, and tests are preserved or improved
- cognitive/cyclomatic complexity is flat or lower by inspection/tooling
- public API surface does not grow
- names remain domain-level and readable
- no hidden state, order dependency, dense one-liner, or side-effect compression was introduced
- a reviewer can explain the new code at least as easily as the old code
```

Reject metric gaming:

```text
- deleting comments/docstrings/docs to reduce lines
- replacing clear code with dense syntax
- extracting helpers that increase net executable LOC without domain or testing value
- generic helpers controlled by boolean flags for unrelated behavior
- macros/callbacks/dynamic dispatch only to save lines
- changing warnings, ordering, filenames, stdout/stderr, exceptions, ABI, or API behavior without explicit user approval
```

## References

Load only the reference needed for the target:

```text
references/policy.md        core acceptance/rejection policy
references/python.md        Python-specific cleanup rules
references/rust.md          Rust-specific cleanup rules
references/c_cpp.md         C/C++-specific cleanup rules
references/agent_packets.md subagent handoff packet templates
```
