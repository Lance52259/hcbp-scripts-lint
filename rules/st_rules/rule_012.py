#!/usr/bin/env python3
"""
ST.012 - File Header and Footer Whitespace Check

This module implements the ST.012 rule which validates that Terraform files
have proper whitespace formatting at the beginning and end of the file.

Rule Specification:
- Files should not have empty lines before the first non-empty line
- Files should have exactly one empty line after the last non-empty line
- This ensures consistent file formatting and readability

Examples:
    Valid file structure:
        # This is the first line (no empty lines before)
        resource "huaweicloud_vpc" "test" {
          name = "test-vpc"
        }
        # This is the last line
        [empty line]

    Invalid file structure:
        [empty line]
        [empty line]
        # This is the first line (too many empty lines before)
        resource "huaweicloud_vpc" "test" {
          name = "test-vpc"
        }
        # This is the last line (no empty line after)

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Optional


def check_st012_file_whitespace(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if Terraform files have proper whitespace formatting at the beginning and end.
    
    This function validates that Terraform files follow proper whitespace formatting
    rules: no empty lines before the first non-empty line, and exactly one empty
    line after the last non-empty line. This ensures consistent file formatting
    and improves readability.
    
    The function specifically checks:
    - File header: No empty lines should precede the first non-empty line
    - File footer: Exactly one empty line should follow the last non-empty line
    - Multiple violations: Reports the number of illegal lines when multiple violations occur
    
    Valid formatting:
    - Files start directly with content (no leading empty lines)
    - Files end with exactly one empty line after the last content line
    - Consistent formatting across all Terraform files
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to extract and validate whitespace patterns.
        log_error_func (Callable[[str, str, str, Optional[int]], None]): 
                      Callback function for logging validation errors. The function
                      signature expects (file_path, rule_id, error_message, line_number).
                      The line_number parameter is optional and can be None.
    
    Returns:
        None: This function doesn't return any value. All validation results
              are communicated through the log_error_func callback.
    
    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    
    Example:
        >>> def sample_log_func(path, rule, msg, line_num):
        ...     print(f"{rule} at {path}:{line_num}: {msg}")
        >>> 
        >>> content = '''
        ... 
        ... resource "huaweicloud_vpc" "test" {
        ...   name = "test-vpc"
        ... }
        ... '''
        >>> check_st012_file_whitespace("main.tf", content, sample_log_func)
        ST.012 at main.tf:2: File has 2 empty lines before first non-empty line (should have 0)
    """
    lines = content.split('\n')
    
    # Find first non-empty line
    first_non_empty_line = None
    leading_empty_lines = 0
    
    for line_num, line in enumerate(lines, 1):
        if line.strip():  # Non-empty line found
            first_non_empty_line = line_num
            break
        else:
            leading_empty_lines += 1
    
    # Check for leading empty lines
    if leading_empty_lines > 0:
        if leading_empty_lines == 1:
            log_error_func(
                file_path,
                "ST.012",
                f"File has 1 empty line before first non-empty line (should have 0)",
                first_non_empty_line
            )
        else:
            log_error_func(
                file_path,
                "ST.012",
                f"File has {leading_empty_lines} empty lines before first non-empty line (should have 0)",
                first_non_empty_line
            )
    
    # Find last non-empty line
    last_non_empty_line = None
    trailing_empty_lines = 0
    
    # Start from the end and work backwards
    for line_num in range(len(lines) - 1, -1, -1):
        line = lines[line_num]
        if line.strip():  # Non-empty line found
            last_non_empty_line = line_num + 1  # Convert to 1-based indexing
            break
        else:
            trailing_empty_lines += 1
    
    # Check for trailing empty lines
    if trailing_empty_lines == 0:
        log_error_func(
            file_path,
            "ST.012",
            f"File has 0 empty lines after last non-empty line (should have 1)",
            last_non_empty_line
        )
    elif trailing_empty_lines > 1:
        if trailing_empty_lines == 2:
            log_error_func(
                file_path,
                "ST.012",
                f"File has 2 empty lines after last non-empty line (should have 1)",
                last_non_empty_line
            )
        else:
            log_error_func(
                file_path,
                "ST.012",
                f"File has {trailing_empty_lines} empty lines after last non-empty line (should have 1)",
                last_non_empty_line
            )


def get_rule_description() -> dict:
    """
    Get the rule description for ST.012.
    
    Returns:
        dict: Rule description with name, description, and examples
    """
    return {
        "name": "File header and footer whitespace check",
        "description": "Validates that Terraform files have proper whitespace formatting at the beginning and end. Files should not have empty lines before the first non-empty line, and should have exactly one empty line after the last non-empty line.",
        "category": "Style/Format",
        "severity": "warning",
        "examples": {
            "valid": [
                "# This is the first line (no empty lines before)\nresource \"huaweicloud_vpc\" \"test\" {\n  name = \"test-vpc\"\n}\n# This is the last line\n",
                "resource \"huaweicloud_vpc\" \"test\" {\n  name = \"test-vpc\"\n}\n"
            ],
            "invalid": [
                "\n\n# This is the first line (too many empty lines before)\nresource \"huaweicloud_vpc\" \"test\" {\n  name = \"test-vpc\"\n}",
                "resource \"huaweicloud_vpc\" \"test\" {\n  name = \"test-vpc\"\n}\n\n\n# Too many empty lines at end"
            ]
        },
        "fix_suggestions": [
            "Remove all empty lines before the first non-empty line",
            "Ensure exactly one empty line follows the last non-empty line",
            "Use consistent file formatting across all Terraform files"
        ]
    } 