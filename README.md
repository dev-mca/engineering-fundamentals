# Engineering Fundamentals for Claude Code

**Make your coding agent work like a disciplined software engineer – not just a fast
one.**

AI agents write code quickly. Without engineering discipline, they also write
code that nobody understands, that isn't really tested, and that gets harder to
change with every prompt. This plugin teaches Claude Code the fundamentals that
keep software maintainable: clean code, refactoring, sound design, test-driven
development, systematic test data, clean Git history, automated quality gates,
documentation, and a verifiable agentic workflow.

It is built for:

- **People who vibe-code** and want the result to stay understandable and
  changeable.
- **Developers** who want their agent to follow good practice without repeating it
  in every prompt.
- **Students and teams** learning software engineering, who want an agent that
  works the way they are taught.

> This is an amplifier, not an autopilot. It makes good behaviour much more likely
> and blocks a few dangerous mistakes, but you (the human) remain responsible for
> what gets merged.

---

## What changes when it's installed

| Without | With Engineering Fundamentals |
|---|---|
| Writes code first, maybe tests later | Writes tests from your requirements first, shows them failing, then implements |
| "Done!" with a red or un-run build | Not done until the full build (tests + checks) passes – and says so honestly if it can't run it |
| Big rewrites mixed with new features | Small steps; refactoring and behaviour changes in separate commits |
| `fix stuff` commit messages | Conventional Commits explaining *why* |
| Clever, over-engineered abstractions | The simplest design that is easy to test and change |
| Magic numbers, 80-line methods, `a.getB().getC().getD()` | Named constants, small methods, Law of Demeter |
| Happy-path tests only | Equivalence classes, boundary values, error cases |
| Tests that call the real payment API / clock | Isolated tests with stubs, fakes and mocks |
| Silent assumptions | Open questions asked; decisions explained in plain language |

### Before / after example

```java
// Before: typical quick generated code
public double calc(int d, String t) {
    double p = d * 50;
    if (d >= 7 && d < 14) p = p * 0.97;
    if (d >= 14 && d < 28) p = p * 0.93;
    if (d >= 28) p = p * 0.85;
    if (t.equals("DE")) p = p * 0.93;   // ???
    return p;
}
```

```java
// After: intent-revealing, testable, each rule in one place
public Money totalFee(RentalPeriod period) {
    Money base = dailyRate.times(period.days());
    return discountPolicy.apply(base, period);   // branch-specific policy, injected
}
```

…with tests like `rentalOfExactlySevenDaysGetsThreePercentDiscount()` and
`rentalOfThirteenDaysStillGetsThreePercent()` derived from the business rules –
written *before* the implementation.

---

## Installation

