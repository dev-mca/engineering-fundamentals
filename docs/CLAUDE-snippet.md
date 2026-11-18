# Copy this into your project's CLAUDE.md

Adjust the commands and paths, delete what doesn't apply.

```markdown
## Engineering rules

Use the engineering-fundamentals skills for every code change
(start with engineering-core).

- Build & test (must pass before anything is "done"): `<your build command>`
  e.g. `./mvnw clean verify` | `npm ci && npm test && npm run lint` | `uv run pytest`
- Work test-first: write tests from the requirement, run them and show they fail,
  then implement.
- Small steps. Refactoring and behaviour changes in separate commits.
- Commit messages: Conventional Commits, explain why.
- Branch per task: `feature/<issue>-<slug>`; never push to main without approval.
- Keep the design simple; add abstractions only for real variation or testability.
- Business logic stays out of UI/controllers and is unit-testable.
- Don't weaken or delete tests or checks to get a green build.
- After each task: summarise what changed, why, how it was verified, what is left.
```
