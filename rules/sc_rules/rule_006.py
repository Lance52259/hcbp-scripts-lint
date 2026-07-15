#!/usr/bin/env python3
"""
SC.006 - Hardcoded Credential Literal Check

Flags string literals assigned to known credential attribute names
(e.g. access_key = \"...\") when the value is not a Terraform reference
or an allowed placeholder.

Does not scan *.tfvars, heredocs, or perform global entropy detection.

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, Optional

from rules.common.sensitive_patterns import (
    CREDENTIAL_ATTRIBUTE_NAMES,
    is_placeholder_literal,
    is_reference_expression,
    strip_line_comment,
)


_ATTR_LITERAL_RE = re.compile(
    r"(?P<attr>"
    + "|".join(re.escape(name) for name in sorted(CREDENTIAL_ATTRIBUTE_NAMES, key=len, reverse=True))
    + r')\s*=\s*(?P<value>"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\')'
)


def check_sc006_hardcoded_credential_literals(
    file_path: str,
    content: str,
    log_error_func: Callable[[str, str, str, Optional[int]], None],
) -> None:
    """Flag hardcoded credential string literals on known attribute names."""
    if not file_path.endswith(".tf"):
        return

    for line_number, line in enumerate(content.split("\n"), 1):
        clean = strip_line_comment(line)
        if not clean:
            continue

        for match in _ATTR_LITERAL_RE.finditer(clean):
            attr = match.group("attr")
            raw_value = match.group("value")
            # Unwrap quotes
            inner = raw_value[1:-1]
            if is_placeholder_literal(inner):
                continue
            if is_reference_expression(raw_value):
                continue

            log_error_func(
                file_path,
                "SC.006",
                (
                    f"Hardcoded credential literal assigned to '{attr}'. "
                    f"Use a variable reference (e.g. var.{attr}) or a placeholder "
                    f"such as CHANGEME instead of embedding secrets in .tf files."
                ),
                line_number,
            )


def get_rule_description() -> dict:
    """Get the rule description for SC.006."""
    return {
        "rule_id": "SC.006",
        "title": "Hardcoded credential literal check",
        "category": "Security Code",
        "severity": "error",
        "description": (
            "Detects string literals assigned to known credential attributes "
            f"({', '.join(sorted(CREDENTIAL_ATTRIBUTE_NAMES))}) in .tf files. "
            "References and placeholders are allowed."
        ),
        "rationale": (
            "Embedding access keys, secrets, or tokens in Terraform source leaks "
            "credentials into VCS and diverges from example-repo hygiene."
        ),
        "scope": ["providers.tf", "main.tf", "variables.tf", "credential_attributes"],
        "implementation": "modular",
        "version": "1.0.0",
        "related_rules": ["SC.005", "SC.007"],
        "examples": {
            "valid": [
                'access_key = var.access_key',
                'secret_key = var.secret_key',
                'token = "CHANGEME"',
            ],
            "invalid": [
                'access_key = "HPUAFAKE00000000001"',
                'secret_key = "FAKE_SECRET_KEY_DO_NOT_USE"',
            ],
        },
        "fix_suggestions": [
            "Replace literals with var.access_key / var.secret_key",
            "Use placeholders only for local scaffolding",
            "Never commit real credentials in .tf sources",
        ],
    }
