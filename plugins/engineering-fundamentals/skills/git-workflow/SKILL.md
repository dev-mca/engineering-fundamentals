---
name: git-workflow
description: Version control discipline with Git. Use when committing, writing commit messages, creating or merging branches, rebasing, resolving merge conflicts, opening or reviewing pull/merge requests, tagging releases, choosing a branching workflow, setting up .gitignore, or deciding what belongs in version control.
---

# Git Workflow

Version control makes every change traceable and every state restorable. History
is communication: years later, people (and agents) read it to understand *why*
something changed.

## Before any git operation

- Check the project's own conventions first (CONTRIBUTING, README, existing
  history via `git log --oneline -20`). **Existing project conventions win** over
  the defaults below.
- Only commit, push, merge or rewrite history when the user wants it. Never push
  to a shared main branch, force-push, or delete branches without explicit
  permission.
- Run `git status` often; know which files are untracked, modified, staged.

## What belongs in version control

Everything needed to rebuild and run a specific version: source, tests, build
scripts, dependency declarations (with pinned versions), configuration as code,
CI config, documentation, `.gitignore`.

Not: build output (`target/`, `build/`, `dist/`, `node_modules/`), IDE/OS files
(`.idea/`, `.vscode/` personal settings, `.DS_Store`), generated artefacts, and
**never secrets** (`.env`, API keys, tokens, passwords, private keys). A pushed
secret stays in the history – rotate it, don't just delete the file.

- Create `.gitignore` at project start (templates: github.com/github/gitignore)
  and commit it.
- Ignoring an already-tracked file requires `git rm --cached <file>` plus a
  commit.

## Commits

- **One logical change per commit.** Small commits are easier to review, revert
  and bisect.
- **Never mix refactoring and behaviour change** in one commit.
- **Don't commit broken code** – build and tests pass before each commit.
- Stage deliberately (`git add -p` or specific paths), not blindly `git add .`;
  review `git diff --staged` before committing.
- Delete code instead of commenting it out; history keeps it.

### Commit messages

Explain **why**; the diff already shows what. Rules independent of convention:
short subject (≈50, max 72 chars), blank line, body with motivation/context/
trade-offs, issue reference (`Refs: #42`, `Closes #15`).

Default convention: **Conventional Commits** (unless the project uses another):

```
<type>(<optional scope>): <summary in imperative mood>

<body: why, context, trade-offs>

<footer: Closes #87, BREAKING CHANGE: ...>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`, `build`,
`ci`, `revert`. A breaking change gets `!` after the type or a
`BREAKING CHANGE:` footer. The structure enables generated changelogs and semantic
version bumps.

```
fix(rental): correct CHF currency conversion

The conversion factor was hard-coded to 1.0, so international customers
were charged in the wrong currency.

Closes #87
```

Bad: `fix bug`, `updated stuff`, `changes to RentalService and pom.xml`, `wip`.

More examples and the alternative styles: `references/commit-messages.md`.

## Branches and integration

- Create branches with `git switch -c <type>/<short-description>`
  (e.g. `feature/add-discount`, `fix/negative-rental-days`).
- Keep branches **short-lived** (a day or two). Long-lived branches mean painful
  merges and break continuous integration. Integrate (pull/rebase from the trunk)
  often.
- **Merge vs rebase:** merge preserves history and is safe for shared branches;
  rebase makes linear history but rewrites commits – **only rebase local, unpushed
  commits**. Never rebase or force-push commits others may have pulled. If a
  force-push of your own feature branch is needed, use
  `--force-with-lease`.
- Use `git fetch` to inspect before integrating; `git pull` = fetch + merge.

### Merge conflicts

1. `git status` to list conflicted files.
2. Open each file, understand *both* sides (read the commits that caused them),
   combine deliberately – don't just pick "ours".
3. Remove all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
4. Build and run tests.
5. `git add` the resolved files, then `git commit` (or `git rebase --continue`).

### Undoing

- `git restore <file>` – discard working-copy changes (irreversible!).
- `git restore --staged <file>` – unstage, keep changes.
- `git restore -s <commit> <file>` – bring back an old version of one file.
- `git revert <commit>` – undo a pushed commit safely with a new commit.
- `git reset --hard` rewrites history and discards work – only on local,
  unpushed state, and never without the user's explicit consent.

## Choosing a workflow

| Workflow | Fits | Requirements |
|---|---|---|
| Trunk-based (commit to main/develop, branches < 1 day, feature flags) | Small experienced teams, continuous delivery | High test coverage, solid CI, discipline |
| Feature branch + pull/merge requests | Most teams | CI on every branch, timely reviews |
| GitLab flow (feature branches + environment/release branches or tags) | Separation of "ready to test" and "released" | CI/CD per environment |
| Gitflow (main, develop, feature/*, release/*, hotfix/*) | Scheduled releases, several supported versions | More overhead; not for continuous deployment |

Details and branch naming: `references/branching-workflows.md`.

## Pull / merge requests

A good PR has: a clear title, a description (why, what, how to test), a focused
diff (one concern), a green pipeline, and linked issues. Keep it small. Respond to
review feedback with new commits (or fixups squashed before merge if the project
prefers clean history).

When reviewing, see the `code-review` skill.

## Versions, tags, releases

- **Semantic versioning** `MAJOR.MINOR.PATCH`: MAJOR = incompatible change,
  MINOR = backward-compatible feature, PATCH = backward-compatible fix.
- Tag releases with **annotated** tags: `git tag -a v1.2.0 -m "Release 1.2.0"`, then
  `git push origin v1.2.0` (tags aren't pushed automatically).
- Tag what you release, release what you tag. Released versions are immutable.

## Good team habits

Pull often, push often, commit even more often; meaningful messages; don't break
the build (and fix it first if it is red); delete instead of commenting out; never
edit `.git/` by hand.
