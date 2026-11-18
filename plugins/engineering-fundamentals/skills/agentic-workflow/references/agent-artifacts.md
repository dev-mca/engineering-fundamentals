# Templates for Agent Workflow Artefacts

Adapt names, commands and paths to the project. Keep each artefact small.

## Project rules file (`CLAUDE.md` / `AGENTS.md`)

```markdown
# Project rules for coding agents

## Build & test
- Full build (must pass before any task is "done"): `./mvnw clean verify`
- Fast loop: `./mvnw test -Dtest=<ClassName>`

## Structure
- `domain/` business rules – no UI, no persistence, no provider SDKs
- `application/` use cases; `adapters/` UI, persistence, payment providers
- Dependency rules are enforced by `config/import-control.xml`

## Conventions
- Conventional Commits; one logical change per commit; refactorings separate
- Tests: JUnit 5, Given/When/Then comments, names describe behaviour
- Money as `BigDecimal`/`Money`, never `double`

## Workflow
1. Work on a branch `feature/<issue>-<slug>` per issue.
2. Write tests from the acceptance criteria first; run them and show they fail.
3. Implement until `./mvnw clean verify` passes. Never weaken tests or checks.
4. Compare coverage/violations with `develop` before proposing a merge.
5. Summarise: issue, tests, build result, metric deltas, open questions.

## Never
- Commit secrets, `target/`, IDE files
- Push to `main`/`develop` or force-push without explicit approval
```

## Skill: implement an issue

`.claude/skills/implement-issue/SKILL.md`

```markdown
---
name: implement-issue
description: Implement a tracked issue end to end on its own branch, test-first, until the full build passes. Use when asked to implement, fix or work on an issue/ticket number.
---

1. Read the issue (via the tracker integration or ask for its text). Extract
   acceptance criteria, examples and open questions; ask about open questions
   that change behaviour.
2. `git switch -c feature/<id>-<slug>` from the integration branch.
3. Run the full build once; note pre-existing failures.
4. Write the test list. Implement tests for it; run them; confirm they fail for
   the right reason. Commit: `test(<scope>): <behaviour> (#<id>)`.
5. Implement in small steps; after each, run the affected tests; at the end, the
   full build. Commit: `feat|fix(<scope>): ... (#<id>)`.
6. Refactor while green; separate `refactor:` commits.
7. Run the quality comparison (see the `compare-quality` skill).
8. Report: issue, commits, tests (and their red run), build result, metric
   deltas, assumptions, follow-ups.
```

## Skill: compare quality before merge

```markdown
---
name: compare-quality
description: Compare build quality metrics between the current branch and its target branch before a merge. Use before proposing or performing a merge.
---

1. Determine the target branch (default: develop).
2. Collect reports on both (CI artefacts, or run `./mvnw -q verify site` on a
   clean checkout of each): JaCoCo branch coverage per class, Checkstyle/PMD
   violation counts, CPD duplications, max cyclomatic complexity, class fan-out.
3. Produce a table: metric | target | branch | delta.
4. Rules: coverage must not decrease; violations, duplication, complexity and
   coupling must not increase; no new bug-category findings.
5. For each regression, draft an issue (title, location, impact, suggested fix)
   and ask the user which to fix before merging. Create issues only if allowed.
```

## Hook: block commits when tests fail (Claude Code)

`.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/require-green-build.sh"
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/require-green-build.sh`

```bash
#!/usr/bin/env bash
# Blocks `git commit` unless the fast test suite passes.
input="$(cat)"
case "$input" in
  *'"command"'*'git commit'*) ;;
  *) exit 0 ;;
esac
if ! ./mvnw -q -B test > /tmp/agent-test.log 2>&1; then
  echo "Tests are failing – fix them before committing. See /tmp/agent-test.log" >&2
  exit 2   # exit code 2 blocks the tool call and shows stderr to the agent
fi
exit 0
```

Keep hooks fast; put the slow full `verify` in CI or in an explicit step.

## Subagent: test author (separate from implementer)

`.claude/agents/test-author.md`

```markdown
---
name: test-author
description: Writes failing tests from acceptance criteria before implementation. Use when a work item needs tests written independently of the implementation.
tools: Read, Grep, Glob, Write, Edit, Bash
---

You write tests only, never production code. Derive tests from the acceptance
criteria and examples you are given, complete them with equivalence classes and
boundary values, run them and confirm they fail for the expected reason. Report
the test list, the files written and the failing output.
```

## Evaluating an agent workflow

Track per work item: lead time, number of agent iterations until green, human
review time, defects found in review/after merge, metric deltas. Compare with a
baseline. Keep what demonstrably helps; remove rules nobody needs.
