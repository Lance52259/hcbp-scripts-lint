#!/usr/bin/env python3
"""Self-upgrade helpers for locally installed HCBP lint tools."""

import errno
import os
import re
import subprocess
import time
from collections import namedtuple
from datetime import datetime, timezone

from ._project import get_project_root

DEFAULT_INSTALL_DIR = os.path.expanduser("~/.local/share/terraform-linter")
INSTALL_DIR_ENV_VAR = "HCBP_LINT_TOOL_DIR"
DEFAULT_BRANCH_CANDIDATES = ("master", "main")
UPGRADE_LOCK_FILENAME = ".hcbp-upgrade.lock"
UPGRADE_LOCK_STALE_SEC = 300
SMOKE_TEST_DIR = os.path.join("examples", "good-examples", "basic")
SMOKE_TEST_TIMEOUT_SEC = 60
CHANGELOG_VERSION_PATTERN = re.compile(r"^## \[([^\]]+)\]", re.MULTILINE)
REINSTALL_HINT = (
    "Please reinstall using quick_install.sh:\n"
    "  curl -fsSL https://raw.githubusercontent.com/chnsz/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash"
)

UpgradeResult = namedtuple(
    "UpgradeResult",
    [
        "success",
        "message",
        "old_version",
        "new_version",
        "old_commit",
        "new_commit",
        "already_up_to_date",
        "rolled_back",
        "release_branch",
        "dry_run",
    ],
)


def resolve_tool_install_dir():
    """Resolve the directory that should be upgraded."""
    env_dir = os.environ.get(INSTALL_DIR_ENV_VAR, "").strip()
    if env_dir:
        return os.path.abspath(env_dir)

    project_root = get_project_root()
    if os.path.isdir(os.path.join(project_root, ".git")):
        return project_root

    return DEFAULT_INSTALL_DIR


def _parse_changelog_version(content):
    match = CHANGELOG_VERSION_PATTERN.search(content)
    if not match:
        return "unknown"
    return match.group(1).strip()


def _read_version_from_changelog(changelog_path):
    if not os.path.isfile(changelog_path):
        return "unknown"

    with open(changelog_path, "r", encoding="utf-8") as changelog_file:
        return _parse_changelog_version(changelog_file.read())


def _read_changelog_at_ref(cwd, ref):
    code, stdout, stderr = _run_git_command(["show", "{0}:CHANGELOG.md".format(ref)], cwd=cwd)
    if code != 0 or not stdout:
        return "unknown", stderr or stdout or "Failed to read CHANGELOG at {0}".format(ref)
    return _parse_changelog_version(stdout), ""


