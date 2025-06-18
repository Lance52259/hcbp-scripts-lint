#!/usr/bin/env python3
"""
IO.003 - Required Variable Declaration Check in terraform.tfvars

This module implements the IO.003 rule which validates that all required variables
(variables without default values) are declared with values in the terraform.tfvars
file in the same directory.

Rule Specification:
- Check all variables defined in the current file
- Required variables are those without default values
- All required variables must be declared in terraform.tfvars
- Variables with default values are optional and don't need to be in terraform.tfvars
- Report each missing variable declaration individually with precise line numbers
- Helps ensure all necessary input values are provided for deployment

Examples:
    Valid definition:
        # variables.tf (required variables declared in terraform.tfvars)
        variable "instance_name" {        # Line 2: Required variable
          description = "Name of the ECS instance"
          type        = string
          # No default value - this is required
        }

        variable "flavor_id" {            # Line 8: Optional variable
          description = "The flavor ID of the ECS instance"
          type        = string
          default     = "c6.2xlarge.4"   # Has default - optional
        }

        # terraform.tfvars must contain:
        instance_name = "my-instance"     # Required variable declared
        # flavor_id is optional because it has default value

    Invalid definition:
        # main.tf
        variable "cpu_cores" {            # Line 2: Required variable missing from tfvars
          description = "Number of CPU cores"
          type        = number
          # No default - required but missing from terraform.tfvars
        }

        variable "memory_size" {          # Line 8: Required variable missing from tfvars
          description = "Memory size in GB"
          type        = number
          # No default - required but missing from terraform.tfvars
        }

        variable "flavor_id" {            # Line 14: Optional variable
          description = "The flavor ID"
          type        = string
          default     = "c6.2xlarge.4"   # Has default - optional
        }

        # terraform.tfvars
        # Missing declarations for required variables cpu_cores and memory_size
        flavor_id = "c6.4xlarge.8"       # Optional variable declared (not required)

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, List, Dict, Any, Set, Optional, Tuple


def check_io003_required_variables(file_path: str, content: str, 
                                  log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that all required variables are declared in terraform.tfvars according to IO.003 rule specifications.
    
    This function validates that all required variables (variables without default values)
    defined in the current file are properly declared in the terraform.tfvars file.
    Each missing variable declaration is reported individually with precise line numbers.
    
    The validation process:
    1. Extract all variable definitions from the current file
    2. Identify which variables are required (no default value)
    3. Check if terraform.tfvars exists and read its content
    4. Verify that each required variable is declared in terraform.tfvars
    5. Report violations for each missing variable declaration individually
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to find variable definitions.
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
        >>> # Content with required variable missing from terraform.tfvars
        >>> content = '''
        ... variable "cpu_cores" {
        ...   description = "Number of CPU cores"
        ...   type        = number
        ... }
        ... '''
        >>> check_io003_required_variables("main.tf", content, sample_log_func)
        IO.003 at main.tf:1: Required variable 'cpu_cores' used and must be declared in terraform.tfvars
    """
    # Get the directory of the current file
    file_dir = os.path.dirname(file_path)
    
    # Extract all required variables (those without default values) from current file
    required_variables = _extract_required_variables_with_lines(content)
    
    if not required_variables:
        # No required variables in this file, nothing to check
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
            # Can't read terraform.tfvars, treat as empty
            pass
    
    # Check each required variable for declaration in terraform.tfvars
    for var_name, line_number in required_variables:
        if var_name not in declared_variables:
            log_error_func(
                file_path,
                "IO.003",
                f"Required variable '{var_name}' used and must be declared in terraform.tfvars",
                line_number
            )


def _extract_required_variables_with_lines(content: str) -> List[Tuple[str, int]]:
    """
    Extract variable names and line numbers for variables that are required (don't have default values).

    Args:
        content (str): Content of the Terraform file

    Returns:
        List[Tuple[str, int]]: List of tuples containing (variable_name, line_number)
    """
    required_vars = []
    lines = content.split('\n')
    
    # Pattern to match variable blocks with their full content
    var_pattern = r'variable\s+"([^"]+)"\s*\{'
    
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.search(var_pattern, line)
        if match:
            var_name = match.group(1)
            line_number = i + 1  # Convert to 1-indexed
            
            # Find the end of this variable block
            brace_count = line.count('{') - line.count('}')
            j = i + 1
            var_content = line
            
            while j < len(lines) and brace_count > 0:
                var_content += '\n' + lines[j]
                brace_count += lines[j].count('{') - lines[j].count('}')
                j += 1
            
            # Check if variable has a default value
            if not re.search(r'default\s*=', var_content):
                required_vars.append((var_name, line_number))
            
            i = j
        else:
            i += 1
    
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
            "values) are declared in the terraform.tfvars file. Each missing "
            "variable declaration is reported individually with precise line numbers."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Required variables must have values provided through terraform.tfvars "
            "to ensure successful deployment. Missing required variables will cause "
            "Terraform to fail during execution. Each violation is reported "
            "separately for precise error identification."
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

# terraform.tfvars
instance_name = "my-instance"  # Required variable declared
# flavor_id is optional, no need to declare
'''
            ],
            "invalid": [
                '''
# main.tf
variable "cpu_cores" {            # Line 2: Missing from terraform.tfvars
  description = "Number of CPU cores"
  type        = number
  # No default - required
}

variable "memory_size" {          # Line 8: Missing from terraform.tfvars
  description = "Memory size in GB"
  type        = number
  # No default - required
}

variable "flavor_id" {            # Line 14: Optional
  description = "The flavor ID"
  type        = string
  default     = "c6.2xlarge.4"   # Has default - optional
}

# terraform.tfvars
# Missing declarations for required variables cpu_cores and memory_size
flavor_id = "c6.4xlarge.8"       # Optional variable (not required)

# Expected errors:
# ERROR: main.tf (2): [IO.003] Required variable 'cpu_cores' used and must be declared in terraform.tfvars
# ERROR: main.tf (8): [IO.003] Required variable 'memory_size' used and must be declared in terraform.tfvars
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.002"],
        "configuration": {
            "check_all_required_variables": True,
            "require_tfvars_file": True,
            "report_individual_violations": True
        }
    }