You need [Claude Code](https://code.claude.com). Then, **inside a Claude Code
session**, run:

```
/plugin marketplace add dev-mca/engineering-fundamentals
/plugin install engineering-fundamentals@engineering-fundamentals
```

Restart Claude Code (or run `/reload-plugins`). That's it – the skills load
automatically when they are relevant.

Or from your terminal:

```bash
claude plugin marketplace add dev-mca/engineering-fundamentals
claude plugin install engineering-fundamentals@engineering-fundamentals
```

### Let Claude install it for you

Just tell Claude Code:

> Install the Claude Code plugin from https://github.com/dev-mca/engineering-fundamentals –
> follow the installation section of its README.

### Manual installation (without the plugin system)

If you only want the skills (no hooks, no reviewer agent):

```bash
git clone https://github.com/dev-mca/engineering-fundamentals.git
mkdir -p ~/.claude/skills
cp -r engineering-fundamentals/plugins/engineering-fundamentals/skills/* ~/.claude/skills/
```

### Update / uninstall

```
/plugin marketplace update engineering-fundamentals
/plugin uninstall engineering-fundamentals@engineering-fundamentals
```

---

## What's inside

### Skills (loaded automatically when relevant)

You can also call any skill directly, e.g. `/engineering-fundamentals:code-review`.

| Skill | Claude uses it when… |
|---|---|
| `engineering-core` | writing or changing any code: working loop, simplicity rules, Definition of Done, plain-language summaries |
| `clean-code` | naming, readability, code smells, safe refactoring, Law of Demeter |
| `software-design` | structuring classes and modules: cohesion, coupling, SOLID, design by contract, dependency injection, decomposition |
| `testing` | TDD, FIRST, Right-BICEP, equivalence classes & boundary values, test doubles, coverage |
| `feature-to-code` | turning a feature request into stories, rules, examples (Gherkin) and a test list |
| `understanding-code` | exploring an unfamiliar codebase or explaining what code does |
| `git-workflow` | commits, Conventional Commits, branching, merging/rebasing, PRs, semantic versioning |
| `build-and-ci` | builds, CI pipelines, quality gates, metrics (complexity, cohesion, coupling, duplication), releases |
| `architecture-and-docs` | quality attributes, trade-offs, architectural styles, ADRs, C4/UML in PlantUML/Mermaid, API docs |
| `logging` | log levels, messages, exceptions, audit logs, configuration |
| `agentic-workflow` | autonomous multi-step work: branch per issue, tests visibly red first, self-correction until green, metric comparison before merge; designing agent workflows for teams |
| `code-review` | reviewing diffs and pull requests with prioritised, actionable feedback |

### Subagent

- **`code-reviewer`** – an independent reviewer with fresh context, so your agent's
  work isn't grading itself. Ask: *"Have the code-reviewer agent review my last
  commits."*

### Hooks (guardrails Claude can't skip)

- **Session start:** reminds Claude to use the skills and core rules.
- **Git guard** (needs Python 3; silently disabled if Python is missing). Blocks:
  - staging or committing files that look like secrets (`.env`, private keys,
    `credentials.json`, …);
  - force-pushing to `main`, `master`, `develop` and similar shared branches;
  - commit messages that don't follow Conventional Commits – **only** if your repo
    uses that convention (or is new). Repos with another established style are
    left alone.

Opt out per shell/session:

```bash
export EF_CONVENTIONAL_COMMITS=off   # keep the guard, skip message format checks
export EF_GIT_GUARD=off              # disable the git guard completely
```

### Make it stricter for one project (optional)

Copy [`docs/CLAUDE-snippet.md`](docs/CLAUDE-snippet.md) into your project's
`CLAUDE.md` and fill in your build command. The rules are then loaded in every
session for that project, which makes the behaviour even more consistent.

---

## How it works

Claude Code always sees the short description of each skill. When your request
matches (e.g. "add a discount rule", "commit this", "why is this class so
complicated?"), Claude loads the full skill – a compact procedure with checklists
– and reads the detailed reference files only when needed. Hooks run as small
scripts outside the model, so they apply even when the model forgets.

The skills are **language-agnostic**; most examples are in Java (with Maven), and
there are notes for TypeScript/JavaScript and Python where tools differ. They
always defer to your project's existing conventions.

---

## Principles behind it

- Software engineering is programming over time: optimise for the next person who
  changes the code.
- Work empirically: small steps, fast feedback, decisions based on tests and
  measurements.
- Manage complexity: modularity, cohesion, loose coupling, separation of concerns,
  abstraction – and no accidental complexity.
- Testability is the north star of good design.
- Generated code deserves the same – or more – scrutiny than hand-written code.

---

## Contributing

Issues and pull requests are welcome. Please:

- keep `SKILL.md` files short (procedures and checklists); put detail into
  `references/`,
- write rules as instructions ("when X, do Y"), with a short example,
- validate before opening a PR: `claude plugin validate .`

## Credits & sources

The content is based on the course **Software Engineering Fundamentals (SWEF)** at
FHNW (University of Applied Sciences and Arts Northwestern Switzerland) by
**Martin Kropp** and **Sibylle Peter**, used and adapted with their permission. It
was distilled into agent instructions by Melih Can.

The course and this plugin build on the work of many authors, including:
David Farley (*Modern Software Engineering*); Winters, Manshreck & Wright
(*Software Engineering at Google*); Robert C. Martin (*Clean Code*, SOLID);
Martin Fowler (*Refactoring*, articles on CI, mocks and technical debt); Kent Beck
(TDD, *Tidy First?*); Langr, Hunt & Thomas (*Pragmatic Unit Testing*); Meszaros
(*xUnit Test Patterns*); Freeman & Pryce (*Growing Object-Oriented Software,
Guided by Tests*); Demeyer, Ducasse & Nierstrasz (*Object-Oriented Reengineering
Patterns*); Feathers (*Working Effectively with Legacy Code*); Simon Brown (C4
model); Ford, Parsons & Kua (*Building Evolutionary Architectures*); Matt Wynne
(Example Mapping); Urs Enzler (Clean Code Cheat Sheet); Chacon & Straub
(*Pro Git*); the Conventional Commits and Semantic Versioning specifications.

## License

[Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.
