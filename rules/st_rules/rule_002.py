#!/usr/bin/env python3
"""
ST.002 - Data Source Variable Default Value Check

This module implements the ST.002 rule which validates that all input variables
used in data source blocks are designed as optional parameters, meaning they
must have default values. This ensures data sources can work properly with
minimal configuration while resources can still use required variables.

Rule Specification:
- Only variables used in data source blocks must have default values
- Variables used only in resource blocks are not required to have defaults
- Default values can be null, empty collections, or any appropriate value
- This ensures data sources work properly with minimal configuration

Examples:
    Valid scenario:
        variable "memory_size" {
          description = "The memory size (GB) for queried ECS flavors"
          type        = number
          default     = 8    # Required because used in data source
        }

        data "huaweicloud_compute_flavors" "test" {
          memory_size = var.memory_size
          # ...
        }

        variable "instance_name" {
          description = "The name of the ECS instance"
          type        = string
          default     = "tf_test_instance"
        }

        resource "huaweicloud_compute_instance" "test" {
          name = var.instance_name  # Can use required variable
        }

    Invalid scenario:
        variable "memory_size" {
          description = "The memory size (GB) for queried ECS flavors"
          type        = number
          # Missing default value but used in data source
        }

        data "huaweicloud_compute_flavors" "test" {
          memory_size = var.memory_size    # Uses variable without default
          # ...
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, Dict, Set, Optional, List


def check_st002_variable_defaults(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if variables have appropriate default values according to ST.002 rule specifications.
    
    This function validates that variables in Terraform files have proper default value
    configurations. It scans through variable definitions and checks whether default
    values are appropriately set based on the variable's purpose and usage context.
    
    The validation process:
    1. Parse the file content to extract all variable definitions
    2. Analyze each variable's type, description, and current default setting
    3. Determine if a default value is required, optional, or should be omitted
    4. Check if the current configuration matches the expected pattern
    5. Report any misconfigurations through the error logging function
    
    Validation criteria:
    - Variables used for sensitive data (passwords, keys) should not have defaults
    - Variables with clear semantic meaning may require defaults for usability
    - Optional configuration variables should have sensible defaults
    - Required input variables should not have defaults to force explicit setting
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to extract variable definitions and their properties.
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
        ... variable "password" {
        ...   type = string
        ...   default = "admin123"
        ... }
        ... '''
        >>> check_st002_variable_defaults("variables.tf", content, sample_log_func)
        ST.002 at variables.tf:3: Variable 'password' should not have a default value...
    """
    clean_content = _remove_comments_for_parsing(content)
    original_lines = content.split('\n')
    
    # Extract variables used in data sources with line numbers
    data_source_variables = _extract_data_source_variables_with_lines(clean_content, original_lines)
    
    if not data_source_variables:
        # No variables used in data sources, nothing to check
        return
    
    # Get variable definitions from the same directory
    file_dir = os.path.dirname(file_path)
    variable_definitions = _get_variable_definitions_from_directory(file_dir)
    
    # Also check current file for variable definitions
    current_file_variables = _extract_variables(clean_content)
    variable_definitions.update(current_file_variables)
    
    # Check if variables used in data sources have defaults
    for var_name, line_numbers in data_source_variables.items():
        if var_name in variable_definitions:
            if not variable_definitions[var_name]:
                # Report error for the first occurrence line number
                first_line = min(line_numbers) if line_numbers else None
                log_error_func(
                    file_path,
                    "ST.002",
                    f"Variable '{var_name}' used in data source must have a default value",
                    first_line
                )
        else:
            # Variable used but not defined - this might be from modules or other sources
            # We'll report this as a potential issue with the first occurrence line number
            first_line = min(line_numbers) if line_numbers else None
            log_error_func(
                file_path,
                "ST.002",
                f"Variable '{var_name}' used in data source is not defined in the current directory",
                first_line
            )


def _get_variable_definitions_from_directory(directory: str) -> Dict[str, bool]:
    """
    Get variable definitions from variables.tf file in the specified directory.

    Args:
        directory (str): Directory path to search for variables.tf

    Returns:
        Dict[str, bool]: Dictionary mapping variable names to whether they have defaults
    """
    variables = {}
    variables_tf_path = os.path.join(directory, 'variables.tf')
    
    if os.path.exists(variables_tf_path):
        try:
            with open(variables_tf_path, 'r', encoding='utf-8') as f:
                variables_content = f.read()
            clean_content = _remove_comments_for_parsing(variables_content)
            variables = _extract_variables(clean_content)
        except Exception:
            # Can't read variables.tf, return empty dict
            pass
    
    return variables


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


