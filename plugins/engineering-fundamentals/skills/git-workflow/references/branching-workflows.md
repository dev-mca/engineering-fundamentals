# Branching Workflows

A workflow is a team agreement on whether and how branches are used, when work is
merged, and how changes are reviewed. Good workflows provide **isolation**,
**quality gates** (review + tests before main), and **traceability** (each change
linked to a purpose).

## Trunk-based development

Everyone integrates into one branch (main, or develop as trunk) at least daily;
branches, if any, live less than a day. Unfinished features hide behind feature
flags. CI runs on every push.

- + fastest feedback, minimal merge pain
- − every commit must keep the trunk working; needs strong tests and CI
- Review via pairing/ensemble programming or very small PRs

## Feature branch workflow

1. `git switch -c feature/add-discount-calculation` from main.
2. Commit as often as you like.
3. Push and open a pull/merge request.
4. Review, adjust, CI green.
5. Merge into main; delete the branch.

Risk: long-running branches create parallel versions and undermine continuous
integration – keep branches to a day or two.

## GitLab flow

Feature branches → main via merge requests; main deploys automatically to staging;
production via a production branch or release tags.

## Gitflow

`main` (production), `develop` (integration), `feature/*` (from develop),
`release/*` (stabilisation, version bump), `hotfix/*` (from main for urgent fixes,
merged into main and develop). For scheduled releases and several supported
versions; too heavy for small teams and continuous deployment.

## Comparison

| Criterion | Trunk-based | Feature branch | Gitflow |
|---|---|---|---|
| Team size | small (2–5) | small–medium (2–10) | medium–large (5+) |
| Release cadence | continuous | continuous or periodic | scheduled |
| Complexity | low | low | high |
| Code review | pairing / tiny PRs | merge requests | merge requests |
| CI requirement | essential | strongly recommended | recommended |

## Example decisions

- **Student/small team, weekly meetings, manual deployment at the end:** develop as
  trunk with small, frequent commits (or short feature branches with PRs to learn
  reviewing); main only receives releases via merge request (ideally
  fast-forward). Hotfix: branch from main, fix with a test, merge back to main
  and develop.
- **SaaS team deploying many times a day:** trunk-based with feature flags,
  mandatory CI, pairing or small PRs; critical fix = normal fast path.
- **Regulated product, quarterly releases, several maintained versions:** Gitflow
  or release branches with protected branches, required reviews and CI;
  hotfix branches from the release tag, cherry-picked/merged into all supported
  lines.

## Branch naming

`<type>/<issue-id>-<short-kebab-description>`, e.g.
`feature/42-branch-discounts`, `fix/87-chf-conversion`, `refactor/extract-pricing`,
`docs/adr-payment-provider`. Types mirror commit types.

## Merge rules to agree on

- Who may merge to main/develop; protected branches.
- Required: green pipeline, ≥ 1 approval, no unresolved threads.
- Merge style: merge commit, squash, or rebase + fast-forward.
- Quality gate must not get worse (coverage, smells, coupling) – see
  `build-and-ci`.
