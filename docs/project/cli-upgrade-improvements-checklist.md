# CLI Upgrade (`-u` / `--upgrade`) Improvements Checklist

This checklist tracks known gaps in the current `hcbp-lint -u` self-upgrade design.
Use it to prioritize follow-up work after the initial MVP release.

**Current baseline score (strict):** 6.1 / 10  
**Target after P0:** ≥ 7.5 / 10  
**Target after P0 + P1:** ≥ 8.5 / 10  
**Target after P2:** ≥ 9.2 / 10

---

## P0 — Must fix before calling the feature production-ready

- [x] **P0-1: Automatic rollback on post-pull verification failure**
  - Record `HEAD` commit before `git pull`
  - If `--help` verification fails after pull, run `git reset --hard <previous_commit>`
  - Surface rollback result clearly to the user (success / rollback failed)
  - See: [cli-upgrade-p0-design.md](./cli-upgrade-p0-design.md)

- [x] **P0-2: Use commit hash as the source of truth for upgrade state**
  - Compare `HEAD` before and after pull to detect real code changes
  - Do not rely solely on `CHANGELOG.md` version or `Already up to date` string parsing
  - Display short commit hashes in upgrade output (e.g. `abc1234 -> def5678`)
  - See: [cli-upgrade-p0-design.md](./cli-upgrade-p0-design.md)

---

## P1 — Should fix in the next iteration

- [x] **P1-1: Pin pull target branch explicitly**
  - Resolve default remote branch (`origin/HEAD` or `master` / `main` fallback)
  - Use `git pull --ff-only origin <branch>` instead of ambiguous `git pull --ff-only origin`
  - See: [cli-upgrade-p1-design.md](./cli-upgrade-p1-design.md)

- [x] **P1-2: Reject dirty working tree before pull**
  - Run `git status --porcelain` before upgrade
  - Fail early with actionable message if local modifications exist
  - See: [cli-upgrade-p1-design.md](./cli-upgrade-p1-design.md)

- [x] **P1-3: Document `-u` semantics in help and README**
  - Clarify that `-u` is mutually exclusive with lint operations
  - Clarify that upgrade only works for git-based local installations
  - Clarify dev-repo vs installed-copy behavior when `HCBP_LINT_TOOL_DIR` is unset
  - See: [cli-upgrade-p1-design.md](./cli-upgrade-p1-design.md)

- [x] **P1-4: Improve failure remediation guidance**
  - On unrecoverable failure, always suggest `quick_install.sh` reinstall path
  - On ff-only failure, suggest checking `git status` and local modifications
  - See: [cli-upgrade-p1-design.md](./cli-upgrade-p1-design.md)

---

## P2 — Nice to have / future enhancements

- [x] **P2-1: Add `--install-dir` override**
  - Allow explicit upgrade target: `hcbp-lint -u --install-dir ~/.local/share/terraform-linter`
  - See: [cli-upgrade-p2-design.md](./cli-upgrade-p2-design.md)

- [x] **P2-2: Deepen post-upgrade verification**
  - Beyond `--help`, run a minimal smoke test:
    - `import rules` succeeds
    - Optional: lint a bundled good-example fixture with 0 errors
  - See: [cli-upgrade-p2-design.md](./cli-upgrade-p2-design.md)

- [x] **P2-3: Prevent concurrent upgrades**
  - Acquire a file lock (e.g. `<install_dir>/.hcbp-upgrade.lock`) for the duration of upgrade
  - See: [cli-upgrade-p2-design.md](./cli-upgrade-p2-design.md)

- [x] **P2-4: Add dry-run mode**
  - `hcbp-lint -u --dry-run` reports available updates without modifying the install
  - See: [cli-upgrade-p2-design.md](./cli-upgrade-p2-design.md)

- [x] **P2-5: Proxy / offline environment hints**
  - Detect common `git fetch` proxy/SSL failures and print configuration hints
  - See: [cli-upgrade-p2-design.md](./cli-upgrade-p2-design.md)

- [x] **P2-6: Integration tests with real git repository**
  - Cover: successful upgrade, already up-to-date, ff-only rejection, rollback path
  - See: [cli-upgrade-p2-design.md](./cli-upgrade-p2-design.md)

---

## Verification matrix (to complete after each priority batch)

| Scenario | Expected behavior | P0 | P1 | P2 |
|----------|-------------------|:--:|:--:|:--:|
| Normal upgrade (remote ahead) | Success, version + commit shown | [x] | [x] | [x] |
| Already up to date | Success, no file changes | [x] | [x] | [x] |
| Pull succeeds, `--help` fails | Rollback + failure message | [x] | — | — |
| Rollback itself fails | Critical error + reinstall hint | [x] | [x] | [x] |
| Dirty working tree | Fail before pull | — | [x] | [x] |
| Diverged history (ff-only fails) | Fail with remediation hint | — | [x] | [x] |
| Non-git install directory | Fail with reinstall hint | [x] | [x] | [x] |
| No network | Fail at fetch | [x] | [x] | [x] |
| Concurrent `-u` | Second call blocked or retried | — | — | [x] |

---

## Related files

| File | Role |
|------|------|
| `tools/cli/upgrade.py` | Core upgrade logic |
| `.github/scripts/terraform_lint.py` | CLI entry, `-u` / `--upgrade` flag |
| `tools/en-us/quick_install.sh` | Sets `HCBP_LINT_TOOL_DIR` |
| `tools/zh-cn/quick_install.sh` | Sets `HCBP_LINT_TOOL_DIR` |
| `acceptances/good/cli_upgrade/test_cli_upgrade.py` | Unit tests |
| `acceptances/good/cli_upgrade/integration/test_upgrade_integration.py` | Integration tests (real git) |
| `.github/workflows/cli_upgrade_tests.yml` | CI workflow for unit + integration tests |
| `docs/project/cli-upgrade-p0-design.md` | P0 implementation design |
| `docs/project/cli-upgrade-p1-design.md` | P1 implementation design |
| `docs/project/cli-upgrade-p2-design.md` | P2 implementation design |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-09 | Initial checklist created from design review |
| 2026-07-09 | P0 completed; P1 design added |
| 2026-07-09 | P1 completed |
| 2026-07-09 | P2 design added |
| 2026-07-09 | P2 completed |
| 2026-07-09 | Added integration tests for diverged history, rollback, and concurrent upgrade |
| 2026-07-09 | Added `.github/workflows/cli_upgrade_tests.yml` to run unit + integration tests in CI |
| 2026-07-09 | Trimmed redundant unit tests now covered by integration tests (25 → 16) |
