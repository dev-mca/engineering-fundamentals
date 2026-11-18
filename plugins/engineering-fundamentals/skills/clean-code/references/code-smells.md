# Code Smells (method and statement level)

A code smell is a surface sign of a deeper problem. The code may work; the smell
makes it harder to understand, change and test. Smells are prompts to look closer,
not automatic verdicts.

Examples are in Java; the ideas apply to any language.

---

## Magic numbers and strings

Literal values without explanation. What do `7` and `0.10` mean? If the value
appears in several places, changing it means hunting every copy.

**Fix:** Replace magic number with symbolic constant.

```java
// Before
if (rentalDays > 7) {
    discount = totalFee * 0.10;
}

// After
private static final int LONG_RENTAL_THRESHOLD_DAYS = 7;
private static final double LONG_RENTAL_DISCOUNT_RATE = 0.10;

if (rentalDays > LONG_RENTAL_THRESHOLD_DAYS) {
    discount = totalFee * LONG_RENTAL_DISCOUNT_RATE;
}
```

Business values that may change (thresholds, rates) often belong in configuration
or a domain object rather than scattered constants.

---

## Inconsistent or cryptic naming

`getUserName()`, `fetch_email()` and `retrieveAddr()` in one codebase; `d`,
`genymdhms`, `pszqint`.

**Fix:** Rename (with the IDE/tooling so every reference updates). Use the domain's
vocabulary.

```java
// Before
static int score(int[] d, int n) {
    int i = 0;
    for (int j : d) { if (j == n) { i += n; } }
    return i;
}

// After
static int sumOfMatchingDice(int[] dice, int faceValue) {
    int sum = 0;
    for (int die : dice) {
        if (die == faceValue) {
            sum += faceValue;
        }
    }
    return sum;
}
```

---

## Dead code

Unused variables, unreachable branches, unused methods, commented-out blocks.

**Fix:** Safe delete. Git keeps the history.

---

## Temporary variables that obscure meaning

A temp holds an expression result, or one variable is reused for unrelated values.

**Fix:** Replace temp with query; split temporary variable.

```java
// Split temporary variable
// Before
double temp = 2 * (height + width);
System.out.println(temp);
temp = height * width;
System.out.println(temp);

// After
final double perimeter = 2 * (height + width);
System.out.println(perimeter);
final double area = height * width;
System.out.println(area);
```

```java
// Replace temp with query
// Before
double basePrice = quantity * itemPrice;
return basePrice > 1000 ? basePrice * 0.95 : basePrice * 0.98;

// After
return basePrice() > 1000 ? basePrice() * 0.95 : basePrice() * 0.98;

private double basePrice() { return quantity * itemPrice; }
```

---

## Long method

A method that does too much: hard to understand, test and reuse. A comment
announcing "the next block does X" is a strong hint that X is a method.

**Fix:** Extract method; name it after *what* it does.

```java
// Before
void printOwing(double amount) {
    printBanner();
    // print details
    System.out.println("name: " + name);
    System.out.println("amount: " + amount);
}

// After
void printOwing(double amount) {
    printBanner();
    printDetails(amount);
}

private void printDetails(double amount) {
    System.out.println("name: " + name);
    System.out.println("amount: " + amount);
}
```

**One level of abstraction.** Compare three versions of a Roman numeral converter:

```java
// Integration method: reads top-down without comments
public static int convert(String roman) {
    int[] absoluteValues = map(roman);
    int[] correctedValues = applySubtractionRule(absoluteValues);
    return sum(correctedValues);
}
```

A version that mixes one extracted helper with inline logic ("hybrid") is shorter
but often *harder* to read than either the single cohesive method or the clean
integration method. Extract to reach one level of abstraction, not just to shorten.

---

## Duplicated code

The same or similar logic in several places; a change must be applied to every
copy, and missing one is a bug. Copies drift apart over time.

Kinds: exact clones, parameterised clones (same structure, different
names/literals), near-miss clones (small edits – often a missed abstraction).

**Fix depends on location:**
- same class → extract a private method;
- sibling classes → extract to a shared collaborator (or pull up, if a common base
  type genuinely exists);
- unrelated classes → extract a new class/module both depend on.

**Caveat:** code that looks alike but serves different purposes and will change
for different reasons is *not* duplication. Test: "would the same change have to
be made in both places?" If not, leave it.

---

## Flag (selector) arguments

```java
// Before: every caller must know what `isEU` means
public void ship(String country, boolean isEU) { ... }

// After
public void ship(String country) { send("UPS", country); }
public void shipWithinEU(String country) { send(euCarrier(), country); }
```

---

## Output parameters

`appendFooter(report)` – is `report` read or modified? Prefer
`report.appendFooter()` or return a new value.

---

## Negative conditionals

`if (!buffer.avoidCompaction())` → `if (buffer.shouldCompact())`.

---

## Redundant boolean logic

```java
// Before
if (aBool == true) { return true; } else { return false; }
// After
return aBool;
```

---

## Clever combined statements

```java
// Before
d = (a = b + c) + r;
// After
a = b + c;
d = a + r;
```

---

## Inappropriate static

```java
// Fine: pure utility, no state, no polymorphism
Math.max(a, b);

// Smell: depends on one object's data and might vary by type
static boolean canRentMoreMovies(User user)
// Better
user.canRentMoreMovies()
```

---

## Exception handling inside loops

```java
// Before
for (String s : values) {
    try {
        results.add(Integer.parseInt(s));
    } catch (NumberFormatException e) {
        log.warn("Invalid value: {}", s);
    }
}

// After
for (String s : values) {
    addIfValid(s, results);
}
```

---

## Fields not defining state

A field used only to pass temporary data between methods. Use a local variable or
a parameter, or extract a class if the data belongs together.

---

## Hidden temporal coupling

`init()` must be called before `process()`, but nothing enforces it. Make the
order impossible to get wrong: require the data in the constructor, return an
object from step one that step two needs, or combine the steps.

---

## Primitive obsession

Passing raw strings and ints for domain concepts (`String iban`, `double money`).
Prefer small value objects (`Iban`, `Money`) that validate themselves and carry
behaviour – especially for money (avoid floating point for currency amounts; use
decimal types).
