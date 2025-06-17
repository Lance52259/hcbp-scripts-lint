#!/usr/bin/env python3
"""
IO.004 - Variable Naming Convention Check

This module implements the IO.004 rule which validates that all variable names
follow standard naming conventions. Names should use lowercase letters and
underscores only, and should not start with underscores.

Rule Specification:
- Variable names must use snake_case (lowercase with underscores)
- Names must not contain uppercase letters
- Names must not start with underscores
- Names must start with a letter
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
from typing import Callable, List


def check_io004_variable_naming(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate that variable names follow naming conventions according to IO.004 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all variable names follow standard naming conventions using snake_case format.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all variable definitions from the file
    3. Check each name against naming convention rules
    4. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all variable definitions.

        log_error_func (Callable[[str, str, str], None]): A callback function used
                      to report rule violations. The function should accept three
                      parameters: file_path, rule_id, and error_message.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Example:
        >>> def mock_logger(path, rule, msg):
        ...     print(f"{rule}: {msg}")
        >>> content = 'variable "BadName" { type = string }'
        >>> check_io004_variable_naming("variables.tf", content, mock_logger)
        IO.004: Variable 'BadName' should use snake_case naming convention
    """
    clean_content = _remove_comments_for_parsing(content)
    
    # Check variable names
    variables = _extract_variables(clean_content)
    for var_name in variables:
        if not _is_valid_name(var_name):
            log_error_func(
                file_path,
                "IO.004",
                f"Variable '{var_name}' should use snake_case naming convention (lowercase letters and underscores only, not starting with underscore)"
            )


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from content for parsing, but preserve line structure.

    Args:
        content (str): The original file content

    Returns:
        str: Content with comments removed
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


def _extract_variables(content: str) -> List[str]:
    """
    Extract variable names from the content.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[str]: List of variable names
    """
    var_pattern = r'variable\s+"([^"]+)"\s*\{'
    return re.findall(var_pattern, content)


def _is_valid_name(name: str) -> bool:
    """
    Check if a name follows the snake_case naming convention.

    Args:
        name (str): The name to validate

    Returns:
        bool: True if the name is valid, False otherwise
    """
    # Must start with a lowercase letter
    if not re.match(r'^[a-z]', name):
        return False
    
    # Must contain only lowercase letters, numbers, and underscores
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        return False
    
    # Must not have consecutive underscores
    if '__' in name:
        return False
    
    # Must not end with underscore
    if name.endswith('_'):
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
        "name": "Variable naming convention check",
        "description": (
            "Validates that variable names follow standard naming conventions "
            "using snake_case format. Names should use lowercase letters and "
            "underscores only, and should not start with underscores."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Consistent naming conventions improve code readability and "
            "maintainability. Snake_case is the standard convention for "
            "Terraform variable names."
        ),
        "examples": {
            "valid": [
                'variable "instance_count" { type = number }',
                'variable "vpc_cidr_block" { type = string }'
            ],
            "invalid": [
                'variable "BadVariableName" { type = string }',
                'variable "_underscore_start" { type = string }'
            ]
        }
    }
