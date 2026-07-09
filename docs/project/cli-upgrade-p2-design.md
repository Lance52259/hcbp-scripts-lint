# P2 Design: CLI Upgrade Enhancements (Verification, Concurrency, Dry-Run, DX)

## Context

P0 (rollback + commit detection) and P1 (branch pinning, dirty tree, docs, remediation) are complete.
The upgrade feature is production-viable at **~8.5 / 10**. P2 addresses remaining gaps in
verification depth, concurrency safety, operator ergonomics, and test realism.

**Current score (after P1):** 8.5 / 10  
**Target after P2:** ≥ 9.2 / 10

**Prerequisites:** P0 + P1 complete  
**Tracking checklist:** [cli-upgrade-improvements-checklist.md](./cli-upgrade-improvements-checklist.md)

---

## P2 scope overview

| ID | Item | Primary file(s) | Effort | Priority within P2 |
|----|------|-----------------|--------|-------------------|
| P2-2 | Deepen post-upgrade verification | `tools/cli/upgrade.py` | M | **1** |
| P2-3 | Prevent concurrent upgrades | `tools/cli/upgrade.py` | S | **2** |
| P2-4 | Add dry-run mode | `upgrade.py`, `terraform_lint.py` | M | **3** |
| P2-1 | Add `--install-dir` override | `upgrade.py`, `terraform_lint.py` | S | **4** |
| P2-5 | Proxy / offline environment hints | `tools/cli/upgrade.py` | S | **5** |
| P2-6 | Integration tests with real git repo | `acceptances/good/cli_upgrade/` | L | **6** |

**Recommended implementation order:** P2-2 → P2-3 → P2-4 → P2-1 → P2-5 → P2-6

Rationale: strengthen safety first (verification + lock), then operator UX (dry-run + install-dir),
then polish (proxy hints), finally real-git integration tests as quality gate.

---

## P2-2: Deepen post-upgrade verification

### Problem

Current `_verify_tool()` only runs `--help`. A broken rules import or runtime lint failure would
only surface on the user's next real invocation.

### Goal

After pull (when commit changes), verify three layers:

| Layer | Check | Catches |
|-------|-------|---------|
| L1 | `python3 terraform_lint.py --help` | Missing templates, argparse errors |
| L2 | `python3 -c "import rules"` with install dir on `sys.path` | Broken rules package |
| L3 | Minimal lint smoke test on bundled fixture | Runtime rule execution failures |

Skip L2/L3 when `already_up_to_date` (commit unchanged) — same rationale as skipping L1 in P1.

### Proposed `_verify_tool()` refactor

```python
SMOKE_TEST_DIR = "examples/good-examples/basic"
SMOKE_TEST_TIMEOUT_SEC = 60

def _verify_tool(install_dir):
    lint_script = os.path.join(install_dir, ".github", "scripts", "terraform_lint.py")

    # L1: --help
    help_ok, help_error = _run_lint_command([lint_script, "--help"], install_dir)
    if not help_ok:
        return False, help_error

    # L2: import rules
    import_ok, import_error = _run_python_snippet(
        "import sys; sys.path.insert(0, {0!r}); import rules".format(install_dir),
        install_dir,
    )
    if not import_ok:
        return False, "Rules import failed: {0}".format(import_error)

    # L3: smoke lint
    smoke_dir = os.path.join(install_dir, SMOKE_TEST_DIR)
    if os.path.isdir(smoke_dir):
        lint_ok, lint_error = _run_lint_command(
            [lint_script, "--directory", smoke_dir, "--performance-monitoring", "false"],
            install_dir,
        )
        if not lint_ok:
            return False, "Smoke lint failed: {0}".format(lint_error)

    return True, ""
```

### Design decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Which smoke fixture? | `examples/good-examples/basic` | Stable, small, already passes lint |
| Skip L3 if fixture missing? | **Yes** (warn in verbose mode) | Don't block upgrade for trimmed installs |
| Smoke test performance | Disable perf monitoring | Faster, less noisy |
| Timeout | 60s per subprocess | Prevent hung upgrade |

