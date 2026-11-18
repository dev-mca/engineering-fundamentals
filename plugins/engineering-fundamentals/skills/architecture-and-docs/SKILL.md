---
name: architecture-and-docs
description: Software architecture and technical documentation. Use when making or explaining significant design decisions, choosing an architectural style (layered, modular monolith, hexagonal, microservices, event-driven, plugin), weighing quality attributes and trade-offs (performance, scalability, availability, security, maintainability), writing architecture decision records (ADRs), drawing C4/UML diagrams (component, class, sequence, activity, use case) in PlantUML or Mermaid, documenting APIs (Javadoc, JSDoc, docstrings, OpenAPI), or keeping docs up to date with code.
---

# Architecture and Documentation

Architecture = the significant design decisions, where *significant* is measured
by cost of change. It is driven mostly by non-functional requirements, and it is
a team responsibility: decisions must be understood and shared, not handed down.

Neither big design up front nor no design: decide early what is expensive to
reverse, defer the rest to the last responsible moment.

## Decide early (costly to reverse)

- overall shape (client–server, web, mobile, distributed, sync vs async),
- code structure inside the parts (layers, features/modules, ports & adapters),
- technologies and frameworks,
- approaches to performance, scalability, availability, security,
- the domain model and its vocabulary (write a glossary).

## From requirements to design goals

Architecture drivers:
- **Functional requirements** – raise questions like sync vs async, where data
  lives, backward compatibility.
- **Quality attributes** – performance, scalability, availability, security,
  privacy, disaster recovery, accessibility, monitoring, audit, extensibility,
  maintainability, compliance, internationalisation/localisation. Pick the few
  that shape *this* system; several conflict.
- **Constraints** – budget, time, licences, existing systems (identity
  management, payment providers), deployment platform, organisation.
- **Principles** – coding standards, automation, team policies.
- **Security** always – authentication/authorisation, data protection (at rest,
  in transit, retention, GDPR), attack surface, auditability, dependency risk.
  Retrofitting it is always more expensive.

Ask concrete questions ("max acceptable response time? how many concurrent users
on a Friday evening peak?"), then write **measurable design goals**: "Response time
< 2 s at 1,000 concurrent users". Make each trade-off explicit: which attribute you
favour and which you sacrifice.

## Fitness functions

An automated check that a design goal or rule still holds, ideally in CI:
architecture/dependency tests (allowed imports, no cycles), performance/load tests
(possibly nightly), dependency vulnerability scans, static analysis thresholds.
They tell a developer within minutes that a guideline was broken and evolve with
the architecture. See `build-and-ci/references/maven-quality-gate.md` for import
control.

## Architectural styles (choose deliberately)

- **Structure:** layered; pipes and filters; modular monolith (with ports &
  adapters / hexagonal, clean or onion architecture – business logic at the
  centre, frameworks and I/O at the edges).
- **Distribution:** client–server, peer-to-peer, SOA, event-driven (incl. event
  sourcing), microservices.
- **Interaction:** MVC, reactive.
- **Plugin / extension architecture:** small stable core with extension points
  (contracts); plugins implement them without changing the core (inversion of
  control: "don't call us, we call you"). Good for third-party extensions and
  optional features; costs: extension points are hard to design and hard to change,
  plugin versions must be managed, plugin code is foreign code.

Default for an uncertain future: a **modular monolith** with good internal
boundaries. Split out a service only for clearly different load, scaling,
availability or release needs. For external dependencies that may multiply
(payment providers, notification channels), use ports & adapters: the core owns
the interface, each provider is an adapter – adding one changes no core code.

For slow or unreliable third parties (payment providers): explicit timeouts,
retries with idempotency keys, clear states (pending → confirmed/failed),
asynchronous confirmation where appropriate, and no business logic that only works
in the desktop UI – web and desktop must call the same core service.

## Visualising design

Use diagrams to give an overview, create shared language, communicate change and
check decomposition (tangled diagrams usually mean tangled code). Keep them as
code (PlantUML, Mermaid, Structurizr DSL, D2) next to the source.

**C4 model** – zoom levels, each with a legend:
1. **System context** – the system, its users and external systems (recommended).
2. **Container** – deployable units (apps, databases) and their communication,
   with technology choices (recommended).
3. **Component** – parts inside one container with responsibilities and
   interfaces (when needed).
4. **Code** – classes (rarely; keep short-lived).

**UML** where precision helps: class diagram (domain model), component diagram
(subsystems with provided/required interfaces), sequence diagram (interactions
over time), activity diagram (control flow, in plain language), use case diagram
(functional overview). Notation and PlantUML snippets:
`references/uml-plantuml.md`.

## Documenting design

Documentation is communication. Typical failures: unrecorded decisions,
docs drifting from code, scattered information, 200-page documents nobody reads,
formats that can't be diffed. Remedy: **docs as code** – plain text (Markdown,
AsciiDoc) in the repository, reviewed in PRs, built and published by CI, updated as
part of the Definition of Done. Document what is hard to understand, not
everything.

| Type | Audience | Examples |
|---|---|---|
| API specification | developers using your code | Javadoc/JSDoc/docstrings, OpenAPI |
| Architecture docs | developers maintaining it | C4 diagrams, ADRs, arc42 |
| Internal comments | readers of the source | why-comments, TODO/FIXME with context |
| User docs | end users | guides, tutorials, FAQ |

### Architecture Decision Records

One short file per significant decision in `docs/adr/` (or `doc/adr/`), numbered,
never rewritten – superseded by a new ADR instead. The **Context** section (forces,
constraints, alternatives) is the valuable part: without it, future developers
either follow outdated decisions blindly or change things they don't understand.
Template: `references/adr-template.md`.

### arc42

A 12-section template (goals, constraints, context, solution strategy, building
blocks, runtime, deployment, cross-cutting concepts, decisions, quality,
risks/debt, glossary). Use it as a checklist to find gaps, not a form to fill
completely. ADRs fit into section 9.

### API documentation as a contract

Document every public API with its contract: purpose, preconditions, postconditions,
exceptions/errors. Write it before or together with the implementation. Every
documented behaviour is a promise you must keep – don't be overly generous.
Guidelines and tag reference: `references/api-docs.md`.

## When asked to "document the design" or "explain the architecture"

Deliver, adapted to the audience (e.g. external experts who won't read the code):
1. Context diagram and one paragraph on purpose and users.
2. Container/component view with responsibilities and interfaces.
3. One or two sequence diagrams of key flows.
4. Quality attributes that matter, and where the current structure fits or not.
5. Decisions with their trade-offs (ADRs), risks and technical debt.
