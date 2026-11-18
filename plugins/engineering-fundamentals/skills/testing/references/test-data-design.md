# Designing Test Data: Equivalence Classes and Boundary Values

Goal: cover the input domain with as few tests as possible, with a clear stopping
criterion. Examples from a requirement are a good start; they are not yet a
complete suite.

## Step 1 – Equivalence classes (EC)

Partition each input into regions where the same behaviour is expected. Describe
each class in words plus its expected outcome.

```java
/** A valid order is 1 to 20 pizzas. */
static boolean isValidOrderSize(int pizzas) { return pizzas >= 1 && pizzas <= 20; }
```

| EC | Description | Representative | Expected |
|---|---|---|---|
| EC-1 | fewer than 1 pizza (no order) | -3 | false |
| EC-2 | 1..20 pizzas | 5 | true |
| EC-3 | more than 20 (oversized) | 50 | false |

ECs are not limited to booleans – an order size → category mapping (single,
small, family, party, invalid below, invalid above) has six classes and five
outcomes.

## Step 2 – Boundary values (BV)

Most off-by-one errors live between classes. For each class, test its edges.
Describe boundaries in words first:

| Class | Lower boundary | Upper boundary |
|---|---|---|
| no order | negative infinity | smallest valid order − 1 |
| valid | smallest valid order | largest valid order |
| oversized | largest valid order + 1 | infinity |

Then translate to concrete values:

| Class | Typical (EC) | Boundaries |
|---|---|---|
| no order | -3 | `Integer.MIN_VALUE`, 0 |
| valid | 5 | 1, 20 |
| oversized | 50 | 21, `Integer.MAX_VALUE` |

Why words first: they justify the boundary ("smallest valid order"), suggest
constant names (`MIN_ORDER_SIZE`), survive business changes, and stay
language-neutral. Typical values must not be boundary values. Reference types add
`null`, empty collections, empty/blank strings.

## Step 3 – Multiple parameters

Example: a driver accepts an order if `pizzas` fits the free capacity (vehicle max
10) **and** the delivery time is strictly before shift end − 30 minutes.

Parameter `pizzas` (driver already carries 2, so 8 free):

| ID | Description | Value | Expected |
|---|---|---|---|
| EC-1 | within free capacity | 5 | true |
| EC-2 | exceeds free capacity but ≤ max | 9 | false |
| EC-3 | invalid: ≤ 0 | -1 | false |
| EC-4 | invalid: > max capacity | 375 | false |
| BV-1 | smallest valid | 1 | true |
| BV-2 | largest valid (= free capacity) | 8 | true |
| BV-3 | too small | 0 | false |
| BV-4 | too big | 11 | false |

Parameter `deliveryTime` (shift ends 20:00, cut by the minute, "before" taken
strictly after asking the PO):

| ID | Description | Value | Expected |
|---|---|---|---|
| EC-5 | valid: before 19:30 | 19:00 | true |
| EC-6 | invalid: at/after 19:30 | 20:30 | false |
| BV-5 | last valid minute | 19:29 | true |
| BV-6 | first invalid minute | 19:30 | false |

The full cross product is large. Because the result is a logical AND, pair each
invalid value with valid values of the other parameter, and combine the valid
variants:

| pizzas | deliveryTime | Expected |
|---|---|---|
| EC-1 | EC-5 | true |
| BV-1 | BV-5 | true |
| BV-2 | EC-5 | true |
| EC-1 | EC-6 | false |
| BV-1 | BV-6 | false |
| EC-2 | EC-5 | false |
| EC-3 | EC-5 | false |
| EC-4 | BV-5 | false |
| BV-3 | EC-5 | false |
| BV-4 | BV-5 | false |

Don't assume the order of conditions in the implementation – tests should still
catch someone flipping them. Two parameterised tests (one per expected result)
carry all rows.

Time-dependent tests: pass the time (or a `Clock`) in; never call `now()` inside
the code under test or the test.

## Rule of thumb

Combine classes as a cross product, then prune combinations the specification
makes redundant; test every boundary at least once.

## Limits

EC/BV fit stateless, value-range specifications. Beyond that:

- **State/history** (capacity shrinking with each accepted order) – classes depend
  on state; design call sequences (state-based testing).
- **Time** – make time an input.
- **Combinatorial explosion** – pairwise testing, or redesign to fewer independent
  parameters.
- **Specifications you can't enumerate** ("any valid JSON") – property-based
  testing.

## Library example: requirement → classes

"Members may borrow up to six items; staff any number."

| Class | Boundaries | Expected |
|---|---|---|
| member below limit | 0 and 5 items borrowed | loan granted |
| member at/above limit | 6 items borrowed | loan refused |
| staff | 0 and one large value | loan granted (no limit) |

The examples from the conversation covered "fewer than 6" and "exactly 6"; the
lower boundary (first item ever) was missing – systematic design finds such gaps,
and also new questions ("what if the due date is a public holiday?") for the
product owner.