### Rollback interaction

Unchanged from P0 — if any verification layer fails, trigger `git reset --hard <previous_commit>`.

### Tests (P2-2)

| Test | Assert |
|------|--------|
| `test_verify_runs_import_check` | `import rules` subprocess called |
| `test_verify_runs_smoke_lint_when_fixture_exists` | lint `--directory examples/good-examples/basic` called |
| `test_verify_skips_smoke_lint_when_fixture_missing` | upgrade succeeds without L3 |
| `test_verify_failure_triggers_rollback` | L2 or L3 failure → reset called |

---

## P2-3: Prevent concurrent upgrades

### Problem

Two simultaneous `hcbp-lint -u` invocations can race on `git fetch` / `git pull` / `git reset`.

### Goal

Only one upgrade per install directory at a time.

### Proposed mechanism

Use an exclusive lock file: `<install_dir>/.hcbp-upgrade.lock`

```python
UPGRADE_LOCK_FILENAME = ".hcbp-upgrade.lock"
UPGRADE_LOCK_STALE_SEC = 300  # 5 minutes

def _acquire_upgrade_lock(install_dir):
    """
    Create lock file exclusively (O_CREAT | O_EXCL).
    Returns (acquired, lock_path, error_message).
    """
```

**Python 3.6 compatible** — use `os.open()` with `os.O_CREAT | os.O_EXCL | os.O_WRONLY`:

```python
import errno

def _acquire_upgrade_lock(install_dir):
    lock_path = os.path.join(install_dir, UPGRADE_LOCK_FILENAME)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode("utf-8"))
        os.close(fd)
        return True, lock_path, ""
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            return False, lock_path, str(exc)
        # stale lock check
        if _is_stale_lock(lock_path):
            os.remove(lock_path)
            return _acquire_upgrade_lock(install_dir)  # single retry
        return False, lock_path, "Another upgrade is already in progress."
```

```python
def _release_upgrade_lock(lock_path, acquired):
    if acquired and lock_path and os.path.isfile(lock_path):
        try:
            os.remove(lock_path)
        except OSError:
            pass
```

### Insertion point

Wrap entire `upgrade_tool()` body:

```python
def upgrade_tool(install_dir=None, dry_run=False):
    target_dir = ...
    acquired, lock_path, lock_error = _acquire_upgrade_lock(target_dir)
    if not acquired:
        return _build_result(success=False, message=_failure_message(..., "concurrent", ...))
    try:
        return _upgrade_tool_impl(target_dir, dry_run=dry_run)
    finally:
        _release_upgrade_lock(lock_path, acquired)
```

Refactor current `upgrade_tool()` logic into `_upgrade_tool_impl()` to keep lock handling clean.

### Stale lock policy

If lock file is older than 5 minutes, assume previous process crashed and remove it.
Write PID + timestamp into lock file for diagnostics:

```
pid=12345
started=2026-07-09T14:30:00Z
```

### Tests (P2-3)

| Test | Assert |
|------|--------|
| `test_concurrent_upgrade_rejected` | second call fails with "in progress" |
| `test_lock_released_after_success` | lock file removed |
| `test_lock_released_after_failure` | lock file removed on exception |
| `test_stale_lock_is_removed_and_retried` | old lock file → upgrade proceeds |

---

## P2-4: Add dry-run mode

### Problem

Users cannot preview whether an upgrade is available without modifying the installation.

### Goal

`hcbp-lint -u --dry-run` reports current vs remote state without pull/checkout/reset.

### CLI changes

```python
# terraform_lint.py — upgrade-only argument group
parser.add_argument('--dry-run', action='store_true',
    help='Preview available upgrade without modifying the installation (use with -u)')

parser.add_argument('--install-dir',
    help='Override the local installation directory to upgrade (use with -u)')

# Validation
if args.dry_run and not args.upgrade:
    parser.error("--dry-run requires --upgrade (-u)")

if args.upgrade:
    result = upgrade_tool(install_dir=args.install_dir, dry_run=args.dry_run)
```

