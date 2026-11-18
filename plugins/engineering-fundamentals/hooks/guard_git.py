#!/usr/bin/env python3
"""PreToolUse guard for Bash commands that run git.

Blocks (exit code 2, reason on stderr) when a command would:
  1. stage or commit files that look like secrets (.env, private keys, ...),
  2. force-push (without --force-with-lease) to a protected branch,
  3. commit with a message that breaks Conventional Commits, if the repository
     uses that convention (or has too little history to tell).

Everything else passes (exit code 0). Any internal error also passes, so the
guard can never break a session.

Opt-outs (environment variables):
  EF_CONVENTIONAL_COMMITS=off   do not check commit message format
  EF_GIT_GUARD=off              disable this guard completely
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED_BRANCHES = {"main", "master", "develop", "trunk", "production", "release"}

SECRET_PATTERNS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "credentials.json",
    "service-account*.json",
    ".npmrc",
    ".pypirc",
    "*.tfstate",
]
SECRET_ALLOWLIST = [".env.example", ".env.sample", ".env.template", ".env.dist"]

CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([\w\-./ ,]+\))?!?: \S"
)
ALWAYS_OK_SUBJECT_RE = re.compile(r"^(Merge |Revert \"|fixup! |squash! |amend! |Initial commit)")


def block(reason: str) -> None:
    sys.stderr.write(reason.strip() + "\n")
    sys.exit(2)


def run_git(args: list[str], cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5
        )
        return result.stdout if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def looks_like_secret(path: str) -> bool:
    name = os.path.basename(path.strip().strip('"'))
    if name in SECRET_ALLOWLIST:
        return False
    return any(fnmatch.fnmatch(name, pattern) for pattern in SECRET_PATTERNS)


def split_segments(command: str) -> list[list[str]]:
    """Split a shell command line into simple commands (on && || ; |)."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return []
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token and set(token) <= set(";&|"):
            segments.append([])
        else:
            segments[-1].append(token)
    return [s for s in segments if s]


def git_subcommand(tokens: list[str]) -> tuple[str, list[str]] | None:
    """Return (subcommand, args) if tokens are a git invocation."""
    if not tokens or os.path.basename(tokens[0]) not in ("git", "git.exe"):
        return None
    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("-C", "-c", "--git-dir", "--work-tree"):
            i += 2
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return tok, tokens[i + 1:]
    return None


def check_secrets_on_add(args: list[str], cwd: str) -> None:
    broad = any(a in (".", "-A", "--all", "*", ":/") for a in args) or not [
        a for a in args if not a.startswith("-")
    ]
    explicit = [a for a in args if not a.startswith("-") and looks_like_secret(a)]
    if explicit:
        block(
            "Blocked by engineering-fundamentals: refusing to stage files that look "
            f"like secrets: {', '.join(explicit)}.\nSecrets must never be committed. "
            "Add them to .gitignore and load them from the environment or a secret "
            "store. If the file is truly safe, the user can stage it manually."
        )
    if broad:
        status = run_git(["status", "--porcelain", "--untracked-files=all"], cwd)
        risky = [
            line[3:]
            for line in status.splitlines()
            if len(line) > 3 and looks_like_secret(line[3:])
        ]
        if risky:
            block(
                "Blocked by engineering-fundamentals: this `git add` would stage files "
                f"that look like secrets: {', '.join(risky)}.\nAdd them to .gitignore "
                "first (and keep an example file such as .env.example instead), then "
                "stage the intended files explicitly."
            )


def check_secrets_on_commit(args: list[str], cwd: str) -> None:
    staged = run_git(["diff", "--cached", "--name-only"], cwd).splitlines()
    commits_all_tracked = any(
        a == "--all" or (re.fullmatch(r"-[a-zA-Z]+", a) is not None and "a" in a[1:])
        for a in args
    )
    if commits_all_tracked:
        staged += run_git(["diff", "--name-only"], cwd).splitlines()
    risky = sorted({p for p in staged if looks_like_secret(p)})
    if risky:
        block(
            "Blocked by engineering-fundamentals: the commit would include files that "
            f"look like secrets: {', '.join(risky)}.\nUnstage them with "
            "`git restore --staged <file>`, add them to .gitignore, and rotate the "
            "secret if it was ever pushed."
        )


