#!/usr/bin/env python3
"""
SC.005 - Sensitive Variable Declaration Check

This module implements the SC.005 rule which validates that sensitive variables
are properly declared with sensitive = true in Terraform variable blocks.

Rule Specification:
- Variables with sensitive names must have sensitive = true declaration
- Supports exact, segment, and contains matching for variable names
- Segment-only allowlist reduces false positives for non-credential names
- Helps prevent sensitive data exposure in Terraform state and logs

Sensitive Variable Patterns:
1. Exact match: email, age, access_key, secret_key, api_key, token, private_key, ...
2. Segment match: auth, token, api_key (underscore-delimited segment equals pattern)
3. Contains match: phone, password, pwd, private_key, credential

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, Optional, List, Dict, Tuple


NON_SENSITIVE_ALLOWLIST = frozenset({
    "auth_type",
    "authorization_mode",
    "oauth_scope",
    "certificate_name",
})


def check_sc005_sensitive_variable_declaration(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if sensitive variables are properly declared with sensitive = true.

    Args:
        file_path (str): Path to the Terraform file being checked
        content (str): Content of the Terraform file
        log_error_func (Callable): Function to log errors with signature (file_path, rule_id, message, line_num)
    """
    sensitive_patterns = _get_sensitive_variable_patterns()
    variable_blocks = _parse_variable_blocks(content)

    for var_block in variable_blocks:
        var_name = var_block['name']
        var_line = var_block['line']
        var_content = var_block['content']

        match_info = _get_sensitive_match(var_name, sensitive_patterns)
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


def _get_sensitive_variable_patterns() -> Dict[str, List[str]]:
    """
    Get the patterns for sensitive variable names.

    Returns:
        Dict[str, List[str]]: Dictionary with exact, segment, and contains pattern lists
    """
    return {
        'exact': [
            'email',
            'age',
            'access_key',
            'secret_key',
            'sex',
            'signature',
            'api_key',
            'token',
            'private_key',
        ],
        'segment': [
            'auth',
            'token',
            'api_key',
        ],
        'contains': [
            'phone',
            'password',
            'pwd',
            'private_key',
            'credential',
        ],
    }


def _split_segments(var_name: str) -> List[str]:
    """Split a snake_case variable name into lowercase segments."""
    return [segment for segment in var_name.lower().split('_') if segment]


def _get_sensitive_match(var_name: str, patterns: Dict[str, List[str]]) -> Optional[Tuple[str, str]]:
    """
    Determine whether a variable name matches a sensitive pattern.

    Matching priority: exact -> segment -> contains.
    Segment matches are skipped when the full variable name is allowlisted.

    Returns:
        Optional[Tuple[str, str]]: (pattern, match_mode) when sensitive, else None
    """
    var_name_lower = var_name.lower()

    for exact_pattern in patterns['exact']:
        if var_name_lower == exact_pattern:
            return exact_pattern, 'exact'

    segments = _split_segments(var_name_lower)
    for segment_pattern in patterns['segment']:
        if segment_pattern in segments:
            if var_name_lower in NON_SENSITIVE_ALLOWLIST:
                continue
            return segment_pattern, 'segment'

    for contains_pattern in patterns['contains']:
        if contains_pattern in var_name_lower:
            return contains_pattern, 'contains'

    return None


def _has_sensitive_declaration(var_content: str) -> bool:
    """
    Check if a variable block contains sensitive = true declaration.

    Args:
        var_content (str): Variable block content

    Returns:
        bool: True if sensitive = true is found, False otherwise
    """
    lines = var_content.split('\n')

    for line in lines:
        clean_line = re.sub(r'#.*$', '', line).strip()
        if not clean_line:
            continue

        sensitive_pattern = r'sensitive\s*=\s*true'
        if re.search(sensitive_pattern, clean_line, re.IGNORECASE):
            return True

    return False


def _parse_variable_blocks(content: str) -> List[Dict[str, any]]:
    """
    Parse variable blocks from Terraform content.

    Args:
        content (str): Terraform file content

    Returns:
        List[Dict[str, any]]: List of variable block information
    """
    variable_blocks = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]

        var_match = re.match(r'variable\s+"([^"]+)"\s*\{', line.strip())
        if var_match:
            var_name = var_match.group(1)
            var_start_line = i + 1

            brace_count = 1
            var_content_lines = [line]
            i += 1

            while i < len(lines) and brace_count > 0:
                line = lines[i]
                var_content_lines.append(line)

                for char in line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            break

                i += 1

            var_content = '\n'.join(var_content_lines)
            variable_blocks.append({
                'name': var_name,
                'line': var_start_line,
                'content': var_content
            })
        else:
            i += 1

    return variable_blocks


def get_rule_description() -> dict:
    """
    Get the rule description for SC.005.

    Returns:
        dict: Rule description containing metadata and details
    """
    patterns = _get_sensitive_variable_patterns()
    return {
        "rule_id": "SC.005",
        "title": "Sensitive Variable Declaration Check",
        "category": "Security Code",
        "severity": "error",
        "description": "Validates that sensitive variables are properly declared with sensitive = true",
        "rationale": "Sensitive variables without proper declaration can expose sensitive data in Terraform state files and logs, creating security risks",
        "scope": ["variable_declaration", "sensitive_data", "security_compliance"],
        "implementation": "modular",
        "version": "1.0.0",
        "sensitive_patterns": {
            "exact_match": patterns['exact'],
            "segment_match": patterns['segment'],
            "contains_match": patterns['contains'],
            "allowlist": sorted(NON_SENSITIVE_ALLOWLIST),
        },
        "examples": {
            "valid": [
                'variable "email" {\n  type        = string\n  description = "User email address"\n  sensitive   = true\n}',
                'variable "user_password" {\n  type        = string\n  description = "User password"\n  sensitive   = true\n}',
                'variable "api_token" {\n  type        = string\n  description = "API token"\n  sensitive   = true\n}',
                'variable "auth_type" {\n  type        = string\n  description = "Authentication type"\n}',
            ],
            "invalid": [
                'variable "email" {\n  type        = string\n  description = "User email address"\n}',
                'variable "api_token" {\n  type        = string\n  description = "API token"\n}',
                'variable "db_credentials" {\n  type        = string\n  description = "Database credentials"\n}',
            ]
        },
        "fix_suggestions": [
            "Add 'sensitive = true' to all sensitive variable declarations",
            "Review variable names against sensitive patterns list",
            "Ensure all variables containing sensitive data are properly marked",
            "Use allowlisted names only for non-credential configuration switches",
            "Regularly audit variable declarations for sensitive data exposure"
        ],
        "security_impact": {
            "risk_level": "high",
            "exposure_points": [
                "Terraform state files",
                "Terraform plan output",
                "Terraform apply logs",
                "CI/CD pipeline logs"
            ],
            "mitigation": "Declaring sensitive variables prevents their values from being displayed in logs and state files"
        }
    }