### Dry-run flow

```
Resolve install dir → preflight (same as normal)
    ↓
dirty tree check (same — report but don't fix)
    ↓
resolve release branch
    ↓
git fetch origin
    ↓
Compare HEAD vs origin/<branch> (no pull, no checkout)
    ↓
Report:
  - Current: v{X} (commit abc1234)
  - Remote:  v{Y} (commit def5678)
  - Status:  "Upgrade available" / "Already up to date"
```

### New helper

```python
def _get_remote_commit(cwd, branch):
    code, stdout, stderr = _run_git_command(
        ["rev-parse", "origin/{0}".format(branch)], cwd=cwd
    )
    ...

def _preview_upgrade(target_dir, release_branch, previous_commit, old_version):
    remote_commit, err = _get_remote_commit(target_dir, release_branch)
    remote_version = _read_version_from_changelog_at_commit(target_dir, remote_commit)
    # For remote version: either read CHANGELOG after fetch (working tree unchanged)
    #   or use `git show origin/<branch>:CHANGELOG.md` — preferred, no side effects
```

**Remote version without pull:**

```python
def _read_changelog_at_ref(cwd, ref):
    code, stdout, _ = _run_git_command(
        ["show", "{0}:CHANGELOG.md".format(ref)], cwd=cwd
    )
    # parse first ## [x.y.z] from stdout
```

### Dry-run output example

```
Dry-run: upgrade preview
Installation directory: ~/.local/share/terraform-linter
Release branch: master
Current:  v3.0.1 (abc1234)
Remote:   v3.0.2 (def5678)
Status:   Upgrade available — run without --dry-run to apply.
```

### Extend `UpgradeResult`

```python
"dry_run",  # bool
```

### Tests (P2-4)

| Test | Assert |
|------|--------|
| `test_dry_run_does_not_pull` | no `git pull` or `git reset` called |
| `test_dry_run_reports_upgrade_available` | remote commit differs → message says "available" |
| `test_dry_run_reports_up_to_date` | remote commit same → "already up to date" |
| `test_dry_run_requires_upgrade_flag` | `--dry-run` alone → argparse error |

---

## P2-1: Add `--install-dir` override

### Problem

Power users / CI may need to upgrade a non-default path without setting `HCBP_LINT_TOOL_DIR`.

### Goal

`hcbp-lint -u --install-dir /path/to/install`

### Implementation

Covered in P2-4 CLI section above. In `upgrade_tool()`:

```python
def upgrade_tool(install_dir=None, dry_run=False):
    target_dir = os.path.abspath(
        install_dir or resolve_tool_install_dir()
    )
```

Priority: `--install-dir` CLI arg > `HCBP_LINT_TOOL_DIR` env > git repo root > default path.

Update `resolve_tool_install_dir()` or pass explicit `install_dir` from CLI (simpler: CLI
passes explicit value, no change to resolution function).

### Tests (P2-1)

| Test | Assert |
|------|--------|
| `test_upgrade_uses_explicit_install_dir` | operations run in given path |
| `test_install_dir_overrides_env_var` | CLI arg wins over `HCBP_LINT_TOOL_DIR` |

---

## P2-5: Proxy / offline environment hints

### Problem

Corporate environments often fail at `git fetch` with SSL/proxy errors. Current P1 `network`
remediation is generic.

### Goal

Classify common fetch error patterns and append specific hints.

### New helper

```python
def _classify_fetch_failure(fetch_error, fetch_output):
    combined = "{0} {1}".format(fetch_error or "", fetch_output or "").lower()
    if "could not resolve host" in combined or "name resolution" in combined:
        return "dns"
    if "connection timed out" in combined or "failed to connect" in combined:
        return "timeout"
    if "ssl" in combined or "certificate" in combined:
        return "ssl"
    if "proxy" in combined or "407" in combined:
        return "proxy"
    if "could not read from remote" in combined or "authentication failed" in combined:
        return "auth"
    return "network"
```

