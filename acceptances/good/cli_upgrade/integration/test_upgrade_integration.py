#!/usr/bin/env python3
"""Integration tests for CLI upgrade with a real local git repository."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.cli.upgrade import UPGRADE_LOCK_FILENAME, upgrade_tool  # noqa: E402


def _run_git(args, cwd):
    completed = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "git {0} failed in {1}: {2}".format(
                " ".join(args),
                cwd,
                completed.stderr.strip() or completed.stdout.strip(),
            )
        )
    return completed.stdout.strip()


class UpgradeIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if subprocess.run(["git", "--version"], stdout=subprocess.PIPE).returncode != 0:
            raise unittest.SkipTest("git not available")

        cls.temp_root = tempfile.mkdtemp()
        cls.remote_dir = os.path.join(cls.temp_root, "remote.git")
        cls.install_dir = os.path.join(cls.temp_root, "install")
        cls.work_dir = os.path.join(cls.temp_root, "work")

        _run_git(["init", "--bare", cls.remote_dir], cls.temp_root)
        os.makedirs(cls.work_dir, exist_ok=True)

        _run_git(["init"], cls.work_dir)
        _run_git(["config", "user.email", "test@example.com"], cls.work_dir)
        _run_git(["config", "user.name", "Test User"], cls.work_dir)

        changelog = "## [1.0.0] - 2026-07-09\n"
        tools_dir = os.path.join(cls.work_dir, ".github", "scripts")
        os.makedirs(tools_dir, exist_ok=True)
        with open(os.path.join(cls.work_dir, "CHANGELOG.md"), "w", encoding="utf-8") as handle:
            handle.write(changelog)
        with open(os.path.join(tools_dir, "terraform_lint.py"), "w", encoding="utf-8") as handle:
            handle.write("#!/usr/bin/env python3\nprint('ok')\n")

        _run_git(["add", "."], cls.work_dir)
        _run_git(["commit", "-m", "initial"], cls.work_dir)
        cls.initial_commit = _run_git(["rev-parse", "HEAD"], cls.work_dir)

        _run_git(["branch", "-M", "master"], cls.work_dir)
        _run_git(["remote", "add", "origin", cls.remote_dir], cls.work_dir)
        _run_git(["push", "-u", "origin", "master"], cls.work_dir)

        subprocess.run(["git", "clone", cls.remote_dir, cls.install_dir], cwd=cls.temp_root, check=True)
        _run_git(["symbolic-ref", "HEAD", "refs/remotes/origin/master"], cls.remote_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_root, ignore_errors=True)

    def setUp(self):
        _run_git(["checkout", "master"], self.work_dir)
        _run_git(["reset", "--hard", self.initial_commit], self.work_dir)
        _run_git(["push", "--force", "origin", "master"], self.work_dir)

        _run_git(["checkout", "master"], self.install_dir)
        _run_git(["reset", "--hard", self.initial_commit], self.install_dir)
        _run_git(["fetch", "origin"], self.install_dir)
        _run_git(["config", "user.email", "test@example.com"], self.install_dir)
        _run_git(["config", "user.name", "Test User"], self.install_dir)

        lock_path = os.path.join(self.install_dir, UPGRADE_LOCK_FILENAME)
        if os.path.isfile(lock_path):
            os.remove(lock_path)

    def _push_new_version(self, version):
        changelog = "## [{0}] - 2026-07-09\n".format(version)
        with open(os.path.join(self.work_dir, "CHANGELOG.md"), "w", encoding="utf-8") as handle:
            handle.write(changelog)
        _run_git(["add", "CHANGELOG.md"], self.work_dir)
        _run_git(["commit", "-m", "release {0}".format(version)], self.work_dir)
        new_commit = _run_git(["rev-parse", "HEAD"], self.work_dir)
        _run_git(["push", "origin", "master"], self.work_dir)
        return new_commit

    def test_real_upgrade_pulls_new_commit(self):
        new_commit = self._push_new_version("1.1.0")

        with mock.patch("tools.cli.upgrade._verify_tool", return_value=(True, "")):
            result = upgrade_tool(install_dir=self.install_dir)

        self.assertTrue(result.success)
        self.assertEqual(result.old_version, "1.0.0")
        self.assertEqual(result.new_version, "1.1.0")
        self.assertEqual(_run_git(["rev-parse", "HEAD"], self.install_dir), new_commit)

    def test_real_upgrade_already_up_to_date(self):
        with mock.patch("tools.cli.upgrade._verify_tool", return_value=(True, "")):
            result = upgrade_tool(install_dir=self.install_dir)

        self.assertTrue(result.success)
        self.assertTrue(result.already_up_to_date)

    def test_real_dry_run_reports_upgrade_available(self):
        self._push_new_version("1.2.0")

        result = upgrade_tool(install_dir=self.install_dir, dry_run=True)

        self.assertTrue(result.success)
        self.assertTrue(result.dry_run)
        self.assertIn("Upgrade available", result.message)
        self.assertEqual(_run_git(["rev-parse", "HEAD"], self.install_dir), self.initial_commit)

    def test_real_upgrade_rejects_dirty_tree(self):
        self._push_new_version("1.3.0")
        dirty_file = os.path.join(self.install_dir, "CHANGELOG.md")
        with open(dirty_file, "a", encoding="utf-8") as handle:
            handle.write("\n# dirty\n")

        result = upgrade_tool(install_dir=self.install_dir)

        self.assertFalse(result.success)
        self.assertIn("local modifications detected", result.message)

    def test_real_upgrade_fails_when_history_diverged(self):
        self._push_new_version("1.1.0")
        _run_git(["fetch", "origin"], self.install_dir)

        local_changelog = os.path.join(self.install_dir, "CHANGELOG.md")
        with open(local_changelog, "w", encoding="utf-8") as handle:
            handle.write("## [9.9.9] - 2026-07-09\n")
        _run_git(["add", "CHANGELOG.md"], self.install_dir)
        _run_git(["commit", "-m", "local diverged commit"], self.install_dir)
        diverged_commit = _run_git(["rev-parse", "HEAD"], self.install_dir)

        result = upgrade_tool(install_dir=self.install_dir)

        self.assertFalse(result.success)
        self.assertIn("origin/master", result.message)
        self.assertIn("diverged", result.message.lower())
        self.assertEqual(_run_git(["rev-parse", "HEAD"], self.install_dir), diverged_commit)

    def test_real_upgrade_rolls_back_when_verification_fails(self):
        self._push_new_version("1.1.0")
        before_commit = _run_git(["rev-parse", "HEAD"], self.install_dir)

        with mock.patch("tools.cli.upgrade._verify_tool", return_value=(False, "verification broken")):
            result = upgrade_tool(install_dir=self.install_dir)

        self.assertFalse(result.success)
        self.assertTrue(result.rolled_back)
        self.assertIn("rolled back", result.message.lower())
        self.assertIn("verification broken", result.message)
        self.assertEqual(_run_git(["rev-parse", "HEAD"], self.install_dir), before_commit)

    def test_real_concurrent_upgrade_is_rejected(self):
        lock_path = os.path.join(self.install_dir, UPGRADE_LOCK_FILENAME)
        try:
            with open(lock_path, "w", encoding="utf-8") as handle:
                handle.write("pid=99999\nstarted=2026-07-09T00:00:00Z\n")

            result = upgrade_tool(install_dir=self.install_dir)

            self.assertFalse(result.success)
            self.assertIn("in progress", result.message.lower())
            self.assertIn(UPGRADE_LOCK_FILENAME, result.message)
            self.assertEqual(_run_git(["rev-parse", "HEAD"], self.install_dir), self.initial_commit)
        finally:
            if os.path.isfile(lock_path):
                os.remove(lock_path)


if __name__ == "__main__":
    unittest.main()
