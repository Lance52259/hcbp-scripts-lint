#!/usr/bin/env python3
"""
ST.009 - Variable Definition Order Check

This module implements the ST.009 rule which validates that variable definitions
in variables.tf follow the same order as their first usage in sibling *.tf files.

Rule Specification:
- Variable definition order in variables.tf must match first-use order
- First-use is collected from all sibling *.tf files except variables.tf
  (alphabetical file order, then top-to-bottom within each file)
- Provider-related variables are excluded from ordering
- Helps developers understand variable dependencies and usage patterns

Examples:
    Valid ordering (variables.tf matches main.tf usage order):
        # main.tf uses variables in order: flavor_id, performance_type, instance_name
        data "huaweicloud_compute_flavors" "test" {
          count = var.flavor_id == "" ? 1 : 0

          performance_type = var.performance_type
        }

        resource "huaweicloud_compute_instance" "test" {
          name       = var.instance_name
          flavor_id  = try(data.huaweicloud_compute_flavors.test.flavors[0].id, var.flavor_id)
        }

        # variables.tf defines variables in same order
        variable "flavor_id" {
          description = "The flavor ID of the ECS instance"
          type        = string
          default     = ""
        }

        variable "performance_type" {
          description = "The performance type of the ECS instance"
          type        = string
          default     = "normal"
        }
        
        variable "instance_name" {
          description = "The name of the ECS instance"
          type        = string
        }

    Invalid ordering (variables.tf order doesn't match main.tf usage):
        # main.tf uses variables in order: flavor_id, performance_type, instance_name
        # But variables.tf defines them in different order
        data "huaweicloud_compute_flavors" "test" {
          count = var.flavor_id == "" ? 1 : 0

          performance_type = var.performance_type
        }

        resource "huaweicloud_compute_instance" "test" {
          name       = var.instance_name
          flavor_id  = try(data.huaweicloud_compute_flavors.test.flavors[0].id, var.flavor_id)
        }

        # variables.tf defines variables in same order
        variable "instance_name" {
          description = "The name of the ECS instance"
          type        = string
        }

        variable "flavor_id" {
          description = "The flavor ID of the ECS instance"
          type        = string
          default     = ""
        }

        variable "performance_type" {
          description = "The performance type of the ECS instance"
          type        = string
          default     = "normal"
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
import glob
from typing import Callable, List, Optional, Set, Tuple

from rules.common.provider_variables import is_provider_related_variable


def check_st009_variable_order(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that variable definition order in variables.tf matches first-use order
    across sibling *.tf files (excluding variables.tf).

    First-use semantics:
    1. Collect sibling ``*.tf`` files sorted by basename (alphabetical)
    2. Skip ``variables.tf`` so validation cross-refs do not drive ordering
    3. Walk each file top-to-bottom; first ``var.<name>`` wins
    4. Compare against definition order in variables.tf

    Args:
        file_path: Path being linted (must be variables.tf to run).
        content: Content of variables.tf.
        log_error_func: Error reporting callback.
    """
    if not file_path.endswith('variables.tf'):
        return

    file_dir = os.path.dirname(file_path)
    usage_order = _get_variable_usage_order_in_directory(file_dir)
    definition_order = _extract_variable_definition_order(content)

    if not usage_order or not definition_order:
        return

    order_errors = _check_order_consistency(usage_order, definition_order)

    for error_msg, line_number in order_errors:
        log_error_func(file_path, "ST.009", error_msg, line_number)


def _get_variable_usage_order_in_directory(directory: str) -> List[str]:
    """
    Collect first-use order of non-provider var.* references.

    Scans sorted sibling *.tf files, excluding variables.tf.
    """
    usage_order: List[str] = []
    seen_variables: Set[str] = set()
    tf_files = sorted(glob.glob(os.path.join(directory, '*.tf')))

    for tf_file in tf_files:
        if os.path.basename(tf_file) == 'variables.tf':
            continue
        try:
            with open(tf_file, 'r', encoding='utf-8') as handle:
                tf_content = handle.read()
        except OSError:
            continue
        _append_variable_usage_order(tf_content, usage_order, seen_variables)

    return usage_order


def _append_variable_usage_order(
    content: str,
    usage_order: List[str],
    seen_variables: Set[str],
) -> None:
    """Append newly seen non-provider var.* names from *content* into *usage_order*."""
    var_pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
    for match in re.finditer(var_pattern, content):
        var_name = match.group(1)
        if var_name not in seen_variables and not is_provider_related_variable(var_name):
            usage_order.append(var_name)
            seen_variables.add(var_name)


def _extract_variable_usage_order(tf_content: str) -> List[str]:
    """
    Extract first-use order of variable references from a single .tf file content.

    Excludes shared provider-related variables from ordering.
    """
    usage_order: List[str] = []
    seen_variables: Set[str] = set()
    _append_variable_usage_order(tf_content, usage_order, seen_variables)

    return usage_order


