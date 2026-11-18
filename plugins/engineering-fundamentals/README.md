# engineering-fundamentals (plugin)

This folder is the Claude Code plugin. It contains twelve skills (clean code,
refactoring, software design, testing/TDD, feature-to-code, understanding code,
Git workflow, build and CI, architecture and docs, logging, agentic workflow, code
review), an independent `code-reviewer` subagent, a session-start reminder and a
Git guard hook that blocks committing secrets, force-pushing to shared branches and
non-conventional commit messages.

Install (inside Claude Code):

```
/plugin marketplace add dev-mca/engineering-fundamentals
/plugin install engineering-fundamentals@engineering-fundamentals
```

Usage, options and credits: see the [repository README](../../README.md).
