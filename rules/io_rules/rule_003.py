#!/usr/bin/env python3
"""
IO.003 - Required Variable Declaration Check in terraform.tfvars

This module implements the IO.003 rule which validates that all required variables
(variables without default values) used in resources are declared in the
terraform.tfvars file in the same directory.

Rule Specification:
- Check all variables used in resources within the current directory
- Required variables are those defined in variables.tf without default values
- All required variables used in resources must be declared in terraform.tfvars
- Variables with default values are optional and don't need to be in terraform.tfvars
- Helps ensure all necessary input values are provided for deployment

Examples:
    Valid definition:
        # parameters defined in variables.tf (instance_name is required, flavor_id is optional)
        variable "instance_name" {
          description = "Name of the ECS instance"
          type        = string
          # No default value - this is required
        }

        variable "flavor_id" {
          description = "The flavor ID of the ECS instance"
          type        = string
          default     = "c6.2xlarge.4"  # Has default - optional
        }

        # instance resource using name and flavor_id variables in main.tf
        resource "huaweicloud_compute_instance" "test" {
          name      = var.instance_name  # Uses required variable
          flavor_id = var.flavor_id    # Uses optional variable
          # ...
        }

        # terraform.tfvars must contain:
        instance_name = "my-instance"  # Required because used in resource and no default
        # flavor_id is optional because it has default value

    Invalid definition:
        # variables.tf
        variable "instance_name" {
          description = "Name of the ECS instance"
          type        = string
          # No default - required
        }

        variable "flavor_id" {
          description = "The flavor ID of the ECS instance"
          type        = string
          default     = "c6.2xlarge.4"  # Has default - optional
        }

        # main.tf
        resource "huaweicloud_compute_instance" "test" {
          name      = var.instance_name  # Uses required variable
          flavor_id = var.flavor_id      # Uses optional variable
          # ...
        }

        # terraform.tfvars
        # Missing declaration for required variable instance_name
        flavor_id = "c6.4xlarge.8"  # Optional variable declared (not required)

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, List, Dict, Any, Set


def check_io003_required_variables(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate that all required variables used in resources are declared in terraform.tfvars according to IO.003 rule specifications.

    This function checks if all variables without default values that are used in 
    resources in the current directory are declared in the terraform.tfvars file 
    in the same directory.

    The validation process:
    1. Extract all variable usage from resource blocks in the current file
    2. Find variables.tf in the same directory and identify required variables (no default)
    3. Filter used variables to only include required ones
    4. Check if terraform.tfvars exists and contains declarations for required variables
    5. Report violations for missing required variable declarations

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all variable and resource definitions.

        log_error_func (Callable[[str, str, str], None]): A callback function used
                      to report rule violations. The function should accept three
                      parameters: file_path, rule_id, and error_message.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Example:
        >>> def mock_logger(path, rule, msg):
        ...     print(f"{rule}: {msg}")
        >>> # Assuming resource uses required variable "instance_name"
        >>> # but terraform.tfvars doesn't declare it
        >>> check_io003_required_variables("main.tf", content, mock_logger)
        IO.003: Required variable 'instance_name' used in resources must be declared in terraform.tfvars
    """
    # Get the directory of the current file
    file_dir = os.path.dirname(file_path)
    
    # Find variables.tf in the same directory
    variables_tf_path = os.path.join(file_dir, 'variables.tf')
    if not os.path.exists(variables_tf_path):
        # No variables.tf file, so no variables to check
        return
    
    # Read variables.tf content
    try:
        with open(variables_tf_path, 'r', encoding='utf-8') as f:
            variables_content = f.read()
    except Exception:
        # Can't read variables.tf, skip this check
        return
    
    # Extract all required variables (those without default values)
    all_required_variables = _extract_required_variables(variables_content)
    
    if not all_required_variables:
        # No required variables, nothing to check
        return
    
    # Extract variables used in resources in the current file
    used_variables = _extract_variables_used_in_resources(content)
    
    # Find required variables that are actually used in resources
    required_used_variables = all_required_variables.intersection(used_variables)
    
    if not required_used_variables:
        # No required variables used in resources, nothing to check
        return
    
    # Find terraform.tfvars in the same directory
    tfvars_path = os.path.join(file_dir, 'terraform.tfvars')
    declared_variables = set()
    
    if os.path.exists(tfvars_path):
        try:
            with open(tfvars_path, 'r', encoding='utf-8') as f:
                tfvars_content = f.read()
            declared_variables = _extract_declared_variables(tfvars_content)
        except Exception:
            # Can't read terraform.tfvars
            pass
    
    # Check for missing required variables
    for var_name in required_used_variables:
        if var_name not in declared_variables:
            log_error_func(
                file_path,
                "IO.003",
                f"Required variable '{var_name}' used in resources must be declared in terraform.tfvars"
            )


