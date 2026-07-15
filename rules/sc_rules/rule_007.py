#!/usr/bin/env python3
"""
SC.007 - Sensitive Variable Non-Empty Default Check

Sensitive-named variables must not use a non-empty, non-placeholder string default.
Empty string, null, and placeholders (CHANGEME, etc.) are allowed.

Author: Lance
License: Apache 2.0
"""

from typing import Callable, Optional

from rules.common.sensitive_patterns import (
    extract_default_assignment,
    get_sensitive_match,
    is_dangerous_string_default,
)
from rules.sc_rules.rule_005 import parse_variable_blocks


def check_sc007_sensitive_variable_default(
    file_path: str,
    content: str,
    log_error_func: Callable[[str, str, str, Optional[int]], None],
) -> None:
    """Flag dangerous non-empty defaults on sensitive-named variables."""
    for var_block in parse_variable_blocks(content):
        var_name = var_block["name"]
        if get_sensitive_match(var_name) is None:
            continue

        default_info = extract_default_assignment(var_block["content"])
        if default_info is None:
            continue

        rhs, default_line_in_block = default_info
        if not is_dangerous_string_default(rhs):
            continue

        # Line number of the default assignment within the file
        line_number = var_block["line"] + default_line_in_block - 1
        log_error_func(
            file_path,
            "SC.007",
            (
                f"Sensitive variable '{var_name}' must not use a non-empty string default "
                f"(got {rhs}). Use no default, null, \"\", or a placeholder such as CHANGEME."
            ),
            line_number,
        )


def get_rule_description() -> dict:
    """Get the rule description for SC.007."""
    return {
        "rule_id": "SC.007",
        "title": "Sensitive variable non-empty default check",
        "category": "Security Code",
        "severity": "error",
        "description": (
            "Sensitive-named variables must not declare a non-empty, non-placeholder "
            "string default. Complements SC.005 (sensitive flag) with default hygiene."
        ),
        "rationale": (
            "Non-empty defaults on credential-like inputs embed secrets in module "
            "interfaces and example repositories."
        ),
        "scope": ["variable_declaration", "sensitive_data", "default_values"],
        "implementation": "modular",
        "version": "1.0.0",
        "related_rules": ["SC.005", "SC.006"],
        "examples": {
            "valid": [
                'variable "api_token" {\n  type = string\n  sensitive = true\n}',
                'variable "access_key" {\n  type = string\n  sensitive = true\n  default = ""\n}',
                'variable "secret_key" {\n  type = string\n  sensitive = true\n  default = "CHANGEME"\n}',
            ],
            "invalid": [
                'variable "api_token" {\n  type = string\n  sensitive = true\n  default = "eyJhbGciOi..."\n}',
            ],
        },
        "fix_suggestions": [
            "Remove the default, or set default = null / \"\"",
            "Use a placeholder such as CHANGEME for local scaffolding only",
            "Supply real secrets via tfvars or environment variables",
        ],
    }