### Extended remediation templates

```python
"dns": "DNS resolution failed. Check network connectivity and DNS settings.",
"timeout": "Connection timed out. Check firewall rules and proxy settings.",
"ssl": "SSL verification failed. Corporate proxies may require git SSL config:\n  git config --global http.sslVerify false  # use with caution",
"proxy": "Proxy authentication may be required:\n  export https_proxy=http://proxy:port\n  git config --global http.proxy http://proxy:port",
"auth": "GitHub authentication failed. For HTTPS, configure credentials or use SSH remote.",
"concurrent": "Another upgrade is in progress. Wait for it to finish or remove stale lock:\n  rm -f <install_dir>/.hcbp-upgrade.lock",
```

Wire into fetch failure path:

```python
fetch_stage = _classify_fetch_failure(fetch_error, fetch_output)
return _build_result(..., message=_failure_message(..., fetch_stage, ...))
```

### Tests (P2-5)

| Test | Assert |
|------|--------|
| `test_fetch_ssl_failure_includes_ssl_hint` | message mentions SSL |
| `test_fetch_proxy_failure_includes_proxy_hint` | message mentions proxy |
| `test_fetch_dns_failure_includes_dns_hint` | message mentions DNS |

---

## P2-6: Integration tests with real git repository

### Problem

All 19 current tests use mocked `_run_git_command`. Real git edge cases (ff-only rejection,
actual rollback) are unverified.

### Goal

Add a small number of **real git** integration tests using a local bare remote.

### Test harness design

```
acceptances/good/cli_upgrade/integration/
  test_upgrade_integration.py
  fixtures/
    bare-remote/        # created at runtime in tmpdir, not committed
```

**Setup (per test class):**

```python
class UpgradeIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_root = tempfile.mkdtemp()
        cls.remote_dir = os.path.join(cls.temp_root, "remote.git")
        cls.install_dir = os.path.join(cls.temp_root, "install")

        # Create bare repo with initial commit
        subprocess.run(["git", "init", "--bare", cls.remote_dir], check=True)
        # Clone, add minimal files (terraform_lint.py stub + CHANGELOG), push
        # ...

    def test_real_upgrade_pulls_new_commit(self):
        # Push v2 to bare remote
        # Run upgrade_tool(install_dir=self.install_dir)
        # Assert HEAD changed, success=True
```

### Scope control

| Scenario | Real git test? |
|----------|---------------|
| Normal upgrade | ✓ |
| Already up to date | ✓ |
| ff-only rejection (diverged local commit) | ✓ |
| Rollback on verify failure | ✓ (inject broken file in remote commit) |
| Concurrent lock | ✓ (two threads) |
| Dry-run | ✓ |

**Skip in CI without git?** No — git is already a prerequisite for the tool.

### Guard: skip if git not available

```python
def setUp(self):
    if subprocess.run(["git", "--version"], stdout=subprocess.PIPE).returncode != 0:
        self.skipTest("git not available")
```

### Estimated effort

~150 lines harness + 6 integration tests. Longest P2 item.

---

## Updated `upgrade_tool()` signature

```python
def upgrade_tool(install_dir=None, dry_run=False):
    """Pull or preview the latest lint tool code for a local installation."""
```

Internal refactor:

```python
def upgrade_tool(install_dir=None, dry_run=False):
    target_dir = os.path.abspath(install_dir or resolve_tool_install_dir())
    acquired, lock_path, lock_error = _acquire_upgrade_lock(target_dir)
    if not acquired:
        return _failure_result(...)
    try:
        if dry_run:
            return _preview_upgrade(target_dir)
        return _execute_upgrade(target_dir)
    finally:
        _release_upgrade_lock(lock_path, acquired)
```

---

## CLI / help / README updates (P2)

### `terraform_lint.py` new arguments

```python
parser.add_argument('--install-dir', help='Override local installation directory (use with -u)')
parser.add_argument('--dry-run', action='store_true',
                    help='Preview upgrade without applying changes (requires -u)')
```

