# Tidy-First Checklist

Small, behaviour-preserving tidyings to apply to code *before* changing it, so the
real change becomes easy. Each item is its own small step and commit.

## Formatting
- [ ] Consistent indentation and whitespace (run the project formatter).
- [ ] Long lines wrapped; introduce helper variables if a call is unreadable.
- [ ] Braces always present for blocks (no dangling `else`); remove unnecessary
      parentheses.
- [ ] Symmetries made visible through parallel formatting and names:
      ```java
      double x = xStart + 3 * (i + PADDING);
      double y = yStart + 3 * (j + PADDING);
      ```
- [ ] Blank lines (one at a time) only to separate groups of related statements.

## Variables & constants
- [ ] Meaningful names that follow the language conventions
      (`hasNegative`, not `neg_finder`; constants `MAX_SIZE`).
- [ ] Declaration close to first use; loop variables scoped to the loop.
- [ ] Complex expressions split into explanatory variables/constants:
      ```java
      var players = teamData[0];
      var yellowCards = teamData[1];
      var redCards = teamData[2];
      var fairnessScore = (yellowCards + 5 * redCards) / players;
      return fairnessScore / BASELINE * 100;
      ```
- [ ] Unused variables, parameters, methods and classes removed.

## Comments
- [ ] Comments that repeat the code removed (often a rename makes them
      redundant).
- [ ] Helpful comments added where the code cannot speak for itself
      (e.g. "reader only accepts UNIX-style paths, even on Windows").
- [ ] Commented-out code deleted.
- [ ] Public methods documented (contract).

## Structure
- [ ] Guard clauses instead of deep nesting for invalid input.
- [ ] Explanatory variable for compound conditions
      (`boolean hasHospitals = hospitals != null && hospitals.length > 0;`).
- [ ] Redundant checks removed only if a diagram/tests prove behaviour stays the
      same (e.g. a `length > 0` check before a loop that would simply not run).
- [ ] Existing helper methods used instead of re-implementing the comparison
      (`hospital.hasCapacity()` instead of `h.freeRooms() > 0`).

Tidying must not "fix" odd behaviour you discover – record it (issue/TODO) and
change it later as a separate, test-driven behaviour change.
