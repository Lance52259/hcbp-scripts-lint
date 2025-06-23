#!/usr/bin/env python3
"""
ST.009 - Variable Definition Order Check

This module implements the ST.009 rule which validates that variable definitions
in variables.tf follow the same order as their usage in main.tf.

Rule Specification:
- Variable definition order in variables.tf must match usage order in main.tf
- The first variable used in main.tf should be defined first in variables.tf
- This ensures logical consistency between variable definitions and usage
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
from typing import Callable, List, Dict, Optional, Tuple


def check_st009_variable_order(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that variable definition order in variables.tf matches usage order in main.tf.

    This function checks that the order of variable definitions in variables.tf
    corresponds to the order in which variables are first used in main.tf.
    This ensures logical consistency and helps developers understand variable
    dependencies and usage patterns.

    The validation process:
    1. If checking variables.tf, find the corresponding main.tf in the same directory
    2. Extract variable usage order from main.tf
    3. Extract variable definition order from variables.tf
    4. Compare the orders and report any inconsistencies

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This should be the content of variables.tf.

        log_error_func (Callable[[str, str, str, Optional[int]], None]): A callback function used
                      to report rule violations. The function should accept four
                      parameters: file_path, rule_id, error_message, and optional line_number.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    """
    # Only check variables.tf files
    if not file_path.endswith('variables.tf'):
        return
    
    # Get the directory containing variables.tf
    file_dir = os.path.dirname(file_path)
    main_tf_path = os.path.join(file_dir, 'main.tf')
    
    # Check if main.tf exists
    if not os.path.exists(main_tf_path):
        return  # No main.tf to compare against
    
    try:
        with open(main_tf_path, 'r', encoding='utf-8') as f:
            main_tf_content = f.read()
    except Exception:
        return  # Can't read main.tf
    
    # Extract variable usage order from main.tf
    usage_order = _extract_variable_usage_order(main_tf_content)
    
    # Extract variable definition order from variables.tf
    definition_order = _extract_variable_definition_order(content)
    
    if not usage_order or not definition_order:
        return  # No variables to check
    
    # Check order consistency
    order_errors = _check_order_consistency(usage_order, definition_order)
    
    for error_msg in order_errors:
        log_error_func(file_path, "ST.009", error_msg, None)


def _extract_variable_usage_order(main_tf_content: str) -> List[str]:
    """
    Extract the order of variable usage from main.tf content.

    Args:
        main_tf_content (str): Content of main.tf file

    Returns:
        List[str]: List of variable names in order of first usage
    """
    usage_order = []
    seen_variables = set()
    
    # Find all variable references in order
    var_pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
    matches = re.finditer(var_pattern, main_tf_content)
    
    for match in matches:
        var_name = match.group(1)
        if var_name not in seen_variables:
            usage_order.append(var_name)
            seen_variables.add(var_name)
    
    return usage_order


