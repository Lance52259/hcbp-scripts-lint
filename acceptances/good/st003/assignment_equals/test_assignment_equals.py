#!/usr/bin/env python3
"""Unit tests for ST.003 assignment equals detection helpers."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from rules.st_rules.rule_003 import (  # noqa: E402
    _find_assignment_equals_pos,
    _get_after_assignment_equals,
    _get_before_assignment_equals,
    _has_assignment_equals,
    _check_equals_after_spacing,
    _check_parameter_alignment_in_section,
)


class AssignmentEqualsDetectionTest(unittest.TestCase):
    def test_comparison_only_lines_have_no_assignment(self):
        cases = [
            '      ]) == length(var.role_ids)',
            '  foo == bar',
            '  x != y',
            '  a <= b',
            '  a >= b',
            'for x in y : x if x == 1',
        ]
        for line in cases:
            with self.subTest(line=line):
                self.assertFalse(_has_assignment_equals(line))
                self.assertEqual(_find_assignment_equals_pos(line), -1)

    def test_assignment_with_inline_comparison(self):
        line = '  name = var.x == var.y'
        self.assertEqual(_find_assignment_equals_pos(line), 7)
        self.assertEqual(_get_before_assignment_equals(line).strip(), 'name')
        self.assertEqual(_get_after_assignment_equals(line), 'var.x == var.y')

    def test_assignment_inside_strings_is_ignored(self):
        self.assertEqual(_find_assignment_equals_pos('  key = "x=y"'), 6)
        self.assertEqual(_find_assignment_equals_pos("  key = 'a==b'"), 6)

    def test_multiline_condition_continuation_is_not_checked(self):
        section = [
            ('      condition = length([', 0),
            ('        for role_id in var.role_ids : role_id', 1),
            ('      ]) == length(var.role_ids)', 2),
        ]
        errors = _check_parameter_alignment_in_section(section, 'resource.test', 0, [l for l, _ in section])
        error_lines = {line_num for line_num, _ in errors}
        self.assertNotIn(3, error_lines)

    def test_spacing_check_skips_comparison_lines(self):
        errors = _check_equals_after_spacing('      ]) == length(var.role_ids)', 2, 'resource.test', 0)
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
