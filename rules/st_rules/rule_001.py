#!/usr/bin/env python3
"""
ST.001 - Resource and Data Source Instance Naming Convention Check

This module implements the ST.001 rule which validates that all resource and
data source blocks use "test" as their instance name. This ensures consistency
in example code and test environments.

Rule Specification:
- All resource blocks must use "test" as the instance name
- All data source blocks must use "test" as the instance name
- This applies to the second quoted string in resource/data declarations
- Helps maintain consistency in example and test code

Examples:
    Valid declarations:
        data "huaweicloud_availability_zones" "test" {
          ...
        }
        resource "huaweicloud_compute_instance" "test" {
          ...
        }

    Invalid declarations:
        data "huaweicloud_availability_zones" "my_az" {
          ...
        }
        resource "huaweicloud_compute_instance" "my_instance" {
          ...
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple


def check_st001_naming_convention(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate resource and data source naming convention according to ST.001 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all data sources and resources use 'test' as their instance name. This
    ensures consistency across Terraform configurations and follows established
    naming conventions.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all data source definitions
    3. Extract all resource definitions
    4. Validate each instance name against the 'test' standard
    5. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all resource and data source definitions.

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
        >>> content = 'data "huaweicloud_availability_zones" "test" {}\\nresource "huaweicloud_compute_instance" "my_instance" {}'
        >>> errors = []
        >>> def log_func(path, rule, msg): errors.append(msg)
        >>> check_st001_naming_convention("test.tf", content, log_func)
        >>> len(errors)
        1
    """
    clean_content = _remove_comments_for_parsing(content)

    # Check data sources
    data_sources = _extract_data_sources(clean_content)
    for data_type, instance_name in data_sources:
        if instance_name != 'test':
            log_error_func(
                file_path,
                "ST.001",
                f"Data source '{data_type}' instance name '{instance_name}' should be 'test'"
            )

    # Check resources
    resources = _extract_resources(clean_content)
    for resource_type, instance_name in resources:
        if instance_name != 'test':
            log_error_func(
                file_path,
                "ST.001",
                f"Resource '{resource_type}' instance name '{instance_name}' should be 'test'"
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


def _extract_data_sources(content: str) -> List[Tuple[str, str]]:
    """
    Extract data source definitions from content.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[Tuple[str, str]]: List of (data_type, instance_name) tuples
    """
    # Match data "type" "name" { ... }
    pattern = r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{'
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches


def _extract_resources(content: str) -> List[Tuple[str, str]]:
    """
    Extract resource definitions from content.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[Tuple[str, str]]: List of (resource_type, instance_name) tuples
    """
    # Match resource "type" "name" { ... }
    pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.001 rule.

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
        Resource and data source naming convention check
    """
    return {
        "id": "ST.001",
        "name": "Resource and data source naming convention check",
        "description": (
            "Validates that all data source and resource instance names follow "
            "the standard naming convention of using 'test' as the instance name. "
            "This ensures consistency across Terraform configurations and makes "
            "code more predictable and maintainable."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Consistent naming conventions improve code readability and "
            "maintainability. Using a standard instance name like 'test' "
            "makes Terraform configurations more predictable and easier to "
            "understand across different projects."
        ),
        "examples": {
            "valid": [
                '''
data "huaweicloud_availability_zones" "test" {
  ...
}
''',
                '''
resource "huaweicloud_compute_instance" "test" {
  ...
}
'''
            ],
            "invalid": [
                '''
data "huaweicloud_availability_zones" "my_az" {
  ...
}
''',
                '''
resource "huaweicloud_compute_instance" "my_instance" {
  ...
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal"
    }