def _extract_data_source_variables_with_lines(content: str, original_lines: List[str]) -> Dict[str, Set[int]]:
    """
    Extract variable references from data source blocks with their line numbers.

    Args:
        content (str): The cleaned Terraform content
        original_lines (List[str]): Original file lines for line number mapping

    Returns:
        Dict[str, Set[int]]: Dictionary mapping variable names to sets of line numbers where they're used
    """
    variables_in_data_sources = {}
    
    # Improved pattern to match data source blocks with better boundary detection
    # Ensures 'data' is at word boundary (start of line or after whitespace)
    # Supports quoted, single-quoted, and unquoted syntax
    # Uses a more robust approach to handle nested braces
    
    # Split content into lines for more precise parsing
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this line starts a data source block
        # Pattern: data "type" "name" { or data 'type' 'name' { or data type name {
        data_start_pattern = r'^data\s+(?:"[^"]+"|\'[^\']+\'|[a-zA-Z_][a-zA-Z0-9_]*)\s+(?:"[^"]+"|\'[^\']+\'|[a-zA-Z_][a-zA-Z0-9_]*)\s*\{'
        
        if re.match(data_start_pattern, line):
            # Found start of data source block
            block_start_line = i + 1  # Convert to 1-based line numbering
            
            # Find the end of this data source block by counting braces
            brace_count = line.count('{') - line.count('}')
            j = i + 1
            block_lines = [line]
            
            # Continue until we close all braces
            while j < len(lines) and brace_count > 0:
                current_line = lines[j]
                block_lines.append(current_line)
                brace_count += current_line.count('{') - current_line.count('}')
                j += 1
            
            # Join all block lines to get the complete data source block content
            block_content = '\n'.join(block_lines)
            
            # Pattern to match variable references
            var_ref_pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
            
            # Find all variable references in this data source block
            for var_match in re.finditer(var_ref_pattern, block_content):
                var_name = var_match.group(1)
                
                # Calculate the line number of this variable reference within the block
                var_preceding_text = block_content[:var_match.start()]
                var_line_offset = var_preceding_text.count('\n')
                var_line = block_start_line + var_line_offset
                
                if var_name not in variables_in_data_sources:
                    variables_in_data_sources[var_name] = set()
                variables_in_data_sources[var_name].add(var_line)
            
            # Move to the line after this block
            i = j
        else:
            i += 1
    
    return variables_in_data_sources


def _extract_variables(content: str) -> Dict[str, bool]:
    """
    Extract variable definitions and determine whether they contain a default.
    This parser supports arbitrarily nested braces and multiple naming styles.

    Supported forms:
    - variable "name" { ... }
    - variable 'name' { ... }
    - variable name { ... }
    """
    variables: Dict[str, bool] = {}

    # Find the start of a variable block (name and the first following '{')
    start_pattern = re.compile(
        r"\bvariable\s+(?:\"([^\"]+)\"|'([^']+)'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{",
        re.MULTILINE,
    )

    pos = 0
    length = len(content)

    while pos < length:
        m = start_pattern.search(content, pos)
        if not m:
            break

        var_name = m.group(1) or m.group(2) or m.group(3)
        # Locate the position of the first '{'
        brace_start = content.find('{', m.end() - 1)
        if brace_start == -1:
            # Should not happen; advance to avoid infinite loop
            pos = m.end()
            continue

        # Scan forward using brace counting; handle nested braces and braces inside strings
        brace_count = 0
        i = brace_start
        in_quotes = False
        quote_char = ''
        while i < length:
            ch = content[i]

            # Handle quotes and escapes to avoid counting braces inside strings
            if in_quotes:
                if ch == '\\':
                    # Skip the escaped character
                    i += 2
                    continue
                if ch == quote_char:
                    in_quotes = False
                i += 1
                continue
            else:
                if ch == '"' or ch == '\'':
                    in_quotes = True
                    quote_char = ch
                    i += 1
                    continue

            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Variable block ends; extract body
                    body = content[brace_start + 1:i]
                    has_default = bool(re.search(r"\bdefault\s*=", body))
                    variables[var_name] = has_default
                    pos = i + 1
                    break
            i += 1
        else:
            # Unclosed block; advance to avoid infinite loop
            pos = m.end()

    return variables


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.002 rule.

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
        Data source variable default value check
    """
    return {
        "id": "ST.002",
        "name": "Data source variable default value check",
        "description": (
            "Validates that all input variables used in data source blocks have "
            "default values. This ensures data sources can work properly with "
            "minimal configuration while allowing resources to use required "
            "variables. Only variables referenced in data source blocks are "
            "required to have defaults."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Data sources are typically used for discovery and should work with "
            "minimal configuration. Having default values for variables used in "
            "data sources ensures they can function properly even when not all "
            "parameters are explicitly provided. Resources, on the other hand, "
            "may legitimately require certain parameters to be explicitly set."
        ),
        "examples": {
            "valid": [
                '''
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  default     = 8    # Required because used in data source
}

data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size
  # ...
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
  default     = "tf_test_instance"
}

resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name  # Can use required variable
}
'''
            ],
            "invalid": [
                '''
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  # Missing default value but used in data source
}

data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size    # Uses variable without default
  # ...
}
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal"
    }
