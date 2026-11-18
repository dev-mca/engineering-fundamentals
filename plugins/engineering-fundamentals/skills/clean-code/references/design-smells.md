# Design Smells (across classes)

Where the smell, its fix, or both reach beyond one class. Two threads run through
all of them:

- **Coupling** – one class knows too much about another: insider trading, feature
  envy, message chains.
- **Cohesion** – responsibilities sit in the wrong place: large class, divergent
  change, shotgun surgery.

The fixes are the familiar refactorings (extract method/class, move method/field)
applied across class boundaries.

---

## Insider trading

Two classes access each other's internals directly, bypassing encapsulation
(information hiding). Consequences: high coupling (both break when internals
change), leaked representation, the class no longer controls its own state.
Common between parent/child classes and in code that manipulates parameters.

```java
// Smell
class Order {
    List<String> items = new ArrayList<>();   // package-private, unprotected
    String status = "NEW";
}

class OrderProcessor {
    void process(Order o) {
        o.status = "PROCESSING";               // reaching into Order
        o.items.add("gift-wrap");
    }
}

// Fix: Order owns its state and exposes behaviour
class Order {
    private final List<String> items = new ArrayList<>();
    private OrderStatus status = OrderStatus.NEW;

    void startProcessing() { status = OrderStatus.PROCESSING; }
    void addGiftWrap()     { items.add("gift-wrap"); }
}

class OrderProcessor {
    void process(Order order) {
        order.startProcessing();
        order.addGiftWrap();
    }
}
```

Refactorings: encapsulate field, move field, extract method, move method, extract
class.

---

## Feature envy

A method is more interested in another class's data than its own – typically it
calls many getters on another object to compute something. Unlike insider trading,
it uses public methods.

```java
// Smell: buildSummary only cares about Rental's data
class RentalReport {
    String buildSummary(Rental rental) {
        String name = rental.getUser().getFirstName() + " " + rental.getUser().getName();
        double rate = rental.getCar().getPriceCategory().getCharge(1);
        return name + ": " + rate;
    }
}

// Fix: move the knowledge to where the data lives
class Rental {
    String summary() { return user.fullName() + ": " + dailyRate(); }
    double dailyRate() { return car.dailyRate(); }
}
class User { String fullName() { return firstName + " " + name; } }
class Car  { double dailyRate() { return priceCategory.getCharge(1); } }
```

Refactorings: extract method, move method.

---

## Message chains (Law of Demeter)

`a.getB().getC().getD()` couples the caller to the whole chain of objects. If any
intermediate class changes, the caller breaks. The Law of Demeter ("talk only to
your direct friends", "shy code") says a method should call methods only on:
itself, its parameters, objects it creates, and its own fields – not on objects
returned by those.

```java
// Smell: caller must know Rental → Car → PriceCategory → charge
double rate = rental.getCar().getPriceCategory().getCharge(1);

// Fix: hide the delegate behind an intention-revealing method
double rate = rental.dailyRate();
```

Not every dotted chain is a violation: fluent builders and stream pipelines
(`list.stream().filter(...).map(...)`) return the same kind of object and are fine.
The smell is navigation through *different* objects' internals.

Deep mock chains in tests (`when(a.b().c().d())`) are the same smell showing up in
your test code – fix the production design.

---

## Large class (God class)

Too many fields, methods or responsibilities. Example: an `Order` that handles
customer data, items, pricing, payment and e-mail notifications. Everything is
"about an order", but the concerns change independently, and every test needs a
huge fixture.

**Fix:** ask "what changes together, for whom?" Group fields and methods by
responsibility and extract classes (`Customer`, `OrderItems`, `PriceCalculator`,
`PaymentProcessor`, `OrderNotifier`), then decide the relationships. A good design
for a big domain may legitimately have many small classes.

Metric hint: high LCOM (lack of cohesion), many fields, many methods, high fan-out.

---

## Divergent change

One class is modified for different, unrelated reasons – e.g. `Invoice` changes
whenever the database schema changes *and* whenever the PDF layout changes.
Violates single responsibility; the class need not be large.

```java
// Smell
class Invoice {
    void saveToDatabase() { ... }   // changes with the DB / ORM
    String formatAsPdf()   { ... }  // changes with branding / templates
    double calculateTotal() { ... }
}

// Fix: one class per reason to change
class Invoice           { double calculateTotal() { ... } }
class InvoiceRepository { void save(Invoice invoice) { ... } }
class InvoicePdfRenderer { byte[] render(Invoice invoice) { ... } }
```

---

## Shotgun surgery

The opposite of divergent change: one logical change forces edits in many classes.
A concept is scattered.

```java
// Smell: tax rate hard-coded in three classes
class Invoice { double total() { return subtotal * 1.077; } }
class Receipt { double total() { return amount * 1.077; } }
class Quote   { double total() { return price * 1.077; } }

// Fix: one owner for the concept
final class Vat {
    static final double STANDARD_RATE = 0.077;
    static double gross(double net) { return net * (1 + STANDARD_RATE); }
}
```

Refactorings: introduce constant/field, extract class, move method.

---

## Other design smells worth naming

- **Rigidity** – a small change causes a cascade of changes.
- **Fragility** – one change breaks things in unrelated places.
- **Immobility** – parts cannot be reused elsewhere because of tangled
  dependencies.
- **Needless complexity** – elements that are not useful now (speculative
  generality, unused extension points, configuration nobody needs).
- **Needless repetition** – duplication of code or of design ideas.
- **Opacity** – code that is hard to understand.
- **Hidden dependencies** – singletons/service locators/global state that a class
  uses without declaring it. Prefer constructor injection.
- **Artificial coupling** – things that don't depend on each other are coupled
  anyway (e.g. a shared "Utils" class, a constants file for unrelated features).
- **Base class depending on derivatives** – a parent that knows its children.
- **Misplaced responsibility / code at the wrong level of abstraction** – e.g. a
  `percentageFull` property on a generic `Stack`, or business rules inside a UI
  handler.
- **Business logic in the UI** – no other caller can reach the rule and no test
  can run it without starting the UI. Move it into the domain/service layer.
