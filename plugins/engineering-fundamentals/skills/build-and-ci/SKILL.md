---
name: build-and-ci
description: Build automation, continuous integration/delivery and code quality metrics. Use when setting up or fixing a build (Maven, Gradle, npm, pip/uv, etc.), writing CI pipelines (GitLab CI, GitHub Actions), adding linters, static analysis, coverage or quality gates, interpreting metrics (cyclomatic complexity, LCOM, coupling, duplication, technical debt), managing dependencies, or creating releases.
---

# Build Automation, CI/CD and Quality Metrics

If software only builds on one laptop, the project is already fragile. The
standard: **with only an OS and the repository, anyone can build, test and run the
product with one command.**

## A good build is CRISP

- **Complete** – every step (compile, test, analyse, package) runs; no hidden
  manual steps, no "install tool X by hand".
- **Repeatable** – same commit → same result. Build scripts and pinned dependency
  versions live in version control; use tool wrappers (`./mvnw`, `./gradlew`,
  lockfiles, `.nvmrc`, `.python-version`).
- **Informative** – reports test results, metrics, logs, generated docs.
- **Schedulable** – runs on triggers (push, merge request, tag, nightly). The CI
  result counts, not "works on my machine".
- **Portable** – runs on any dev machine, the CI server, the deployment
  environment (e.g. a pinned Docker image in CI).

One build button, documented in the README under "Build & Test", e.g.
`./mvnw clean verify` · `./gradlew build` · `npm ci && npm test && npm run lint` ·
`uv run pytest`.

## Rules for agents

- Find and use the project's existing build command (README, CI config, build
  files). Don't invent a parallel build.
- **Work is done only when the full build passes locally**, including the static
  checks. If it fails, fix the cause – don't skip tests, lower thresholds,
  add blanket suppressions, or delete checks to get green.
- If you cannot run the build (missing tool, no network), say so clearly.
- Don't commit on top of a red build; if the pipeline is red, fixing it comes
  first.

## Continuous integration

Everyone integrates into the shared trunk at least daily; every integration is
verified by an automated build with tests. Prerequisites: version control, an
automated build, a self-testing test suite, agreed coding standards enforced by
tools.

Pipeline steps (conceptual): fetch → compile → test → analyse → report →
(package → publish for delivery).

Practices: commit frequently; never commit a failing build (run it locally
first); don't commit on a broken build; keep the build fast (minutes); single
source repository; self-testing build; notify on failure; split long suites into
stages (unit on push, slow integration/system tests nightly).

The three Cs: **continuous integration** (build + unit tests + static analysis on
every push), **continuous delivery** (additionally deploy to test environments,
run further tests, package and publish automatically; a person decides when to
release, e.g. by pushing a tag), **continuous deployment** (every green build
goes to production automatically; needs feature flags, monitoring, rollback).

Pipeline examples: `references/ci-cd.md`.

## Quality gate

A quality gate = automated, objective conditions code must satisfy before it may
be merged. It lives in two places: the local build (stops the push) and the
pipeline (stops the merge).

Typical conditions:
- all tests pass;
- style/convention checks pass (Checkstyle, ESLint, Ruff, …);
- bug-pattern checks pass (PMD, SpotBugs, Sonar rules, …);
- no new duplication above a threshold (CPD, jscpd);
- complexity limits per method (e.g. cyclomatic complexity ≤ 10);
- coupling limits (e.g. class fan-out ≤ 20) and allowed dependencies between
  modules (import control / architecture tests);
- coverage threshold, preferably on **branch** coverage, and "**must not
  decrease**" for new code.

Two decisions are separate: *what counts as acceptable* (the rule configuration –
the team's standard) and *whether violations fail the build* (e.g. Maven
`failOnViolation`). A report nobody must act on is not a gate.

Before merging a feature, compare metrics with the main branch: coverage must not
drop, coupling and smells must not rise, no new bugs. If they do, fix or record an
issue and let the user decide.

Maven reference configuration: `references/maven-quality-gate.md`.

## Reading metrics

A metric measures an **indicator**, not the quality itself. A value out of range
is a question ("look here"), not a verdict.

| Metric | Measures | Guideline | Typical action |
|---|---|---|---|
| Cyclomatic complexity (CC) | Independent paths in a method (decisions + 1) | 1–10 fine, 11–20 consider refactoring, > 20 refactor | Extract method, guard clauses, polymorphism; CC = minimum tests for full branch coverage |
| LCOM (e.g. LCOM-HS 0..1) | Lack of cohesion: do methods share fields? | < 0.3 good, > 0.7 poor (DTOs are high by design) | Extract class |
| Fan-in / fan-out; Ca / Ce | Incoming / outgoing dependencies (class / package) | High fan-out = fragile; high fan-in = must be stable | Split responsibilities, introduce interfaces |
| Instability I = Ce / (Ca + Ce) | 0 stable … 1 unstable | Depend in the direction of stability; no cycles | Invert dependencies |
| Duplication | % duplicated lines/blocks | < 3% good, > 5% problematic | Extract shared code (if truly the same knowledge) |
| Coverage | Code executed by tests | Trends over absolutes; branch over line | Add tests for uncovered branches |

Details, formulas and technical debt: `references/quality-metrics.md`.

## Dependency management

- Declare direct dependencies with explicit versions; let the tool resolve
  transitive ones, and inspect them (`mvn dependency:tree`, `npm ls`,
  `pipdeptree`).
- Use the narrowest scope (`test`, `devDependencies`, …).
- Released versions are immutable; snapshots/pre-releases are not reproducible.
- Scan dependencies for vulnerabilities in CI (OWASP Dependency-Check,
  `npm audit`, Dependabot/Renovate) – a security fitness function.

## Delivery and releases

A release = **version** (semantic versioning) + **artefacts** + **release notes**.
- Tag what you release; release what you tag; releases must be reproducible from
  the tag (no snapshots, no environment-dependent paths).
- Generate release notes from Conventional Commits where possible.
- Release jobs run only on version tags, separate from test jobs.
- Secrets come from masked, protected CI variables or job tokens – **never commit
  tokens**, never use personal tokens in pipelines.
- Know about checksums/signing once you publish binaries.

## Logs of your tools

Build and VCS tools log too: `mvn -X` (debug) / `-q` (quiet), `GIT_TRACE=1`, IDE
logs. Use them to diagnose build failures before guessing.
