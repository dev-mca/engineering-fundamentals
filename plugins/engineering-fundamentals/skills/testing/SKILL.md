---
name: testing
description: Automated testing and test-driven development. Use when writing or reviewing tests, doing TDD (red-green-refactor), deciding what to test, choosing test data (equivalence classes, boundary values), isolating code from databases, networks, clocks or LLMs with stubs/mocks/fakes, fixing flaky tests, or interpreting code coverage.
---

# Testing

Without tests, the behaviour of software is unknown and every change is a risk.
Automated tests make that risk cheap to check after every change. They are also
the most trustworthy documentation: they fail when they stop being true.

**Generated code needs tests more, not less.** Plausible is not correct: generated
code reads convincingly, so off-by-one errors, swapped arguments and unhandled
cases slip through review. And tests must come from the **specification, not from
the implementation** – tests derived from existing code encode its bugs and pass.

## Test-driven development (default way of working)

1. Write a **test list**: the behaviours the feature needs, simplest first (often
   an edge case: empty input, zero capacity).
2. Pick **one** item. Write the test (Given/When/Then). Make it compile.
3. Run it – it must **fail**, for the reason you expect (🔴). A test that passes
   immediately is either redundant or not testing what you think.
4. Write the **simplest code** that makes it pass (🟢). Add new ideas to the list
   instead of implementing them now.
5. Run **all** tests.
6. **Refactor** test and production code while green (🔵). Run all tests again.
7. **Commit** – behaviour and refactoring in separate commits
   (red → green → commit → refactor → commit).
8. Repeat until the list is empty.

Fixing a bug = TDD too: first a test that reproduces the defect and fails, then
the fix. The test guards against regression forever.

When working as an agent, make the red step visible (run and report the failing
test before implementing) so a human can review that the test really tests the
requirement.

## What to test

- Test anything that can break: happy path first, then error cases ("how could I
  break my own code?").
- Test **your** code, not libraries or the framework.
- Skip trivial getters/setters and truly generated code (regenerated from a
  checked spec). AI-written code is *not* "generated" in this sense – test it like
  hand-written code.
- Test behaviour through public interfaces, not private internals.

**Right-BICEP** – what to check: **Right** results, **B**oundary conditions,
**I**nverse relationships, **C**ross-check with another method, forced **E**rror
conditions, **P**erformance (measure, don't guess).

## Properties of a good unit test – FIRST

- **Fast** – milliseconds. Slow suites stop being run.
- **Isolated** – one behaviour; independent of other tests and of order.
- **Repeatable** – same result every run: no real clock, randomness, shared DB or
  network. Inject them.
- **Self-validating** – asserts automatically; no reading console output.
- **Timely** – written with (ideally before) the code.

Plus: small, descriptive name, visible Given/When/Then structure, production code
quality. Details and test smells: `references/test-quality.md`.

## Structure and naming

```java
@Test
void rentalOfEightDaysGetsTenPercentDiscount() {
    // Given
    Rental rental = new Rental(car, days(8));
    // When
    Money fee = rental.fee();
    // Then
    assertEquals(Money.chf("252.00"), fee);
}
```

- Name states the claim: behaviour + condition + expected outcome. Pick one naming
  convention per project and keep it.
- One behaviour per test; multiple asserts are fine if they verify the same
  behaviour (use `assertAll` to report all failures).
- Compare floating point with a tolerance; better, use decimal types for money.
- Expected exceptions with `assertThrows` (never a `try/catch` that can pass
  silently).
- Name the cases that carry meaning; parameterise the rest.

## Choosing test data

Gut-feeling data leaves regions untested, duplicates tests, misses `<` vs `<=`,
and gives no stopping criterion. Use:

1. **Equivalence classes** – partition each input into ranges with the same
   expected behaviour; one representative per class (not a boundary value).
2. **Boundary values** – for each class, the values at its edges (just inside and
   just outside), described in words first ("smallest valid order", "largest
   valid order + 1"), then translated to concrete values (`1`, `21`,
   `Integer.MAX_VALUE`, `null`, empty list).
3. **Combine** parameters, then prune combinations the logic makes redundant
   (e.g. for an AND condition, pair each invalid class with valid values).
4. Parameterised tests per expected outcome keep the suite compact.

Systematic test data often reveals gaps in the requirement – raise them as
questions instead of guessing. Worked examples: `references/test-data-design.md`.

When behaviour depends on **state or history** (remaining capacity), design call
sequences; on **time**, inject a controllable clock; for **many booleans**, use
pairwise testing or reduce the parameters; for "**any valid input**", consider
property-based testing.

## Isolation with test doubles

Replace collaborators that are slow, non-deterministic, external or unavailable
(DB, HTTP services, payment providers, file system, clock, LLM calls):

| Double | Does | Use for |
|---|---|---|
| Dummy | Fills a parameter, never used | Required argument the test ignores |
| Stub | Returns canned answers | Collaborator must return specific values |
| Fake | Simplified working implementation (in-memory repo) | Realistic collaborator without infrastructure |
| Spy | Stub that records calls | Check a call happened, without strict expectations |
| Mock | Pre-programmed expectations | Verify an interaction is the observable effect |

Rules:
- Prefer **state verification** (assert on results); use behaviour verification
  (`verify(...)`) only when the interaction itself is the requirement
  ("confirming a booking charges the card").
- **Don't mock what you don't own** – wrap third-party APIs (payment SDK, HTTP
  client) in your own interface and mock that; test the wrapper separately with
  integration/contract tests.
- Don't mock value objects; construct real ones.
- Tests dominated by `verify()` or with long mock setups are a design smell:
  too many collaborators (SRP), fat interfaces (ISP), or message chains (Demeter).
  Listen to the tests – fix the design.
- Use real collaborators when they are cheap, deterministic and I/O-free.

Details, Mockito examples, sociable vs solitary tests: `references/test-doubles.md`.

## Coverage

Coverage shows which code the tests **executed**, not whether they **verified**
it. Use it to find gaps, never as proof of quality or as a personal target.

- Prefer **branch** coverage over line coverage – 100% lines can hide a never-taken
  `else` (and its `NullPointerException`).
- Cyclomatic complexity = minimum number of tests for full branch coverage.
- Watch trends and "coverage must not decrease" rules rather than absolute
  numbers; exclude generated code.
- Boundary tests often add no coverage but catch the off-by-one bugs.

## Test levels (pyramid)

Many fast **unit** tests at the base; fewer **integration** tests (component +
DB/REST); few **end-to-end/UI** tests; manual/exploratory testing only where
automation is impossible. Unit tests run before every commit, integration tests in
CI, long-running suites nightly.

## Before you finish

- [ ] Every new behaviour has a test that failed before the change.
- [ ] Boundaries and error cases are tested, not only the happy path.
- [ ] Tests are deterministic (no `now()`, random, network, shared state).
- [ ] The whole suite passes; no test was disabled or weakened to make it pass.
- [ ] If you could not run the tests, you said so.
