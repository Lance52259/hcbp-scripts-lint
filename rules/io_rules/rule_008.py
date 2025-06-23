#!/usr/bin/env python3
"""
IO.008 - Variable Type Check

This module implements the IO.008 rule which validates that all input variable
definitions include type specifications. This ensures proper type validation
and helps prevent configuration errors.

Rule Specification:
- All variable definitions must include a type field
- Type specifications help with validation and documentation
- Helps improve module robustness and error detection

Examples:
    Valid declarations:
        variable "instance_name" {
          description = "Name of the ECS instance"
          type        = string
        }

        variable "instance_count" {
          description = "Number of instances to create"
          type        = number
          default     = 1
        }

        variable "tags" {
          description = "Tags to apply to resources"
          type        = map(string)
          default     = {}
        }

    Invalid declarations:
        variable "instance_name" {
          description = "Name of the ECS instance"
          # Missing type specification
        }

        variable "vpc_cidr" {
          description = "CIDR block for VPC"
          default     = "10.0.0.0/16"
          # Missing type specification
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Dict, Any, Optional


def check_io008_variable_type(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that all variables have explicit type declarations according to IO.008 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all variable definitions include explicit type declarations. Type declarations
    improve code clarity, prevent type-related errors, and enhance tooling support
    for validation and autocompletion.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all variable definitions from the file
    3. Check each variable for the presence of a type declaration
    4. Validate that type declarations are meaningful and specific
    5. Report violations through the error logging function

    Type requirements:
    - All variables must have an explicit type declaration
    - Type declarations should be specific (string, number, bool, list, map, etc.)
    - Avoid using 'any' type unless absolutely necessary
    - Complex types should be properly structured

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

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.

    Example:
        >>> def mock_logger(path, rule, msg, line_num):
        ...     print(f"{rule}: {msg}")
        >>> content = '''
        ... variable "example" {
        ...   description = "Example variable"
        ... }
        ... '''
        >>> check_io008_variable_type("variables.tf", content, mock_logger)
        IO.008: Variable 'example' must include a type declaration
    """
    variables = _extract_variables(content)
    
    for variable in variables:
        if not variable['has_type']:
            log_error_func(
                file_path,
                "IO.008",
                f"Variable '{variable['name']}' must include a type field",
                variable.get('line_number')
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

    # Pattern to match variable blocks - support quoted, single-quoted, and unquoted syntax
    variable_pattern = r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    
    # Find all variable matches with their positions
    for match in re.finditer(variable_pattern, clean_content, re.DOTALL):
        # Get variable name from quoted, single-quoted, or unquoted group
        variable_name = match.group(1) if match.group(1) else (match.group(2) if match.group(2) else match.group(3))
        variable_body = match.group(4)
        
        # Find line number by counting newlines before match
        preceding_text = clean_content[:match.start()]
        line_number = preceding_text.count('\n') + 1
        
        # Check for type field
        has_type = bool(re.search(r'type\s*=', variable_body))
        
        # Extract type if present
        type_match = re.search(r'type\s*=\s*([^\n]+)', variable_body)
        type_value = type_match.group(1).strip() if type_match else ""
        
        variable_info = {
            'name': variable_name,
            'has_type': has_type,
            'type': type_value,
            'has_description': bool(re.search(r'description\s*=', variable_body)),
            'has_default': bool(re.search(r'default\s*=', variable_body)),
            'body': variable_body.strip(),
            'line_number': line_number
        }
        variables.append(variable_info)

    return variables


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.008 rule.

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
        Variable type check
    """
    return {
        "id": "IO.008",
        "name": "Variable type check",
        "description": (
            "Validates that all input variable definitions include type "
            "specifications. This ensures proper type validation and helps "
            "prevent configuration errors by providing clear type constraints."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Type specifications in variable definitions are essential for "
            "proper validation and error prevention. They help Terraform "
            "validate input values, provide better error messages, and "
            "improve module documentation and usability."
        ),
        "examples": {
            "valid": [
                '''variable "instance_name" {
  description = "Name of the ECS instance"
  type        = string
}''',
                '''variable "instance_count" {
  description = "Number of instances to create"
  type        = number
  default     = 1
}''',
                '''variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}'''
            ],
            "invalid": [
                '''variable "instance_name" {
  description = "Name of the ECS instance"
  # Missing type specification
}''',
                '''variable "vpc_cidr" {
  description = "CIDR block for VPC"
  default     = "10.0.0.0/16"
  # Missing type specification
}''',
                '''variable "enable_monitoring" {
  description = "Enable monitoring for resources"
  default     = true
  # Missing type specification
}'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.004", "IO.006"],
        "configuration": {
            "require_type_specification": True,
            "allow_implicit_types": False
        }
    }
