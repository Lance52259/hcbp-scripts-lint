# P1 Design: CLI Upgrade Hardening (Branch Pinning, Dirty Tree, Docs)

## Context

P0 delivered rollback and commit-based state detection. The upgrade feature is now safe against
post-pull verification failures, but still has predictable gaps in branch targeting, local
modification handling, user guidance, and failure remediation.

**Current score (after P0):** 7.5 / 10  
**Target after P1:** ≥ 8.5 / 10

**Prerequisite:** P0 complete ([cli-upgrade-p0-design.md](./cli-upgrade-p0-design.md))

**Tracking checklist:** [cli-upgrade-improvements-checklist.md](./cli-upgrade-improvements-checklist.md)

---

## P1 scope overview

| ID | Item | Primary file(s) | Effort |
|----|------|-----------------|--------|
| P1-1 | Pin pull target branch explicitly | `tools/cli/upgrade.py` | M |
| P1-2 | Reject dirty working tree before pull | `tools/cli/upgrade.py` | S |
| P1-3 | Document `-u` semantics | `cli_help.template`, `README.md` | S |
| P1-4 | Improve failure remediation guidance | `tools/cli/upgrade.py` | S |

**Recommended implementation order:** P1-1 → P1-2 → P1-4 → P1-3  
(Docs last so they reflect final behavior.)

---

## P1-1: Pin pull target branch explicitly

### Problem

Current pull logic:

```python
git pull --ff-only origin      # ambiguous — no branch ref
git pull --ff-only             # fallback — depends on upstream config
```

Risks:
- User on a feature branch pulls that branch's remote, not `master`
- Clone without upstream tracking causes first pull attempt to fail unnecessarily
- Behavior varies across git versions and local config

### Goal

Always pull the repository's **default release branch** from `origin`, regardless of the
currently checked-out local branch — unless the user is already on that branch.

For `hcbp-scripts-lint`, the release branch is `master` (per `quick_install.sh` clone URL).

### Proposed branch resolution

```
┌────────────────────────────────────────────┐
│ 1. git symbolic-ref --short refs/remotes/  │
│    origin/HEAD  →  e.g. "origin/master"    │
└──────────────────┬─────────────────────────┘
                   │ success
                   ▼
         branch = "master"  (strip "origin/" prefix)
                   │
                   │ failure
                   ▼
┌────────────────────────────────────────────┐
│ 2. Check remote branches in order:         │
│    origin/master → origin/main             │
└──────────────────┬─────────────────────────┘
                   │ found
                   ▼
         branch = "master" or "main"
                   │
                   │ not found
                   ▼
         FAIL: "Cannot determine default branch"
```

### New helper

```python
DEFAULT_BRANCH_CANDIDATES = ("master", "main")

def _resolve_origin_branch(cwd):
    """
    Return the origin branch name to pull (e.g. 'master').
    Returns (branch_name, error_message).
    """
```

**Resolution steps:**

1. `git symbolic-ref --short refs/remotes/origin/HEAD`
   - Strip `origin/` prefix → e.g. `master`
2. Fallback: `git branch -r --list origin/master origin/main`
   - Prefer `master`, then `main`
3. If all fail → return error before pull

### Updated pull command

```python
branch, branch_error = _resolve_origin_branch(target_dir)
if not branch:
    return _build_result(success=False, message=branch_error, ...)

# Replace current two-step pull with single explicit command:
pull_code, pull_output, pull_error = _run_git_command(
    ["pull", "--ff-only", "origin", branch],
    cwd=target_dir,
)
# REMOVE fallback: git pull --ff-only (no longer needed)
```

### Checkout strategy (decision required)

Two options — **recommend Option A** for minimal scope:

| Option | Behavior | Pros | Cons |
|--------|----------|------|------|
| **A: Pull current branch only if it matches origin default; else checkout default first** | If `git rev-parse --abbrev-ref HEAD` != `branch`, run `git checkout <branch>` then pull | Always upgrades to latest release | Modifies user's checked-out branch |
| **B: Always pull explicit branch into current HEAD** | `git merge --ff-only origin/<branch>` without checkout | Non-destructive to branch pointer | More complex; may fail if on wrong branch |

**Recommended: Option A** — local install is a tool copy, not a dev workspace. Checking out
`master` before pull is acceptable and matches `quick_install.sh` intent.