def _extract_variable_definition_order(variables_tf_content: str) -> List[Tuple[str, int]]:
    """
    Extract the order of variable definitions from variables.tf content.

    Args:
        variables_tf_content (str): Content of variables.tf file

    Returns:
        List[Tuple[str, int]]: List of (variable_name, line_number) tuples in definition order
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
            definition_order.append((var_name, line_num))
    
    return definition_order


def _check_order_consistency(usage_order: List[str], definition_order: List[Tuple[str, int]]) -> List[str]:
    """
    Check if variable definition order matches usage order.

    Args:
        usage_order (List[str]): Variables in order of usage in main.tf
        definition_order (List[Tuple[str, int]]): Variables in definition order with line numbers

    Returns:
        List[str]: List of error messages
    """
    errors = []
    
    # Extract just the variable names from definition order
    defined_vars = [var_name for var_name, _ in definition_order]
    
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
                errors.append(
                    f"Variable '{actual_order[i]}' is not in the correct order. "
                    f"Expected order: {', '.join(expected_order)}. Current order: {', '.join(actual_order)}"
                )
                break
    
    return errors


def _analyze_variable_usage_patterns(main_tf_content: str, variables_tf_content: str) -> dict:
    """
    Analyze variable usage patterns between main.tf and variables.tf.

    Args:
        main_tf_content (str): Content of main.tf
        variables_tf_content (str): Content of variables.tf

    Returns:
        dict: Analysis results including usage statistics
    """
    usage_order = _extract_variable_usage_order(main_tf_content)
    definition_order = _extract_variable_definition_order(variables_tf_content)
    
    defined_vars = [var_name for var_name, _ in definition_order]
    used_vars = set(usage_order)
    defined_vars_set = set(defined_vars)
    
    # Variables used but not defined
    missing_definitions = used_vars - defined_vars_set
    
    # Variables defined but not used
    unused_definitions = defined_vars_set - used_vars
    
    # Variables in correct order
    common_vars = [var for var in usage_order if var in defined_vars]
    actual_order = [var for var in defined_vars if var in common_vars]
    correct_order = common_vars == actual_order
    
    return {
        'total_variables_used': len(usage_order),
        'total_variables_defined': len(defined_vars),
        'common_variables': len(common_vars),
        'missing_definitions': list(missing_definitions),
        'unused_definitions': list(unused_definitions),
        'correct_order': correct_order,
        'expected_order': common_vars,
        'actual_order': actual_order,
        'usage_order': usage_order,
        'definition_order': [var_name for var_name, _ in definition_order]
    }


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
            "order as their usage in main.tf. This ensures logical consistency "
            "between variable definitions and their usage patterns, making it "
            "easier for developers to understand variable dependencies and relationships."
        ),
        "category": "Style/Format",
        "severity": "warning",
        "rationale": (
            "Maintaining consistent ordering between variable definitions and usage "
            "improves code readability and helps developers understand the logical "
            "flow of variable dependencies. When variables are defined in the same "
            "order they are used, it becomes easier to trace variable relationships "
            "and understand the configuration structure."
        ),
        "examples": {
            "valid": [
                '''
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
'''
            ],
            "invalid": [
                '''
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
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.003"],
        "configuration": {
            "check_usage_order": True,
            "require_main_tf": True,
            "ignore_unused_variables": False
        }
    }

def _extract_assignment_blocks(content: str) -> List[Dict]:
    """
    Extract assignment blocks and their parameter assignments.
    """
    blocks = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Match different types of blocks - support quoted, single-quoted, and unquoted syntax
        block_patterns = [
            r'(resource|data)\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{',  # resource/data
            r'(variable|output)\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{',  # variable/output
            r'(provider|terraform|locals)\s*\{',  # provider/terraform/locals
        ]
        
        matched = False
        for pattern in block_patterns:
            block_match = re.match(pattern, line)
            if block_match:
                matched = True
                block_type = block_match.group(1)
                
                if block_type in ['resource', 'data']:
                    # Extract resource/data type and name
                    type_name = (block_match.group(2) if block_match.group(2) else 
                                (block_match.group(3) if block_match.group(3) else block_match.group(4)))
                    instance_name = (block_match.group(5) if block_match.group(5) else 
                                   (block_match.group(6) if block_match.group(6) else block_match.group(7)))
                    block_name = f'{block_type} "{type_name}" "{instance_name}"'
                elif block_type in ['variable', 'output']:
                    # Extract variable/output name
                    name = (block_match.group(2) if block_match.group(2) else 
                           (block_match.group(3) if block_match.group(3) else block_match.group(4)))
                    block_name = f'{block_type} "{name}"'
                else:
                    block_name = block_type
                
                # Find all assignments within this block
                assignments = _extract_assignments_from_block(lines, i)
                
                # Find the end of the block
                brace_count = line.count('{') - line.count('}')
                j = i + 1
                while j < len(lines) and brace_count > 0:
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    j += 1
                
                blocks.append({
                    'name': block_name,
                    'start_line': i + 1,
                    'end_line': j,
                    'assignments': assignments
                })
                
                i = j
                break
        
        if not matched:
            i += 1
    
    return blocks
