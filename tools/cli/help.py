#!/usr/bin/env python3
"""
CLI help template renderer for the Terraform lint tool.

Loads a shared template from tools/cli/templates/cli_help.template and fills
placeholders based on the invocation context (direct script vs hcbp-lint wrapper).
"""

import os
import sys

TEMPLATE_RELATIVE_PARTS = ("templates", "cli_help.template")
LOCAL_INSTALL_TOOL_NAME = "hcbp-lint"
SCRIPT_TOOL_NAME = "terraform_lint.py"


def _load_template():
    template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        *TEMPLATE_RELATIVE_PARTS,
    )
    if not os.path.isfile(template_path):
        raise IOError("CLI help template not found: {0}".format(template_path))

    with open(template_path, "r", encoding="utf-8") as template_file:
        return template_file.read()


def resolve_tool_context(argv0=None):
    """
    Resolve tool display names for CLI help based on invocation context.

    Priority:
      1. HCBP_LINT_TOOL_NAME environment variable (set by hcbp-lint wrapper)
      2. Executable basename when invoked as hcbp-lint
      3. Default direct script invocation (python3 terraform_lint.py)

    Returns:
        Tuple[str, str]: (tool_name, example_prefix)
    """
    env_tool_name = os.environ.get("HCBP_LINT_TOOL_NAME", "").strip()
    if env_tool_name:
        return env_tool_name, env_tool_name

    executable_name = os.path.basename(argv0 or sys.argv[0])
    if executable_name == LOCAL_INSTALL_TOOL_NAME:
        return LOCAL_INSTALL_TOOL_NAME, LOCAL_INSTALL_TOOL_NAME

    script_name = SCRIPT_TOOL_NAME if executable_name.endswith(".py") else executable_name
    return script_name, "python3 {0}".format(script_name)


def _format_available_rules(rule_ids, rule_info_lookup):
    lines = []
    for rule_id in sorted(rule_ids):
        info = rule_info_lookup(rule_id) or {}
        rule_name = info.get("name", "Unknown rule")
        lines.append("  {0}: {1}".format(rule_id, rule_name))
    return "\n".join(lines)


def render_cli_help_epilog(
    rule_ids,
    rule_info_lookup,
    tool_version,
    total_rules,
    rule_systems,
    argv0=None,
):
    """
    Render the CLI epilog and resolve the argparse prog name.

    Returns:
        Tuple[str, str]: (epilog_text, tool_name_for_prog)
    """
    tool_name, example_prefix = resolve_tool_context(argv0)
    template = _load_template()

    context = {
        "tool_name": tool_name,
        "example_prefix": example_prefix,
        "available_rules": _format_available_rules(rule_ids, rule_info_lookup),
        "tool_version": tool_version,
        "total_rules": str(total_rules),
        "rule_systems": ", ".join(rule_systems),
    }

    return template.format(**context), tool_name


def build_argument_parser_kwargs(
    rule_ids,
    rule_info_lookup,
    tool_version,
    total_rules,
    rule_systems,
    argv0=None,
):
    """Build argparse kwargs with shared description and rendered epilog."""
    epilog, tool_name = render_cli_help_epilog(
        rule_ids=rule_ids,
        rule_info_lookup=rule_info_lookup,
        tool_version=tool_version,
        total_rules=total_rules,
        rule_systems=rule_systems,
        argv0=argv0,
    )

    import argparse

    return {
        "prog": tool_name,
        "description": "Enhanced Terraform Scripts Lint Tool - Unified Rules Management System",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "epilog": epilog,
    }
