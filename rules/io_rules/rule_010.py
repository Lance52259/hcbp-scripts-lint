#!/usr/bin/env python3
"""
IO.010 - Variable Validation Block Check

Validates structural completeness of validation {} blocks inside variable
definitions. Only variables that already declare at least one validation block
are checked. Variables without validation blocks are not flagged.

Layer A checks (per validation block):
- condition field is required
- error_message field is required and non-empty
- error_message must be at least 10 characters and not equal to the variable name
- validation {} must not be empty

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Dict, Any, Optional, Tuple

_MIN_ERROR_MESSAGE_LENGTH = 10


def check_io010_variable_validation(
    file_path: str,
    content: str,
    log_error_func: Callable[[str, str, str, Optional[int]], None],
) -> None:
    """
    Validate validation block structure for variables in variables.tf.

    Only runs on variables.tf. Variables without validation blocks are skipped.
    """
    if not file_path.endswith("variables.tf"):
        return

    for variable in _extract_variables_with_validations(content):
        for validation in variable["validations"]:
            _validate_validation_structure(
                file_path,
                variable["name"],
                validation,
                log_error_func,
            )


def _validate_validation_structure(
    file_path: str,
    variable_name: str,
    validation: Dict[str, Any],
    log_error_func: Callable[[str, str, str, Optional[int]], None],
) -> None:
    """Run Layer A structural checks on a single validation block."""
    line_number = validation["start_line"]
    body = validation["body"]
    clean_body = _remove_comments_for_parsing(body)

    has_condition = bool(re.search(r"\bcondition\s*=", clean_body))
    error_message = _extract_error_message_value(clean_body)

    if not has_condition and not error_message:
        log_error_func(
            file_path,
            "IO.010",
            f"Variable '{variable_name}' has an empty validation block; "
            f"'condition' and 'error_message' are required",
            line_number,
        )
        return

    if not has_condition:
        log_error_func(
            file_path,
            "IO.010",
            f"Variable '{variable_name}' validation block is missing required field 'condition'",
            line_number,
        )

    if error_message is None:
        log_error_func(
            file_path,
            "IO.010",
            f"Variable '{variable_name}' validation block is missing required field 'error_message'",
            line_number,
        )
        return

    if len(error_message) < _MIN_ERROR_MESSAGE_LENGTH:
        log_error_func(
            file_path,
            "IO.010",
            f"Variable '{variable_name}' validation 'error_message' must be at least "
            f"{_MIN_ERROR_MESSAGE_LENGTH} characters",
            line_number,
        )

    if error_message.lower() == variable_name.lower():
        log_error_func(
            file_path,
            "IO.010",
            f"Variable '{variable_name}' validation 'error_message' must not be the same as the variable name",
            line_number,
        )


def _extract_variables_with_validations(content: str) -> List[Dict[str, Any]]:
    """Parse variable blocks and collect nested validation sub-blocks."""
    lines = content.split("\n")
    variables: List[Dict[str, Any]] = []
    i = 0

    while i < len(lines):
        match = re.match(
            r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{',
            lines[i].strip(),
        )
        if not match:
            i += 1
            continue

        variable_name = match.group(1) or match.group(2) or match.group(3)
        block_lines, end_index = _extract_brace_block(lines, i)
        validations = _find_validation_blocks(block_lines, i + 1)

        if validations:
            variables.append(
                {
                    "name": variable_name,
                    "validations": validations,
                }
            )

        i = end_index + 1

    return variables


def _extract_brace_block(lines: List[str], start_index: int) -> Tuple[List[str], int]:
    """Extract a brace-delimited block starting at start_index."""
    depth = 0
    block_lines: List[str] = []

    for i in range(start_index, len(lines)):
        line = lines[i]
        block_lines.append(line)
        depth += line.count("{") - line.count("}")
        if depth == 0 and i > start_index:
            return block_lines, i

    return block_lines, len(lines) - 1


def _find_validation_blocks(
    block_lines: List[str], block_start_line: int
) -> List[Dict[str, Any]]:
    """Find direct validation {} sub-blocks within a variable block."""
    validations: List[Dict[str, Any]] = []
    i = 0

    while i < len(block_lines):
        if re.match(r"validation\s*\{", block_lines[i].strip()):
            validation_lines, end_index = _extract_brace_block(block_lines, i)
            validations.append(
                {
                    "body": "\n".join(validation_lines),
                    "start_line": block_start_line + i,
                }
            )
            i = end_index + 1
        else:
            i += 1

    return validations


def _extract_error_message_value(clean_body: str) -> Optional[str]:
    """
    Extract the string value assigned to error_message, if present.

    Returns:
        - str when error_message is present (may be empty string)
        - None when error_message field is absent
    """
    double_quoted = re.search(r'\berror_message\s*=\s*"([^"]*)"', clean_body, re.DOTALL)
    if double_quoted:
        return double_quoted.group(1)

    single_quoted = re.search(r"\berror_message\s*=\s*'([^']*)'", clean_body, re.DOTALL)
    if single_quoted:
        return single_quoted.group(1)

    if re.search(r"\berror_message\s*=", clean_body):
        return ""

    return None


def _remove_comments_for_parsing(content: str) -> str:
    """Remove comments while preserving line structure."""
    cleaned_lines: List[str] = []

    for line in content.split("\n"):
        if "#" not in line:
            cleaned_lines.append(line)
            continue

        in_quotes = False
        quote_char: Optional[str] = None
        cut_at: Optional[int] = None

        for idx, char in enumerate(line):
            if char in ['"', "'"] and (idx == 0 or line[idx - 1] != "\\"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
            elif char == "#" and not in_quotes:
                cut_at = idx
                break

        cleaned_lines.append(line if cut_at is None else line[:cut_at].rstrip())

    return "\n".join(cleaned_lines)


def get_rule_description() -> Dict[str, Any]:
    """Return IO.010 rule metadata."""
    return {
        "id": "IO.010",
        "name": "Variable validation block check",
        "description": (
            "Validates that validation {} blocks inside variable definitions are "
            "structurally complete. Each validation block must include condition "
            "and error_message fields. Variables without validation blocks are not checked."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Validation blocks document input constraints at the variable definition "
            "site. Requiring condition and error_message ensures failures are actionable "
            "without evaluating expression semantics statically."
        ),
        "examples": {
            "valid": [
                '''variable "vpc_name" {
  type = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]+$", var.vpc_name))
    error_message = "VPC name must contain only alphanumeric characters, underscores, and hyphens."
  }
}''',
                '''variable "subnet_name" {
  type = string
}''',
            ],
            "invalid": [
                '''variable "example_a" {
  type = string
  validation {
    error_message = "Value is invalid."
  }
}''',
                '''variable "example_b" {
  type = string
  validation {}
}''',
            ],
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.003", "IO.008", "SC.003"],
        "configuration": {
            "min_error_message_length": _MIN_ERROR_MESSAGE_LENGTH,
            "require_validation_presence": False,
        },
    }
