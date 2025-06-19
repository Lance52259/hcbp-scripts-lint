#!/usr/bin/env python3
"""
IO.005 - Output Naming Convention Check

This module implements the IO.005 rule which validates that all output names
follow standard naming conventions. Names should use lowercase letters and
underscores only, and should not start with underscores.

Rule Specification:
- Output names must use snake_case (lowercase with underscores)
- Names must not contain uppercase letters
- Names must not start with underscores
- Names must start with a letter
- Helps maintain consistency and readability

Examples:
    Valid names:
        output "instance_id" { ... }
        output "vpc_cidr_block" { ... }

    Invalid names:
        output "BadOutputName" { ... }    # Contains uppercase
        output "_underscore_output" { ... }  # Starts with underscore

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Optional


def check_io005_output_naming(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that output names follow naming conventions according to IO.005 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all output names follow standard naming conventions using snake_case format.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all output definitions from the file with their line numbers
    3. Check each name against naming convention rules
    4. Report violations through the error logging function with line numbers

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all output definitions.

        log_error_func (Callable[[str, str, str, Optional[int]], None]): A callback function used
                      to report rule violations. The function should accept four
                      parameters: file_path, rule_id, error_message, and optional line_number.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Example:
        >>> def mock_logger(path, rule, msg, line_num):
        ...     print(f"{rule} at line {line_num}: {msg}")
        >>> content = 'output "BadName" { value = "test" }'
        >>> check_io005_output_naming("outputs.tf", content, mock_logger)
        IO.005 at line 1: Output 'BadName' should use snake_case naming convention
    """
    clean_content = _remove_comments_for_parsing(content)
    
    # Check output names with line numbers
    outputs_with_lines = _extract_outputs_with_lines(clean_content)
    for output_name, line_number in outputs_with_lines:
        if not _is_valid_name(output_name):
            log_error_func(
                file_path,
                "IO.005",
                f"Output '{output_name}' should use snake_case naming convention (lowercase letters and underscores only, not starting with underscore)",
                line_number
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


def _extract_outputs_with_lines(content: str) -> List[tuple]:
    """
    Extract output names from the content along with their line numbers.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[tuple]: List of tuples containing (output_name, line_number)
    """
    output_pattern = r'output\s+"([^"]+)"\s*\{'
    outputs_with_lines = []
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        matches = re.findall(output_pattern, line)
        for match in matches:
            outputs_with_lines.append((match, line_num))
    
    return outputs_with_lines


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
    Retrieve detailed information about the IO.005 rule.

    Returns:
        dict: A dictionary containing comprehensive rule information
    """
    return {
        "id": "IO.005",
        "name": "Output naming convention check",
        "description": (
            "Validates that output names follow standard naming conventions "
            "using snake_case format. Names should use lowercase letters and "
            "underscores only, and should not start with underscores."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Consistent naming conventions improve code readability and "
            "maintainability. Snake_case is the standard convention for "
            "Terraform output names."
        ),
        "examples": {
            "valid": [
                'output "instance_id" { value = huaweicloud_compute_instance.test.id }',
                'output "vpc_cidr_block" { value = huaweicloud_vpc.test.cidr }'
            ],
            "invalid": [
                'output "BadOutputName" { value = "test" }',
                'output "_underscore_output" { value = "test" }'
            ]
        }
    }