### `cli_help.template` additions

```
  # Preview available upgrade without applying
  {example_prefix} -u --dry-run

  # Upgrade a specific installation directory
  {example_prefix} -u --install-dir ~/.local/share/terraform-linter
```

### README.md additions

Extend Upgrading section with `--dry-run` and `--install-dir` examples.

---

## File change summary

| File | P2-2 | P2-3 | P2-4 | P2-1 | P2-5 | P2-6 |
|------|:----:|:----:|:----:|:----:|:----:|:----:|
| `tools/cli/upgrade.py` | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `.github/scripts/terraform_lint.py` | — | — | ✓ | ✓ | — | — |
| `tools/cli/templates/cli_help.template` | — | — | ✓ | ✓ | — | — |
| `README.md` | — | — | ✓ | ✓ | — | — |
| `acceptances/good/cli_upgrade/test_cli_upgrade.py` | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `acceptances/good/cli_upgrade/integration/` | — | — | — | — | — | ✓ |

**Estimated diff:** ~350 lines added, ~50 removed

---

## Test plan summary (P2)

| # | Test | Covers |
|---|------|--------|
| 1–4 | Verification layer tests | P2-2 |
| 5–8 | Lock acquire/release/stale | P2-3 |
| 9–12 | Dry-run preview | P2-4 |
| 13–14 | `--install-dir` override | P2-1 |
| 15–17 | Fetch error classification | P2-5 |
| 18–23 | Real git integration | P2-6 |

**Total new tests:** ~23 (unit 17 + integration 6)  
**Upgrade suite grows:** 19 → ~42

---

## Risk assessment

| Risk | After P1 | After P2 | Mitigation |
|------|----------|----------|------------|
| `--help` passes but lint broken | 🟡 Medium | 🟢 Low | L2 + L3 verification |
| Concurrent upgrade corruption | 🟡 Medium | 🟢 Low | File lock |
| User can't preview upgrade | 🟡 Medium | 🟢 Low | Dry-run |
| Wrong install dir upgraded | 🟢 Low | 🟢 Low | `--install-dir` explicit override |
| Corporate proxy failures | 🟡 Medium | 🟢 Low | Classified hints |
| Mock-only test blind spots | 🟡 Medium | 🟢 Low | Real git integration |

**Projected score after P2:** 9.2 / 10

**Residual (post-P2):**
- No signed/verified releases (acceptable for git-clone model)
- Smoke test depends on bundled fixture staying valid
- Lock file is advisory (not fcntl flock across all FS edge cases)

---

## Implementation checklist (P2)

- [x] **P2-2** Refactor `_verify_tool()` into L1/L2/L3 layers
- [x] **P2-2** Add `_run_subprocess_command()` helper
- [x] **P2-3** Add `_acquire_upgrade_lock()` / `_release_upgrade_lock()` with stale detection
- [x] **P2-3** Refactor `upgrade_tool()` → lock wrapper + `_execute_upgrade()` impl
- [x] **P2-4** Add `_preview_upgrade()` and `_get_remote_commit()` / `_read_changelog_at_ref()`
- [x] **P2-4** Add `--dry-run` CLI flag with validation
- [x] **P2-1** Add `--install-dir` CLI flag; wire to `upgrade_tool(install_dir=...)`
- [x] **P2-5** Add `_classify_fetch_failure()` and extend remediation templates
- [x] **P2-5** Add `concurrent` remediation stage
- [x] **P2-6** Create `integration/test_upgrade_integration.py` with local bare remote harness
- [x] Update help template and README
- [x] Add unit + integration tests
- [x] Update verification matrix and checklist

---

## Out of scope (post-P2 / future)

- Pin to release tag instead of branch HEAD
- Automatic periodic upgrade check
- `hcbp-lint upgrade` as subcommand (separate from `-u` flag)
- Windows-specific lock handling (`msvcrt.locking`)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-09 | P2 design created after P1 completion |
