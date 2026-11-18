---
name: code-review
description: Review code changes, diffs, branches or pull/merge requests for correctness, clarity, design, tests and maintainability. Use when the user asks for a review, asks "is this code good", before merging, or after finishing a larger change to self-check. Can delegate to the independent code-reviewer agent.
---

# Code Review

Review is a collaborative activity, not an exam. The goal: no code reaches the
main line without being understood by someone other than its author, and both
sides learn.

## How to review

1. **Understand the intent first.** Read the PR description / issue / user request:
   what should change and why? If there is no description, reconstruct it and
   state it.
2. **Get the facts.** Look at the diff in context (not only changed lines). Run the
   build and tests if possible. Check CI status.
3. **Review in this order** (most important first):

| Area | Questions |
|---|---|
| Correctness | Does it do what it claims? Edge cases, boundaries, null/empty, error paths, concurrency, time zones, money rounding? |
| Tests | Do tests exist for the new behaviour, derived from requirements? Would they fail without the change? Boundaries and errors covered? Deterministic? |
| Design | Right place for the logic? Cohesion, coupling, SOLID where it matters, dependencies in the right direction, no business logic in UI/controllers, no needless abstraction? |
| Clarity | Intent-revealing names, small focused methods, no magic numbers, no dead/commented-out code, comments explain why? |
| Smells | Duplication, long methods, feature envy, message chains, large classes, flag arguments, shotgun surgery? |
| Safety | Secrets, injection, unvalidated input, sensitive data in logs, dependency risks? |
| Scope & history | One concern per change? Refactorings separate from behaviour? Meaningful commits? Docs/ADRs updated? |
| Quality gate | Coverage not lower, no new violations, complexity/coupling not higher? |

4. **Write feedback that is specific, actionable, balanced and kind.**
   - Point to the exact location, describe what you see, why it matters, and a
     concrete alternative.
   - "Rename `d` on line 42 to `rentalDays`" beats "this is confusing".
   - "Extract `7` and `0.10` on lines 55–58 into named constants" beats "fix this".
   - Acknowledge what is done well.
   - Critique the code, not the person. Ask when you don't understand a technique.
5. **Classify each finding:** 🔴 must fix (bug, missing test for new behaviour,
   security, broken contract), 🟡 should fix (smell, design issue, unclear code),
   🟢 nit/optional (style beyond the linter, personal preference – mark as such).
6. **Conclude** with an overall verdict (approve / approve with changes / request
   changes) and the top 3 items.

Focus on logic, correctness and maintainability – not on preferences the
formatter or linter should handle.

## Independent review by a subagent

For a significant change you wrote yourself, ask the `code-reviewer` agent (bundled
with this plugin) to review it with fresh context, so the work isn't grading
itself. Give it: the goal/acceptance criteria, the diff range or files, the build
command. Relay its findings to the user and fix 🔴 items before declaring done.

## Self-review before handing over

Before you tell the user a change is finished, run through the table above on your
own diff (`git diff` against the base), then the Definition of Done in
`engineering-core`.

## As the author receiving review

Keep PRs small, describe what and why, respond to each comment (fix, or explain
and agree), update the branch, and keep the pipeline green.
