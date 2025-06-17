#!/usr/bin/env python3
"""
IO.002 - Output Definition File Organization Check

This module implements the IO.002 rule which checks that all output variables
(if any) in TF scripts within each directory are defined in the outputs.tf file
in the same directory level.

Rule Specification:
- All output definitions must be defined in the outputs.tf file in the same directory
- Output definitions in other TF files will be flagged as violations
- Helps maintain consistent project structure and organization
- Only applies when output definitions exist in the directory

Examples:
    Valid organization:
        # outputs.tf
        output "instance_id" {
          description = "The ID of the created ECS instance"
          value       = huaweicloud_compute_instance.test.id
        }

    Invalid organization:
        # main.tf (should not contain output definitions)
        output "instance_id" {
          description = "The ID of the created ECS instance"
          value       = huaweicloud_compute_instance.test.id
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, List, Dict, Any


def check_io002_output_file_location(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate that all output definitions are located in outputs.tf file according to IO.002 rule specifications.

    This function scans through the provided Terraform file content and validates
    that output definitions are properly organized in the outputs.tf file.
    This ensures consistent project structure and organization following Terraform
    best practices.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all output definitions from the file
    3. Check if non-outputs.tf files contain output definitions
    4. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all output definitions that need to be checked.

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
        >>> content = 'output "test" { value = "example" }'
        >>> check_io002_output_file_location("main.tf", content, mock_logger)
        IO.002: Output 'test' should be defined in outputs.tf, not in main.tf
    """
    outputs = _extract_outputs(content)
    
    # Check if non-outputs.tf files contain output definitions
    if outputs and not file_path.endswith('outputs.tf'):
        for output in outputs:
            log_error_func(
                file_path,
                "IO.002",
                f"Output '{output['name']}' should be defined in outputs.tf, not in {os.path.basename(file_path)}"
            )
        
        # Provide summary error message
        log_error_func(
            file_path,
            "IO.002",
            f"File {os.path.basename(file_path)} contains {len(outputs)} output definition(s) that should be moved to outputs.tf"
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


def _extract_outputs(content: str) -> List[Dict[str, Any]]:
    """
    Extract output definitions with their metadata from the content.

    This function parses the content to find all output definitions and
    extracts relevant metadata for validation purposes.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[Dict[str, Any]]: List of output definitions with metadata
    """
    outputs = []
    clean_content = _remove_comments_for_parsing(content)

    # Pattern to match output blocks with their full content
    output_pattern = r'output\s+"([^"]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    output_matches = re.findall(output_pattern, clean_content, re.DOTALL)

    for output_name, output_body in output_matches:
        output_info = {
            'name': output_name,
            'has_value': bool(re.search(r'value\s*=', output_body)),
            'has_description': bool(re.search(r'description\s*=', output_body)),
            'has_sensitive': bool(re.search(r'sensitive\s*=', output_body)),
            'body': output_body.strip()
        }
        outputs.append(output_info)

    return outputs


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.002 rule.

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
        Output definition file organization check
    """
    return {
        "id": "IO.002",
        "name": "Output definition file organization check",
        "description": (
            "Validates that all output variables (if any) in TF scripts within each directory "
            "are defined in the outputs.tf file in the same directory level. "
            "This ensures consistent project structure and organization following "
            "Terraform best practices."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Organizing all output definitions in a dedicated outputs.tf file "
            "within the same directory improves project structure consistency, "
            "facilitates centralized output management, and enhances code "
            "maintainability. This follows Terraform community best practices "
            "for project organization."
        ),
        "examples": {
            "valid": [
                '''
# outputs.tf
output "instance_id" {
  description = "The ID of the created ECS instance"
  value       = huaweicloud_compute_instance.test.id
}

# main.tf
resource "huaweicloud_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}''',
                '''# outputs.tf
output "location" {
  description = "Location of the resource group"
  value       = huaweicloud_resource_group.test.location
}'''
            ],
            "invalid": [
                '''# main.tf (should not contain output definitions)
output "resource_group_name" {
  value       = huaweicloud_resource_group.test.id
}''',
                '''# variables.tf (should not contain output definitions)
output "location" {
  description = "Location of the resource group"
  value       = huaweicloud_resource_group.test.location
}'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal"
    }
