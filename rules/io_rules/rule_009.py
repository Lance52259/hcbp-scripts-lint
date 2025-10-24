#!/usr/bin/env python3
"""
IO.009 - Unused Variable Check

This module implements the IO.009 rule which validates that all variables defined
in variables.tf are actually used in the project's Terraform files. This helps
identify unused variables that can be removed to improve code maintainability.

Rule Specification:
- Check all variables defined in variables.tf
- Verify each variable is used in at least one .tf file in the same directory
- Report variables that are defined but never referenced
- Helps maintain clean and efficient variable definitions
- Excludes provider-related variables that might be used externally

Examples:
    Valid definition (all variables used):
        # variables.tf
        variable "instance_name" {        # Used in main.tf
          description = "Name of the ECS instance"
          type        = string
        }

        variable "flavor_id" {            # Used in main.tf  
          description = "The flavor ID of the ECS instance"
          type        = string
          default     = "c6.2xlarge.4"
        }

        # main.tf
        resource "huaweicloud_compute_instance" "test" {
          name      = var.instance_name   # Using instance_name variable
          flavor_id = var.flavor_id       # Using flavor_id variable
        }

    Invalid definition (unused variables):
        # variables.tf
        variable "instance_name" {        # Used in main.tf
          description = "Name of the ECS instance" 
          type        = string
        }

        variable "unused_var" {           # Line 7: Not used anywhere
          description = "This variable is not used"
          type        = string
          default     = "unused"
        }

        variable "another_unused" {       # Line 13: Not used anywhere
          description = "Another unused variable"
          type        = number
          default     = 10
        }

        # main.tf
        resource "huaweicloud_compute_instance" "test" {
          name = var.instance_name        # Only using instance_name
          # unused_var and another_unused are never referenced
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
import glob
from typing import Callable, List, Dict, Any, Set, Optional, Tuple


def check_io009_unused_variables(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that all variables defined in variables.tf are used in the project according to IO.009 rule specifications.
    
    This function validates that all variable definitions in variables.tf are actually
    referenced in at least one Terraform file within the same directory. It helps identify
    unused variables that can be removed to improve code maintainability.
    
    The validation process:
    1. Only check variables.tf files
    2. Extract all variable definitions from variables.tf
    3. Search all .tf files in the same directory for variable usage
    4. Report any variables that are defined but never used
    5. Exclude provider-related variables that might be used externally
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Only variables.tf files will be processed.
        content (str): The complete content of the variables.tf file as a string.
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
        >>> # Content with unused variable in variables.tf
        >>> content = '''
        ... variable "used_var" {
        ...   type = string
        ... }
        ... variable "unused_var" {
        ...   type = string  
        ... }
        ... '''
        >>> check_io009_unused_variables("variables.tf", content, sample_log_func)
        IO.009 at variables.tf:5: Variable 'unused_var' is defined but never used
    """
    # Only check variables.tf files
    if not file_path.endswith('variables.tf'):
        return
    
    # Get the directory containing variables.tf
    file_dir = os.path.dirname(file_path)
    
    # Extract all variable definitions from variables.tf with line numbers
    defined_variables = _extract_variables_with_lines(content)
    
    if not defined_variables:
        # No variables defined, nothing to check
        return
    
    # Get all variable usage from .tf files in the same directory
    used_variables = _get_used_variables_in_directory(file_dir)
    
    # Check each defined variable for usage
    for var_name, line_number in defined_variables:
        # Skip provider-related variables that might be used externally
        if _should_exclude_variable(var_name):
            continue
            
        if var_name not in used_variables:
            log_error_func(
                file_path,
                "IO.009",
                f"Variable '{var_name}' is defined but never used",
                line_number
            )


