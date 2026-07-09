#!/usr/bin/env python3
"""Acceptance tests for ST.007 nested parameter block spacing checks."""

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from rules.st_rules.rule_007 import (  # noqa: E402
    _extract_resource_blocks_with_parameters,
    check_st007_parameter_block_spacing,
)


class NestedParameterExtractionTest(unittest.TestCase):
    NESTED_BASIC_STRUCTURE = REPO_ROOT / "acceptances/bad/st007/nested_basic_structure/main.tf"

    def test_extracts_nested_structure_siblings_with_correct_parent(self):
        content = self.NESTED_BASIC_STRUCTURE.read_text()
        blocks = _extract_resource_blocks_with_parameters(content)
        parameters = blocks[0]["parameters"]

        by_name = {param["name"]: param for param in parameters}

        self.assertEqual(by_name["cluster_id"]["parent_block"], "clusters")
        self.assertEqual(by_name["installation"]["parent_block"], "clusters")
        self.assertEqual(by_name["installation"]["type"], "structure")
        self.assertEqual(by_name["field_selector"]["parent_block"], "nodes")


class NestedSpacingCheckTest(unittest.TestCase):
    BAD_NESTED_BASIC_STRUCTURE = REPO_ROOT / "acceptances/bad/st007/nested_basic_structure/main.tf"
    BAD_NESTED_STRUCTURE_STRUCTURE = REPO_ROOT / "acceptances/bad/st007/nested_structure_structure/main.tf"
    GOOD_NESTED_VALID_SPACING = REPO_ROOT / "acceptances/good/st007/nested_valid_spacing/main.tf"
    GOOD_JSONENCODE = REPO_ROOT / "acceptances/good/st007/jsonencode_no_false_positive/main.tf"

    def _collect_errors(self, file_path: Path) -> list:
        content = file_path.read_text()
        errors = []

        def log_error(_, __, message, line_num):
            errors.append((line_num, message))

        check_st007_parameter_block_spacing(str(file_path), content, log_error)
        return errors

    def test_nested_basic_structure_missing_blank_line_is_reported(self):
        errors = self._collect_errors(self.BAD_NESTED_BASIC_STRUCTURE)
        self.assertTrue(
            any("cluster_id" in message and "installation" in message for _, message in errors),
            f"expected cluster_id/installation spacing error, got: {errors}",
        )

    def test_nested_structure_structure_missing_blank_line_is_reported(self):
        errors = self._collect_errors(self.BAD_NESTED_STRUCTURE_STRUCTURE)
        self.assertTrue(
            any("network" in message and "storage" in message for _, message in errors),
            f"expected network/storage spacing error, got: {errors}",
        )

    def test_nested_valid_spacing_has_no_errors(self):
        errors = self._collect_errors(self.GOOD_NESTED_VALID_SPACING)
        self.assertEqual(errors, [])

    def test_jsonencode_inner_objects_do_not_trigger_spacing_errors(self):
        errors = self._collect_errors(self.GOOD_JSONENCODE)
        self.assertEqual(errors, [])


class LintCliAcceptanceTest(unittest.TestCase):
    LINTER = REPO_ROOT / ".github/scripts/terraform_lint.py"

    def _run_lint(self, directory: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(self.LINTER),
                "--directory",
                str(directory),
                "--categories",
                "ST",
                "--ignore-rules",
                "ST.001,ST.002,ST.003,ST.004,ST.005,ST.006,ST.008,ST.009,ST.010,ST.011,ST.012,ST.013,ST.014",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_good_acceptance_cases_pass(self):
        good_dir = REPO_ROOT / "acceptances/good/st007"
        result = self._run_lint(good_dir)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bad_acceptance_cases_fail(self):
        bad_dir = REPO_ROOT / "acceptances/bad/st007"
        result = self._run_lint(bad_dir)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ST.007", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
