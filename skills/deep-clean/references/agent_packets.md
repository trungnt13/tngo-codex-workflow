# Deep Clean Agent Packets

Use at most four child agents. Keep packets narrow and file-owned.

## Validation Pipeline Agent

```text
ROLE: Project-specific reference and verification pipeline builder.
GOAL:
  Create a self-contained validation script at ./_tmp_deep_clean_validation.<ext> and capture baseline behavior under ./_tmp_deep_clean_references/.
SCOPE:
  Read project files and add/modify only ./_tmp_deep_clean_validation.<ext> and ./_tmp_deep_clean_references/. Forbidden: cleanup edits, source rewrites, generated artifact churn outside the reference directory.
VALIDATION:
  Run ./_tmp_deep_clean_validation.<ext> --capture, then ./_tmp_deep_clean_validation.<ext> --verify. The script must exit nonzero on behavior drift and be runnable by another agent from the repository root without extra context.
RETURN:
  RESULT: done | blocked | partial
  SUMMARY:
  CHANGES:
    - ./_tmp_deep_clean_validation.<ext>:
        interface: "--capture and --verify"
        references: "./_tmp_deep_clean_references/"
        checks:
  VALIDATION: pass | fail | not_run
  TRADEOFFS:
  NEEDS_ATTENTION:
```

## Discovery Agent

```text
ROLE: Language-specific cleanup candidate miner for <Python|Rust|C/C++>.
GOAL:
  Find behavior-preserving cleanup candidates that reduce countable executable LOC without deleting comments/docs/tests or increasing reasoning cost.
SCOPE:
  Read-only. Allowed files: <paths>. Forbidden: edits, unrelated search, generated artifacts.
VALIDATION:
  Candidate must name focused commands or reference outputs needed to prove behavior.
RETURN:
  RESULT: done | blocked | partial
  SUMMARY:
  CHANGES:
    - candidate_id:
        files:
        transform:
        expected_loc_delta:
        behavior_risk:
        readability_risk:
        validation:
  VALIDATION: not_run
  TRADEOFFS:
  NEEDS_ATTENTION:
```

## Worker Agent

```text
ROLE: Scoped cleanup worker for candidate <id>.
GOAL:
  Apply exactly one cleanup candidate and validate it.
SCOPE:
  Allowed files: <exact files>. Forbidden: unrelated formatting, public API changes, broad renames, generated files.
VALIDATION:
  Run <focused command>. Report failures and stop.
RETURN:
  RESULT: done | blocked | partial
  SUMMARY:
  CHANGES:
    - path:
        minimal_before_after_excerpt:
        reason:
  VALIDATION: pass | fail | not_run
  TRADEOFFS:
  NEEDS_ATTENTION:
```

## Review Agent

```text
ROLE: Adversarial readability and correctness reviewer.
GOAL:
  Reject metric gaming and behavior risk after a candidate appears to pass tests.
SCOPE:
  Review only the candidate diff and baseline evidence.
QUESTIONS:
  - Is behavior/reference output actually unchanged?
  - Did comments/docstrings/docs/tests disappear?
  - Did dense syntax hide state, ordering, or side effects?
  - Did helper extraction add flags or public surface?
  - Can the new code be explained faster than the old code?
RETURN:
  RESULT: done
  SUMMARY:
  CHANGES:
    - finding:
  VALIDATION: pass | fail | not_run
  TRADEOFFS:
  NEEDS_ATTENTION:
```
