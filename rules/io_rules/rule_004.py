#!/usr/bin/env python3
"""
IO.004 - Variable Naming Convention Check

This module implements the IO.004 rule which validates that all input variable names
follow standard naming conventions. Names should use lowercase letters and
underscores only, and should not start with underscores.

Rule Specification:
- Variable names must use snake_case (lowercase with underscores)
- Names must not contain uppercase letters
- Names must not start with underscores
- Names must start with a letter
- Each invalid variable reports an individual error with precise line numbers
- Helps maintain consistency and readability

Examples:
    Valid names:
        variable "instance_count" { ... }
        variable "vpc_cidr_block" { ... }

    Invalid names:
        variable "BadVariableName" { ... }    # Contains uppercase
        variable "_underscore_start" { ... }  # Starts with underscore

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Optional, Tuple


def check_io004_variable_naming(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that variable names follow naming conventions according to IO.004 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all variable names follow standard naming conventions using snake_case format.
    Each invalid variable name is reported individually with precise line numbers.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all variable definitions with their line numbers
    3. Check each variable name against naming convention rules
    4. Report each violation with the specific line number where the variable is defined

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all variable definitions.

        log_error_func (Callable[[str, str, str, Optional[int]], None]): A callback function used
                      to report rule violations. The function should accept four
                      parameters: file_path, rule_id, error_message, and optional line_number.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Example:
        >>> def mock_logger(path, rule, msg, line_num):
        ...     print(f"{rule} at line {line_num}: {msg}")
        >>> content = 'variable "BadName" { type = string }'
        >>> check_io004_variable_naming("variables.tf", content, mock_logger)
        IO.004 at line 1: Variable 'BadName' should use snake_case naming convention
    """
    clean_content = _remove_comments_for_parsing(content)
    
    # Extract variables with their line numbers
    variables_with_lines = _extract_variables_with_lines(clean_content)
    
    # Check each variable name and report violations individually
    for var_name, line_number in variables_with_lines:
        if not _is_valid_variable_name(var_name):
            log_error_func(
                file_path,
                "IO.004",
                f"Variable '{var_name}' should use snake_case naming convention (lowercase letters and underscores only, not starting with underscore)",
                line_number
            )


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from content for parsing, but preserve line structure.

    Args:
        content (str): The original file content

    Returns:
        str: Content with comments removed but line numbers preserved
    """
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        # Remove comments but keep the line structure
        if '#' in line:
            # Find the first # that's not inside quotes
            in_quotes = False
            quote_char = None
            for i, char in enumerate(line):
                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                elif char == '#' and not in_quotes:
                    line = line[:i]
                    break
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def _extract_variables_with_lines(content: str) -> List[Tuple[str, int]]:
    """
    Extract variable names from the content with their line numbers.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[Tuple[str, int]]: List of tuples containing (variable_name, line_number)
    """
    variables_with_lines = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Match variable definitions - support quoted, single-quoted, and unquoted syntax
        # Quoted: variable "name" { ... }
        # Single-quoted: variable 'name' { ... }
        # Unquoted: variable name { ... }
        var_pattern = r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{'
        match = re.search(var_pattern, line)
        if match:
            # Get variable name from quoted, single-quoted, or unquoted group
            var_name = match.group(1) if match.group(1) else (match.group(2) if match.group(2) else match.group(3))
            variables_with_lines.append((var_name, line_num))
    
    return variables_with_lines


def _is_valid_variable_name(name: str) -> bool:
    """
    Check if a variable name follows the snake_case naming convention.

    Args:
        name (str): The variable name to validate

    Returns:
        bool: True if the name is valid, False otherwise
    """
    # Must start with a lowercase letter (not underscore)
    if not re.match(r'^[a-z]', name):
        return False
    
    # Must contain only lowercase letters, numbers, and underscores
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        return False
    
    return True


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.004 rule.

    Returns:
        dict: A dictionary containing comprehensive rule information
    """
    return {
        "id": "IO.004",
        "name": "Variable Naming Convention Check",
        "description": (
            "Validates that each input variable name follows standard naming conventions "
            "using snake_case format. Variable names should use lowercase letters and "
            "underscores only, and should not start with underscores. Each invalid "
            "variable name is reported individually with precise line numbers."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Consistent naming conventions improve code readability and "
            "maintainability. Snake_case is the standard convention for "
            "Terraform variable names. Each violation is reported individually "
            "to facilitate precise error identification and correction."
        ),
        "examples": {
            "valid": [
                'variable "instance_count" {\n  type = number\n}',
                'variable "vpc_cidr_block" {\n  type = string\n}',
                'variable "environment_name" {\n  type = string\n}'
            ],
            "invalid": [
                'variable "BadVariableName" {\n  type = string\n}  # Contains uppercase letters',
                'variable "_underscore_start" {\n  type = string\n}  # Starts with underscore',
                'variable "variable-with-hyphens" {\n  type = string\n}  # Contains hyphens'
            ]
        },
        "error_format": "Variable '{variable_name}' should use snake_case naming convention (lowercase letters and underscores only, not starting with underscore)",
        "line_number_reporting": "Reports the exact line number where each invalid variable is defined",
        "precision": "Individual error reporting for each invalid variable name",
        "related_rules": ["ST.001", "IO.005"]
    }
