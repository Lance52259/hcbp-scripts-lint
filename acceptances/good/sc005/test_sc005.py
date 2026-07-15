#!/usr/bin/env python3
"""Tests for SC.005 sensitive variable declaration rule."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from rules.sc_rules.rule_005 import (  # noqa: E402
    _get_sensitive_match,
    _get_sensitive_variable_patterns,
    check_sc005_sensitive_variable_declaration,
)


class SensitiveMatchTest(unittest.TestCase):
    def setUp(self):
        self.patterns = _get_sensitive_variable_patterns()

    def test_exact_match_access_key(self):
        match = _get_sensitive_match("access_key", self.patterns)
        self.assertEqual(match, ("access_key", "exact"))

    def test_contains_match_user_password(self):
        match = _get_sensitive_match("user_password", self.patterns)
        self.assertEqual(match, ("password", "contains"))

    def test_segment_match_api_token(self):
        match = _get_sensitive_match("api_token", self.patterns)
        self.assertEqual(match, ("token", "segment"))

    def test_segment_match_iam_auth_key(self):
        match = _get_sensitive_match("iam_auth_key", self.patterns)
        self.assertEqual(match, ("auth", "segment"))

    def test_contains_match_db_credentials(self):
        match = _get_sensitive_match("db_credentials", self.patterns)
        self.assertEqual(match, ("credential", "contains"))

    def test_contains_match_private_key_pem(self):
        match = _get_sensitive_match("private_key_pem", self.patterns)
        self.assertEqual(match, ("private_key", "contains"))

    def test_non_sensitive_author(self):
        self.assertIsNone(_get_sensitive_match("author", self.patterns))

    def test_non_sensitive_authority_id(self):
        self.assertIsNone(_get_sensitive_match("authority_id", self.patterns))

    def test_allowlist_auth_type(self):
        self.assertIsNone(_get_sensitive_match("auth_type", self.patterns))

    def test_non_sensitive_microphone(self):
        self.assertIsNone(_get_sensitive_match("microphone", self.patterns))

    def test_non_sensitive_speakerphone(self):
        self.assertIsNone(_get_sensitive_match("speakerphone", self.patterns))

    def test_segment_match_user_phone(self):
        match = _get_sensitive_match("user_phone", self.patterns)
        self.assertEqual(match, ("phone", "segment"))

    def test_allowlist_does_not_apply_to_exact_token(self):
        match = _get_sensitive_match("token", self.patterns)
        self.assertEqual(match, ("token", "exact"))


class CheckSc005IntegrationTest(unittest.TestCase):
    def _run_rule(self, rel_path: str):
        file_path = REPO_ROOT / rel_path
        content = file_path.read_text(encoding="utf-8")
        errors = []

        def log_error(path, rule_id, message, line_num):
            errors.append((path, rule_id, message, line_num))

        check_sc005_sensitive_variable_declaration(str(file_path), content, log_error)
        return errors

    def test_compliant_examples_pass(self):
        errors = self._run_rule("acceptances/good/sc005/compliant/variables.tf")
        self.assertEqual(errors, [])

    def test_allowlist_examples_pass(self):
        errors = self._run_rule("acceptances/good/sc005/allowlist/variables.tf")
        self.assertEqual(errors, [])

    def test_non_sensitive_examples_pass(self):
        errors = self._run_rule("acceptances/good/sc005/non_sensitive/variables.tf")
        self.assertEqual(errors, [])

    def test_microphone_examples_pass(self):
        errors = self._run_rule("acceptances/good/sc005/microphone/variables.tf")
        self.assertEqual(errors, [])

    def test_missing_sensitive_examples_fail(self):
        errors = self._run_rule("acceptances/bad/sc005/missing_sensitive/variables.tf")
        self.assertEqual(len(errors), 5)
        variable_names = {message.split("'")[1] for _, _, message, _ in errors}
        self.assertEqual(
            variable_names,
            {"api_token", "private_key_pem", "db_credentials", "iam_auth_key", "email"},
        )


if __name__ == "__main__":
    unittest.main()
