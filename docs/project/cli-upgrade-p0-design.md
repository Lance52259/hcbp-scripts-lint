# P0 Design: CLI Upgrade Rollback & Commit-Based State Detection

## Problem statement

The current `upgrade_tool()` implementation has two critical gaps:

1. **No rollback:** If `git pull` succeeds but post-upgrade `--help` verification fails, the
   installation is left in a broken state with no automatic recovery.
2. **Unreliable upgrade detection:** Upgrade status is inferred from `CHANGELOG.md` version strings
   and the substring `"Already up to date"` in `git pull` output. This can misrepresent the
   actual code state (hotfixes without changelog bumps, i18n differences in git output, etc.).

---

## Goals (P0 scope)

| ID | Goal |
|----|------|
| G1 | Never leave a broken installation after a failed verification |
| G2 | Use git commit hash as the authoritative indicator of whether code changed |
| G3 | Keep `CHANGELOG` version as user-facing supplementary info only |
| G4 | Remain Python 3.6 compatible |
| G5 | Minimize diff scope — enhance `tools/cli/upgrade.py` only |

**Out of scope for P0:** branch pinning (P1), dirty-tree checks (P1), deep smoke tests (P2).

---

## Proposed flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Resolve install dir + preflight checks (existing)        │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Snapshot state BEFORE pull                               │
│    • previous_commit = git rev-parse HEAD                   │
│    • old_version       = CHANGELOG first entry (display)    │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. git fetch origin + git pull --ff-only (existing)         │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Snapshot state AFTER pull                                │
│    • new_commit  = git rev-parse HEAD                       │
│    • new_version = CHANGELOG first entry (display)          │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
              ┌────────────┴────────────┐
              │ previous_commit ==      │
              │ new_commit ?            │
              └────────────┬────────────┘
                    yes    │    no
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌──────────────────┐    ┌──────────────────────┐
   │ Already up to    │    │ 5. Run --help verify │
   │ date → SUCCESS   │    └──────────┬───────────┘
   └──────────────────┘               │
                                 pass │ fail
                           ┌──────────┴──────────┐
                           ▼                     ▼
                ┌──────────────────┐   ┌───────────────────────┐
                │ SUCCESS          │   │ 6. git reset --hard     │
                │ show commit +    │   │    <previous_commit>    │
                │ version info     │   └──────────┬────────────┘
                └──────────────────┘              │
                                          ok      │ fail
                                    ┌─────────────┴────────────┐
                                    ▼                          ▼
                         ┌──────────────────┐      ┌─────────────────────┐
                         │ FAILURE          │      │ CRITICAL FAILURE    │
                         │ "Rolled back"    │      │ "Rollback failed,   │
                         │ exit 1           │      │  reinstall required"│
                         └──────────────────┘      │ exit 1              │
                                                   └─────────────────────┘
```

---

## API changes

### `UpgradeResult` (extend namedtuple)

```python
UpgradeResult = namedtuple(
    "UpgradeResult",
    [
        "success",
        "message",
        "old_version",
        "new_version",
        "old_commit",        # NEW: full SHA before pull
        "new_commit",        # NEW: full SHA after pull
        "already_up_to_date",
        "rolled_back",       # NEW: True if rollback was performed
    ],
)
```

Backward compatibility: callers currently only use `.success` and `.message` in
`terraform_lint.py` — no breaking change for the CLI entry point.

### New internal helpers

```python
def _get_head_commit(cwd):
    """Return full HEAD commit SHA, or None on failure."""

def _short_commit(commit_sha):
    """Return 7-char abbreviated SHA for display."""

def _rollback_to_commit(cwd, commit_sha):
    """Run git reset --hard <commit>. Return (ok, error_message)."""
```

---

## Detailed behavior

### 1. Snapshot before pull

```python
previous_commit = _get_head_commit(target_dir)
if not previous_commit:
    return UpgradeResult(success=False, message="Failed to read current HEAD commit.", ...)
