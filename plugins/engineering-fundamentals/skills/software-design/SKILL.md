---
name: software-design
description: Class- and module-level design. Use when creating classes, interfaces or modules, deciding where code belongs, splitting a growing class or system into parts, introducing dependency injection, applying SOLID, cohesion/coupling, separation of concerns or information hiding, defining preconditions/postconditions/invariants (design by contract), or making code testable and easy to change.
---

# Software Design

Good design is design that keeps the cost of change low: changes stay local, safe
and proportional in effort, and people who did not write the code can still
maintain it. Design is judged mainly by **testability** – if a part can easily be
tested automatically from the outside, its boundaries are probably good.

Most work happens in existing systems: understand and evaluate the current design
before deciding how to implement a change.

## The five design principles

They apply at every level: method, class, package/module, service.

| Principle | Meaning | Warning signs |
|---|---|---|
| **Modularity** | Split the system into parts with a clear inside and outside | Everything in one file/class; no boundaries |
| **High cohesion** | What is inside a module belongs together (prefer grouping by *domain*, not by technical type) | Methods that use disjoint fields; a class needing many methods of another class |
| **Loose coupling** | Modules depend on each other as little and as abstractly as possible | Changing one module breaks others; concrete classes `new`-ed everywhere |
| **Separation of concerns** | Each module addresses one concern (e.g. validation, calculation, persistence, presentation) | A method that validates, transforms *and* saves |
| **Abstraction / information hiding** | Expose only what callers need; hide internal decisions behind an interface | Public fields; leaking internal types; flag parameters |

Improving cohesion usually reduces coupling. Adding abstractions loosens coupling
but adds complexity – it is a trade-off, decided by context (see the simplicity
rules in `engineering-core`).

**Forms of coupling** (from least to most troublesome): control coupling via a
small interface (normal, keep interfaces small), shared environment (logger,
config – accept consciously), dynamic coupling (DI, observers – loose statically,
harder to trace), logical coupling (always change together – consider merging),
semantic coupling (one module silently relies on another having run first – the
hardest to spot; make it explicit).

## SOLID (class-level guidelines)

| | Principle | Rule of thumb | Testability benefit |
|---|---|---|---|
| S | Single Responsibility | A class has one reason to change = it serves one actor | One cause per failing test |
| O | Open/Closed | Add behaviour by adding new types, not by editing tested code | Existing tests stay untouched |
| L | Liskov Substitution | A subtype must honour its parent's contract (no stronger preconditions, no weaker guarantees, no surprise exceptions) | Doubles behave like the real thing |
| I | Interface Segregation | Small, client-specific interfaces | Stubs/mocks implement only what is needed |
| D | Dependency Inversion | Business logic depends on abstractions; details implement them; wire at a composition root (constructor injection) | Every collaborator replaceable in tests |

Apply SOLID to remove a concrete pain (hard to test, frequent edits to the same
`if/else` chain, a class changed by different stakeholders), not by default. Full
explanation and examples: `references/solid.md`.

## Making code testable (design smells that block isolation)

| Smell | Refactoring |
|---|---|
| `new ConcreteService()` inside business logic | Constructor injection of an interface |
| Static calls to non-deterministic code (`now()`, `random()`, file/network APIs) | Pass a `Clock`/value as parameter, or wrap the static API in a small injectable class |
| `Singleton.getInstance()` | Inject the instance |
| Concrete field without injection point | Constructor parameter |
| Business logic inside UI handlers or controllers | Move into a domain/service class the UI calls |

Last resort for legacy code: extract the untestable call into a protected method
and override it in a test subclass.

```java
// Before: hard-wired, untestable
class OrderService {
    private final EmailNotification email = new EmailNotification();
    void placeOrder(Order o) { /* ... */ email.notify("Order confirmed: " + o.id()); }
}

// After: depends on an abstraction, wired once at the composition root
interface NotificationService { void notify(String message); }

class OrderService {
    private final NotificationService notifier;
    OrderService(NotificationService notifier) { this.notifier = notifier; }
    void placeOrder(Order o) { /* ... */ notifier.notify("Order confirmed: " + o.id()); }
}

// main / composition root
var service = new OrderService(new EmailNotification());
```

## Design by contract

Make the behaviour of every public method explicit:

- **Preconditions** – what the caller must guarantee (valid parameter ranges,
  required state). Enforce with guard clauses that fail fast.
- **Postconditions** – what the method guarantees afterwards. Verify with unit
  tests.
- **Invariants** – what is true for every instance after construction and before
  and after every public method call. They drive constructor validation.
- **Exception conditions** – which errors occur when, documented with the method.

Contracts map directly to tests: preconditions → *Given*, action → *When*,
postconditions → *Then*. Boundaries of the contract are your boundary-value tests.
Details and a worked example: `references/design-by-contract.md`.

## Decomposing a system

When something grows (new requirement, new team, new deployment needs), split it
into subsystems with high internal cohesion and small interfaces between them.
Three routes, often combined:

- **Top-down** – group related use cases; each subsystem offers a coherent set of
  services. Services with no semantic connection → split further.
- **Bottom-up** – cluster the domain object model; cut where clusters are joined by
  few dependencies, then replace the direct dependency with an interface.
- **By impact of change** – group everything one likely change would touch.

Prefer showing relationships as provided/required interfaces (lollipop notation)
once you know the interface; a plain dependency arrow hides what must be preserved
when replacing a part. Details: `references/decomposition.md`.

## Extension points and plugins

When new variants must be added *without touching the core* (new payment
providers, file formats, regional rules), define an extension point: a small,
stable interface owned by the core, implementations registered from outside (DI,
configuration, service loader, plugin registry). Trade-off: good extension
points are hard to design and the contract is hard to change later – don't build
one for a single implementation.

## Checklist before you finish a design change

- [ ] Each new class/module has one clear responsibility you can state in a
      sentence.
- [ ] Dependencies point from volatile/detail code towards stable/abstract code;
      no cycles between packages/modules.
- [ ] Business rules are reachable and testable without UI, DB, network or clock.
- [ ] Interfaces are small and named after what clients need.
- [ ] Public methods have explicit contracts and guard clauses.
- [ ] No abstraction exists that has no current reason.
- [ ] The design decision and its trade-off are explained (and recorded as an ADR
      if significant – see `architecture-and-docs`).
