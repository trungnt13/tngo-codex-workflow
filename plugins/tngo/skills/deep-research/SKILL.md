---
name: deep-research
description: Run a Copilot /research-style deep investigation in Codex with phase-tuned research subagents. Use when the user explicitly invokes $deep-research, asks for deep research, source-grounded investigation, cross-repository or web/GitHub evidence gathering, contradiction/risk audit, or wants a cited Markdown research report. Produces research reports and evidence summaries, not code changes, unless the user separately asks for implementation.
---

# Deep Research

Emulate Copilot CLI `/research` using only Codex skills plus custom subagents. Treat `$deep-research TOPIC` as the user-facing entrypoint. Do not claim this is a native slash command.

## Contract

- Work autonomously once a topic is present. Ask only if the topic is missing or impossible to scope safely.
- Do not modify project source, configs, credentials, or user data. The only intended write is the final Markdown report under `~/.codex/research/`.
- Use subagents for evidence gathering; synthesize in the parent thread.
- Prefer primary sources, source code, official docs, and exact file references over secondary summaries.
- State uncertainty. Separate facts, inferences, and hypotheses.

## Report Path

Save a report for every completed research task:

```text
~/.codex/research/YYYY-MM-DD/<topic-slug>.md
```

Use the local date when available. Build `<topic-slug>` by lowercasing the topic, replacing non-alphanumeric runs with `-`, trimming leading/trailing `-`, and limiting to a practical length. If a file exists, append `-2`, `-3`, etc.

## Workflow

1. Parse the topic from the prompt after `$deep-research`.
2. Classify the request:
   - Process/how-to: prioritize reproducible steps, commands, configuration, and failure modes.
   - Conceptual/explanatory: prioritize definitions, mental models, tradeoffs, and examples.
   - Technical deep dive: prioritize code paths, architecture, APIs, diagrams, and edge cases.
   - Current/product/legal/security/financial facts: browse or query authoritative current sources.
3. Preflight available evidence surfaces without exposing secrets:
   - Local repository files via `rg`, `find`, `sed`, `git`, and targeted file reads.
   - Web search if available.
   - GitHub CLI or GitHub MCP tools if already configured.
   - Official docs MCP/tools for product-specific facts when available.
   Record unavailable surfaces as limitations in the report.
4. Create a short research plan before dispatch:
   - Key questions and disconfirming checks.
   - Search terms and likely source locations.
   - Which subagents should answer which questions.
5. Select subagents by research phase and epistemic risk:
   - Discovery: use `researcher_fast` for broad source inventory, terminology, likely files/repos, search-term expansion, and first-pass contradiction leads.
   - Verification: use `researcher` for deeper reading, line-level checking, source comparison, and citation-quality summaries.
   - Audit: use `researcher_auditor` only when conclusions are high-stakes, evidence conflicts, source quality is weak, or the user asks for risk/security/legal/current-fact confidence.
   - Synthesis: keep final integration in the parent thread. Do not spawn extra subagents merely to rewrite the report.
6. Dispatch subagents in parallel where useful:
   - Use `researcher_fast` for broad discovery, search-term expansion, local repo mapping, and first-pass source inventory.
   - Use `researcher` for deeper source reading, verification, contradiction checks, and citation-quality summaries.
   - Use `researcher_auditor` as a later-wave adversarial reviewer, not a default first-wave worker.
   - For small topics, use 2-3 subagents. For complex topics, use 6-10 total dispatches across waves. Avoid fan-out that cannot improve the answer.
7. Spend reasoning effort according to uncertainty, not habit:
   - Retrieval-heavy discovery should maximize coverage and useful leads.
   - Verification should spend effort on exact claims, citations, and contradiction checks.
   - Audit should spend the highest effort only where wrong conclusions would be costly.
   - If evidence is clean and low-risk, prefer fewer agents over more agents.
8. Each subagent prompt must include:
   - ROLE: narrowly scoped research specialist.
   - GOAL: exact question to answer and success criteria.
   - DOMAIN KNOWLEDGE: known facts, hypotheses, and do-not-assume items.
   - SCOPE: allowed sources, forbidden areas, and no-write constraint.
   - VALIDATION: expected citation format and checks.
   - AMBIGUITY: what to mark uncertain instead of guessing.
9. Require this return format from subagents:

```text
RESULT: done | partial | blocked
SUMMARY:
  Concise findings.
EVIDENCE:
  - source: URL or file path with line refs
    claim: minimal claim supported by the source
    confidence: high | medium | low
CONTRADICTIONS_OR_GAPS:
  - ...
VALIDATION: pass | partial | not_run
NEEDS_ATTENTION: yes | no
```

## Reasoning Effort Policy

Use role variance to reduce false confidence without wasting expensive reasoning on simple retrieval.

```text
researcher_fast     gpt-5.3-codex-spark  xhigh  broad discovery and source mapping
researcher          gpt-5.4              high   deep verification and citation checks
researcher_auditor  gpt-5.4              xhigh  contradiction, risk, and confidence audit
parent synthesis    current parent model  high/xhigh final integration and confidence assessment
```

Apply `researcher_auditor` when any of these are true:

- Important sources disagree.
- A claim depends on one weak, stale, indirect, or unofficial source.
- The topic touches security, legal, financial, medical, safety, production incident, or current product behavior.
- The final answer would drive substantial engineering time, money, or irreversible decisions.
- The user explicitly asks for adversarial review, residual risk, or high confidence.

Do not use every agent at maximum effort by default. Most failed research is caused by missing sources, stale assumptions, or poor scoping; solve those with discovery and verification before escalating to audit.

## Evidence Rules

- Cite local code as absolute file links with line numbers when possible.
- Cite GitHub code as `org/repo:path:line-range` or a permalink. Include commit SHA when available.
- Cite web facts with URLs. Prefer official docs, specs, source repositories, issue trackers, release notes, and papers.
- For implementation details, prefer source code over README prose when both exist.
- For claims likely to change over time, verify with current sources before stating them.
- If only one weak source supports an important claim, mark confidence low or medium.
- Do not include long copied passages. Quote sparingly; paraphrase with citations.

## Synthesis

Synthesize only from subagent outputs and sources you personally inspected. The final report should usually contain:

```markdown
# <Title>

Date: YYYY-MM-DD
Topic: <original topic>

## Executive Summary
## Scope and Method
## Key Findings
## Technical Details / Process / Conceptual Model
## Source Map
## Contradictions, Gaps, and Risks
## Confidence Assessment
## Footnotes
```

For technical deep dives, include compact Mermaid diagrams when they clarify architecture or flow. Keep tables dense and useful: source, evidence, relevance, confidence.

## Final Response

After saving the report, respond with:

- The report path.
- 3-5 highest-signal findings.
- Any important limitations, especially unavailable GitHub/web/private-source access.

Do not paste the full report into chat unless the user asks.
