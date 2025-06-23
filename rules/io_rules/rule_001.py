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
from typing import Callable, List, Dict, Any, Optional, Tuple


def check_io001_variable_file_location(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate variable definition file organization according to IO.001 rule specifications.
    
    This function validates that all variable definitions are properly organized 
    in variables.tf files within their respective directories. It ensures that 
    variables are defined in the correct location for better code organization 
    and maintainability.
    
    The validation process:
    1. Check if the current file contains variable definitions
    2. Verify that variable definitions are in the appropriate variables.tf file
    3. Report violations for each misplaced variable definition individually
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to check for variable definitions.
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
        ...     print(f"{rule} at {path}: {msg}")
        >>> 
        >>> # Content with variable definition in wrong file
        >>> content = '''
        ... variable "example" {
        ...   type = string
        ... }
        ... '''
        >>> check_io001_variable_file_location("main.tf", content, sample_log_func)
        IO.001 at main.tf: Variable 'example' should be defined in 'variables.tf'
    """
    variables = _extract_variables_with_lines(content)
    
    # Check if non-variables.tf files contain variable definitions
    if variables and not file_path.endswith('variables.tf'):
        for variable in variables:
            log_error_func(
                file_path,
                "IO.001",
                f"Variable '{variable[0]}' should be defined in 'variables.tf'",
                variable[1]
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


def _extract_variables_with_lines(content: str) -> List[Tuple[str, int]]:
    """
    Extract variable names from the content with their line numbers.

    This function searches for all variable definitions in the Terraform content
    and returns their names along with the line numbers where they are defined.

    Args:
        content (str): The Terraform file content

    Returns:
        List[Tuple[str, int]]: List of tuples containing (variable_name, line_number)
    """
    variables = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Match variable definitions - support quoted, single-quoted, and unquoted syntax
        # Quoted: variable "name" { ... }
        # Single-quoted: variable 'name' { ... }
        # Unquoted: variable name { ... }
        var_match = re.match(r'\s*variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        if var_match:
            # Get variable name from quoted, single-quoted, or unquoted group
            var_name = var_match.group(1) if var_match.group(1) else (var_match.group(2) if var_match.group(2) else var_match.group(3))
            variables.append((var_name, i))
    
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
            "Validates that each input variable is properly defined in "
            "the variables.tf file and not in other files. Each variable "
            "definition found in non-variables.tf files will be reported "
            "as a separate violation."
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
