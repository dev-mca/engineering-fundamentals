# ADR Template

File: `docs/adr/NNNN-short-title.md` (Markdown) or `.adoc`. Keep it to one page.

```markdown
# ADR-NNNN: <Decision in a short noun phrase>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-MMMM
Date: YYYY-MM-DD · Deciders: <names/roles>

## Context
What is the problem? Which forces are at play: requirements, quality
attributes (with measurable goals), constraints, team skills, existing systems?
What options were considered?

- Option A – <short description>; pros / cons
- Option B – ...
- Option C – ...

## Decision
We will <decision>. (Active voice, one or two sentences.)

## Consequences
- Positive: what becomes easier, which quality attributes are favoured.
- Negative: what becomes harder, which attributes are sacrificed, new risks.
- Follow-ups: tasks, fitness functions to add, docs to update.
```

## Example

```markdown
# ADR-0003: Integrate payment providers through a PaymentGateway port

## Status
Accepted · 2026-11-20

## Context
Bookings must be paid when confirmed. Switzerland offers TWINT and Stripe,
Germany Stripe only; more regional providers will follow. Adding or replacing a
provider must not change core code. Providers are external HTTP services that are
sometimes slow. Payments must be testable automatically without charging real
cards, and web front-ends of each branch must use the same payment logic as the
desktop application.

Options:
- A: call provider SDKs directly from the booking service – simple, but couples
  the core to every SDK and makes tests need sandboxes.
- B: a PaymentGateway interface in the core, one adapter per provider, selected
  per branch by configuration (ports & adapters).
- C: a separate payment microservice – isolates load and failures, but adds
  operational complexity the team cannot carry yet.

## Decision
We use option B. The booking core depends only on `PaymentGateway`; adapters
(`StripeGateway`, `TwintGateway`) live in their own module and are wired at
start-up based on branch configuration.

## Consequences
- + New providers = new adapter + configuration; core and its tests unchanged.
- + Core logic is unit tested with a fake gateway; adapters with HTTP stubs.
- − One more module and an interface to keep stable.
- − Slow providers still block a confirmation; timeouts and a pending state are
  required (follow-up: ADR on asynchronous confirmation).
- Follow-up: import-control rule "core must not import adapter packages".
```