def _run_git_command(args, cwd):
    try:
        completed = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
    except OSError as exc:
        return 127, "", str(exc)

    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def _run_subprocess_command(args, cwd=None, timeout=SMOKE_TEST_TIMEOUT_SEC):
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, "", "Command timed out after {0}s".format(timeout)
    except OSError as exc:
        return 127, "", str(exc)

    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def _remediation(stage, install_dir=""):
    templates = {
        "reinstall": REINSTALL_HINT,
        "git_missing": "Install Git and ensure it is available in PATH, then retry.",
        "head_unreadable": (
            "Inspect repository state:\n"
            "  git -C \"{0}\" status\n\n"
            "{1}"
        ).format(install_dir, REINSTALL_HINT),
        "dirty": (
            "Discard local changes, then retry:\n"
            "  git -C \"{0}\" status\n"
            "  git -C \"{0}\" reset --hard HEAD\n"
            "Or reinstall:\n"
            "  curl -fsSL https://raw.githubusercontent.com/chnsz/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash"
        ).format(install_dir),
        "branch": (
            "Check remote configuration:\n"
            "  git -C \"{0}\" remote -v\n"
            "  git -C \"{0}\" branch -r\n\n"
            "{1}"
        ).format(install_dir, REINSTALL_HINT),
        "checkout": (
            "Switch to the release branch manually:\n"
            "  git -C \"{0}\" checkout master\n\n"
            "{1}"
        ).format(install_dir, REINSTALL_HINT),
        "network": (
            "Check your network connection and proxy settings, then retry:\n"
            "  git -C \"{0}\" fetch origin"
        ).format(install_dir),
        "dns": "DNS resolution failed. Check network connectivity and DNS settings.",
        "timeout": "Connection timed out. Check firewall rules and proxy settings.",
        "ssl": (
            "SSL verification failed. Corporate proxies may require git SSL config:\n"
            "  git config --global http.sslVerify false  # use with caution"
        ),
        "proxy": (
            "Proxy authentication may be required:\n"
            "  export https_proxy=http://proxy:port\n"
            "  git config --global http.proxy http://proxy:port"
        ),
        "auth": "GitHub authentication failed. Configure HTTPS credentials or use an SSH remote.",
        "concurrent": (
            "Another upgrade is in progress. Wait for it to finish or remove a stale lock:\n"
            "  rm -f \"{0}/{1}\""
        ).format(install_dir, UPGRADE_LOCK_FILENAME),
        "diverged": (
            "Your installation has diverged from the remote release branch.\n"
            "Inspect local state:\n"
            "  git -C \"{0}\" status\n"
            "  git -C \"{0}\" log --oneline -5\n"
            "To reset and reinstall:\n"
            "  curl -fsSL https://raw.githubusercontent.com/chnsz/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash"
        ).format(install_dir),
        "pull_failed": (
            "Inspect local state:\n"
            "  git -C \"{0}\" status\n\n"
            "{1}"
        ).format(install_dir, REINSTALL_HINT),
    }
    return templates.get(stage, REINSTALL_HINT)


def _failure_message(error_message, remediation_stage, install_dir):
    return "{0}\n\n{1}".format(error_message, _remediation(remediation_stage, install_dir))


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


def _classify_pull_failure(pull_error, pull_output):
    combined = "{0} {1}".format(pull_error or "", pull_output or "").lower()
    if "not possible to fast-forward" in combined or "diverged" in combined:
        return "diverged"
    return "pull_failed"


def _get_head_commit(cwd):
    code, stdout, stderr = _run_git_command(["rev-parse", "HEAD"], cwd=cwd)
    if code != 0 or not stdout:
        return None, stderr or stdout or "Failed to read HEAD commit"
    return stdout.strip(), ""


def _get_remote_commit(cwd, branch):
    code, stdout, stderr = _run_git_command(["rev-parse", "origin/{0}".format(branch)], cwd=cwd)
    if code != 0 or not stdout:
        return None, stderr or stdout or "Failed to read remote commit"
    return stdout.strip(), ""


def _get_current_branch(cwd):
    code, stdout, stderr = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if code != 0 or not stdout:
        return None, stderr or stdout or "Failed to read current branch"
    return stdout.strip(), ""


def _resolve_origin_branch(cwd):
    code, stdout, stderr = _run_git_command(
        ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        cwd=cwd,
    )
    if code == 0 and stdout:
        branch = stdout.strip()
        if branch.startswith("origin/"):
            branch = branch[len("origin/"):]
        if branch:
            return branch, ""

    for candidate in DEFAULT_BRANCH_CANDIDATES:
        check_code, check_stdout, _ = _run_git_command(
            ["branch", "-r", "--list", "origin/{0}".format(candidate)],
            cwd=cwd,
        )
        if check_code == 0 and check_stdout.strip():
            return candidate, ""

    return None, _failure_message(
        "Cannot determine default release branch from origin.",
        "branch",
        cwd,
    )


def _has_dirty_working_tree(cwd):
    code, stdout, stderr = _run_git_command(["status", "--porcelain"], cwd=cwd)
    if code != 0:
        return True, stderr or stdout or "git status failed"
    filtered_lines = [
        line for line in stdout.splitlines()
        if UPGRADE_LOCK_FILENAME not in line
    ]
    filtered_output = "\n".join(filtered_lines).strip()
    return bool(filtered_output), filtered_output or stdout


