---
name: feature-to-code
description: Turn a feature request into working, tested code. Use when the user describes a new feature, requirement or rule, when requirements are vague or incomplete, when writing user stories, acceptance criteria or use cases, running an example-mapping session, writing Gherkin (Given/When/Then) scenarios, or planning how to implement a requirement step by step.
---

# From Feature to Code

A feature says **what** should be possible, **for whom**, and **why** it has
value. Modern practice does not design everything up front: with a rough
architecture in place, the detailed design emerges from concrete examples that
drive tests, which drive the implementation. Write only what the current example
needs; refactor early.

Understanding what the user actually needs is the part an agent cannot skip.
Requirements often arrive as a solution ("add a dropdown with…") – find the goal
behind it.

## Step 1 – Clarify the goal

- **Who** benefits? (A specific role/actor, not "the user". Actors can be other
  systems, e.g. a payment provider or inventory system.)
- **What** outcome is wanted? **Why** is it valuable?
- Non-functional needs: speed, load, availability, security, regulations
  (record them – they drive architecture).

Write it as a story, value first if helpful:

> In order to give customers an exact price on the phone, as an employee I want to
> see the total rental fee including discounts when I enter the rental period.

A story is a token for a conversation, not a specification.

## Step 2 – Rules and examples (example mapping)

For each story, collect (in a ~25-minute conversation, or by asking the user):

- 🟨 **Story** – the story itself.
- 🟦 **Rules** – business rules / acceptance criteria
  ("rentals of 7–14 days get 3% discount").
- 🟩 **Examples** – concrete cases for each rule
  ("10 days at CHF 50/day → CHF 485").
- 🟥 **Questions** – what nobody can answer yet
  ("is the 14th day 3% or 7%?").

Interpretation:
- many rules → the story is too big; split it;
- many questions → clarify with the product owner/user before building;
- examples for each rule and only one or two questions → start implementing; park
  the questions.

As an agent: do not silently invent answers to red-card questions that change
behaviour. Ask, or state your assumption explicitly and make it easy to change
(a named constant, a single place in the code, a test that documents it).

Also agree on **done**: acceptance criteria (functional scope) and the Definition
of Done (quality: tests, build, docs – see `engineering-core`).

## Step 3 – Write examples as Gherkin

```gherkin
Example: Borrow a book successfully
  Given Toni has fewer than 6 items borrowed
  And the book is not a short-term loan
  When Toni borrows the book
  Then the book is loaned
  And the return date is 3 weeks from today

Example: Borrowing rejected at the limit
  Given Toni has 6 items borrowed
  When Toni borrows a book
  Then the book is not loaned
  And the book status remains available
```

- Example title → test name; Given → fixture (arrange); When → action (act);
  Then → assertions.
- Domain experts can read them; the shared understanding comes from the
  conversation, not from the file.
- Scenarios can run as BDD acceptance tests (Cucumber etc.) or be inlined as
  comments in unit tests.

Writing the steps in plain language before code makes the intent explicit and
reveals the objects the feature needs (e.g. `Book`, `Member`, `Loan`). A quick
sketch of those classes is useful; keep it short-lived.

## Step 4 – Complete the examples systematically

Examples show that a rule exists, not that its edges are tested. Derive
equivalence classes and boundary values for each rule (see the `testing` skill, especially
`testing/references/test-data-design.md`). This usually produces new questions for the
product owner – ask them.

## Step 5 – Implement test-first, example by example

1. Start with the smallest, simplest example (often an edge case).
2. Put its Given/When/Then as comments into a new test; write the test code; let
   the IDE/tooling generate the missing methods.
3. Run → red. Implement the simplest thing → green. Commit.
4. Refactor while green. Commit separately.
5. Next example. Push frequently (continuous integration).

The result: no unused code, no speculative design, and a self-testing codebase in
which every rule is documented by a test.

## Use cases (alternative/complement to stories)

A use case diagram gives an overview of what a system does for its actors – also
useful to reverse-engineer an existing (brownfield) system.

- **System boundary** – a rectangle; actors outside, use cases inside.
- **Actors** – people or systems; primary (initiating) on the left, secondary
  (called by the system) on the right.
- **Association** – actor ↔ use case (solid line). Two actors on one use case =
  both are required (AND). An OR between actors is expressed by generalisation.
- **Include** – the base use case always includes the other (shared sub-flow).
- **Extend** – optional extension under a condition (write the condition as a
  note).
- **Generalisation** – between use cases or between actors.
- No associations between use cases.

Granularity: a use case delivers value to an actor, can be completed by the
primary actor in one go, and leaves nobody waiting afterwards.

PlantUML notation: see `architecture-and-docs/references/uml-plantuml.md`.

## Collaborative implementation (when humans are involved)

- **Pair programming** – driver types, navigator reviews and thinks ahead; swap
  every 10–15 minutes or after each failing test.
- **Ensemble (mob) programming** – the whole team, one keyboard; ideas reach the
  computer through someone else's hands; rotate every 5–15 minutes.
Both build review into the work, so no separate review step is needed.

## Deliverables of this skill

When asked to plan or implement a feature, produce (in the reply or the repo):
story/goal, rules, examples, open questions, the test list derived from them, then
the test-driven implementation and a summary of which rules are covered by which
tests.