```python
current_branch = _get_current_branch(target_dir)
if current_branch != branch:
    checkout_code, _, checkout_error = _run_git_command(
        ["checkout", branch], cwd=target_dir
    )
    if checkout_code != 0:
        return _build_result(
            success=False,
            message=(
                "Failed to switch to release branch '{0}':\n{1}"
            ).format(branch, checkout_error),
            ...
        )
    # Re-read HEAD after checkout (commit may differ from previous_commit)
    previous_commit, _ = _get_head_commit(target_dir)
```

> **Note:** If checkout changes `previous_commit`, re-snapshot before pull. Print informative
> message: `Switched to release branch: master`.

### Output enhancement

```
Upgrading HCBP lint tool...
Installation directory: ~/.local/share/terraform-linter
Release branch: master
Current version: v3.0.1 (commit abc1234)
```

### Tests (P1-1)

| Test | Mock | Assert |
|------|------|--------|
| `test_resolve_branch_from_origin_head` | `symbolic-ref` returns `origin/master` | pull uses `origin master` |
| `test_resolve_branch_fallback_to_main` | `symbolic-ref` fails, `branch -r` lists `origin/main` | pull uses `origin main` |
| `test_resolve_branch_fails_when_unknown` | all resolution fails | early abort, no pull |
| `test_checkout_release_branch_when_on_feature` | HEAD branch = `feature/x` | `git checkout master` called before pull |
| `test_no_checkout_when_already_on_release_branch` | HEAD branch = `master` | no checkout call |

---

## P1-2: Reject dirty working tree before pull

### Problem

If the user (or a failed partial upgrade) left modified files in the install directory,
`git pull --ff-only` may fail with a cryptic error — or in edge cases behave unexpectedly.

### Goal

Fail fast **before** `git fetch` with a clear, actionable message.

### New helper

```python
def _has_dirty_working_tree(cwd):
    """
    Return (is_dirty, status_output).
    Uses git status --porcelain.
    """
    code, stdout, stderr = _run_git_command(["status", "--porcelain"], cwd=cwd)
    if code != 0:
        return True, stderr or stdout  # treat as dirty / unsafe to proceed
    return bool(stdout.strip()), stdout
```

### Insertion point

After `_get_head_commit()` succeeds, **before** `print("Upgrading...")`:

```python
is_dirty, status_output = _has_dirty_working_tree(target_dir)
if is_dirty:
    return _build_result(
        success=False,
        message=(
            "Cannot upgrade: local modifications detected in the installation directory.\n"
            "Please discard local changes or reinstall:\n"
            "  git -C \"{0}\" status\n"
            "  git -C \"{0}\" reset --hard HEAD\n"
            "Or reinstall:\n"
            "  curl -fsSL https://raw.githubusercontent.com/chnsz/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash\n"
            "\nModified files:\n{1}"
        ).format(target_dir, status_output or "(unable to read status)"),
        old_version=old_version,
        new_version=old_version,
        old_commit=previous_commit,
        new_commit=previous_commit,
    )
```

### Design decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Block on untracked files? | **Yes** | `git status --porcelain` includes `??` entries; untracked files may interfere |
| Block on staged-only changes? | **Yes** | Any non-empty porcelain output = unsafe |
| Auto `git reset --hard`? | **No** | Too destructive; provide command hint instead |

### Tests (P1-2)

| Test | Mock | Assert |
|------|------|--------|
| `test_upgrade_rejects_dirty_working_tree` | porcelain returns `M file.py` | fail before fetch, message mentions modifications |
| `test_upgrade_proceeds_when_tree_clean` | porcelain returns empty | fetch/pull called |
| `test_upgrade_rejects_when_status_fails` | `git status` returns non-zero | fail early |

---

## P1-4: Improve failure remediation guidance

### Problem

Some failure paths already include `REINSTALL_HINT` (P0), but others return raw git errors
without context-specific next steps.

### Goal

Every failure message includes a **context-specific remediation block**.

### Remediation map

| Failure stage | Remediation block |
|---------------|-------------------|
| Install dir not found | `quick_install.sh` one-liner |
| Not a git repo | `quick_install.sh` one-liner |
| Git not found | "Install git, then retry" |
| HEAD unreadable | `git -C <dir> status` + reinstall hint |
| Dirty working tree (P1-2) | `git reset --hard` + reinstall hint |
| Branch resolution failed | "Check remote: git remote -v" + reinstall hint |
| Checkout failed | "git -C <dir> checkout master" + reinstall hint |
| Fetch failed (network) | "Check network/proxy" + `git -C <dir> fetch origin` |
| Pull ff-only rejected | "Local history diverged" + `git status` + reinstall hint |
| Verify failed + rollback ok | "Upgrade aborted, previous version restored" |
| Verify failed + rollback failed | `REINSTALL_HINT` (existing) |