def _extract_variables_with_lines(content: str) -> List[Tuple[str, int]]:
    """
    Extract variable definitions with their line numbers from variables.tf content.
    
    Args:
        content (str): The variables.tf file content
        
    Returns:
        List[Tuple[str, int]]: List of tuples containing (variable_name, line_number)
    """
    variables = []
    lines = content.split('\n')
    
    # Pattern to match variable definitions - support quoted, single-quoted, and unquoted syntax
    var_pattern = r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{'
    
    for i, line in enumerate(lines, 1):
        match = re.match(var_pattern, line.strip())
        if match:
            # Get variable name from quoted, single-quoted, or unquoted group
            var_name = match.group(1) if match.group(1) else (match.group(2) if match.group(2) else match.group(3))
            variables.append((var_name, i))
    
    return variables


def _get_used_variables_in_directory(directory: str) -> Set[str]:
    """
    Get all variable references from .tf files in the specified directory.
    
    Args:
        directory (str): Directory path to search for .tf files
        
    Returns:
        Set[str]: Set of variable names that are used in the directory
    """
    used_variables = set()
    
    # Find all .tf files in the directory
    tf_files = glob.glob(os.path.join(directory, "*.tf"))
    
    for tf_file in tf_files:
        # Skip variables.tf as we're looking for usage, not definitions
        if os.path.basename(tf_file) == 'variables.tf':
            continue
            
        try:
            with open(tf_file, 'r', encoding='utf-8') as f:
                tf_content = f.read()
            
            # Extract variable usage from this file
            file_variables = _extract_variable_usage(tf_content)
            used_variables.update(file_variables)
            
        except Exception:
            # Can't read file, skip it
            continue
    
    return used_variables


def _extract_variable_usage(content: str) -> Set[str]:
    """
    Extract variable references from Terraform file content.
    
    Args:
        content (str): Terraform file content
        
    Returns:
        Set[str]: Set of variable names referenced in the content
    """
    variables = set()
    
    # Pattern to match variable references: var.variable_name
    var_pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
    
    for match in re.finditer(var_pattern, content):
        var_name = match.group(1)
        variables.add(var_name)
    
    return variables


def _should_exclude_variable(var_name: str) -> bool:
    """
    Check if a variable should be excluded from unused variable check.
    
    Provider-related variables might be used externally or by provider
    configurations and should not be flagged as unused.
    
    Args:
        var_name (str): Variable name to check
        
    Returns:
        bool: True if variable should be excluded from check
    """
    # Exclude provider-related variables that might be used externally
    if var_name.startswith('region'):
        return True
    if var_name in ['access_key', 'secret_key', 'domain_name']:
        return True
    # Exclude common provider configuration variables
    if var_name in ['tenant_name', 'tenant_id', 'user_name', 'user_id', 'project_name', 'project_id']:
        return True
    return False


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from Terraform content for cleaner parsing.
    
    Args:
        content (str): Original Terraform content
        
    Returns:
        str: Content with comments removed
    """
    # Remove single line comments (# and //)
    lines = content.split('\n')
    clean_lines = []
    
    for line in lines:
        # Remove comments but preserve strings
        in_string = False
        quote_char = None
        clean_line = ""
        i = 0
        
        while i < len(line):
            char = line[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    quote_char = char
                    clean_line += char
                elif char == '#' or (char == '/' and i + 1 < len(line) and line[i + 1] == '/'):
                    # Found comment start, ignore rest of line
                    break
                else:
                    clean_line += char
            else:
                clean_line += char
                if char == quote_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    quote_char = None
            
            i += 1
        
        clean_lines.append(clean_line)
    
    return '\n'.join(clean_lines)


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.009 rule.

    Returns:
        dict: A dictionary containing comprehensive rule information
    """
    return {
        "id": "IO.009",
        "name": "Unused variable check",
        "description": (
            "Validates that all variables defined in variables.tf are actually "
            "used in the project's Terraform files. This helps identify unused "
            "variables that can be removed to improve code maintainability and "
            "reduce configuration complexity. Provider-related variables are "
            "excluded as they might be used externally."
        ),
        "category": "Input/Output", 
        "severity": "warning",
        "rationale": (
            "Unused variables create unnecessary complexity and can confuse "
            "developers about the actual configuration requirements. Removing "
            "unused variables improves code clarity, reduces maintenance overhead, "
            "and helps prevent confusion about which variables are actually needed "
            "for the module to function properly."
        ),
        "examples": {
            "valid": [
                '''
# variables.tf
variable "instance_name" {        # Used in main.tf
  description = "Name of the ECS instance"
  type        = string
}

variable "flavor_id" {            # Used in main.tf  
  description = "The flavor ID of the ECS instance"
  type        = string
  default     = "c6.2xlarge.4"
}

# main.tf
resource "huaweicloud_compute_instance" "test" {
  name      = var.instance_name   # Using instance_name variable
  flavor_id = var.flavor_id       # Using flavor_id variable
}
'''
            ],
            "invalid": [
                '''
# variables.tf
variable "instance_name" {        # Used in main.tf
  description = "Name of the ECS instance" 
  type        = string
}

variable "unused_var" {           # Line 7: Not used anywhere
  description = "This variable is not used"
  type        = string
  default     = "unused"
}

variable "another_unused" {       # Line 13: Not used anywhere
  description = "Another unused variable"
  type        = number
  default     = 10
}

# main.tf
resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name        # Only using instance_name
  # unused_var and another_unused are never referenced
}

# Expected errors:
# WARNING: variables.tf (7): [IO.009] Variable 'unused_var' is defined but never used
# WARNING: variables.tf (13): [IO.009] Variable 'another_unused' is defined but never used
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.003", "ST.009"],
        "configuration": {
            "check_unused_variables": True,
            "exclude_provider_variables": True,
            "search_current_directory_only": True,
            "excluded_variable_prefixes": ["region"],
            "excluded_variable_names": [
                "access_key", 
                "secret_key", 
                "domain_name",
                "tenant_name",
                "tenant_id", 
                "user_name",
                "user_id",
                "project_name",
                "project_id"
            ]
        }
    } 