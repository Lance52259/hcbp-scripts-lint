#!/usr/bin/env python3
"""
SC.005 - Sensitive Variable Declaration Check

Validates that sensitive-named variables declare sensitive = true.
Patterns live in rules.common.sensitive_patterns (shared with SC.006/SC.007).

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, Optional, List, Dict, Any

from rules.common.sensitive_patterns import (
    NON_SENSITIVE_ALLOWLIST,
    get_sensitive_match,
    get_sensitive_variable_patterns,
)


# Re-export for acceptances/unit tests
_get_sensitive_variable_patterns = get_sensitive_variable_patterns
_get_sensitive_match = get_sensitive_match


def check_sc005_sensitive_variable_declaration(
    file_path: str,
    content: str,
    log_error_func: Callable[[str, str, str, Optional[int]], None],
) -> None:
    """Check if sensitive variables are properly declared with sensitive = true."""
    sensitive_patterns = get_sensitive_variable_patterns()
    variable_blocks = parse_variable_blocks(content)

    for var_block in variable_blocks:
        var_name = var_block["name"]
        var_line = var_block["line"]
        var_content = var_block["content"]

        match_info = get_sensitive_match(var_name, sensitive_patterns)
        if match_info is None:
            continue

        pattern, match_mode = match_info
        if not _has_sensitive_declaration(var_content):
            error_msg = (
                f"Sensitive variable '{var_name}' must be declared with 'sensitive = true' "
                f"to prevent data exposure in Terraform state and logs "
                f"(matched pattern '{pattern}' via {match_mode} match)."
            )
            log_error_func(file_path, "SC.005", error_msg, var_line)


def _has_sensitive_declaration(var_content: str) -> bool:
    """Return True when the variable block sets sensitive = true."""
    for line in var_content.split("\n"):
        clean_line = re.sub(r"#.*$", "", line).strip()
        if not clean_line:
            continue
        if re.search(r"sensitive\s*=\s*true", clean_line, re.IGNORECASE):
            return True
    return False


def parse_variable_blocks(content: str) -> List[Dict[str, Any]]:
    """Parse variable blocks (quoted, single-quoted, or unquoted names)."""
    variable_blocks: List[Dict[str, Any]] = []
    lines = content.split("\n")
    i = 0
    var_pattern = (
        r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|'
        r'([a-zA-Z][a-zA-Z0-9_]*[a-zA-Z]|[a-zA-Z]))\s*\{'
    )

    while i < len(lines):
        line = lines[i]
        var_match = re.match(var_pattern, line.strip())
        if var_match:
            var_name = var_match.group(1) or var_match.group(2) or var_match.group(3)
            var_start_line = i + 1
            brace_count = 1
            var_content_lines = [line]
            i += 1

            while i < len(lines) and brace_count > 0:
                line = lines[i]
                var_content_lines.append(line)
                for char in line:
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            break
                i += 1

            variable_blocks.append({
                "name": var_name,
                "line": var_start_line,
                "content": "\n".join(var_content_lines),
            })
        else:
            i += 1

    return variable_blocks


# Backward-compatible alias
_parse_variable_blocks = parse_variable_blocks


def get_rule_description() -> dict:
    """Get the rule description for SC.005."""
    patterns = get_sensitive_variable_patterns()
    return {
        "rule_id": "SC.005",
        "title": "Sensitive Variable Declaration Check",
        "category": "Security Code",
        "severity": "error",
        "description": "Validates that sensitive variables are properly declared with sensitive = true",
        "rationale": (
            "Sensitive variables without proper declaration can expose sensitive data "
            "in Terraform state files and logs, creating security risks"
        ),
        "scope": ["variable_declaration", "sensitive_data", "security_compliance"],
        "implementation": "modular",
        "version": "1.1.0",
        "sensitive_patterns": {
            "exact_match": patterns["exact"],
            "segment_match": patterns["segment"],
            "contains_match": patterns["contains"],
            "allowlist": sorted(NON_SENSITIVE_ALLOWLIST),
        },
        "examples": {
            "valid": [
                'variable "email" {\n  type = string\n  sensitive = true\n}',
                'variable "user_phone" {\n  type = string\n  sensitive = true\n}',
                'variable "microphone" {\n  type = string\n}',
                'variable "auth_type" {\n  type = string\n}',
            ],
            "invalid": [
                'variable "api_token" {\n  type = string\n}',
                'variable "db_credentials" {\n  type = string\n}',
                'variable api_token {\n  type = string\n}',
            ],
        },
        "fix_suggestions": [
            "Add 'sensitive = true' to all sensitive variable declarations",
            "Review variable names against sensitive patterns list",
        ],
    }