### Implementation approach

Add a helper to avoid message duplication:

```python
def _remediation(stage, install_dir=None):
    """Return stage-specific remediation text."""

REMEDIATION = {
    "reinstall": REINSTALL_HINT,
    "network": (
        "Check your network connection and proxy settings, then retry:\n"
        "  git -C \"{dir}\" fetch origin"
    ),
    "diverged": (
        "Your installation has diverged from the remote branch.\n"
        "Inspect local state:\n"
        "  git -C \"{dir}\" status\n"
        "  git -C \"{dir}\" log --oneline -5\n"
        "To reset and reinstall:\n"
        "  curl -fsSL https://raw.githubusercontent.com/chnsz/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash"
    ),
    ...
}
```

Refactor existing `_build_result(success=False, ...)` call sites to append `_remediation(...)`.

### Pull ff-only failure — special case (P1-4 + P1-1 synergy)

When `git pull --ff-only origin master` fails:

```python
if pull_code != 0:
    is_dirty, _ = _has_dirty_working_tree(target_dir)  # re-check
    if is_dirty:
        hint = _remediation("dirty", target_dir)
    elif "diverged" in (pull_error or "").lower() or "not possible to fast-forward" in (pull_error or "").lower():
        hint = _remediation("diverged", target_dir)
    else:
        hint = _remediation("pull_failed", target_dir)

    return _build_result(
        success=False,
        message="Failed to pull latest changes from origin/{0}:\n{1}\n\n{2}".format(
            branch, pull_error or pull_output, hint
        ),
        ...
    )
```

### Tests (P1-4)

| Test | Assert |
|------|--------|
| `test_fetch_failure_includes_network_hint` | message contains "network" or "fetch origin" |
| `test_pull_ff_only_failure_includes_diverged_hint` | message contains "git status" |
| `test_all_failure_paths_include_remediation` | parametrize over failure stages |

---

## P1-3: Document `-u` semantics in help and README

### Problem

Users may not understand:
- `-u` exits immediately (does not run lint)
- Only works for git-based installs via `quick_install.sh`
- Dev-repo invocation upgrades the source repo, not `~/.local/share/terraform-linter`

### Goal

Document behavior in two places without bloating `--help` output.

### 1. CLI help template (`tools/cli/templates/cli_help.template`)

Add a concise **Upgrade** section after Examples:

```
Upgrade Notes:
  - Requires a git-based local installation (via quick_install.sh)
  - Pulls the latest release branch from origin (master)
  - Exits immediately; does not run lint checks in the same invocation
  - When run via hcbp-lint, upgrades ~/.local/share/terraform-linter
  - When run via python3 terraform_lint.py from a git repo, upgrades that repo
```

Add to Examples block (already has `{example_prefix} -u`; keep it).

Update argparse help text in `terraform_lint.py`:

```python
parser.add_argument('-u', '--upgrade', action='store_true',
    help='Pull the latest release from origin (git install only; exits without linting)')
```

### 2. README.md

Add under the Local Installation section (~line 110):

```markdown
#### Upgrading

After installation, pull the latest version without re-running the install script:

```bash
hcbp-lint -u
# or
hcbp-lint --upgrade
```

Requirements:
- Installed via `quick_install.sh` (git clone to `~/.local/share/terraform-linter`)
- Network access to GitHub
- Git available in PATH

> **Note:** `-u` only upgrades the tool itself and does not lint your Terraform code.
> It cannot be combined with lint options in the same command.
```

### 3. No new docs file

Keep changes in existing `README.md` and `cli_help.template` only (per minimal-scope principle).

### Tests (P1-3)

| Test | Assert |
|------|--------|
| `test_help_includes_upgrade_notes` | epilog contains "Upgrade Notes" |
| `test_help_upgrade_flag_description` | `-u, --upgrade` help mentions "git" or "without linting" |

---

## Updated flow (after P1)

