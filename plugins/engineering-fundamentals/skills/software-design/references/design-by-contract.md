# Design by Contract

A method's contract: if the caller respects the preconditions, the method
guarantees the postconditions. Introduced by Bertrand Meyer (Eiffel). In other
languages it becomes defensive programming with guard clauses (preconditions),
unit tests (postconditions) and documentation.

## Elements

- **Precondition** – must hold before the call (parameter ranges, required object
  state). Enforced with guard clauses that throw early
  (`IllegalArgumentException` for bad arguments, `IllegalStateException` for a
  wrong object state – or your language's equivalents).
- **Postcondition** – holds after the call if preconditions were met (return
  value, state change, side effects).
- **Invariant** – holds for every instance at all times: after construction, before
  and after every state-changing public method. Can also constrain associations
  ("an A always holds at least one B"). Invariants decide what the constructor and
  every mutator must check.
- **Exception conditions** – which error occurs under which circumstances.

Together they describe a public method as an interface without exposing its
implementation.

## Worked example: an order with at most 4 toppings

Semi-formal specification:

```
@inv  0 <= number of toppings <= MAX_TOPPINGS (4)

add(topping):
  @pre  number of toppings <= MAX_TOPPINGS - 1
  @pre  topping != null and not blank
  @post number of toppings == old(number of toppings) + 1
  @post number of toppings <= MAX_TOPPINGS
```

Implementation with guard clauses, contract in the API docs:

```java
class BurgerOrder {
    // Invariant: toppings is never null and holds 0..MAX_TOPPINGS entries.
    private static final int MAX_TOPPINGS = 4;
    private final List<String> toppings = new ArrayList<>(MAX_TOPPINGS);

    /**
     * Adds a topping to this order.
     *
     * @param topping the topping to add; not null, empty or blank
     * @throws IllegalArgumentException if topping is null, empty or blank
     * @throws IllegalStateException if the order already holds MAX_TOPPINGS toppings
     */
    public void addTopping(String topping) {
        if (topping == null || topping.isBlank()) {
            throw new IllegalArgumentException("Topping must not be null, empty or blank.");
        }
        if (toppings.size() == MAX_TOPPINGS) {
            throw new IllegalStateException("Cannot add more than " + MAX_TOPPINGS + " toppings.");
        }
        toppings.add(topping);
    }

    public List<String> getToppings() {
        return Collections.unmodifiableList(toppings);   // protects the invariant
    }
}
```

Where to document: preconditions in `@param` (or in the `@throws ... if ...`
text), postconditions in the description, `@return` and `@throws`.

## From contract to tests

The contract *is* the test list:

| Test | Given (pre) | When | Then (post / exception) |
|---|---|---|---|
| adds a topping | 2 toppings | add "Cheese" | 3 toppings |
| fills to the limit (boundary) | 3 toppings | add "Onion" | 4 toppings |
| rejects beyond the limit (boundary) | 4 toppings | add "Onion" | `IllegalStateException`, still 4 |
| rejects null | 0 toppings | add `null` | `IllegalArgumentException`, still 0 |
| rejects blank | 0 toppings | add `"  "` | `IllegalArgumentException` |

Note how invariants, examples, and equivalence classes/boundary values describe
the same behaviour from different angles.

## Practice: invariants from a requirement

"A customer may have at most 10 active orders":

```
Customer
  @inv 0 <= activeOrders.size() <= 10

addOrder(order):
  @pre order != null
  @pre order is not already among the active orders
  @pre activeOrders.size() < 10
  @post activeOrders.size() == old + 1
  @post activeOrders contains order
```

"A multiple-choice question has a text, a hint and 2–5 distinct answers, at least
one correct" → invariants for a *complete* question; separate pre-conditions for
`addAnswer` (≤ 5 answers, no duplicates); note that a question under construction
may temporarily violate "≥ 2 answers / ≥ 1 correct" – decide whether to use a
builder that validates on `build()`, or a validity check before publishing. Making
that decision explicit is the point.