def _extract_variable_definition_order(variables_tf_content: str) -> List[Tuple[str, int]]:
    """
    Extract the order of variable definitions from variables.tf content.

    Excludes shared provider-related variables from ordering.

    Args:
        variables_tf_content (str): Content of variables.tf file

    Returns:
        List[Tuple[str, int]]: List of (variable_name, line_number) tuples in definition order (excluding provider variables)
    """
    definition_order = []
    lines = variables_tf_content.split('\n')

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        # Match variable definitions - support quoted, single-quoted, and unquoted syntax
        var_match = re.match(r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        if var_match:
            # Extract variable name from quoted, single-quoted, or unquoted group
            var_name = var_match.group(1) if var_match.group(1) else (var_match.group(2) if var_match.group(2) else var_match.group(3))
            if not is_provider_related_variable(var_name):
                definition_order.append((var_name, line_num))

    return definition_order


def _check_order_consistency(
    usage_order: List[str],
    definition_order: List[Tuple[str, int]],
) -> List[Tuple[str, int]]:
    """
    Check if variable definition order matches usage order.

    Args:
        usage_order (List[str]): Variables in first-use order across sibling *.tf files
        definition_order (List[Tuple[str, int]]): Variables in definition order with line numbers

    Returns:
        List[Tuple[str, int]]: List of (error_message, line_number) for the first mismatch
    """
    errors: List[Tuple[str, int]] = []

    # Extract just the variable names from definition order
    defined_vars = [var_name for var_name, _ in definition_order]
    definition_lines = {var_name: line_num for var_name, line_num in definition_order}

    # Find variables that are both used and defined
    common_vars = [var for var in usage_order if var in defined_vars]

    if len(common_vars) < 2:
        return errors  # Need at least 2 variables to check ordering

    # Check if the order matches
    expected_order = common_vars
    actual_order = [var for var in defined_vars if var in common_vars]

    if expected_order != actual_order:
        # Find the first variable that's out of order
        for i, expected_var in enumerate(expected_order):
            if i < len(actual_order) and actual_order[i] != expected_var:
                mismatched = actual_order[i]
                errors.append(
                    (
                        f"Variable '{mismatched}' is not in the correct order. "
                        f"Expected order: {', '.join(expected_order)}. Current order: {', '.join(actual_order)}",
                        definition_lines.get(mismatched),
                    )
                )
                break

    return errors


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.009 rule.

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
        Variable definition order consistency check
    """
    return {
        "id": "ST.009",
        "name": "Variable definition order consistency check",
        "description": (
            "Validates that variable definitions in variables.tf follow the same "
            "order as their first usage across sibling *.tf files (excluding "
            "variables.tf). First-use order is determined by alphabetical file "
            "basename order, then top-to-bottom within each file. Provider-related "
            "variables (region / region_*, access_key, secret_key, domain_name, "
            "tenant/user/project identifiers) are excluded from ordering validation."
        ),
        "category": "Style/Format",
        "severity": "warning",
        "rationale": (
            "Maintaining consistent ordering between variable definitions and usage "
            "improves code readability and helps developers understand the logical "
            "flow of variable dependencies. When variables are defined in the same "
            "order they are used, it becomes easier to trace variable relationships "
            "and understand the configuration structure. Provider variables are excluded "
            "because they follow different patterns and should not interfere with "
            "business logic variable ordering."
        ),
        "examples": {
            "valid": [
                '''
# main.tf uses variables in order: flavor_id, performance_type, instance_name
# (access_key, secret_key, region_name are excluded from ordering)
data "huaweicloud_compute_flavors" "test" {
  count = var.flavor_id == "" ? 1 : 0

  performance_type = var.performance_type
}

resource "huaweicloud_compute_instance" "test" {
  name       = var.instance_name
  flavor_id  = try(data.huaweicloud_compute_flavors.test.flavors[0].id, var.flavor_id)
}

# variables.tf defines variables in same order (provider variables can be anywhere)
variable "region_name" {
  description = "The region where resources are located"
  type        = string
}

variable "access_key" {
  description = "The access key of the IAM user"
  type        = string
}

variable "flavor_id" {
  description = "The flavor ID of the ECS instance"
  type        = string
  default     = ""
}

variable "performance_type" {
  description = "The performance type of the ECS instance"
  type        = string
  default     = "normal"
}
        
variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
}

variable "secret_key" {
  description = "The secret key of the IAM user"
  type        = string
}
'''
            ],
            "invalid": [
                '''
# main.tf uses variables in order: flavor_id, performance_type, instance_name
# But variables.tf defines them in different order (excluding provider variables)
data "huaweicloud_compute_flavors" "test" {
  count = var.flavor_id == "" ? 1 : 0

  performance_type = var.performance_type
}

resource "huaweicloud_compute_instance" "test" {
  name       = var.instance_name
  flavor_id  = try(data.huaweicloud_compute_flavors.test.flavors[0].id, var.flavor_id)
}

# variables.tf defines variables in wrong order (provider variables excluded from check)
variable "region_name" {
  description = "The region where resources are located"
  type        = string
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
}

variable "flavor_id" {
  description = "The flavor ID of the ECS instance"
  type        = string
  default     = ""
}

variable "performance_type" {
  description = "The performance type of the ECS instance"
  type        = string
  default     = "normal"
}

variable "access_key" {
  description = "The access key of the IAM user"
  type        = string
}

variable "secret_key" {
  description = "The secret key of the IAM user"
  type        = string
}
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.003", "IO.009"],
        "configuration": {
            "check_usage_order": True,
            "scan_sibling_tf_files": True,
            "exclude_variables_tf_from_usage": True,
            "usage_file_sort": "alphabetical_basename",
            "require_main_tf": False,
            "ignore_unused_variables": False,
            "excluded_provider_variables": "shared via rules.common.provider_variables",
        }
    }
