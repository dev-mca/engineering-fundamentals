# UML and C4 with PlantUML (and Mermaid)

Use text-based diagrams so they can be versioned, diffed and rendered in CI.
Useful PlantUML settings:

```
skinparam style strictuml   ' UML 2 style
skinparam linetype ortho    ' straight lines (not for use case diagrams)
hide empty members          ' class diagrams
autoactivate on             ' sequence diagrams: activation bars
```

## Class diagram

Conventions: getters/setters are not modelled (attributes assumed readable and
writable unless marked `{readOnly}`); types after a colon.

| Concept | PlantUML |
|---|---|
| Class with members | `class Rental {\n - days : int\n + fee() : Money\n}` |
| Visibility | `-` private, `~` package, `#` protected, `+` public |
| Static / abstract | `{static} counter : int`, `abstract class Base`, `{abstract} start()` |
| Interface | `interface PaymentGateway <<interface>>` |
| Association (+ label) | `Customer - Order : > places` |
| Multiplicity | `Customer "1" - "0..10" Order` |
| Aggregation (part-of, may exist alone) | `Team o-- Player` |
| Composition (part-of, lifetime bound) | `Order *-- "1..*" OrderItem` |
| Generalisation | `Vehicle <|-- Car` |
| Realisation | `PaymentGateway <|.. StripeGateway` |
| Dependency (uses) | `BookingService ..> PaymentGateway : <<use>>` |
| Note | `note right of Rental::days\n invariant: days >= 1\nend note` |

```plantuml
@startuml
skinparam style strictuml
hide empty members
class Customer {
  - name : String
  + addOrder(order : Order) : void
}
class Order
Customer "1" -- "0..10" Order : > has active
note right of Customer
  inv: 0 <= activeOrders <= 10
end note
@enduml
```

## Component diagram

A component encapsulates its content, is replaceable, and is defined by provided
and required interfaces; implementations should be independently deployable.

```plantuml
@startuml
component Booking
component Payment
component StripeAdapter
interface PaymentGateway
Payment - PaymentGateway        ' provides (lollipop)
Booking ..> PaymentGateway      ' requires
StripeAdapter ..|> PaymentGateway
@enduml
```

Prefer provided/required interfaces (lollipop) over plain dependency arrows once
the interface is known.

## Sequence diagram

```plantuml
@startuml
skinparam style strictuml
autoactivate on
actor Employee
participant ":BookingService" as B
participant ":PaymentGateway" as P
Employee -> B : confirm(booking)
B -> P : charge(amount, card)
alt success
  P -->> B : PaymentResult.OK
  B -->> Employee : confirmed
else declined
  P -->> B : PaymentResult.DECLINED
  B -->> Employee : not confirmed
end
@enduml
```

Lifelines belong to objects (`:Class`). Fragments: `alt/else`, `opt`, `loop` – use
sparingly; two diagrams are often clearer than nested fragments. Create:
`create participant X` / `A -> "X" ** : new`; destroy: `destroy X` or `A ->> X !!`.

## Activity (control flow) diagram

Write actions in plain language, not code.

```plantuml
@startuml
start
:Read rental period;
if (Period longer than 28 days?) then (yes)
  :Apply 15% discount;
elseif (Longer than 14 days?) then (yes)
  :Apply 7% discount;
elseif (At least 7 days?) then (yes)
  :Apply 3% discount;
else (no)
endif
:Show total fee;
stop
@enduml
```

Loops: `while (Hospital has capacity and patients waiting?)` … `endwhile`;
`repeat` … `repeat while (...)`; `switch (x?)` / `case (a)` / `endswitch`;
`break` to leave a loop; `end` for a flow final in concurrent flows.

## Use case diagram

```plantuml
@startuml
left to right direction
actor "Customer (Web)" as C
actor "Shop Admin" as A
actor "Inventory System" as I
rectangle Webshop {
  usecase "View products" as UC1
  usecase "Query inventory" as UC2
  usecase "Place order" as UC3
  usecase "Display error message" as UC4
  usecase "Create products" as UC5
}
C -- UC1
C -- UC3
A -- UC5
UC1 .> UC2 : <<include>>
UC4 .> UC1 : <<extend>>
UC2 -- I
C <|-- A
@enduml
```

Rules: associations only actor ↔ use case; include = always executed; extend =
optional (condition as note); generalisation between actors (OR) or between use
cases; included use cases are connected to an actor only if they can run on their
own.

## C4 with PlantUML (C4-PlantUML)

```plantuml
@startuml
!include <C4/C4_Container>
Person(employee, "Employee", "Books cars for customers")
System_Ext(stripe, "Stripe", "Payment provider")
System_Boundary(ecars, "eCars") {
  Container(desktop, "Desktop App", "Java/Swing", "Booking UI for employees")
  Container(api, "Booking API", "Java", "Bookings, pricing, payments")
  ContainerDb(db, "Database", "PostgreSQL", "Cars, branches, bookings")
}
Rel(employee, desktop, "Uses")
Rel(desktop, api, "Calls", "HTTPS/JSON")
Rel(api, db, "Reads/writes", "JDBC")
Rel(api, stripe, "Charges cards", "HTTPS")
SHOW_LEGEND()
@enduml
```

## Mermaid equivalents (render natively on GitHub/GitLab)

```mermaid
classDiagram
  PaymentGateway <|.. StripeGateway
  BookingService ..> PaymentGateway
  class PaymentGateway {
    <<interface>>
    +charge(amount, card) PaymentResult
  }
```

```mermaid
sequenceDiagram
  Employee->>BookingService: confirm(booking)
  BookingService->>PaymentGateway: charge(amount, card)
  PaymentGateway-->>BookingService: OK
  BookingService-->>Employee: confirmed
```
