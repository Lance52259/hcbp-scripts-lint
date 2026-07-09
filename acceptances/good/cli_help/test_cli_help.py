#!/usr/bin/env python3
"""Tests for CLI help template rendering."""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.cli import (  # noqa: E402
    LOCAL_INSTALL_TOOL_NAME,
    SCRIPT_TOOL_NAME,
    get_tool_version,
    render_cli_help_epilog,
    resolve_tool_context,
)


class ResolveToolContextTest(unittest.TestCase):
    def test_direct_script_invocation(self):
        tool_name, example_prefix = resolve_tool_context("/repo/.github/scripts/terraform_lint.py")
        self.assertEqual(tool_name, SCRIPT_TOOL_NAME)
        self.assertEqual(example_prefix, f"python3 {SCRIPT_TOOL_NAME}")

    def test_local_install_wrapper_name(self):
        with mock.patch.dict(os.environ, {"HCBP_LINT_TOOL_NAME": LOCAL_INSTALL_TOOL_NAME}, clear=False):
            tool_name, example_prefix = resolve_tool_context("/repo/.github/scripts/terraform_lint.py")
        self.assertEqual(tool_name, LOCAL_INSTALL_TOOL_NAME)
        self.assertEqual(example_prefix, LOCAL_INSTALL_TOOL_NAME)

    def test_hcbp_lint_executable_name(self):
        tool_name, example_prefix = resolve_tool_context(f"/home/user/.local/bin/{LOCAL_INSTALL_TOOL_NAME}")
        self.assertEqual(tool_name, LOCAL_INSTALL_TOOL_NAME)
        self.assertEqual(example_prefix, LOCAL_INSTALL_TOOL_NAME)


class RenderCliHelpEpilogTest(unittest.TestCase):
    def _render(self, argv0: str):
        with mock.patch.dict(os.environ, {}, clear=True):
            return render_cli_help_epilog(
                rule_ids=["ST.001", "IO.001"],
                rule_info_lookup=lambda rule_id: {"name": f"Rule {rule_id}"},
                tool_version="3.0.1",
                total_rules=2,
                rule_systems=["ST", "IO"],
                argv0=argv0,
            )

    def test_script_mode_uses_python3_examples(self):
        epilog, tool_name = self._render("/repo/.github/scripts/terraform_lint.py")
        self.assertEqual(tool_name, SCRIPT_TOOL_NAME)
        self.assertIn(f"python3 {SCRIPT_TOOL_NAME}", epilog)
        self.assertNotIn(f"\n  {LOCAL_INSTALL_TOOL_NAME}\n", epilog)

    def test_hcbp_lint_mode_uses_wrapper_examples(self):
        with mock.patch.dict(os.environ, {"HCBP_LINT_TOOL_NAME": LOCAL_INSTALL_TOOL_NAME}, clear=False):
            epilog, tool_name = render_cli_help_epilog(
                rule_ids=["ST.001"],
                rule_info_lookup=lambda rule_id: {"name": f"Rule {rule_id}"},
                tool_version="3.0.1",
                total_rules=1,
                rule_systems=["ST"],
                argv0="/repo/.github/scripts/terraform_lint.py",
            )
        self.assertEqual(tool_name, LOCAL_INSTALL_TOOL_NAME)
        self.assertIn(f"  {LOCAL_INSTALL_TOOL_NAME}\n", epilog)
        self.assertIn(f"{LOCAL_INSTALL_TOOL_NAME} --directory ./infrastructure", epilog)
        self.assertNotIn(f"python3 {SCRIPT_TOOL_NAME} --directory", epilog)

    def test_dynamic_system_information_placeholders(self):
        epilog, _ = self._render("/repo/.github/scripts/terraform_lint.py")
        self.assertIn("Tool Version: v3.0.1", epilog)
        self.assertIn("Total Available Rules: 2", epilog)
        self.assertIn("Rule Systems: ST, IO", epilog)
        self.assertIn("ST.001: Rule ST.001", epilog)

    def test_real_rule_lookup_shows_names_not_unknown(self):
        from rules import get_all_available_rules, get_rules_manager

        epilog, _ = render_cli_help_epilog(
            rule_ids=get_all_available_rules(),
            rule_info_lookup=lambda rule_id: get_rules_manager().get_rule_info(rule_id) or {},
            tool_version=get_tool_version(),
            total_rules=len(get_all_available_rules()),
            rule_systems=["ST", "IO", "DC", "SC"],
            argv0="/repo/.github/scripts/terraform_lint.py",
        )
        self.assertIn("ST.001: Resource and data source naming convention check", epilog)
        self.assertNotIn("Unknown rule", epilog)
        self.assertIn("Tool Version: v{0}".format(get_tool_version()), epilog)
        self.assertIn("Total Available Rules: 29", epilog)


    def test_cli_help_template_file_exists(self):
        template_path = REPO_ROOT / "tools" / "cli" / "templates" / "cli_help.template"
        self.assertTrue(template_path.is_file(), "CLI help template must be tracked in the repository")


if __name__ == "__main__":
    unittest.main()
