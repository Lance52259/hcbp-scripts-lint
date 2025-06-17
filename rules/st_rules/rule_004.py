#!/usr/bin/env python3
"""
ST.004 - Indentation Character Check

This module implements the ST.004 rule which validates that all indentation
in Terraform files uses spaces instead of tabs for consistent formatting
across different editors and environments.

Rule Specification:
- All indentation must use spaces only
- No tabs allowed for indentation
- Mixed indentation (tabs and spaces) is not allowed

Examples:
    Valid indentation:
        variable "instance_name" {
          description = "The name of the instance"
          type        = string
        }

        data "huaweicloud_compute_flavors" "test" {
          performance_type = "normal"
          cpu_core_count   = 4
          memory_size      = 8
        }

        resource "huaweicloud_compute_instance" "test" {
          name               = "demo"
          flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
          security_group_ids = [huaweicloud_networking_secgroup.test.id]
        }

        output "instance_id" {
          description = "The ID of the ECS instance"
          value       = huaweicloud_compute_instance.test.id
        }

    Invalid indentation:
        variable "instance_name" {
        description = "The name of the instance"    # Without space indentation before parameter definition
        type        = string                        # Without space indentation before parameter definition
        default     = "demo"                        # Without space indentation before parameter definition
        }

        data "huaweicloud_compute_flavors" "test" {
        	performance_type = "normal"    # Tab character used
        	cpu_core_count   = 4           # Tab character used
        	memory_size      = 8           # Tab character used
        }

        resource "huaweicloud_compute_instance" "test" {
          # Both tab and spaces are used for indentation
        	name             = "demo"    # Tab character used
          flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
          security_group_ids = [huaweicloud_networking_secgroup.test.id]
        }

        output "instance_id" {
          # Only some spaces are used for indentation
        description = "The ID of the ECS instance"
          value       = huaweicloud_compute_instance.test.id
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable


def check_st004_indentation_character(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate indentation character usage according to ST.004 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all indentation uses spaces instead of tabs. This ensures consistent
    formatting across different editors and development environments.

    The validation process:
    1. Split content into individual lines
    2. Check each line for leading tab characters
    3. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all lines that may contain indentation.

        log_error_func (Callable[[str, str, str], None]): A callback function used
                      to report rule violations. The function should accept three
                      parameters: file_path, rule_id, and error_message.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    """
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        if line.strip() == '':
            continue
            
        leading_whitespace = _get_leading_whitespace(line)
        
        if '\t' in leading_whitespace:
            tab_count = leading_whitespace.count('\t')
            space_count = leading_whitespace.count(' ')
            
            if tab_count > 0 and space_count > 0:
                log_error_func(
                    file_path,
                    "ST.004",
                    f"Line {line_num}: Mixed indentation detected (tabs and spaces). "
                    f"Use spaces only for consistent formatting"
                )
            elif tab_count > 0:
                log_error_func(
                    file_path,
                    "ST.004",
                    f"Line {line_num}: Tab character used for indentation. "
                    f"Use spaces instead for consistent formatting"
                )


def _get_leading_whitespace(line: str) -> str:
    """
    Extract leading whitespace characters from a line.

    Args:
        line (str): The line to analyze

    Returns:
        str: The leading whitespace characters
    """
    match = re.match(r'^(\s*)', line)
    return match.group(1) if match else ''


def _analyze_indentation_pattern(content: str) -> dict:
    """
    Analyze the indentation pattern in the content.

    Args:
        content (str): The file content to analyze

    Returns:
        dict: Analysis results including counts and recommendations
    """
    lines = content.split('\n')
    tab_lines = []
    space_lines = []
    mixed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        if line.strip() == '':
            continue
            
        leading_whitespace = _get_leading_whitespace(line)
        
        if '\t' in leading_whitespace and ' ' in leading_whitespace:
            mixed_lines.append(line_num)
        elif '\t' in leading_whitespace:
            tab_lines.append(line_num)
        elif ' ' in leading_whitespace:
            space_lines.append(line_num)
    
    return {
        'tab_lines': tab_lines,
        'space_lines': space_lines,
        'mixed_lines': mixed_lines,
        'total_indented_lines': len(tab_lines) + len(space_lines) + len(mixed_lines),
        'recommendation': _get_indentation_recommendation(tab_lines, space_lines, mixed_lines)
    }


def _get_indentation_recommendation(tab_lines: list, space_lines: list, mixed_lines: list) -> str:
    """
    Generate indentation recommendation based on analysis.

    Args:
        tab_lines (list): Lines using tab indentation
        space_lines (list): Lines using space indentation
        mixed_lines (list): Lines using mixed indentation

    Returns:
        str: Recommendation message
    """
    if mixed_lines:
        return "Convert all indentation to spaces for consistency"
    elif tab_lines and not space_lines:
        return "Convert all tab indentation to spaces"
    elif tab_lines and space_lines:
        return "Mixed indentation detected - standardize on spaces"
    else:
        return "Indentation is consistent (spaces only)"


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.004 rule.

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
        Indentation character check
    """
    return {
        "id": "ST.004",
        "name": "Indentation character check",
        "description": (
            "Validates that all indentation in Terraform files uses spaces "
            "instead of tabs for consistent formatting across different "
            "editors and environments. This rule ensures code readability "
            "and prevents formatting issues in version control systems."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Using spaces for indentation ensures consistent appearance across "
            "different editors, IDEs, and environments. Tab characters can "
            "render differently depending on editor settings, leading to "
            "inconsistent code formatting and potential readability issues."
        ),
        "examples": {
            "valid": [
                '''
variable "instance_name" {
  description = "The name of the instance"
  type        = string
}

data "huaweicloud_compute_flavors" "test" {
  performance_type = "normal"
  cpu_core_count   = 4
  memory_size      = 8
}

resource "huaweicloud_compute_instance" "test" {
  name               = "demo"
  flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
  security_group_ids = [huaweicloud_networking_secgroup.test.id]
}

output "instance_id" {
  description = "The ID of the ECS instance"
  value       = huaweicloud_compute_instance.test.id
}
'''
            ],
            "invalid": [
                '''
variable "instance_name" {
description = "The name of the instance"    # Without space indentation before parameter definition
type        = string                        # Without space indentation before parameter definition
default     = "demo"                        # Without space indentation before parameter definition
}

data "huaweicloud_compute_flavors" "test" {
	performance_type = "normal"    # Tab character used
	cpu_core_count   = 4           # Tab character used
	memory_size      = 8           # Tab character used
}

resource "huaweicloud_compute_instance" "test" {
  # Both tab and spaces are used for indentation
	name             = "demo"    # Tab character used
  flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
  security_group_ids = [huaweicloud_networking_secgroup.test.id]
}

output "instance_id" {
  # Only some spaces are used for indentation
description = "The ID of the ECS instance"
  value       = huaweicloud_compute_instance.test.id
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.005"],
        "configuration": {
            "indent_size": 2,
            "indent_type": "spaces"
        }
    }
