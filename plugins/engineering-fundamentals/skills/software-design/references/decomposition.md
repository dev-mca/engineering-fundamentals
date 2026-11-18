# Decomposing a System into Subsystems

System design consists of two activities:

1. **Define design goals** from functional and non-functional requirements (they
   often conflict → explicit trade-offs; see `architecture-and-docs`).
2. **Decompose** the system into subsystems with clean responsibilities, high
   internal cohesion, loose coupling between them, and appropriate abstractions.

## Terms

- **Module** – any unit with an inside and an outside separated by a boundary
  (function, class, package, service, whole monolith). Modules nest.
- **Subsystem** – the unit decomposition produces: large enough to own an area of
  responsibility, offering its functionality through a defined interface.
- **Service** – a set of operations a subsystem provides through an interface. A
  subsystem is described by its services, not by the classes inside it.

## Starting points

- functional requirements (use cases, user stories) → services,
- non-functional requirements and quality attributes,
- a static domain/object model, where one exists.

## Three routes

### Top-down: from use cases
Group related use cases; each subsystem offers a coherent set of services. If a
subsystem's services have no semantic connection, split it. Minimise coupling
between subsystems.

Example (route planner in a car): use cases *enter destination*, *calculate
route*, *show map*, *guide by voice*, *receive traffic info*, *update maps* →
subsystems such as *Navigation* (destination, route calculation), *Map* (display,
updates), *Guidance* (voice), *Traffic* (incoming info), each providing services
others require.

### Bottom-up: from the object model
Draw the class dependencies, find clusters that are densely connected inside and
sparsely connected to each other, and make each cluster a subsystem. Then replace
the remaining direct class-to-class connection across the boundary with an
interface provided by one subsystem and required by the other.

```
Before:  [A]-[B] ──────► [D]-[E]        (class B calls a method of class D)
After:   «One»(A,B) ──requires──○ I ──provided by── «Two»(D,E)
```

Only the interface version tells a later reader what must be preserved if `Two`
is replaced.

### By impact of change
Ask which elements one particular change would affect, and put them in one
module. This is separation of concerns applied as a procedure. Likely changes are
often visible in the requirements ("more payment providers will follow", "each
branch has its own discounts", "prices in other currencies").

In practice the routes are combined (Domain-Driven Design and EventStorming do so
implicitly).

## Notation

- **Lollipop (provided/required interface)** – use once you know the interface.
- **Use-dependency (dashed arrow)** – only records that a dependency exists.

## Typical refactoring steps towards loose coupling

1. **Introduce interfaces** for functionality other components access, so the
   provider can change internally.
2. **Increase cohesion** – merge components that always change together or where
   one is tiny and mostly uses the other.
3. **Split interfaces** (ISP) – a client needing a fraction of an interface gets
   its own smaller interface, which can remove dependencies between clients.

## Checking a decomposition

- Can each subsystem be tested automatically from the outside through its
  interface? Then the boundary is probably good, and its inside can change
  without changing those tests.
- Do dependencies flow towards stable parts, without cycles?
- Can each subsystem be explained in one sentence?
- Would the next likely change stay inside one subsystem?
- Can the boundary be enforced automatically (module system, architecture tests
  such as ArchUnit, Checkstyle import control, dependency-cruiser)? See
  fitness functions in `architecture-and-docs`.

## Modular monolith first

When required scale or team size is unclear, start with a well-decomposed modular
monolith. Split out a separately deployed service only when a module has clearly
different load, scaling, availability or release needs – a good internal boundary
makes that split possible later.
