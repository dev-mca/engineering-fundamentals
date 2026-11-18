---
name: clean-code
description: Rules for readable, maintainable code and safe refactoring. Use when writing new code, cleaning up or refactoring code, fixing smells (long methods, magic numbers, duplication, feature envy, message chains / Law of Demeter, large classes, shotgun surgery), naming things, or when the user says the code is messy, hard to read or too complicated.
---

# Clean Code

Code is read far more often than it is written, and most of its lifetime cost is
maintenance. Clean code is code a teammate understands without effort: its purpose
is obvious, it does one thing, it has no surprises, and it is easy to change
without breaking something. Clean code is not clever code.

Generated code needs the same standard. Agents produce working but badly structured
code easily; the person committing it is still responsible for it.

## Rules while writing code

### Names
- Names reveal intent. If a name needs a comment, rename it.
- Classes/types are nouns (`Rental`, `PriceCalculator`), methods are verbs
  (`calculateFee()`), booleans read as questions (`isActive()`, `hasCapacity()`,
  `canRentMore()`).
- One word per concept across the codebase (don't mix `get`/`fetch`/`retrieve`).
- No encodings or type prefixes (`strName`, `iCount`), no disinformation
  (`accountList` that is not a list), no near-identical names.
- Pronounceable, searchable names. Single letters only for tiny loop scopes.
- Long scope → longer, more descriptive name; tiny scope → short name is fine.

### Functions / methods
- Do one thing, at one level of abstraction. A useful test: if you can extract a
  meaningful sub-function, the method did more than one thing.
- Prefer separating **integration** methods (only call other methods, read like a
  recipe) from **operation** methods (contain the logic).
- Order methods top-down (step-down rule): caller above callees.
- Rule of thumb: > ~15–20 lines in OO code deserves a second look; deep nesting
  (> 2 levels) usually means a missing extraction or guard clause.
- Few parameters. Many parameters → introduce a parameter object or move the
  behaviour.
- No flag/selector arguments (`ship(country, isEU)`): split into two methods.
- No output parameters: mutate the owning object (`report.appendFooter()`) or
  return a new value.
- Prefer positive conditionals (`shouldCompact()` over `!avoidCompaction()`), and
  encapsulate complex conditions in a well-named method or variable.
- Use boolean expressions directly (`return a < b;`, never `if (x == true)`).
- Fail fast: validate preconditions with guard clauses at the top.
- Avoid inappropriate statics: a method that operates on an object's data belongs
  to that object (allows polymorphism and testing).

### Values, variables, comments, formatting
- No magic numbers or strings: extract named constants (`LONG_RENTAL_THRESHOLD`).
- Declare variables close to first use; one purpose per variable.
- Explanatory variables for complex expressions.
- Comments explain **why** (a constraint, a workaround, a decision), never repeat
  **what** the code says. Document public APIs (see `architecture-and-docs`).
- Delete dead code and commented-out code – version control remembers it.
- Format consistently using the project's formatter/linter; blank lines separate
  concepts; keep lines readable (~100–120 chars).
- Don't optimise prematurely; write it clearly first, measure before optimising.

### Errors
- Use exceptions (or the language's error type), not error codes or `null`.
- Catch specific exceptions, only where you can react meaningfully.
- Never swallow exceptions silently. Don't use exceptions for normal control flow.
- Keep `try/catch` out of tight loops – extract the body.

## Refactoring

Refactoring = changing structure **without** changing observable behaviour.

**Prerequisites (non-negotiable):** version control, passing tests that cover the
code (write characterisation tests first if missing), a build you can run.

**The cycle – one refactoring at a time:**
1. Identify the smell and name it.
2. Run the tests – they must be green before you start.
3. Choose the matching refactoring (see `references/refactoring-catalog.md`).
4. Apply it, preferably with automated IDE/tooling refactorings (rename, extract,
   move) rather than hand-editing.
5. Run the tests. Red → undo immediately and retry smaller.
6. Commit the single refactoring (e.g. `refactor: extract fee calculation`).

**Two hats:** never mix a refactoring and a behaviour change in one step or one
commit. If a test fails you must know which of the two caused it.

**When to refactor:** before adding a feature (make the change easy, then make the
easy change), right after the test goes green in TDD, after a hard-to-find bug, and
on the third occurrence of duplication (rule of three). Not as a big-bang rewrite.

**Refactoring and agents:** when you (the agent) refactor, keep steps small and
mechanical, run the tests after each step, and report which refactorings you
applied. Do not "improve" code outside the requested scope without asking.

## Smell → fix quick map

| Smell | Typical fix |
|---|---|
| Magic number/string | Extract constant |
| Inconsistent / unclear naming | Rename |
| Dead or commented-out code | Safe delete |
| Obscure temporary variable | Replace temp with query, split variable |
| Long method | Extract method |
| Duplicated code | Extract method / extract class, then reuse |
| Insider trading (touching another class's fields) | Encapsulate field, move method |
| Feature envy (method uses another class's data more than its own) | Move method |
| Message chain `a.getB().getC().getD()` (Law of Demeter) | Hide delegate: add an intention-revealing method on the first object |
| Large class / low cohesion | Extract class by responsibility |
| Divergent change (one class changes for unrelated reasons) | Extract class per reason to change |
| Shotgun surgery (one change touches many classes) | Move behaviour into one place (extract class/constant) |
| Flag argument | Split method |
| Long parameter list | Introduce parameter object |
| Switch on type repeated in many places | Replace conditional with polymorphism (only if it repeats) |

Details, examples and caveats:
- `references/code-smells.md` – method-level smells with before/after examples.
- `references/design-smells.md` – smells across classes (coupling, cohesion,
  Law of Demeter) with examples.
- `references/refactoring-catalog.md` – the refactorings and how to apply them
  safely.
- `references/tidy-first-checklist.md` – a quick checklist for tidying code before
  changing it.

## Static analysis

Let tools enforce the boring rules so reviews can focus on design: a formatter, a
linter/style checker (Checkstyle, ESLint, Ruff…), a bug finder (PMD, SpotBugs,
SonarQube…) and duplication detection, wired into the build. See `build-and-ci`.
A suppressed warning needs a comment saying why; many suppressions of the same rule
mean the rule is configured wrongly.