```

Record **before** `git pull`, not before `git fetch` — fetch does not change `HEAD`.

### 2. Detect "already up to date" via commit comparison

```python
new_commit = _get_head_commit(target_dir)
already_up_to_date = (previous_commit == new_commit)
```

**Replace** the current logic:

```python
# REMOVE — unreliable
already_up_to_date = "Already up to date" in pull_output
```

When `already_up_to_date` is `True`:
- Skip verification (optional optimization — code unchanged, prior install was working)
- Return success immediately

> **Rationale:** If `HEAD` did not move, the working tree is identical to the pre-upgrade state.
> Re-running `--help` adds latency with no safety benefit.

### 3. Verification failure → rollback

```python
if not verified:
    rollback_ok, rollback_error = _rollback_to_commit(target_dir, previous_commit)
    if rollback_ok:
        message = (
            "Upgrade failed verification and was rolled back.\n"
            "Commit: {0}\n"
            "Error: {1}"
        ).format(_short_commit(previous_commit), verify_message)
        rolled_back = True
    else:
        message = (
            "Upgrade failed verification AND rollback failed.\n"
            "Installation may be broken. Please reinstall:\n"
            "  curl -fsSL https://raw.githubusercontent.com/chnsz/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash\n"
            "Verify error: {0}\n"
            "Rollback error: {1}"
        ).format(verify_message, rollback_error)
        rolled_back = False

    return UpgradeResult(success=False, message=message, rolled_back=rolled_back, ...)
```

### 4. Success message format

```python
# Already up to date
"Tool is already up to date (v{version}, commit {short_sha})."

# Upgraded
"Upgrade completed: v{old} -> v{new} ({old_sha} -> {new_sha})."

# Upgraded, same changelog version (hotfix)
"Upgrade completed: v{version} ({old_sha} -> {new_sha})."
```

---

## Error handling matrix

| Stage | Failure | Action | User message |
|-------|---------|--------|--------------|
| `rev-parse HEAD` (pre) | git error | Abort, no pull | "Cannot read current commit" |
| `git fetch` | network/auth | Abort, no pull | Existing fetch error |
| `git pull` | ff-only rejected | Abort, no pull | Existing pull error |
| `rev-parse HEAD` (post) | git error | Attempt rollback to `previous_commit` | "Cannot read new commit, rolled back" |
| `--help` verify | non-zero exit | `reset --hard previous_commit` | "Rolled back to {sha}" |
| `reset --hard` | git error | — | "Rollback failed, reinstall required" |

---

## Test plan (P0 additions)

Add to `acceptances/good/cli_upgrade/test_cli_upgrade.py`:

| Test case | Mock strategy | Assertion |
|-----------|---------------|-----------|
| `test_upgrade_rolls_back_on_verify_failure` | pull succeeds, verify fails, reset succeeds | `success=False`, `rolled_back=True`, reset called with previous SHA |
| `test_upgrade_critical_failure_when_rollback_fails` | pull succeeds, verify fails, reset fails | message contains "reinstall" |
| `test_already_up_to_date_detected_by_commit` | pull returns same HEAD | `already_up_to_date=True`, verify skipped |
| `test_upgrade_success_shows_commit_hashes` | pull changes HEAD, verify passes | message contains `abc1234 -> def5678` |
| `test_get_head_commit_returns_none_on_git_failure` | rev-parse fails | early abort before pull |

---

## Implementation checklist (P0 coding tasks)

- [x] Add `_get_head_commit()`, `_short_commit()`, `_rollback_to_commit()` to `upgrade.py`
- [x] Extend `UpgradeResult` with `old_commit`, `new_commit`, `rolled_back`
- [x] Refactor `upgrade_tool()` to follow the proposed flow
- [x] Replace string-based "already up to date" detection with commit comparison
- [x] Skip verification when `previous_commit == new_commit`
- [x] Add rollback path on verification failure
- [x] Update `tools/cli/__init__.py` exports if needed
- [x] Add 5 new unit tests (see test plan above)
- [x] Update checklist in `cli-upgrade-improvements-checklist.md` when done

---

## Risk assessment after P0

| Risk | Before P0 | After P0 |
|------|-----------|----------|
| Broken install after failed verify | 🔴 High | 🟢 Low |
| False "already up to date" | 🟡 Medium | 🟢 Low |
| False "upgraded" (changelog only) | 🟡 Medium | 🟢 Low |
| Rollback itself fails | 🔴 High | 🟡 Medium (explicit critical message) |
| Wrong branch pulled | 🟡 Medium | 🟡 Medium (unchanged, P1) |
| Dirty working tree | 🟡 Medium | 🟡 Medium (unchanged, P1) |

**Projected score after P0:** 7.5 / 10

---

## Estimated change size

| File | Lines changed (est.) |
|------|---------------------|
| `tools/cli/upgrade.py` | +80 / -20 |
| `tools/cli/__init__.py` | +2 |
| `acceptances/good/cli_upgrade/test_cli_upgrade.py` | +60 |
| `docs/project/cli-upgrade-improvements-checklist.md` | checkbox updates |

**No changes required** to `terraform_lint.py`, install scripts, or help template for P0.
