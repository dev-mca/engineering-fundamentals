---
name: understanding-code
description: Systematically understand and explain an unfamiliar or legacy codebase. Use before changing code you did not write, when onboarding to a repository, when the user asks "what does this code do", "explain my project", "where is X implemented", or when debugging behaviour you don't yet understand.
---

# Understanding Code

Most working time goes into reading code somebody else wrote – increasingly code
an AI wrote, faster than anyone reviewed it. Before changing a system you must work
out what it does; usually the source (and its tests) is the only honest
description. Don't read from the top of the package tree down; collect evidence.

## 1. Get a map (shallow pass)

- Skim the whole repository quickly without trying to understand details: size,
  languages, build files, package/module names, test folders, README, CI config,
  anything that looks odd. ("Read all the code in one hour" – for an agent: list
  the tree, read build files and the README, sample a few files per package.)
- Read the **package/module structure as a map** – the one design document the
  compiler enforces. Then check the **imports**: they are the real dependency list.
  Do they respect the structure (e.g. UI only talks to an API/service layer)?
- **Speculate, then check**: state where you expect something ("the discount rule
  is in the pricing/domain package") and verify. Being wrong reveals where the
  system isn't built the way it looks – valuable information.

## 2. Find the way in

Start from something observable, not from `main` (it shows start-up, rarely where
the interesting work is):

- **Search for text on the screen / in the output** (button labels, error
  messages, log lines, API paths) – it leads to the handler.
- **Find the handler** (listener, controller method, route, CLI command) – one
  handler shows you its siblings.
- **Look for the nouns** users talk about – they are classes (`Rental`, `Car`,
  `PriceCategory`) and show where the domain model lives.

## 3. Follow one path to the end (depth first)

From the entry point, follow the call into the method that does the actual work.
For each method ask: *does it do work, or hand the request on?* Skip pure
delegation; read calculating, deciding, formatting and storing code twice.

Note where the work sits: business logic in a view/controller is a finding – no
other caller can reach that rule and no test can run it without the UI.

Use call hierarchy / "find usages" and "go to definition" instead of scrolling.

If a passage stays unclear: **refactor to understand** in your working copy
(rename a variable to what you think it holds, extract a block into a method named
after what you think it does) and see whether your reading survives. Revert
unless the team wants the change.

## 4. Read and write tests

Tests are the documentation that fails when it stops being true.

- Read a test as: **name** (the claim) → **assertion** (the criterion) → **setup**
  (what must exist; shows dependencies).
- Run a single test with coverage or a breakpoint to see which code it reaches.
- **No tests?** That is a finding: the current behaviour *is* the whole
  specification, defined by accident. Record it.
- **Write tests to understand**: instead of reasoning about what a method returns
  for an empty list, a null or a boundary, write a test and run it. Keep tests
  that reveal business rules and name them after the rule. Such tests are
  **characterisation tests** – they record what the code does (not necessarily
  what it should do) and are the safety net before changing it.
- Caveat: a test written after the code by the same person tends to describe the
  implementation rather than the requirement – weaker evidence.

## 5. Watch it run

Reading tells you what the code says; running it tells you what it does with real
data.

- Breakpoint at the method you study, trigger the feature like a user would.
- Step over (follow the method), step into (follow the work down), call stack
  (how did we get here?), variables view (watch a value become wrong).
- Conditional breakpoints for rare cases (`rentalDays > 7`).
- Timing-dependent or production-only failures can't be debugged this way – use
  logs (see `logging`).
- As an agent without a debugger: run small scripts/tests, add temporary log
  output, inspect results, then remove the instrumentation.

## 6. Draw the control flow when paths multiply

When a method is hard because of many paths, draw an activity (control flow)
diagram: start → statements in sequence → a decision diamond per branch, one path
per outcome → loops back → stop. **Write boxes in plain language, not code**
("apply long-rental discount", not `if (d > 7) f *= 0.9`). A non-programmer can
then check it, and it survives implementation changes. The number of independent
paths = cyclomatic complexity = minimum number of tests for branch coverage.

PlantUML activity syntax: `architecture-and-docs/references/uml-plantuml.md`.

## 7. Write it down where the code is

Record: entry point, classes the feature passes through (in order, one line each),
where the work happens, surprises. Put open questions next to the code (a TODO
with context, or an issue referencing file and line), not in private notes.

## Explaining code to the user

When the user asks what their code does, answer at their level:

1. One-paragraph purpose of the system/feature in domain language.
2. The main parts (modules/classes) and what each is responsible for – a small
   diagram helps (component or sequence diagram).
3. The path of one typical request through the code.
4. Risks found: untested areas, logic in the wrong place, smells, surprising
   behaviour – with concrete file references.
5. Suggested next steps (e.g. characterisation tests before changes), without
   changing code unless asked.