def _short_commit(commit_sha):
    if not commit_sha:
        return "unknown"
    return commit_sha[:7]


def _rollback_to_commit(cwd, commit_sha):
    code, stdout, stderr = _run_git_command(["reset", "--hard", commit_sha], cwd=cwd)
    if code != 0:
        return False, stderr or stdout or "git reset --hard failed"
    return True, ""


def _is_stale_lock(lock_path):
    try:
        age = time.time() - os.path.getmtime(lock_path)
    except OSError:
        return False
    return age > UPGRADE_LOCK_STALE_SEC


def _acquire_upgrade_lock(install_dir, retry=True):
    lock_path = os.path.join(install_dir, UPGRADE_LOCK_FILENAME)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = "pid={0}\nstarted={1}\n".format(os.getpid(), timestamp)

    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, payload.encode("utf-8"))
        os.close(fd)
        return True, lock_path, ""
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            return False, lock_path, str(exc)
        if retry and _is_stale_lock(lock_path):
            try:
                os.remove(lock_path)
            except OSError as remove_error:
                return False, lock_path, str(remove_error)
            return _acquire_upgrade_lock(install_dir, retry=False)
        return False, lock_path, "Another upgrade is already in progress."


def _release_upgrade_lock(lock_path, acquired):
    if not acquired or not lock_path:
        return
    try:
        if os.path.isfile(lock_path):
            os.remove(lock_path)
    except OSError:
        pass


def _verify_tool(install_dir):
    lint_script = os.path.join(install_dir, ".github", "scripts", "terraform_lint.py")
    if not os.path.isfile(lint_script):
        return False, "Lint script not found: {0}".format(lint_script)

    help_code, help_stdout, help_stderr = _run_subprocess_command(
        ["python3", lint_script, "--help"],
        cwd=install_dir,
    )
    if help_code != 0:
        error_output = help_stderr or help_stdout or "unknown --help error"
        return False, "Upgraded tool verification failed: {0}".format(error_output)

    import_snippet = (
        "import sys; sys.path.insert(0, {0!r}); import rules"
    ).format(install_dir)
    import_code, import_stdout, import_stderr = _run_subprocess_command(
        ["python3", "-c", import_snippet],
        cwd=install_dir,
    )
    if import_code != 0:
        error_output = import_stderr or import_stdout or "unknown import error"
        return False, "Rules import failed: {0}".format(error_output)

    smoke_dir = os.path.join(install_dir, SMOKE_TEST_DIR)
    if os.path.isdir(smoke_dir):
        lint_code, lint_stdout, lint_stderr = _run_subprocess_command(
            [
                "python3",
                lint_script,
                "--directory",
                smoke_dir,
                "--performance-monitoring",
                "false",
            ],
            cwd=install_dir,
        )
        if lint_code != 0:
            error_output = lint_stderr or lint_stdout or "unknown smoke lint error"
            return False, "Smoke lint failed: {0}".format(error_output)

    return True, ""


def _build_result(
    success,
    message,
    old_version="unknown",
    new_version="unknown",
    old_commit="",
    new_commit="",
    already_up_to_date=False,
    rolled_back=False,
    release_branch="",
    dry_run=False,
):
    return UpgradeResult(
        success=success,
        message=message,
        old_version=old_version,
        new_version=new_version,
        old_commit=old_commit,
        new_commit=new_commit,
        already_up_to_date=already_up_to_date,
        rolled_back=rolled_back,
        release_branch=release_branch,
        dry_run=dry_run,
    )


