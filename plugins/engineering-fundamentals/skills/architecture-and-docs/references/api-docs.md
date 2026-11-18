# API Documentation

Write for two readers: those who use your code and those who maintain it – as if
you will have forgotten everything tomorrow.

## What to document

- **Classes/interfaces/modules:** purpose and responsibility. For interfaces, what
  is done, not how.
- **Methods/functions:** what it does, preconditions (parameter constraints,
  required state), postconditions (return value, state change, side effects),
  errors (when and why).
- Not: trivial getters that only repeat the name; implementation details that may
  change.

## Summaries

The first sentence becomes the summary in generated docs:
- start with a verb, third person ("Calculates…", "Returns…"),
- omit the subject ("This method…"),
- say what, not how.

| Don't | Do |
|---|---|
| `/** This method gets the name. */` | `/** Returns the full name of the customer. */` |
| `/** Method to calculate fee */` | `/** Calculates the rental fee from the price category and rental duration. */` |

## Javadoc tags

| Tag | Purpose |
|---|---|
| `@param name` | parameter meaning and constraints (preconditions) |
| `@return` | the result and its guarantees |
| `@throws Type if ...` | when the exception occurs |
| `@see`, `{@link Class#method}` | cross-references (keep them current or omit) |
| `@since`, `@deprecated` | version info, migration hint |
| `{@code expr}` | monospace code without HTML interpretation |

```java
/**
 * Calculates the total rental fee including the applicable discount.
 *
 * @param days rental duration in days; must be at least 1
 * @return the total fee in the branch's currency, never negative
 * @throws IllegalArgumentException if {@code days} is less than 1
 */
public Money totalFee(int days) { ... }
```

## Other languages

- **TypeScript/JavaScript (TSDoc/JSDoc):** `@param`, `@returns`, `@throws`,
  `@example`; types come from the signature in TS.
- **Python (docstrings, Google/NumPy style):** summary line, `Args:`, `Returns:`,
  `Raises:`; type hints in the signature.
- **HTTP APIs:** OpenAPI specification as the contract (paths, schemas, error
  responses, examples), versioned with the code, ideally contract-tested.

## Keeping docs alive

- Docs live in the repo (docs as code) and are generated in CI (`mvn site`,
  TypeDoc, Sphinx/MkDocs) and published (GitLab/GitHub Pages).
- Lint docs in the build where possible (Javadoc `doclint` + `failOnWarnings`,
  `eslint-plugin-jsdoc`, `pydocstyle`/Ruff `D` rules) so "public APIs are
  documented" is enforced, not hoped for.
- Update docs in the same commit/PR as the behaviour change – part of the
  Definition of Done.
- An outdated cross-reference is worse than none.
