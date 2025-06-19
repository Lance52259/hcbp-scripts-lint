#!/usr/bin/env python3
"""
IO.006 - Variable Description Check

This module implements the IO.006 rule which validates that all input variable
definitions include non-empty description fields. This ensures proper
documentation and helps users understand variable purposes and expected values.

Rule Specification:
- All variable definitions must include a description field
- Description fields must not be empty or contain only whitespace
- Helps improve module documentation and usability

Examples:
    Valid declarations:
        variable "instance_name" {
          description = "Name of the ECS instance"
          type        = string
        }

        variable "flavor_id" {
          description = "The flavor ID of the ECS instance"
          type        = string
          default     = "c6.2xlarge.4"
        }

    Invalid declarations:
        variable "instance_name" {
          type = string
          # Missing description
        }

        variable "flavor_id" {
          description = ""  # Empty description
          type        = string
        }

        variable "region" {
          description = "   "  # Whitespace only description
          type        = string
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Dict, Any, Optional


def check_io006_variable_description(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that all variables have meaningful descriptions according to IO.006 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all variable definitions include description fields with meaningful content.
    Descriptions help document the purpose and usage of variables for better code
    maintainability and understanding.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all variable definitions from the file
    3. Check if each variable has a description field
    4. Validate that descriptions are meaningful (not empty or placeholder text)
    5. Report violations through the error logging function

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
        ...   type = string
        ... }
        ... '''
        >>> check_io006_variable_description("variables.tf", content, mock_logger)
        IO.006: Variable 'example' is missing a description
    """
    variables = _extract_variables(content)
    
    for variable in variables:
        if not variable['has_description']:
            log_error_func(
                file_path,
                "IO.006",
                f"Variable '{variable['name']}' must include a description field",
                variable.get('line_number')
            )
        elif variable['description_empty']:
            log_error_func(
                file_path,
                "IO.006",
                f"Variable '{variable['name']}' has an empty description field",
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

    # Pattern to match variable blocks with their full content
    variable_pattern = r'variable\s+"([^"]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    variable_matches = re.findall(variable_pattern, clean_content, re.DOTALL)

    for variable_name, variable_body in variable_matches:
        # Check for description field
        description_match = re.search(r'description\s*=\s*"([^"]*)"', variable_body)
        has_description = description_match is not None
        
        # Check if description is empty or whitespace only
        description_empty = False
        if has_description:
            description_value = description_match.group(1).strip()
            description_empty = len(description_value) == 0
        
        variable_info = {
            'name': variable_name,
            'has_description': has_description,
            'description_empty': description_empty,
            'has_type': bool(re.search(r'type\s*=', variable_body)),
            'has_default': bool(re.search(r'default\s*=', variable_body)),
            'body': variable_body.strip(),
            'line_number': variable_matches.index((variable_name, variable_body)) + 1
        }
        variables.append(variable_info)

    return variables


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.006 rule.

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
        Variable description check
    """
    return {
        "id": "IO.006",
        "name": "Variable description check",
        "description": (
            "Validates that all input variable definitions include non-empty "
            "description fields. This ensures proper documentation and helps "
            "users understand variable purposes and expected values."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Description fields in variable definitions are essential for "
            "module documentation and usability. They help users understand "
            "what each variable represents, what values are expected, and how "
            "the variable affects the configuration."
        ),
        "examples": {
            "valid": [
                '''variable "instance_name" {
  description = "Name of the ECS instance"
  type        = string
}''',
                '''variable "flavor_id" {
  description = "The flavor ID of the ECS instance"
  type        = string
  default     = "c6.2xlarge.4"
}''',
                '''variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}'''
            ],
            "invalid": [
                '''variable "instance_name" {
  type = string
  # Missing description
}''',
                '''variable "flavor_id" {
  description = ""  # Empty description
  type        = string
}''',
                '''variable "region" {
  description = "   "  # Whitespace only description
  type        = string
}'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.002", "IO.003"],
        "configuration": {
            "check_empty_descriptions": True,
            "allow_whitespace_only": False
        }
    }
