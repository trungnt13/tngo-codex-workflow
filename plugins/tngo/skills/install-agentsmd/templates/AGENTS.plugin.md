- For simple work:
  - Use NO subagent if main agent is faster than handoff + check + merge.
  - Use one subagent when parallel work saves time and is easy to verify.
- For other work, use subagents to read large context, explore noisy areas, add domain specific expertise, make focused edits, collect evidence, validate, or review risks.

**Main Agent MUST**
- Keep working unless blocked
- Do not repeat subagent work. Check, use, or reject it
- For complex or ambiguous tasks, always run independent review with domain expert subagents
- For planning, always review with expert subagents and refine for at least 1 iteration, more if there are critical reivews, but maximum 3 iteration
- Each subagent must start with explicit model and reasoning level
- No nested subagents unless allowed
- When spawning subagents with `fork_turns: "all"`; NEVER use `"model"` and `reasoning_effort`

**SUBAGENT MODEL ROUTING**
- small/medium context and clear task -> _GPT-5.3 Codex Spark (xhigh)_
- large context and low to medium ambiguity -> _GPT-5.4 (xhigh)_
- small/medium context and/or high ambiguity -> _GPT-5.5 (high)_
- final hard judgment and/or unresolved high-risk decision -> _GPT-5.5 (xhigh)_

**HANDOFF PACKET**
ROLE:
- Exact expert role
- Example: “Senior Software Engineer for CUDA kernel optimization on sm_86.”
GOAL:
- User-visible result.
- Success criteria.
- Behavior change.
CONTEXT:
- Facts.
- Evidence.
- Root cause.
- Hypotheses.
- Constraints.
- Do-not-assume notes.
SCOPE:
- Allowed files, commands, search areas, edit areas.
BOUNDARY:
- Forbidden files, actions, assumptions, goals.
VALIDATION:
- Commands.
- Expected results.
- Edge cases.
- Time, speed, memory, quality limits.
AMBIGUITY:
- Unknown, unclear, or disputed points.

**SUBAGENT RETURN**
RESULT: done | blocked | partial
SUMMARY:
- Short summary of changes or findings.
CHANGES:
- `path/glob`
- Minimal code, lines, pseudo-code, or structured data.
- Max 3 lines explaining why.
VALIDATION: pass | fail | not_run
- Command plus one-line result, or reason not run.
TRADEOFFS:
- Max 8 bullets: risks, limits, debt, constraints, ambiguity, blockers.
NEEDS_ATTENTION: yes | no