def _validate_installation(target_dir):
    changelog_path = os.path.join(target_dir, "CHANGELOG.md")
    old_version = _read_version_from_changelog(changelog_path)

    if not os.path.isdir(target_dir):
        return None, _build_result(
            success=False,
            message=_failure_message(
                "Installation directory not found: {0}".format(target_dir),
                "reinstall",
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
        )

    if not os.path.isdir(os.path.join(target_dir, ".git")):
        return None, _build_result(
            success=False,
            message=_failure_message(
                "Installation directory is not a git repository: {0}".format(target_dir),
                "reinstall",
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
        )

    git_check_code, _, git_check_error = _run_git_command(["--version"], cwd=target_dir)
    if git_check_code != 0:
        return None, _build_result(
            success=False,
            message=_failure_message(
                "Git is required for upgrade but was not found: {0}".format(git_check_error),
                "git_missing",
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
        )

    previous_commit, commit_error = _get_head_commit(target_dir)
    if not previous_commit:
        return None, _build_result(
            success=False,
            message=_failure_message(
                "Failed to read current HEAD commit: {0}".format(commit_error),
                "head_unreadable",
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
        )

    is_dirty, status_output = _has_dirty_working_tree(target_dir)
    if is_dirty:
        dirty_message = (
            "Cannot upgrade: local modifications detected in the installation directory.\n"
            "Modified files:\n{0}"
        ).format(status_output or "(unable to read status)")
        return None, _build_result(
            success=False,
            message=_failure_message(dirty_message, "dirty", target_dir),
            old_version=old_version,
            new_version=old_version,
            old_commit=previous_commit,
            new_commit=previous_commit,
        )

    release_branch, branch_error = _resolve_origin_branch(target_dir)
    if not release_branch:
        return None, _build_result(
            success=False,
            message=branch_error,
            old_version=old_version,
            new_version=old_version,
            old_commit=previous_commit,
            new_commit=previous_commit,
        )

    return {
        "target_dir": target_dir,
        "changelog_path": changelog_path,
        "old_version": old_version,
        "previous_commit": previous_commit,
        "release_branch": release_branch,
    }, None


def _fetch_origin(target_dir, old_version, previous_commit, release_branch):
    fetch_code, fetch_output, fetch_error = _run_git_command(["fetch", "origin"], cwd=target_dir)
    if fetch_code != 0:
        fetch_stage = _classify_fetch_failure(fetch_error, fetch_output)
        return _build_result(
            success=False,
            message=_failure_message(
                "Failed to fetch latest changes:\n{0}".format(fetch_error or fetch_output),
                fetch_stage,
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
            old_commit=previous_commit,
            new_commit=previous_commit,
            release_branch=release_branch,
        )
    return None


def _prepare_release_branch(state):
    target_dir = state["target_dir"]
    release_branch = state["release_branch"]
    previous_commit = state["previous_commit"]
    old_version = state["old_version"]
    changelog_path = state["changelog_path"]

    current_branch, current_branch_error = _get_current_branch(target_dir)
    if not current_branch:
        return None, _build_result(
            success=False,
            message=_failure_message(
                "Failed to read current branch: {0}".format(current_branch_error),
                "branch",
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
            old_commit=previous_commit,
            new_commit=previous_commit,
            release_branch=release_branch,
        )

    if current_branch != release_branch:
        checkout_code, _, checkout_error = _run_git_command(
            ["checkout", release_branch],
            cwd=target_dir,
        )
        if checkout_code != 0:
            return None, _build_result(
                success=False,
                message=_failure_message(
                    "Failed to switch to release branch '{0}':\n{1}".format(
                        release_branch,
                        checkout_error,
                    ),
                    "checkout",
                    target_dir,
                ),
                old_version=old_version,
                new_version=old_version,
                old_commit=previous_commit,
                new_commit=previous_commit,
                release_branch=release_branch,
            )

        previous_commit, commit_error = _get_head_commit(target_dir)
        if not previous_commit:
            return None, _build_result(
                success=False,
                message=_failure_message(
                    "Failed to read HEAD commit after switching branches: {0}".format(commit_error),
                    "head_unreadable",
                    target_dir,
                ),
                old_version=old_version,
                new_version=old_version,
                release_branch=release_branch,
            )
        old_version = _read_version_from_changelog(changelog_path)
        state["previous_commit"] = previous_commit
        state["old_version"] = old_version
        print("Switched to release branch: {0}".format(release_branch))

    return state, None


def _preview_upgrade(target_dir):
    state, failure = _validate_installation(target_dir)
    if failure:
        return failure

    old_version = state["old_version"]
    previous_commit = state["previous_commit"]
    release_branch = state["release_branch"]

    print("Dry-run: upgrade preview")
    print("Installation directory: {0}".format(target_dir))
    print("Release branch: {0}".format(release_branch))

    fetch_failure = _fetch_origin(target_dir, old_version, previous_commit, release_branch)
    if fetch_failure:
        return fetch_failure._replace(dry_run=True)

    remote_commit, remote_error = _get_remote_commit(target_dir, release_branch)
    if not remote_commit:
        return _build_result(
            success=False,
            message=_failure_message(
                "Failed to read remote commit for origin/{0}: {1}".format(
                    release_branch,
                    remote_error,
                ),
                "branch",
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
            old_commit=previous_commit,
            new_commit=previous_commit,
            release_branch=release_branch,
            dry_run=True,
        )

    remote_version, _ = _read_changelog_at_ref(target_dir, "origin/{0}".format(release_branch))
    already_up_to_date = previous_commit == remote_commit

    if already_up_to_date:
        message = (
            "Dry-run complete.\n"
            "Current: v{0} ({1})\n"
            "Remote:  v{2} ({3})\n"
            "Status:  Already up to date."
        ).format(
            old_version,
            _short_commit(previous_commit),
            remote_version,
            _short_commit(remote_commit),
        )
    else:
        message = (
            "Dry-run complete.\n"
            "Current: v{0} ({1})\n"
            "Remote:  v{2} ({3})\n"
            "Status:  Upgrade available - run without --dry-run to apply."
        ).format(
            old_version,
            _short_commit(previous_commit),
            remote_version,
            _short_commit(remote_commit),
        )

    return _build_result(
        success=True,
        message=message,
        old_version=old_version,
        new_version=remote_version,
        old_commit=previous_commit,
        new_commit=remote_commit,
        already_up_to_date=already_up_to_date,
        release_branch=release_branch,
        dry_run=True,
    )


def _execute_upgrade(target_dir):
    state, failure = _validate_installation(target_dir)
    if failure:
        return failure

    old_version = state["old_version"]
    previous_commit = state["previous_commit"]
    release_branch = state["release_branch"]
    changelog_path = state["changelog_path"]

    state, failure = _prepare_release_branch(state)
    if failure:
        return failure

    previous_commit = state["previous_commit"]
    old_version = state["old_version"]

    print("Upgrading HCBP lint tool...")
    print("Installation directory: {0}".format(target_dir))
    print("Release branch: {0}".format(release_branch))
    print("Current version: v{0} (commit {1})".format(
        old_version,
        _short_commit(previous_commit),
    ))

    fetch_failure = _fetch_origin(target_dir, old_version, previous_commit, release_branch)
    if fetch_failure:
        return fetch_failure

    pull_code, pull_output, pull_error = _run_git_command(
        ["pull", "--ff-only", "origin", release_branch],
        cwd=target_dir,
    )

    if pull_code != 0:
        pull_stage = _classify_pull_failure(pull_error, pull_output)
        return _build_result(
            success=False,
            message=_failure_message(
                "Failed to pull latest changes from origin/{0}:\n{1}".format(
                    release_branch,
                    pull_error or pull_output,
                ),
                pull_stage,
                target_dir,
            ),
            old_version=old_version,
            new_version=old_version,
            old_commit=previous_commit,
            new_commit=previous_commit,
            release_branch=release_branch,
        )

    new_commit, post_pull_commit_error = _get_head_commit(target_dir)
    if not new_commit:
        rollback_ok, rollback_error = _rollback_to_commit(target_dir, previous_commit)
        if rollback_ok:
            message = (
                "Failed to read commit after pull. Upgrade aborted and rolled back to {0}.\n{1}"
            ).format(_short_commit(previous_commit), post_pull_commit_error)
            rolled_back = True
        else:
            message = _failure_message(
                "Failed to read commit after pull and rollback also failed.\n"
                "Read error: {0}\n"
                "Rollback error: {1}".format(post_pull_commit_error, rollback_error),
                "reinstall",
                target_dir,
            )
            rolled_back = False

        return _build_result(
            success=False,
            message=message,
            old_version=old_version,
            new_version=old_version,
            old_commit=previous_commit,
            new_commit=previous_commit,
            rolled_back=rolled_back,
            release_branch=release_branch,
        )

    new_version = _read_version_from_changelog(changelog_path)
    already_up_to_date = previous_commit == new_commit

    if already_up_to_date:
        message = "Tool is already up to date (v{0}, commit {1}).".format(
            new_version,
            _short_commit(new_commit),
        )
        if pull_output:
            message = "{0}\n{1}".format(message, pull_output)
        return _build_result(
            success=True,
            message=message,
            old_version=old_version,
            new_version=new_version,
            old_commit=previous_commit,
            new_commit=new_commit,
            already_up_to_date=True,
            release_branch=release_branch,
        )

    verified, verify_message = _verify_tool(target_dir)
    if not verified:
        rollback_ok, rollback_error = _rollback_to_commit(target_dir, previous_commit)
        if rollback_ok:
            message = (
                "Upgrade failed verification and was rolled back to commit {0}.\n"
                "Version: v{1}\n"
                "Error: {2}"
            ).format(_short_commit(previous_commit), old_version, verify_message)
            rolled_back = True
        else:
            message = _failure_message(
                "Upgrade failed verification AND rollback failed.\n"
                "Installation may be broken.\n"
                "Verify error: {0}\n"
                "Rollback error: {1}".format(verify_message, rollback_error),
                "reinstall",
                target_dir,
            )
            rolled_back = False

        return _build_result(
            success=False,
            message=message,
            old_version=old_version,
            new_version=new_version,
            old_commit=previous_commit,
            new_commit=new_commit,
            rolled_back=rolled_back,
            release_branch=release_branch,
        )

    if old_version == new_version:
        message = "Upgrade completed: v{0} ({1} -> {2}).".format(
            new_version,
            _short_commit(previous_commit),
            _short_commit(new_commit),
        )
    else:
        message = "Upgrade completed: v{0} -> v{1} ({2} -> {3}).".format(
            old_version,
            new_version,
            _short_commit(previous_commit),
            _short_commit(new_commit),
        )

    if pull_output:
        message = "{0}\n{1}".format(message, pull_output)

    return _build_result(
        success=True,
        message=message,
        old_version=old_version,
        new_version=new_version,
        old_commit=previous_commit,
        new_commit=new_commit,
        already_up_to_date=False,
        release_branch=release_branch,
    )


def upgrade_tool(install_dir=None, dry_run=False):
    """Pull or preview the latest lint tool code for a local installation."""
    target_dir = os.path.abspath(install_dir or resolve_tool_install_dir())

    if os.path.isdir(target_dir):
        acquired, lock_path, lock_error = _acquire_upgrade_lock(target_dir)
        if not acquired:
            return _build_result(
                success=False,
                message=_failure_message(
                    "Cannot start upgrade: {0}".format(lock_error),
                    "concurrent",
                    target_dir,
                ),
                dry_run=dry_run,
            )
    else:
        acquired, lock_path = False, ""

    try:
        if dry_run:
            return _preview_upgrade(target_dir)
        return _execute_upgrade(target_dir)
    finally:
        _release_upgrade_lock(lock_path, acquired)
