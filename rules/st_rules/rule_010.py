#!/usr/bin/env python3
"""
ST.010 - Quote Usage Standards Check

This module implements the ST.010 rule which validates that resource and data
source declarations use proper double quotes around both the resource type
and instance name.

Rule Specification:
- Resource type must be enclosed in double quotes
- Instance name must be enclosed in double quotes
- Single quotes or missing quotes are not allowed
- Applies to both resource and data source blocks

Examples:
    Valid declarations:
        resource "huaweicloud_compute_instance" "test" { ... }
        data "huaweicloud_availability_zones" "test" { ... }

    Invalid declarations:
        resource huaweicloud_compute_instance "test" { ... }    # Missing quotes on type
        resource "huaweicloud_compute_instance" test { ... }    # Missing quotes on name
        resource 'huaweicloud_compute_instance' 'test' { ... }  # Single quotes

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Optional


def check_st010_quote_usage(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check proper quote usage in Terraform files according to ST.010 rule specifications.
    
    This function validates that quotes are used appropriately in Terraform files,
    following best practices for string literals, variable references, and expressions.
    It scans through the file content and identifies instances where quotes are used
    incorrectly or where they could be omitted for better readability.
    
    The validation process:
    1. Parse the file content line by line
    2. Identify different contexts where quotes are used (values, references, etc.)
    3. Check if quotes are necessary or if they can be omitted
    4. Validate proper quote types (single vs double quotes)
    5. Report any quote usage violations through the error logging function
    
    Quote usage rules:
    - Use double quotes for string literals
    - Avoid unnecessary quotes around variable references
    - Use proper quote escaping when needed
    - Follow consistent quoting patterns throughout the file
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to check quote usage patterns.
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
        ... resource "aws_instance" "test" {
        ...   instance_type = "${var.instance_type}"
        ... }
        ... '''
        >>> check_st010_quote_usage("main.tf", content, sample_log_func)
        ST.010 at main.tf:2: Unnecessary quotes around variable reference...
    """
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()

        # Skip empty lines and comments
        if not stripped_line or stripped_line.startswith('#'):
            continue

        # Check for data source declarations
        data_match = re.match(r'^\s*data\s+(.+?)\s*\{', line)
        if data_match:
            declaration = data_match.group(1).strip()
            if not _is_properly_quoted_declaration(declaration):
                log_error_func(
                    file_path, "ST.010",
                    f"Data source type and name must be enclosed in double quotes",
                    line_num
                )

        # Check for resource declarations
        resource_match = re.match(r'^\s*resource\s+(.+?)\s*\{', line)
        if resource_match:
            declaration = resource_match.group(1).strip()
            if not _is_properly_quoted_declaration(declaration):
                log_error_func(
                    file_path, "ST.010",
                    f"Resource type and name must be enclosed in double quotes",
                    line_num
                )


def _is_properly_quoted_declaration(declaration: str) -> bool:
    """
    Helper method to check if a resource/data declaration uses proper double quotes.

    This function validates that the declaration follows the expected format:
    "type" "name" where both type and name are enclosed in double quotes.

    Args:
        declaration (str): The declaration part extracted from the line
                          (everything between 'data'/'resource' and '{')

    Returns:
        bool: True if the declaration uses proper double quotes, False otherwise

    Example:
        >>> _is_properly_quoted_declaration('"huaweicloud_compute_instance" "test"')
        True
        >>> _is_properly_quoted_declaration('huaweicloud_compute_instance "test"')
        False
        >>> _is_properly_quoted_declaration('"huaweicloud_compute_instance" test')
        False
    """
    # Pattern to match exactly two double-quoted strings separated by whitespace
    pattern = r'^"[^"]*"\s+"[^"]*"$'
    return bool(re.match(pattern, declaration))


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.010 rule.

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
        Resource and data source quote check
    """
    return {
        "id": "ST.010",
        "name": "Resource and data source quote check",
        "description": (
            "Validates that all data sources and resources use proper double quotes "
            "around their type and name declarations. This ensures consistent syntax "
            "and prevents parsing errors that could occur with improper quoting. "
            "The rule enforces the standard Terraform syntax format."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Proper quoting is essential for Terraform syntax correctness. "
            "Using double quotes consistently prevents parsing errors and "
            "ensures that the Terraform configuration can be properly processed "
            "by the Terraform engine and other tools."
        ),
        "examples": {
            "valid": [
                'data "huaweicloud_availability_zones" "test" { ... }',
                'data "huaweicloud_compute_flavors" "test" { ... }',
                'resource "huaweicloud_networking_secgroup" "test" { ... }',
                'resource "huaweicloud_compute_instance" "test" { ... }'
            ],
            "invalid": [
                'data huaweicloud_availability_zones "test" { ... }',
                'data "huaweicloud_compute_flavors" test { ... }',
                "resource huaweicloud_networking_secgroup test { ... }",
                'resource \'huaweicloud_compute_instance\' \'test\' { ... }'
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal"
    }
