# Quality Metrics and Technical Debt

## Quality model

ISO/IEC 25010 defines eight product quality characteristics: functional
suitability, performance efficiency, compatibility, usability, reliability,
security, maintainability, portability. Developers influence two directly through
the code: **functional suitability** (measured by tests) and **maintainability**
(modularity, reusability, analysability, modifiability, testability – measured by
static metrics). Code that works but can't be changed is a liability; well
structured but untested code can't be changed with confidence.

Internal quality isn't traded against time and cost – high internal quality
lowers the cost of future features. Because its decline produces no visible
event, it must be measured – automatically, on every build.

A useful metric is measurable, independent (can't be gamed), reliable and
accurate. Static metrics read the code; dynamic metrics (coverage, runtime,
memory) are collected while running.

## Cyclomatic complexity (McCabe)

Number of independent paths = **decision points + 1**. Counted (e.g. by
Checkstyle): `if`, `while`, `do`, `for`, `case`, `catch`, `?:`, `&&`, `||`.
`else`/`default` don't count. Equivalent: regions of the control flow graph
(including the outer region).

| CC | Interpretation |
|---|---|
| 1–10 | simple, low risk |
| 11–20 | moderate; consider refactoring |
| 21–50 | high; hard to test thoroughly |
| > 50 | very high risk |

CC is the **lower bound of tests needed for full branch coverage**. Remedy:
extract methods, guard clauses, replace conditionals with polymorphism or lookup
tables. Exception: a flat 20-case `switch` dispatch can be perfectly readable.

Example – count for:

```java
public static int distributePatients(Hospital[] hospitals, int patients) {
    if (hospitals == null || hospitals.length == 0 || patients <= 0) {  // if, ||, ||  → 3
        return patients;
    }
    for (Hospital hospital : hospitals) {                                  // for → 1
        while (hospital.hasCapacity() && patients > 0) {                   // while, && → 2
            hospital.checkIn();
            patients--;
        }
        if (patients == 0) {                                               // if → 1
            return patients;
        }
    }
    return patients;
}
// CC = 7 + 1 = 8 → at least 8 tests for full branch coverage
```

## Cohesion: LCOM-HS (Henderson-Sellers)

LCOM-HS = (m − avg(m(v))) / (m − 1), where m = number of methods, v = attributes,
m(vᵢ) = methods accessing attribute vᵢ. Range 0..1.

| LCOM-HS | Interpretation |
|---|---|
| 0 – 0.3 | good cohesion |
| 0.3 – 0.7 | check for several responsibilities |
| > 0.7 | poor; probably several concerns |

Example: a `UserManager` with `users`, `logger`, `emailService`, `auditTrail`,
where `sendNewsletter` uses only users+email and `exportAuditLog` only the audit
trail → high LCOM → split into `UserRegistry`, `NewsletterService`,
`AuditExporter`. A `Rectangle` whose methods all use `width` and `height` → near
0. DTOs/value objects score high by construction – a deliberate design, not debt.

## Coupling

- **Fan-in** – how many modules call this one (high → must be stable and well
  tested).
- **Fan-out** – how many modules this one calls (high → fragile, doing too much,
  e.g. a controller using eight services).
- **Afferent coupling Ca** (package level) – classes outside depending on this
  package. **Efferent coupling Ce** – classes inside depending on outside.
- **Instability I = Ce / (Ca + Ce)**: 0 = maximally stable, 1 = maximally unstable.
  Dependencies should flow towards stability (Stable Dependencies Principle):
  `controller (I=1) → service (I=0.5) → model (I=0)`. A package with high Ca *and*
  high Ce is rigid and fragile at once. Cycles are always a problem.

Reducing a controller's fan-out: introduce an application service/facade per use
case (e.g. `PlaceOrderUseCase`) that orchestrates the services, so the controller
depends on one abstraction.

## Duplication

Types: exact clones, parameterised clones, near-miss clones. Measured by token
sequence search with a minimum length (e.g. CPD with 50–100 tokens).

| Duplication | Interpretation |
|---|---|
| < 3% | good |
| 3–5% | acceptable, monitor |
| 5–20% | problematic |
| > 20% | severe |

Remove true duplication (DRY: every piece of knowledge has one authoritative
representation). Leave similar-looking code that will change for different
reasons.

## Coverage

Statement, branch (decision), path coverage; tools also report line, method,
class, instruction coverage.

- 100% line coverage can hide untested branches – look at branch coverage.
- Path coverage grows exponentially (10 independent ifs → 1024 paths); impractical.
- Coverage measures execution, not verification: a test without assertions still
  "covers".
- Diminishing returns above ~80%; exclude generated code and boilerplate.
- Don't use coverage as a personal performance metric; watch trends; enforce
  "must not decrease" and thresholds per class or for new code rather than a
  global average that hides untested classes.

Classic trap:

```java
public String pathExample(boolean condition) {
    String value = null;
    if (condition) { value = " " + condition + " "; }
    return value.trim();                      // NPE when condition == false
}
// One test with `true` → 100% line coverage, 50% branch coverage, bug undetected.
```

## Technical debt

Shortcuts and not-quite-right code accrue interest: every later change costs
more. Fowler's quadrant: deliberate vs inadvertent × reckless vs prudent.
Prudent deliberate debt ("ship now, fix next sprint") is legitimate *if repaid*;
reckless debt is the dangerous kind.

Metrics as debt indicators: high CC (complexity debt), high LCOM (cohesion debt),
high fan-out/Ce (coupling debt), low fan-in with high fan-out (possibly dead or
misplaced code), low coverage (test debt).

Managing it: quality gates for new code; the Scout Rule (leave code cleaner);
a visible refactoring backlog (issues with severity/priority and the impact of
each problem); conscious, recorded trade-offs (debt in a throw-away prototype is
fine, in a core module changed daily it is not). Tools like SonarQube estimate
debt in time – the trend matters more than the number.

## Suppressing false positives

Suppress as narrowly as possible (line > method > file), always with a comment
saying why. PMD: `// NOPMD` or `@SuppressWarnings("PMD.RuleName")`; Checkstyle:
suppression comments/filters or a suppressions file; JaCoCo: exclusion patterns.
A suppression states "the code is right and the rule doesn't apply here" – it is
not a way to get a red build green. Many suppressions of one rule mean the rule is
misconfigured.