def extract_message(args: list[str]) -> str | None:
    for i, arg in enumerate(args):
        if arg in ("-m", "--message") and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith("--message="):
            return arg.split("=", 1)[1]
        if arg.startswith("-m") and len(arg) > 2 and not arg.startswith("--"):
            return arg[2:]
        if re.fullmatch(r"-[a-zA-Z]*m", arg) and i + 1 < len(args):
            return args[i + 1]
    return None


def unwrap_heredoc(message: str) -> str:
    """Turn "$(cat <<'EOF'\\nsubject\\n...\\nEOF\\n)" into the message text."""
    match = re.match(r"^\$\(\s*cat\s+<<-?\s*['\"]?(\w+)['\"]?\s*\n(.*)", message, re.S)
    if not match:
        return message
    marker, rest = match.group(1), match.group(2)
    lines = []
    for line in rest.splitlines():
        if line.strip() == marker:
            break
        lines.append(line)
    return "\n".join(lines)


def repo_uses_conventional_commits(cwd: str) -> bool:
    subjects = [s for s in run_git(["log", "-30", "--format=%s"], cwd).splitlines() if s]
    relevant = [s for s in subjects if not ALWAYS_OK_SUBJECT_RE.match(s)]
    if len(relevant) < 5:
        return True  # too little history to tell: default to the convention
    matching = sum(1 for s in relevant if CONVENTIONAL_RE.match(s))
    return matching / len(relevant) >= 0.5


def check_commit_message(args: list[str], cwd: str) -> None:
    if os.environ.get("EF_CONVENTIONAL_COMMITS", "").lower() in ("off", "false", "0", "no"):
        return
    message = extract_message(args)
    if message is None:
        return
    message = unwrap_heredoc(message).strip()
    if not message or message.startswith("$("):
        return
    subject = message.splitlines()[0].strip()
    if ALWAYS_OK_SUBJECT_RE.match(subject) or CONVENTIONAL_RE.match(subject):
        if len(subject) > 72:
            block(
                f"Blocked by engineering-fundamentals: commit subject is {len(subject)} "
                "characters; keep it at most 72 (ideally ~50). Put details in the body."
            )
        return
    if not repo_uses_conventional_commits(cwd):
        return
    block(
        "Blocked by engineering-fundamentals: the commit subject does not follow "
        "Conventional Commits:\n"
        f"  {subject}\n"
        "Expected: <type>(<optional scope>): <imperative summary>, e.g.\n"
        "  feat(rental): show total fee including discounts\n"
        "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.\n"
        "Explain the why in the body. (Opt out with EF_CONVENTIONAL_COMMITS=off.)"
    )


def check_push(args: list[str], cwd: str) -> None:
    force = any(a in ("--force", "-f") or (re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) is not None) for a in args)
    lease = any(a.startswith("--force-with-lease") or a.startswith("--force-if-includes") for a in args)
    plus_refspec = any(a.startswith("+") for a in args)
    if not (force or plus_refspec) or (lease and not plus_refspec):
        return
    positional = [a for a in args if not a.startswith("-")]
    current = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd).strip()
    targets = set()
    for ref in positional[1:]:
        target = re.sub(r"^\+", "", ref).split(":")[-1].replace("refs/heads/", "")
        targets.add(current if target == "HEAD" and current else target)
    if not targets and current:
        targets = {current}
    protected = sorted(t for t in targets if t in PROTECTED_BRANCHES)
    if protected or not targets:
        names = ", ".join(protected) if protected else "an unknown branch"
        block(
            f"Blocked by engineering-fundamentals: force-push to {names}.\n"
            "Rewriting shared history breaks everyone who already pulled it. Use a "
            "new commit (e.g. git revert) instead. If the user explicitly wants this, "
            "they can run the command themselves."
        )


def main() -> None:
    if os.environ.get("EF_GIT_GUARD", "").lower() in ("off", "false", "0", "no"):
        return
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if payload.get("tool_name") != "Bash":
        return
    command = (payload.get("tool_input") or {}).get("command") or ""
    if "git" not in command:
        return
    cwd = payload.get("cwd") or os.getcwd()

    for tokens in split_segments(command):
        parsed = git_subcommand(tokens)
        if not parsed:
            continue
        sub, args = parsed
        if sub == "add":
            check_secrets_on_add(args, cwd)
        elif sub == "commit":
            check_secrets_on_commit(args, cwd)
            check_commit_message(args, cwd)
        elif sub == "push":
            check_push(args, cwd)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:  # never break the session because of the guard itself
        sys.exit(0)
