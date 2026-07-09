#!/usr/bin/env python3
"""Tests for CLI self-upgrade support."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.cli.upgrade import (  # noqa: E402
    DEFAULT_INSTALL_DIR,
    _classify_fetch_failure,
    _resolve_origin_branch,
    resolve_tool_install_dir,
    upgrade_tool,
)

OLD_COMMIT = "aaa1111111111111111111111111111111111111111"
NEW_COMMIT = "bbb2222222222222222222222222222222222222222"
RELEASE_BRANCH = "master"


def _base_git_handler(state):
    commits = iter(state.get("commits", [OLD_COMMIT]))
    checkout_calls = []

    def fake_run_git(args, cwd):
        release_branch = state.get("release_branch", RELEASE_BRANCH)
        if args == ["--version"]:
            return 0, "git version 2.17.1", ""
        if args == ["rev-parse", "HEAD"]:
            try:
                return 0, next(commits), ""
            except StopIteration:
                return 0, state.get("commits", [OLD_COMMIT])[-1], ""
        if args == ["rev-parse", "origin/{0}".format(release_branch)]:
            return 0, state.get("remote_commit", NEW_COMMIT), ""
        if args == ["show", "origin/{0}:CHANGELOG.md".format(release_branch)]:
            return 0, state.get("remote_changelog", "## [3.0.2] - 2026-07-09\n"), ""
        if args == ["status", "--porcelain"]:
            return 0, state.get("porcelain", ""), ""
        if args == ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"]:
            if state.get("symbolic_ref_fail"):
                return 1, "", "not found"
            return 0, "origin/{0}".format(release_branch), ""
        if args == ["branch", "-r", "--list", "origin/master"]:
            listed = [
                item for item in state.get("remote_branches", ["origin/master"])
                if item == "origin/master"
            ]
            return 0, "\n".join(listed), ""
        if args == ["branch", "-r", "--list", "origin/main"]:
            listed = [
                item for item in state.get("remote_branches", [])
                if item == "origin/main"
            ]
            return 0, "\n".join(listed), ""
        if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return 0, state.get("current_branch", RELEASE_BRANCH), ""
        if args == ["fetch", "origin"]:
            if state.get("fetch_fail"):
                return 1, "", state.get("fetch_error", "network unreachable")
            return 0, "", ""
        if args == ["pull", "--ff-only", "origin", release_branch]:
            if state.get("pull_fail"):
                return 1, "", state.get("pull_error", "pull failed")
            return 0, state.get("pull_output", "Updating files."), ""
        if args == ["checkout", release_branch]:
            checkout_calls.append(args[1])
            if state.get("checkout_fail"):
                return 1, "", "checkout failed"
            return 0, "", ""
        if args[:2] == ["reset", "--hard"]:
            reset_calls = state.setdefault("reset_calls", [])
            reset_calls.append(args[2])
            if state.get("reset_fail"):
                return 1, "", "fatal: cannot reset"
            return 0, "", ""
        return 1, "", "unexpected git command: {0}".format(args)

    fake_run_git.checkout_calls = checkout_calls
    return fake_run_git


class ResolveToolInstallDirTest(unittest.TestCase):
    def test_prefers_environment_variable(self):
        with mock.patch.dict(os.environ, {"HCBP_LINT_TOOL_DIR": "/custom/install"}, clear=False):
            self.assertEqual(resolve_tool_install_dir(), "/custom/install")

    def test_uses_git_repository_root_when_available(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_tool_install_dir(), str(REPO_ROOT))

    def test_falls_back_to_default_install_dir_without_git_repo(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("tools.cli.upgrade.get_project_root", return_value="/tmp/not-a-repo"):
                self.assertEqual(resolve_tool_install_dir(), DEFAULT_INSTALL_DIR)


class ResolveOriginBranchTest(unittest.TestCase):
    def test_resolve_branch_from_origin_head(self):
        handler = _base_git_handler({"release_branch": RELEASE_BRANCH})

        with mock.patch("tools.cli.upgrade._run_git_command", side_effect=handler):
            branch, error = _resolve_origin_branch(str(REPO_ROOT))

        self.assertEqual(branch, RELEASE_BRANCH)
        self.assertEqual(error, "")

    def test_resolve_branch_fallback_to_main(self):
        handler = _base_git_handler({
            "symbolic_ref_fail": True,
            "release_branch": "main",
            "remote_branches": ["origin/main"],
        })

        with mock.patch("tools.cli.upgrade._run_git_command", side_effect=handler):
            branch, error = _resolve_origin_branch(str(REPO_ROOT))

        self.assertEqual(branch, "main")
        self.assertEqual(error, "")


class ClassifyFetchFailureTest(unittest.TestCase):
    def test_classify_ssl_failure(self):
        self.assertEqual(_classify_fetch_failure("SSL certificate problem", ""), "ssl")

    def test_classify_proxy_failure(self):
        self.assertEqual(_classify_fetch_failure("proxy authentication required 407", ""), "proxy")


class UpgradeToolTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_upgrade_fails_when_install_directory_missing(self):
        result = upgrade_tool("/tmp/missing-hcbp-install-dir")
        self.assertFalse(result.success)
        self.assertIn("Installation directory not found", result.message)

    def test_upgrade_fails_when_directory_is_not_git_repository(self):
        install_dir = os.path.join(self.temp_dir, "not-git")
        os.makedirs(install_dir)
        result = upgrade_tool(install_dir)
        self.assertFalse(result.success)
        self.assertIn("not a git repository", result.message)

    def test_upgrade_aborts_when_head_commit_cannot_be_read(self):
        install_dir = str(REPO_ROOT)

        def fake_run_git(args, cwd):
            if args == ["--version"]:
                return 0, "git version 2.17.1", ""
            if args == ["rev-parse", "HEAD"]:
                return 1, "", "fatal: not a valid object name"
            return 1, "", "unexpected git command"

        with mock.patch("tools.cli.upgrade._run_git_command", side_effect=fake_run_git):
            result = upgrade_tool(install_dir)

        self.assertFalse(result.success)
        self.assertIn("Failed to read current HEAD commit", result.message)

    def test_upgrade_checkout_release_branch_when_on_feature(self):
        install_dir = str(REPO_ROOT)
        handler = _base_git_handler({
            "commits": [OLD_COMMIT, OLD_COMMIT],
            "current_branch": "feature/test",
        })

        with mock.patch("tools.cli.upgrade._run_git_command", side_effect=handler):
            with mock.patch("tools.cli.upgrade._verify_tool", return_value=(True, "")):
                result = upgrade_tool(install_dir)

        self.assertTrue(result.success)
        self.assertEqual(handler.checkout_calls, [RELEASE_BRANCH])

    def test_fetch_failure_includes_ssl_hint(self):
        install_dir = str(REPO_ROOT)
        handler = _base_git_handler({
            "fetch_fail": True,
            "fetch_error": "SSL certificate problem",
        })

        with mock.patch("tools.cli.upgrade._run_git_command", side_effect=handler):
            result = upgrade_tool(install_dir)

        self.assertFalse(result.success)
        self.assertIn("SSL", result.message)

    def test_upgrade_uses_explicit_install_dir(self):
        install_dir = str(REPO_ROOT)
        seen = {}

        def fake_run_git(args, cwd):
            seen["cwd"] = cwd
            return _base_git_handler({"commits": [OLD_COMMIT, OLD_COMMIT]})(args, cwd)

        with mock.patch("tools.cli.upgrade._run_git_command", side_effect=fake_run_git):
            result = upgrade_tool(install_dir=install_dir)

        self.assertTrue(result.success)
        self.assertEqual(seen["cwd"], install_dir)

    def test_verify_runs_import_and_smoke_layers(self):
        install_dir = str(REPO_ROOT)
        handler = _base_git_handler({"commits": [OLD_COMMIT, NEW_COMMIT]})
        calls = []

        def fake_subprocess(args, cwd=None, timeout=60):
            calls.append(list(args))
            return 0, "", ""

        with mock.patch("tools.cli.upgrade._run_git_command", side_effect=handler):
            with mock.patch("tools.cli.upgrade._run_subprocess_command", side_effect=fake_subprocess):
                result = upgrade_tool(install_dir)

        self.assertTrue(result.success)
        self.assertTrue(any("import rules" in " ".join(call) for call in calls))
        self.assertTrue(any("--directory" in call for call in calls))


class UpgradeCliOptionTest(unittest.TestCase):
    def test_help_includes_upgrade_options_and_notes(self):
        completed = subprocess.run(
            ["python3", str(REPO_ROOT / ".github" / "scripts" / "terraform_lint.py"), "-h"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("-u, --upgrade", completed.stdout)
        self.assertIn("--dry-run", completed.stdout)
        self.assertIn("--install-dir", completed.stdout)
        self.assertIn("Upgrade Notes:", completed.stdout)

    def test_dry_run_requires_upgrade_flag(self):
        completed = subprocess.run(
            ["python3", str(REPO_ROOT / ".github" / "scripts" / "terraform_lint.py"), "--dry-run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--dry-run requires --upgrade", completed.stderr)


if __name__ == "__main__":
    unittest.main()
