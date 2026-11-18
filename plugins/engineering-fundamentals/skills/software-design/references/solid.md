# SOLID in Detail

Introduced by Robert C. Martin; they translate cohesion, coupling and abstraction
into five guidelines for object-oriented code. S and I are about cohesion /
modularisation, O and L about the right abstraction, D about loose coupling.

---

## S – Single Responsibility Principle

A module should have one reason to change; equivalently, it should be responsible
to one actor (one group of stakeholders whose requirements drive changes).

```java
// Violation: three actors share one class
class BurgerOrder {
    String formatReceipt()             { ... }  // customer
    String getPreparationInstructions() { ... } // cook
    String getDeliveryRoute()          { ... }  // driver
}
```

A new receipt layout, allergen warnings for the kitchen, and live traffic for the
driver all force edits (and re-tests) of the same class.

```java
// Better: one class per actor; BurgerOrder keeps only order data
class CustomerReceipt { String format(BurgerOrder order) { ... } }
class KitchenTicket   { String instructions(BurgerOrder order) { ... } }
class DeliverySlip    { String route(BurgerOrder order) { ... } }
```

Long Method is SRP at method level (fix: extract method / move method).

---

## O – Open/Closed Principle

Open for extension, closed for modification: add behaviour by adding code, not by
editing existing, tested code. Achieved through abstraction.

```java
// Smell: every new discount type edits this method
class DiscountCalculator {
    double calculate(Order order) {
        if (order.getType().equals("STUDENT")) return order.getTotal() * 0.10;
        else if (order.getType().equals("LOYALTY")) return order.getTotal() * 0.15;
        return 0;
    }
}

// Better
interface DiscountPolicy { double calculate(Order order); }
class StudentDiscount implements DiscountPolicy { public double calculate(Order o) { return o.getTotal() * 0.10; } }
class LoyaltyDiscount implements DiscountPolicy { public double calculate(Order o) { return o.getTotal() * 0.15; } }

class DiscountCalculator {
    private final DiscountPolicy policy;
    DiscountCalculator(DiscountPolicy policy) { this.policy = policy; }
    double calculate(Order order) { return policy.calculate(order); }
}
```

**When it pays:** variants are added regularly, or per-region/per-customer rules
(e.g. each branch with its own discount scale). **When not:** two stable cases that
will never grow – a simple `if` is fine.

---

## L – Liskov Substitution Principle

If S is a subtype of T, objects of T can be replaced by S without breaking the
program's desirable properties. A subtype must honour the parent's contract:

- no stronger preconditions,
- no weaker postconditions,
- no new exceptions the parent never threw,
- invariants preserved.

Symptoms of violation: `instanceof` checks in client code; overrides that throw
`UnsupportedOperationException`; overrides that silently drop a rule.

```java
// Violation: PremiumOrder removes Order's 4-topping limit
class Order { void addTopping(String t) { if (toppings.size() >= 4) throw new IllegalStateException(); toppings.add(t); } }
class PremiumOrder extends Order { @Override void addTopping(String t) { toppings.add(t); } }

// Better: separate types implementing an interface whose contract allows both
interface Order { void addTopping(String topping); List<String> getToppings(); }
class StandardOrder implements Order { /* throws IllegalStateException when 4 toppings reached */ }
class PremiumOrder  implements Order { /* unlimited, documented */ }
```

Prefer composition over inheritance when the "is-a" relationship is doubtful.

---

## I – Interface Segregation Principle

Clients should not depend on methods they do not use.

```java
// Smell: one interface, three concerns
interface OrderRepository {
    Order findById(int id);
    List<Order> findByCustomer(String customerId);
    void save(Order order);
    void delete(int id);
    List<Order> findOverdueOrders();   // only the scheduler needs this
}

// Better
interface OrderReader { Order findById(int id); List<Order> findByCustomer(String customerId); }
interface OrderWriter { void save(Order order); void delete(int id); }
interface OverdueOrderQuery { List<Order> findOverdueOrders(); }

class ReportService {
    private final OrderReader reader;
    ReportService(OrderReader reader) { this.reader = reader; }
}
```

A single implementation class may implement all three; clients see only what
they need. Testing benefit: a stub for `OrderReader` implements two methods, not
five. A fat interface often signals a class with too many responsibilities.

---

## D – Dependency Inversion Principle

1. High-level modules (business logic) should not depend on low-level modules
   (DB, e-mail, file system). Both depend on abstractions.
2. Abstractions should not depend on details; details depend on abstractions.

The source-code dependency is inverted: instead of
`OrderService → EmailNotification` you get
`OrderService → NotificationService ← EmailNotification`.

The abstraction is owned by (and named for) the high-level module's needs, not by
the detail. Wiring happens once, at the **composition root** (`main`, application
bootstrap, or a DI framework). For small systems manual constructor injection is
enough.

DIP is the usual way to achieve OCP: new behaviour = new implementation of the
interface.

```java
@Test
void placeOrder_sendsConfirmation() {
    NotificationService notifier = mock(NotificationService.class);
    OrderService service = new OrderService(notifier);

    service.placeOrder(new Order(42, 2));

    verify(notifier).notify("Order confirmed: 42");
}
```

---

## How the principles relate

| Principle | Design principle | Testability benefit |
|---|---|---|
| SRP | Cohesion | Each class tested in isolation; a failure points to one cause |
| OCP | Abstraction | Extending behaviour leaves existing tests untouched |
| LSP | Contract correctness | Test doubles behave consistently with the replaced type |
| ISP | Cohesion of interfaces | Doubles implement only needed methods |
| DIP | Loose coupling | Constructor injection makes every collaborator replaceable |

## Related package-level principles

- **Acyclic Dependencies Principle** – no cycles between packages/modules.
- **Stable Dependencies Principle** – depend in the direction of stability
  (unstable, frequently changing code depends on stable code).
- **Stable Abstractions Principle** – the more stable a package, the more
  abstract it should be.
- **Common Closure Principle** – classes that change together are packaged
  together.
- **Common Reuse Principle** – classes used together are packaged together.