def _extract_variables_used_in_resources(content: str) -> Set[str]:
    """
    Extract variable names that are used in resource blocks.

    Args:
        content (str): Content of the Terraform file

    Returns:
        Set[str]: Set of variable names used in resources
    """
    used_vars = set()
    clean_content = _remove_comments_for_parsing(content)
    
    # Find all resource blocks
    resource_pattern = r'resource\s+"[^"]+"\s+"[^"]+"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    resource_matches = re.findall(resource_pattern, clean_content, re.DOTALL)
    
    # Find all data source blocks
    data_pattern = r'data\s+"[^"]+"\s+"[^"]+"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    data_matches = re.findall(data_pattern, clean_content, re.DOTALL)
    
    # Combine resource and data source content
    all_blocks = resource_matches + data_matches
    
    # Extract variable references from all blocks
    var_pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
    
    for block_content in all_blocks:
        var_matches = re.findall(var_pattern, block_content)
        used_vars.update(var_matches)
    
    return used_vars


def _extract_required_variables(content: str) -> Set[str]:
    """
    Extract variable names that are required (don't have default values).

    Args:
        content (str): Content of variables.tf file

    Returns:
        Set[str]: Set of required variable names
    """
    required_vars = set()
    clean_content = _remove_comments_for_parsing(content)
    
    # Pattern to match variable blocks with their full content
    var_pattern = r'variable\s+"([^"]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    var_matches = re.findall(var_pattern, clean_content, re.DOTALL)
    
    for var_name, var_body in var_matches:
        # Check if variable has a default value
        if not re.search(r'default\s*=', var_body):
            required_vars.add(var_name)
    
    return required_vars


def _extract_declared_variables(content: str) -> Set[str]:
    """
    Extract variable names that are declared in terraform.tfvars.

    Args:
        content (str): Content of terraform.tfvars file

    Returns:
        Set[str]: Set of declared variable names
    """
    declared_vars = set()
    clean_content = _remove_comments_for_parsing(content)
    
    # Pattern to match variable declarations in tfvars
    # Matches: variable_name = value
    var_decl_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*='
    
    for line in clean_content.split('\n'):
        line = line.strip()
        if line:
            match = re.match(var_decl_pattern, line)
            if match:
                declared_vars.add(match.group(1))
    
    return declared_vars


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from content for parsing, but preserve line structure.

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


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.003 rule.

    Returns:
        dict: A dictionary containing comprehensive rule information
    """
    return {
        "id": "IO.003",
        "name": "Required variable declaration check in terraform.tfvars",
        "description": (
            "Validates that all required variables (variables without default "
            "values) used in resources are declared in the terraform.tfvars file. "
            "This ensures all necessary input values are provided for deployment."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Required variables used in resources must have values provided through "
            "terraform.tfvars to ensure successful deployment. Missing required "
            "variables will cause Terraform to fail during execution."
        ),
        "examples": {
            "valid": [
                '''
# variables.tf
variable "instance_name" {
  description = "Name of the ECS instance"
  type        = string
  # No default - required
}

variable "flavor_id" {
  description = "The flavor ID of the ECS instance"
  type        = string
  default     = "c6.2xlarge.4"  # Has default - optional
}

# main.tf
resource "huaweicloud_compute_instance" "test" {
  name      = var.instance_name  # Uses required variable
  flavor_id = var.flavor_id      # Uses optional variable
  # ...
}

# terraform.tfvars
instance_name = "my-instance"  # Required variable declared
# flavor_id is optional, no need to declare
'''
            ],
            "invalid": [
                '''
# variables.tf
variable "instance_name" {
  description = "Name of the ECS instance"
  type        = string
  # No default - required
}

variable "flavor_id" {
  description = "The flavor ID of the ECS instance"
  type        = string
  default     = "c6.2xlarge.4"  # Has default - optional
}

# main.tf
resource "huaweicloud_compute_instance" "test" {
  name      = var.instance_name  # Uses required variable
  flavor_id = var.flavor_id      # Uses optional variable
  # ...
}

# terraform.tfvars
# Missing declaration for required variable instance_name
flavor_id = "c6.4xlarge.8"  # Optional variable declared (not required)
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.002"],
        "configuration": {
            "check_resource_usage": True,
            "require_tfvars_file": True,
            "ignore_optional_variables": True
        }
    }
