#!/usr/bin/env python3
"""
ST.002 - Data Source Variable Default Value Check

This module implements the ST.002 rule which validates that all input variables
used in data source blocks are designed as optional parameters, meaning they
must have default values. This ensures data sources can work properly with
minimal configuration while resources can still use required variables.

Rule Specification:
- Only variables used in data source blocks must have default values
- Variables used only in resource blocks are not required to have defaults
- Default values can be null, empty collections, or any appropriate value
- This ensures data sources work properly with minimal configuration

Examples:
    Valid scenario:
        variable "memory_size" {
          description = "The memory size (GB) for queried ECS flavors"
          type        = number
          default     = 8    # Required because used in data source
        }

        data "huaweicloud_compute_flavors" "test" {
          memory_size = var.memory_size
          # ...
        }

        variable "instance_name" {
          description = "The name of the ECS instance"
          type        = string
          default     = "tf_test_instance"
        }

        resource "huaweicloud_compute_instance" "test" {
          name = var.instance_name  # Can use required variable
        }

    Invalid scenario:
        variable "memory_size" {
          description = "The memory size (GB) for queried ECS flavors"
          type        = number
          # Missing default value but used in data source
        }

        data "huaweicloud_compute_flavors" "test" {
          memory_size = var.memory_size    # Uses variable without default
          # ...
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, Dict, Set


def check_st002_variable_defaults(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate that variables used in data sources have default values according to ST.002 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all variables used in data source blocks include a default value. This
    ensures that data sources can work properly with minimal configuration while
    allowing resources to use required variables.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all data source blocks and identify variables used in them
    3. Look for variable definitions in the same directory (variables.tf)
    4. Report violations for variables used in data sources without defaults

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all variable definitions and data source blocks.

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
        >>> content = '''
        ... variable "test" { type = string }
        ... data "huaweicloud_availability_zones" "example" {
        ...   region = var.test
        ... }
        ... '''
        >>> check_st002_variable_defaults("main.tf", content, mock_logger)
        ST.002: Variable 'test' used in data source must have a default value
    """
    clean_content = _remove_comments_for_parsing(content)
    
    # Extract variables used in data sources
    data_source_variables = _extract_data_source_variables(clean_content)
    
    if not data_source_variables:
        # No variables used in data sources, nothing to check
        return
    
    # Get variable definitions from the same directory
    file_dir = os.path.dirname(file_path)
    variable_definitions = _get_variable_definitions_from_directory(file_dir)
    
    # Also check current file for variable definitions
    current_file_variables = _extract_variables(clean_content)
    variable_definitions.update(current_file_variables)
    
    # Check if variables used in data sources have defaults
    for var_name in data_source_variables:
        if var_name in variable_definitions:
            if not variable_definitions[var_name]:
                log_error_func(
                    file_path,
                    "ST.002",
                    f"Variable '{var_name}' used in data source must have a default value"
                )
        else:
            # Variable used but not defined - this might be from modules or other sources
            # We'll report this as a potential issue
            log_error_func(
                file_path,
                "ST.002",
                f"Variable '{var_name}' used in data source is not defined in the current directory"
            )


def _get_variable_definitions_from_directory(directory: str) -> Dict[str, bool]:
    """
    Get variable definitions from variables.tf file in the specified directory.

    Args:
        directory (str): Directory path to search for variables.tf

    Returns:
        Dict[str, bool]: Dictionary mapping variable names to whether they have defaults
    """
    variables = {}
    variables_tf_path = os.path.join(directory, 'variables.tf')
    
    if os.path.exists(variables_tf_path):
        try:
            with open(variables_tf_path, 'r', encoding='utf-8') as f:
                variables_content = f.read()
            clean_content = _remove_comments_for_parsing(variables_content)
            variables = _extract_variables(clean_content)
        except Exception:
            # Can't read variables.tf, return empty dict
            pass
    
    return variables


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


def _extract_data_source_variables(content: str) -> Set[str]:
    """
    Extract variable references from data source blocks.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        Set[str]: Set of variable names used in data sources
    """
    variables_in_data_sources = set()
    
    # Pattern to match data source blocks
    data_pattern = r'data\s+"[^"]+"\s+"[^"]+"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    data_matches = re.findall(data_pattern, content, re.DOTALL)
    
    # Pattern to match variable references
    var_ref_pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
    
    for data_body in data_matches:
        var_matches = re.findall(var_ref_pattern, data_body)
        variables_in_data_sources.update(var_matches)
    
    return variables_in_data_sources


def _extract_variables(content: str) -> Dict[str, bool]:
    """
    Extract variable definitions and check if they have default values.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        Dict[str, bool]: Dictionary mapping variable names to whether they have defaults
    """
    variables = {}
    var_pattern = r'variable\s+"([^"]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    var_matches = re.findall(var_pattern, content, re.DOTALL)

    for var_name, var_body in var_matches:
        has_default = bool(re.search(r'default\s*=', var_body))
        variables[var_name] = has_default

    return variables


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.002 rule.

    This function provides metadata about the rule including its purpose,
    validation criteria, and examples. This information can be used for
    documentation generation, help systems, or configuration interfaces.

    Returns:
        dict: A dictionary containing comprehensive rule information including:
            - id: The unique rule identifier
            - name: Human-readable rule name
            - description: Detailed explanation of what the rule validates
            - category: The rule category (Style/Format)
            - severity: The severity level of violations
            - examples: Dictionary with valid and invalid examples

    Example:
        >>> info = get_rule_description()
        >>> print(info['name'])
        Data source variable default value check
    """
    return {
        "id": "ST.002",
        "name": "Data source variable default value check",
        "description": (
            "Validates that all input variables used in data source blocks have "
            "default values. This ensures data sources can work properly with "
            "minimal configuration while allowing resources to use required "
            "variables. Only variables referenced in data source blocks are "
            "required to have defaults."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Data sources are typically used for discovery and should work with "
            "minimal configuration. Having default values for variables used in "
            "data sources ensures they can function properly even when not all "
            "parameters are explicitly provided. Resources, on the other hand, "
            "may legitimately require certain parameters to be explicitly set."
        ),
        "examples": {
            "valid": [
                '''
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  default     = 8    # Required because used in data source
}

data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size
  # ...
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
  default     = "tf_test_instance"
}

resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name  # Can use required variable
}
'''
            ],
            "invalid": [
                '''
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  # Missing default value but used in data source
}

data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size    # Uses variable without default
  # ...
}
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal"
    }
