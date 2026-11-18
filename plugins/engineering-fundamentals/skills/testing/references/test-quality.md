# Test Quality: Smells, Fixtures, Naming

## Fixtures

- **Inline** – each test builds what it needs. Clear; duplicates quickly.
- **Delegate** – a helper/factory method builds the object (`createOrder(5)`),
  can take parameters for variants. Keeps setup visible in each test.
- **Implicit** – `@BeforeEach`/`setUp`. Fresh per test; use for infrastructure and
  common state only – a reader should understand a test from the test method.
- `@BeforeAll` only for expensive, read-only shared setup.
- Everything before the single action under test is fixture.

## Naming conventions (pick one per project)

| Convention | Example |
|---|---|
| method_state_expected | `divide_byZero_throwsException` |
| should_expected_when_state | `should_throwException_when_dividingByZero` |
| given_when_then | `given_negativeInput_when_abs_then_positiveResult` |
| descriptive sentence | `emptyListHasSizeZero` |

Name the system under test consistently (`sut`/`testee`) and the result (`result`)
if the project has no other convention.

## Test smells

| Smell | Problem | Fix |
|---|---|---|
| No assertion / assertion on the wrong thing | Passes without testing | Assert the expected outcome |
| Test swallowing exceptions | Passes on failure | `assertThrows` or let it propagate |
| Fixture code inside `assertThrows` | The exception may come from setup | Build the fixture outside, only the action inside |
| `now()`/random in tests | Flaky | Inject clock/seed |
| Too large test / multiple scenarios | Unclear failure reason | One scenario per test |
| Checking more than necessary | Breaks on unrelated changes (e.g. order of an unordered collection) | Assert only what the behaviour needs |
| Excessive setup | Hides what is tested; often SRP violation | Builders/helpers; split the class under test |
| Excessive mocking / checking fakes instead of the testee | Tests the mocks | Use real objects; assert on the testee |
| Conditional logic in tests | Hard to read, can hide branches | Separate tests / parameterise |
| Checking internals via reflection | Blocks refactoring | Test through the public interface |
| Test logic in production code | Production shaped for tests | Inject collaborators instead |
| Organised around methods, not behaviour | Brittle | Test complete small use cases |
| Chatty test (prints to console) | Manual inspection | Assertions |
| Erratic/flaky test | Destroys trust | Remove shared state, time, order dependence |
| Test only works on one machine | Environment-dependent | Run in CI; remove local dependencies |
| Obsolete test | Tests removed behaviour, blocks cleanup | Delete it |
| Disabled/skipped test committed | Hides broken behaviour | Fix or delete; never commit `@Disabled` to make CI green |

Example – fixture inside the lambda:

```java
// Smell: constructor might throw, test still passes
assertThrows(IllegalArgumentException.class, () -> {
    PizzaOrder order = new PizzaOrder(11, LocalDate.now().plusDays(3));
    order.validate();
});

// Better: fixture outside, fixed date, only the action inside
PizzaOrder order = new PizzaOrder(11, DELIVERY_DATE);
assertThrows(IllegalArgumentException.class, order::validate);
```

## TDD process smells

- Using coverage as the goal → tests that raise numbers but not confidence.
- No green bar for > ~10 minutes → steps too big.
- Not running the test before writing production code → you don't know it can
  fail.
- Not spending time refactoring → design debt accumulates.
- Skipping something "too easy" or "too hard" to test → bugs hide there; if hard,
  simplify the design.

## Useful TDD tactics

- **Fake it till you make it** – return a constant to get green, then generalise.
- **Triangulate** – a second example forces the real abstraction.
- **Obvious implementation** – if trivial, just write it; step back if red.
- **One to many** – implement for one element first, then for collections.
- **Learning test** – a test against a third-party API to confirm how it behaves.
- **Characterisation test** – records current behaviour of legacy code before
  changing it.

## Reasons people give for not testing (and why they don't hold)

"No time" (tests save time by catching defects early and enabling refactoring),
"too slow to run" (make them fast/isolated), "not my job" (developers must show
their code works), "don't know the expected behaviour" (then write a test to find
out and ask), "it compiles" (compiling is not working).
