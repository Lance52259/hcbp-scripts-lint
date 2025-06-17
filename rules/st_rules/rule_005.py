#!/usr/bin/env python3
"""
ST.005 - Indentation Level Check

This module implements the ST.005 rule which validates that indentation levels
in Terraform files follow the correct nesting pattern where each level uses
exactly 2 spaces per nesting depth (current_level * 2 spaces).

Rule Specification:
- Each indentation level must be exactly current_level * 2 spaces
  For example:
  - Level 1 (resource root parameters): 1 * 2 = 2 spaces
  - Level 2 (nested blocks): 2 * 2 = 4 spaces  
  - Level 3 (deeply nested): 3 * 2 = 6 spaces
- Indentation must be consistent and properly nested

Examples:
    Valid indentation levels:
        resource "huaweicloud_compute_instance" "test" {    # Level 0
          name      = "tf_test_instance"                    # Level 1: 1*2=2 spaces
          flavor_id = "c6.large.2"                          # Level 1: 1*2=2 spaces
          image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"
          
          tags = {                                          # Level 1: 1*2=2 spaces
            foo = "bar"                                     # Level 2: 2*2=4 spaces
            Environment = "dev"                             # Level 2: 2*2=4 spaces
          }
        }

    Invalid indentation levels:
        resource "huaweicloud_compute_instance" "test" {
        name = "example"          # Wrong: should be 2 spaces (1*2), not 0
          flavor_id = "c6.large.2"
            
            tags = {              # Wrong: should be 2 spaces (1*2), not 4
              foo = "bar"         # Wrong: should be 4 spaces (2*2), not 6
            }
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Optional


def check_st005_indentation_level(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate indentation level consistency according to ST.005 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all indentation uses consistent 2-space levels. This ensures proper
    code structure and readability across the entire file.

    The validation process:
    1. Split content into individual lines
    2. Analyze indentation depth for each line
    3. Check if indentation is in multiples of 2 spaces
    4. Validate proper nesting levels
    5. Report violations through the error logging function

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
    indentation_stack = []
    
    for line_num, line in enumerate(lines, 1):
        if line.strip() == '':
            continue
            
        indent_level = _get_indentation_level(line)
        
        # Skip lines with no indentation (top-level declarations)
        if indent_level == 0:
            indentation_stack = []
            continue
            
        # Check if indentation is a multiple of 2
        if indent_level % 2 != 0:
            log_error_func(
                file_path,
                "ST.005",
                f"Line {line_num}: Indentation level {indent_level} is not a multiple of 2 spaces. "
                f"Use 2-space indentation consistently"
            )
            continue
        
        # Validate proper nesting
        current_depth = indent_level // 2
        validation_errors = _validate_nesting_level(
            line_num, current_depth, indentation_stack, line.strip()
        )
        
        for error_msg in validation_errors:
            log_error_func(file_path, "ST.005", error_msg)
        
        # Update indentation stack
        _update_indentation_stack(indentation_stack, current_depth, line.strip())


def _get_indentation_level(line: str) -> int:
    """
    Calculate the indentation level (number of leading spaces) for a line.

    Args:
        line (str): The line to analyze

    Returns:
        int: Number of leading spaces
    """
    leading_spaces = 0
    for char in line:
        if char == ' ':
            leading_spaces += 1
        elif char == '\t':
            # If tabs are found, treat as invalid (should be caught by ST.004)
            return -1
        else:
            break
    return leading_spaces


def _validate_nesting_level(line_num: int, current_depth: int, indentation_stack: List[int], line_content: str) -> List[str]:
    """
    Validate proper nesting levels based on code structure.

    Args:
        line_num (int): Current line number
        current_depth (int): Current indentation depth (in 2-space units)
        indentation_stack (List[int]): Stack of previous indentation levels
        line_content (str): Content of the current line

    Returns:
        List[str]: List of error messages
    """
    errors = []
    
    # If this is the first indented line or after a top-level declaration
    if not indentation_stack:
        if current_depth != 1:
            errors.append(
                f"Line {line_num}: First indentation level should be 2 spaces, "
                f"found {current_depth * 2} spaces"
            )
        return errors
    
    last_depth = indentation_stack[-1]
    
    # Check for proper nesting increment/decrement
    if current_depth > last_depth:
        # Increasing indentation should only increase by 1 level
        if current_depth - last_depth > 1:
            errors.append(
                f"Line {line_num}: Indentation increased by {(current_depth - last_depth) * 2} spaces. "
                f"Increase indentation by 2 spaces only"
            )
    elif current_depth < last_depth:
        # Decreasing indentation should match a previous level
        if current_depth not in indentation_stack:
            errors.append(
                f"Line {line_num}: Indentation level {current_depth * 2} spaces "
                f"doesn't match any previous indentation level"
            )
    
    return errors


def _update_indentation_stack(indentation_stack: List[int], current_depth: int, line_content: str) -> None:
    """
    Update the indentation stack based on the current line.

    Args:
        indentation_stack (List[int]): Stack of indentation levels
        current_depth (int): Current indentation depth
        line_content (str): Content of the current line
    """
    # Remove deeper levels from stack if current depth is less
    while indentation_stack and indentation_stack[-1] >= current_depth:
        indentation_stack.pop()
    
    # Add current depth to stack
    if not indentation_stack or indentation_stack[-1] < current_depth:
        indentation_stack.append(current_depth)


def _analyze_indentation_consistency(content: str) -> dict:
    """
    Analyze indentation consistency throughout the file.

    Args:
        content (str): The file content to analyze

    Returns:
        dict: Analysis results including patterns and recommendations
    """
    lines = content.split('\n')
    indent_levels = []
    inconsistent_lines = []
    
    for line_num, line in enumerate(lines, 1):
        if line.strip() == '':
            continue
            
        indent_level = _get_indentation_level(line)
        if indent_level > 0:
            indent_levels.append(indent_level)
            if indent_level % 2 != 0:
                inconsistent_lines.append((line_num, indent_level))
    
    # Calculate statistics
    if indent_levels:
        unique_levels = sorted(set(indent_levels))
        consistent_levels = [level for level in unique_levels if level % 2 == 0]
        inconsistent_count = len([level for level in indent_levels if level % 2 != 0])
    else:
        unique_levels = []
        consistent_levels = []
        inconsistent_count = 0
    
    return {
        'total_indented_lines': len(indent_levels),
        'unique_indent_levels': unique_levels,
        'consistent_levels': consistent_levels,
        'inconsistent_lines': inconsistent_lines,
        'inconsistent_count': inconsistent_count,
        'consistency_percentage': (
            ((len(indent_levels) - inconsistent_count) / len(indent_levels) * 100)
            if indent_levels else 100
        )
    }


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.005 rule.

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
        Indentation level check
    """
    return {
        "id": "ST.005",
        "name": "Indentation level check",
        "description": (
            "Validates that indentation levels in Terraform files follow the "
            "correct nesting pattern where each level uses exactly current_level * 2 spaces. "
            "For example, resource root parameters should use 1*2=2 spaces, nested blocks "
            "should use 2*2=4 spaces, and so on. This ensures consistent code structure "
            "and proper visual hierarchy."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Consistent indentation levels using the current_level * 2 formula "
            "provide clear visual hierarchy and make code structure immediately "
            "apparent. This standard helps developers quickly understand nesting "
            "relationships and ensures consistent formatting across the codebase."
        ),
        "examples": {
            "valid": [
                '''
resource "huaweicloud_compute_instance" "test" {    # Level 0
  name      = "tf_test_instance"                    # Level 1: 1*2=2 spaces
  flavor_id = "c6.large.2"                          # Level 1: 1*2=2 spaces
  image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"
  
  tags = {                                          # Level 1: 1*2=2 spaces
    foo = "bar"                                     # Level 2: 2*2=4 spaces
    Environment = "dev"                             # Level 2: 2*2=4 spaces
  }
}
'''
            ],
            "invalid": [
                '''
resource "huaweicloud_compute_instance" "test" {
name = "example"          # Wrong: should be 2 spaces (1*2), not 0
  flavor_id = "c6.large.2"
    
    tags = {              # Wrong: should be 2 spaces (1*2), not 4
      foo = "bar"         # Wrong: should be 4 spaces (2*2), not 6
    }
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.004"],
        "configuration": {
            "indent_size": 2,
            "indent_type": "spaces",
            "max_nesting_depth": 10
        }
    }
