# Refactoring Catalog

Refactoring changes structure without changing observable behaviour. Each entry:
when to use it, how to do it safely. Prefer the IDE's/tooling's automated
refactoring – it updates all references and checks for conflicts. When working as
an agent without IDE refactorings, make the same small mechanical steps by hand,
compile and run tests after each one.

## Safety protocol (every refactoring)

1. Tests green before you start. If the code has no tests, add characterisation
   tests (tests that record what the code does today) first.
2. One refactoring per step.
3. Compile + run tests after the step. Red → revert, take a smaller step.
4. Commit each successful refactoring separately (`refactor: ...`).
5. Never mix with behaviour changes (two hats).
6. If you change a public signature, update all callers *and* the tests in the
   same step; consider keeping the old signature delegating to the new one
   temporarily (parallel change) when callers are outside your control.

## Most used (learn these first)

| Refactoring | Use when | Steps |
|---|---|---|
| **Rename** (variable, method, class, package) | A name doesn't reveal intent | Use tooling rename; check string references (reflection, config, templates) |
| **Extract Method** | Long method; a block deserves a name; duplication | Select a coherent block, identify inputs (parameters) and outputs (return value), name it after *what* it does |
| **Extract Variable** | A complex expression needs a name | Introduce a well-named local |
| **Extract Constant** | Magic number/string | Introduce a named constant at the right scope |
| **Inline** (variable/method) | The name adds nothing or an indirection is useless | Replace usages with the body, delete the definition |

## Moving responsibility

| Refactoring | Use when |
|---|---|
| **Move Method / Move Field** | Feature envy; the data/behaviour belongs to another class |
| **Extract Class** | Large class, divergent change, low cohesion |
| **Inline Class** | A class does too little to justify itself |
| **Hide Delegate** | Message chains (Law of Demeter) |
| **Encapsulate Field** | Public/package fields accessed from outside (insider trading) |
| **Introduce Parameter Object** | Long parameter lists; parameters that travel together |
| **Replace Temp with Query** | A temp hides a reusable computation |
| **Split Temporary Variable** | One variable reused for different purposes |
| **Replace Conditional with Polymorphism** | The same type switch appears in several places, or new types are added often (OCP) |
| **Change Signature** | Add/remove/reorder parameters |
| **Introduce Interface / Extract Interface** | A collaborator must be replaceable (tests, multiple implementations, DIP) |

## Larger restructurings

- **Isolate change** – first isolate the code to be refactored from the rest
  (e.g. behind a method or interface), then refactor inside, then remove the
  isolation if no longer needed.
- **Reconcile differences** – change two similar pieces of code step by step until
  they are identical, then remove one.
- **Temporary parallel implementation** – build the new algorithm next to the old
  one, switch callers one by one, delete the old one when no caller is left.
- **Migrate data** – move from one representation to another with temporary
  duplication of data structures.

## From legacy code to clean code (strategy)

1. Always keep a running system; move from working state to working state.
2. Identify features; prioritise by how likely and risky future changes are.
3. Introduce boundary interfaces so the system can be tested with doubles (DB,
   file system, network, clock).
4. Cover features with acceptance/characterisation tests as a safety net.
5. Identify components within features; prioritise them.
6. Refactor interfaces between components so each can be tested in isolation.
7. Per component decide: **refactor** (redesign step by step with unit tests),
   **re-engineer** (re-implement test-driven), or **keep** (few future changes,
   few past defects).

## Testing around signature changes

If a refactoring changes a method signature that tests call, change tests and
production code in the same automated step (tooling "change signature"), or use a
parallel change: add the new method, migrate callers and tests, delete the old
method – committing after each green step.
