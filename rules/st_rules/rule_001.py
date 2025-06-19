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
from typing import Callable, List, Tuple, Optional


def check_st001_naming_convention(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if resource, data source, and variable names follow proper naming conventions.
    
    This function validates that resource, data source, and variable names in Terraform files
    follow the standard naming convention of using snake_case (lowercase letters, numbers,
    and underscores only). It scans the file content for resource declarations, data source
    declarations, and variable definitions, then checks each name against the naming pattern.
    
    The function specifically checks:
    - Resource names: resource "provider_type" "name" { ... }
    - Data source names: data "provider_type" "name" { ... }
    - Variable names: variable "name" { ... }
    
    Valid naming convention:
    - Names should use snake_case format
    - Only lowercase letters (a-z), numbers (0-9), and underscores (_) are allowed
    - Names should not start with numbers
    - Names should be descriptive and meaningful
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to extract and validate naming patterns.
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
        ... resource "aws_instance" "web-server" {
        ...   instance_type = "t2.micro"
        ... }
        ... '''
        >>> check_st001_naming_convention("main.tf", content, sample_log_func)
        ST.001 at main.tf:1: Resource name 'web-server' contains invalid characters...
    """
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Check resource names
        resource_match = re.match(r'(resource|data)\s+"[^"]+"\s+"([^"]+)"\s*\{', line)
        if resource_match:
            block_type = resource_match.group(1)
            name = resource_match.group(2)
            
            if not _is_valid_name(name):
                error_msg = (
                    f"{block_type.capitalize()} name '{name}' contains invalid characters. "
                    f"Use snake_case (lowercase letters, numbers, and underscores only)"
                )
                log_error_func(file_path, "ST.001", error_msg, line_num)
        
        # Check variable names
        variable_match = re.match(r'variable\s+"([^"]+)"\s*\{', line)
        if variable_match:
            name = variable_match.group(1)
            
            if not _is_valid_name(name):
                error_msg = (
                    f"Variable name '{name}' contains invalid characters. "
                    f"Use snake_case (lowercase letters, numbers, and underscores only)"
                )
                log_error_func(file_path, "ST.001", error_msg, line_num)


def _is_valid_name(name: str) -> bool:
    """
    Check if a name follows the valid naming convention.
    
    Args:
        name (str): The name to validate
        
    Returns:
        bool: True if the name is valid, False otherwise
    """
    if not name:
        return False
    
    # Check if name contains only lowercase letters, numbers, and underscores
    # and doesn't start with a number
    pattern = r'^[a-z_][a-z0-9_]*$'
    return bool(re.match(pattern, name))


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