```
Resolve install dir
    ↓
Preflight: dir exists, is git repo, git available
    ↓
Snapshot HEAD commit + CHANGELOG version
    ↓
[P1-2] git status --porcelain → reject if dirty
    ↓
[P1-1] Resolve origin default branch (master/main)
    ↓
[P1-1] Checkout release branch if needed
    ↓
Re-snapshot HEAD if branch switched
    ↓
git fetch origin
    ↓
[P1-1] git pull --ff-only origin <branch>
    ↓
[P1-4] On failure → context-specific remediation
    ↓
Compare commits (P0)
    ↓
If changed → verify --help (P0) → rollback on failure (P0)
    ↓
Success message with version + commit
```

---

## API changes

### `UpgradeResult` — optional extension

```python
# Add optional field (backward-compatible for CLI entry point):
"release_branch",  # e.g. "master" — empty string if not resolved
```

CLI entry (`terraform_lint.py`) still only reads `.success` and `.message` — no change required.

### New exported helpers (internal)

```python
_resolve_origin_branch(cwd)
_get_current_branch(cwd)
_has_dirty_working_tree(cwd)
_remediation(stage, install_dir)
```

Not exported from `tools/cli/__init__.py` unless needed for testing.

---

## File change summary

| File | P1-1 | P1-2 | P1-3 | P1-4 |
|------|:----:|:----:|:----:|:----:|
| `tools/cli/upgrade.py` | ✓ | ✓ | — | ✓ |
| `tools/cli/templates/cli_help.template` | — | — | ✓ | — |
| `.github/scripts/terraform_lint.py` | — | — | ✓ | — |
| `README.md` | — | — | ✓ | — |
| `acceptances/good/cli_upgrade/test_cli_upgrade.py` | ✓ | ✓ | ✓ | ✓ |
| `docs/project/cli-upgrade-improvements-checklist.md` | ✓ | ✓ | ✓ | ✓ |

**Estimated diff:** ~180 lines added, ~30 removed

---

## Test plan summary (P1)

| # | Test name | Covers |
|---|-----------|--------|
| 1 | `test_resolve_branch_from_origin_head` | P1-1 |
| 2 | `test_resolve_branch_fallback_to_main` | P1-1 |
| 3 | `test_resolve_branch_fails_when_unknown` | P1-1 |
| 4 | `test_checkout_release_branch_when_on_feature` | P1-1 |
| 5 | `test_upgrade_rejects_dirty_working_tree` | P1-2 |
| 6 | `test_upgrade_proceeds_when_tree_clean` | P1-2 |
| 7 | `test_fetch_failure_includes_network_hint` | P1-4 |
| 8 | `test_pull_failure_includes_diverged_hint` | P1-4 |
| 9 | `test_help_includes_upgrade_notes` | P1-3 |
| 10 | `test_help_upgrade_flag_description` | P1-3 |

**Total new tests:** 10 (upgrade suite grows from 11 → ~21)

---

## Risk assessment

| Risk | Before P1 | After P1 | Mitigation |
|------|-----------|----------|------------|
| Pull wrong branch | 🟡 Medium | 🟢 Low | Explicit branch + checkout |
| Dirty tree corrupts upgrade | 🟡 Medium | 🟢 Low | Early rejection |
| User confusion about `-u` | 🟡 Medium | 🟢 Low | README + help notes |
| Cryptic git errors | 🟡 Medium | 🟢 Low | Remediation map |
| Checkout loses local branch pointer | 🟢 Low | 🟢 Low | Acceptable for tool install dir |

**Residual risks (deferred to P2):**
- No dry-run preview
- No concurrent upgrade lock
- Shallow verification (`--help` only)

---

## Implementation checklist (P1)

- [x] **P1-1** Add `_resolve_origin_branch()` and `_get_current_branch()`
- [x] **P1-1** Checkout release branch when not already on it; re-snapshot HEAD
- [x] **P1-1** Replace ambiguous pull with `git pull --ff-only origin <branch>`
- [x] **P1-1** Print `Release branch: <branch>` in upgrade output
- [x] **P1-2** Add `_has_dirty_working_tree()` and early rejection
- [x] **P1-4** Add `_remediation()` helper and refactor all failure messages
- [x] **P1-4** Special-case ff-only and fetch failure messages
- [x] **P1-3** Add "Upgrade Notes" section to `cli_help.template`
- [x] **P1-3** Update `-u` argparse help text
- [x] **P1-3** Add "Upgrading" subsection to `README.md`
- [x] Add 10 new unit tests
- [x] Update verification matrix in checklist
- [x] Mark P1 items complete in checklist

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-09 | P1 design created after P0 implementation |
