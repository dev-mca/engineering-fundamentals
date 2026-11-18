# Commit Messages

## Why it matters

The subject line is all most tools show (`git log --oneline`, PR lists, blame).
The body is where future readers learn *why*. A good history lets someone answer
"why is this here?" without asking you.

## Conventional Commits cheat sheet

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

| Type | Use for | SemVer effect |
|---|---|---|
| `feat` | New user-visible behaviour | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | – |
| `refactor` | Structure change, no behaviour change | – |
| `test` | Adding or fixing tests only | – |
| `perf` | Performance improvement | PATCH |
| `style` | Formatting, whitespace (no code meaning) | – |
| `build` | Build system, dependencies | – |
| `ci` | CI configuration | – |
| `chore` | Maintenance not covered above | – |
| `revert` | Reverts a previous commit | depends |
| any type with `!` or footer `BREAKING CHANGE:` | Incompatible change | MAJOR |

Scope: the module or area (`rental`, `pricing`, `api`). Description: imperative
mood ("add", not "added"/"adds"), lowercase, no trailing period.

### Examples

```
feat(pricing): apply branch-specific discount scales

Each branch can now define its own discount tiers. The German branch
uses 5% from 10 days and 12% from 21 days; Swiss branches keep the
existing tiers.

Closes #112
```

```
refactor(rental): extract fee calculation from RentalController

No behaviour change. Moves the calculation into RentalFeeCalculator so
it can be unit tested without the UI.
```

```
test(rental): add boundary tests for 7, 14 and 28 rental days
```

```
feat(api)!: return amounts as Money objects instead of doubles

BREAKING CHANGE: clients must read `amount.value` and `amount.currency`.
```

## Alternative conventions

- **Classic style** – free-form imperative subject, then body:
  `Fix currency conversion for CHF rentals`.
  Seven rules (Chris Beams): separate subject and body with a blank line; limit
  the subject to ~50 chars; capitalise it; no period at the end; imperative mood;
  wrap the body at 72; explain what and why, not how.
- **Issue-first** – `#87 Fix CHF currency conversion` for traceability-first
  teams.

Pick one per project and apply it consistently. Follow the existing history when
joining a project.

## TDD rhythm in history

A healthy test-driven history shows the feature growing behaviour by behaviour:

```
test: reject orders above vehicle capacity
feat(driver): accept orders within free capacity
refactor(driver): extract capacity check
feat(driver): reject deliveries later than 30 min before shift end
```

(Whether the failing test is its own commit depends on the team – a commit should
not leave the build red on a shared branch; locally or on a feature branch it
documents the red step.)

## Commit hygiene before a PR

Use interactive rebase on your own unpushed branch to squash "fix typo" commits
into the commits they belong to, reorder, or reword. Never on shared history.
