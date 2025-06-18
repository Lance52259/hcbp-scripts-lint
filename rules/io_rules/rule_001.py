#!/usr/bin/env python3
"""
IO.001 - Variable Definition File Location Check

This module implements the IO.001 rule which ensures that all variable definitions
are properly organized in the variables.tf file and not scattered across other files.

Rule Specification:
- All input variables must be defined in the variables.tf file
- Variable definitions in other files will be flagged as violations
- Helps maintain consistent project structure and organization

Examples:
    Valid organization:
        # variables.tf
        variable "flavor_id" {
          description = "The flavor ID of the compute instance"
          type        = string
          default     = "c6.2xlarge.4"
        }

    Invalid organization:
        # main.tf (should not contain variable definitions)
        variable "flavor_id" {
          description = "The flavor ID of the compute instance"
          type        = string
          default     = "c6.2xlarge.4"
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, List, Dict, Any


def check_io001_variable_file_location(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate that all variable definitions are located in variables.tf file according to IO.001 rule specifications.

    This function scans through the provided Terraform file content and validates
    that variable definitions are properly organized in the variables.tf file.
    This ensures consistent project structure and organization following Terraform
    best practices.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all variable definitions from the file
    3. Check if non-variables.tf files contain variable definitions
    4. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all variable definitions that need to be checked.

        log_error_func (Callable[[str, str, str], None]): A callback function used
                      to report rule violations. The function should accept three
                      parameters: file_path, rule_id, and error_message.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.

    Example:
        >>> def mock_logger(path, rule, msg):
        ...     print(f"{rule}: {msg}")
        >>> content = 'variable "test" { type = string }'
        >>> check_io001_variable_file_location("main.tf", content, mock_logger)
        IO.001: Variable 'test' should be defined in variables.tf, not in main.tf
    """
    variables = _extract_variables(content)
    
    # Check if non-variables.tf files contain variable definitions
    if variables and not file_path.endswith('variables.tf'):
        for variable in variables:
            log_error_func(
                file_path,
                "IO.001",
                f"Variable '{variable['name']}' should be defined in variables.tf, not in {os.path.basename(file_path)}"
            )
        
        # Provide summary error message
        log_error_func(
            file_path,
            "IO.001",
            f"File {os.path.basename(file_path)} contains {len(variables)} variable definition(s) that should be moved to variables.tf"
        )


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from content for parsing, but preserve line structure.

    This helper function removes all comments from the Terraform content
    while maintaining the line structure for accurate parsing.

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


def _extract_variables(content: str) -> List[Dict[str, Any]]:
    """
    Extract variable definitions with their metadata from the content.

    This function parses the content to find all variable definitions and
    extracts relevant metadata for validation purposes.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[Dict[str, Any]]: List of variable definitions with metadata
    """
    variables = []
    clean_content = _remove_comments_for_parsing(content)

    # Pattern to match variable blocks with their full content
    var_pattern = r'variable\s+"([^"]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    var_matches = re.findall(var_pattern, clean_content, re.DOTALL)

    for var_name, var_body in var_matches:
        variable_info = {
            'name': var_name,
            'has_default': bool(re.search(r'default\s*=', var_body)),
            'has_description': bool(re.search(r'description\s*=', var_body)),
            'has_type': bool(re.search(r'type\s*=', var_body)),
            'body': var_body.strip()
        }
        variables.append(variable_info)

    return variables


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.001 rule.

    This function provides metadata about the rule including its purpose,
    validation criteria, and examples. This information can be used for
    documentation generation, help systems, or configuration interfaces.

    Returns:
        dict: A dictionary containing comprehensive rule information including:
            - id: The unique rule identifier
            - name: Human-readable rule name
            - description: Detailed explanation of what the rule validates
            - category: The rule category (Input/Output)
            - severity: The severity level of violations
            - examples: Dictionary with valid and invalid examples

    Example:
        >>> info = get_rule_description()
        >>> print(info['name'])
        Variable definition file location check
    """
    return {
        "id": "IO.001",
        "name": "Variable definition file location check",
        "description": (
            "Validates that all variable definitions are properly organized in "
            "the variables.tf file and not scattered across other files. This "
            "ensures consistent project structure and organization following "
            "Terraform best practices."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Organizing all variable definitions in a dedicated variables.tf file "
            "improves project structure consistency, facilitates centralized variable "
            "management, and enhances code maintainability. This follows Terraform "
            "community best practices for project organization."
        ),
        "examples": {
            "valid": [
                '''
# variables.tf
variable "flavor_id" {
  description = "The flavor ID of the compute instance"
  type        = string
  default     = "c6.2xlarge.4"
}

# main.tf
resource "huaweicloud_compute_instance" "test" {
  flavor_id = var.flavor_id
  # ...
}
'''
            ],
            "invalid": [
                '''
# main.tf (should not contain variable definitions)
variable "flavor_id" {
  description = "The flavor ID of the compute instance"
  type        = string
  default     = "c6.2xlarge.4"
}

resource "huaweicloud_compute_instance" "test" {
  flavor_id = var.flavor_id
  # ...
}
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal"
    }
