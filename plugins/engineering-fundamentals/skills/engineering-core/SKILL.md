---
name: engineering-core
description: Core engineering discipline for any code change. Use whenever you write, change, fix, refactor or plan code in any language, before you start editing. Sets the working loop (understand, test, small steps, verify), the Definition of Done, and routes to the specialised skills of this plugin.
---

# Engineering Core

Software engineering is programming over time: code is read, changed and run by
other people (and other agents) long after it was written. Optimise for the next
person who has to change this code, not for the fastest way to make it work once.

Two ideas drive everything in this plugin:

- **Learning** – work in small, verified steps and decide on evidence (tests,
  measurements, feedback), not on gut feeling.
- **Managing complexity** – keep accidental complexity (complexity you add) as low
  as possible; the problem's essential complexity is hard enough.

## The working loop

For every non-trivial change, follow this loop. Skip steps only when the change is
truly trivial (a typo, a version bump).

1. **Understand the goal.** Restate what the user wants as an outcome: who
   benefits, what must be true afterwards. If the request describes *how* instead
   of *what*, ask for (or infer and state) the underlying goal. For features, see
   the `feature-to-code` skill.
2. **Understand the code you touch.** Read before you write. Find the entry point,
   follow one path to where the work happens, read the existing tests. See
   `understanding-code`.
3. **Secure the behaviour.** If the code you will change has no tests, write
   characterisation tests first that pin down today's behaviour. Refactoring or
   changing untested code is guessing.
4. **Plan small steps.** Break the work into steps that each leave the system
   working. Prefer test-first: one example → one failing test → simplest code that
   passes → tidy up. See `testing`.
5. **Wear one hat at a time.** A step either changes behaviour *or* restructures
   code, never both. Commit them separately. See `clean-code` and `git-workflow`.
6. **Verify after every step.** Run the tests (and the project's build/linters).
   Never report work as done when the build is red or tests were not run.
7. **Leave it cleaner.** Fix small things in code you touched (a bad name, a magic
   number, dead code). Do not start unrelated rewrites.
8. **Explain what you did.** End with a short plain-language summary (see below).

## Simplicity rules (anti over-engineering)

Good design is the *simplest* design that keeps change cheap.

- Write only the code the current requirement needs. No speculative features,
  options or layers "for later" (YAGNI).
- Add an abstraction (interface, strategy, factory, layer) only when at least one
  of these is true: there is real variation *now*, a collaborator must be replaced
  in tests, or you are removing duplication for the third time (rule of three).
- Prefer clear and boring over clever. Readability beats saving lines.
- Prefer the language's and project's existing conventions over your own taste.
- When unsure between two designs, pick the one that is easier to test and easier
  to delete later.

## Quality criteria to aim for

Use these to judge any change. With good testability the others usually follow.

| Criterion | Question to ask |
|---|---|
| Testability | Can this be tested automatically, fast, in isolation? |
| Deployability | Is the system still in a releasable state after this change? |
| Fast feedback | Will a mistake show up within minutes (test, build, CI)? |
| Controlled variables | Is everything needed to build and run it in version control (config as code)? |
| Continuous delivery | Can build, test and release run without manual steps? |

## Design principles (short form)

Modularity, high cohesion, loose coupling, separation of concerns, abstraction /
information hiding. They apply at method, class and system level. Details and
SOLID: `software-design`.

## Definition of Done

A change is done only when **all** apply (adapt to the project's own DoD if it has
one):

- [ ] The requested behaviour works and matches the acceptance criteria/examples.
- [ ] New or changed behaviour is covered by meaningful automated tests that
      would fail without the change (check boundaries and error cases, not only the
      happy path).
- [ ] The full build passes (e.g. `mvn clean verify`, `npm test && npm run lint`,
      `pytest`), including the project's static checks.
- [ ] No new code smells in touched code; names reveal intent; no magic numbers,
      dead code or commented-out code.
- [ ] Public APIs you added or changed are documented (contract: inputs,
      guarantees, errors).
- [ ] Docs/ADRs are updated if a design decision or usage changed.
- [ ] Changes are committed in small, focused commits with meaningful messages
      (only if the user wants commits).
- [ ] Nothing secret, generated or machine-specific was added to version control.

If you cannot meet an item (no test runner, no permission to run the build), say
so explicitly instead of implying it was done.

## Explaining your work

Many users cannot read every line you write. After a change, give a summary that a
non-expert can follow:

1. **What changed** – in terms of behaviour, not files.
2. **Why it is built this way** – one or two sentences on the main design choice
   and the alternative you rejected.
3. **How it was verified** – which tests/build ran and their result.
4. **What is left / risks** – open questions, known limits, follow-ups.

Explain technical terms briefly the first time (e.g. "a *mock* is a stand-in object
used in tests"). Never hide a failing test, a skipped step or an assumption.

## Which skill to use

| Situation | Skill |
|---|---|
| Writing or reviewing code readability, smells, refactoring | `clean-code` |
| Structuring classes/modules, interfaces, SOLID, contracts | `software-design` |
| Writing tests, TDD, choosing test data, mocks, coverage | `testing` |
| Turning a feature request into stories, examples, tests | `feature-to-code` |
| Getting into an unfamiliar codebase or explaining code | `understanding-code` |
| Commits, branches, merges, pull requests, versioning | `git-workflow` |
| Build tools, CI pipelines, quality gates, metrics, releases | `build-and-ci` |
| Architecture, quality attributes, ADRs, diagrams, API docs | `architecture-and-docs` |
| Adding or reviewing logging | `logging` |
| Working as an autonomous agent or designing agent workflows | `agentic-workflow` |
| Reviewing a change or a pull request | `code-review` |
