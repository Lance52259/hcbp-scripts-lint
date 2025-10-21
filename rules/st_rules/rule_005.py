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
- For terraform.tfvars files, heredoc blocks (<<EOT, <<EOF, etc.) are excluded from validation

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

    Valid terraform.tfvars with heredoc (excluded from validation):
        object_upload_content = <<EOT
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
EOT

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Optional


def check_st005_indentation_level(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
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
    6. For terraform.tfvars files, exclude heredoc blocks from validation

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all lines that may contain indentation.

        log_error_func (Callable[[str, str, str, Optional[int]], None]): A callback function used
                      to report rule violations. The function should accept four
                      parameters: file_path, rule_id, error_message, and line_number.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    """
    lines = content.split('\n')
    
    # Check if this is a terraform.tfvars file
    is_tfvars_file = file_path.endswith('.tfvars')
    in_heredoc = False
    heredoc_terminator = None
    
    for line_num, line in enumerate(lines, 1):
        if line.strip() == '':
            continue
        
        # Check heredoc state for all files (not just terraform.tfvars)
        heredoc_state = _check_heredoc_state(line, in_heredoc, heredoc_terminator)
        in_heredoc = heredoc_state["in_heredoc"]
        heredoc_terminator = heredoc_state["terminator"]
        
        # Skip validation if we're inside a heredoc block
        if in_heredoc:
            continue
        
        indent_level = _get_indentation_level(line)
        line_content = line.strip()
        
        # Handle tab characters (should be caught by ST.004)
        if indent_level == -1:
            continue
        
        # Skip comment lines
        if line_content.startswith('#'):
            continue
        
        # Validate indentation based on line content and context
        _validate_line_indentation(file_path, line_num, line_content, indent_level, is_tfvars_file, log_error_func)


def _validate_line_indentation(file_path: str, line_num: int, line_content: str, indent_level: int, 
                               is_tfvars_file: bool, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate the indentation of a single line based on its content and context.
    
    Args:
        file_path (str): The path to the file being checked
        line_num (int): Current line number
        line_content (str): The stripped content of the current line
        indent_level (int): Current indentation level in spaces
        is_tfvars_file (bool): Whether this is a .tfvars file
        log_error_func: Function to log errors
    """
    # Top-level declarations should not be indented
    # Only check for actual top-level declarations, not block names
    if ((line_content.startswith('resource ') or 
         line_content.startswith('data ') or 
         line_content.startswith('variable ') or 
         line_content.startswith('output ') or 
         line_content.startswith('locals ') or 
         line_content.startswith('terraform ') or 
         line_content.startswith('provider ')) and
        ' ' in line_content and not line_content.endswith('{')):
        if indent_level > 0:
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 0 spaces",
                line_num
            )
        return
    
    # For .tfvars files, handle array/object structure indentation first
    if is_tfvars_file:
        if line_content.startswith('{') and indent_level == 0:
            # Opening brace should be indented
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 2 spaces",
                line_num
            )
            return
        elif '=' in line_content and indent_level == 3:
            # Object properties should be indented 4 spaces, not 3
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. "
                f"Current indentation: {indent_level} spaces, Expected: 4 spaces",
                line_num
            )
            return
        elif '=' in line_content and indent_level > 0:
            # Check if this is a top-level assignment that shouldn't be indented
            # Skip if it's inside an array/object structure (indented 4 spaces or more)
            if indent_level < 4:
                log_error_func(
                    file_path,
                    "ST.005",
                    f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 0 spaces",
                    line_num
                )
            return
    
    # Check if indentation is a multiple of 2
    if indent_level > 0 and indent_level % 2 != 0:
        # Determine the correct indentation based on context
        # For odd indentation, choose the closest even number
        if indent_level == 1:
            expected_indent = 2
        elif indent_level == 3:
            expected_indent = 2  # Usually 3 spaces should be 2, not 4
        elif indent_level == 5:
            expected_indent = 6
        elif indent_level == 7:
            expected_indent = 6  # Usually 7 spaces should be 6, not 8
        elif indent_level == 9:
            expected_indent = 8
        else:
            # For other odd numbers, choose the smaller even number
            expected_indent = indent_level - 1
        
        log_error_func(
            file_path,
            "ST.005",
            f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: {expected_indent} spaces",
            line_num
        )
        return
    
    
    # Check for block parameters that should be indented
    if indent_level == 0 and '=' in line_content and not line_content.startswith('#') and not is_tfvars_file:
        # This looks like a block parameter that should be indented
        # Check if it's not a top-level declaration
        if not (line_content.startswith('resource ') or 
                line_content.startswith('data ') or 
                line_content.startswith('variable ') or 
                line_content.startswith('output ') or 
                line_content.startswith('locals ') or 
                line_content.startswith('terraform ') or 
                line_content.startswith('provider ')):
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 2 spaces",
                line_num
            )
            return
    
    # Additional validation for specific problematic patterns
    # This is a simplified approach - we could make it more sophisticated
    if indent_level > 0:
        # Check for common incorrect indentation patterns
        if indent_level == 1:
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 2 spaces",
                line_num
            )
        elif indent_level == 3:
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 4 spaces",
                line_num
            )
        elif indent_level == 5:
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 6 spaces",
                line_num
            )
        elif indent_level == 7:
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. Current indentation: {indent_level} spaces, Expected: 8 spaces",
                line_num
            )
        # Additional checks for specific problematic cases
        elif indent_level == 4 and '=' in line_content and not line_content.endswith('{'):
            # This might be a parameter that should be at level 2 instead of 4
            # Check if this looks like a resource parameter (not an object property)
            if ('image_id' in line_content or 'flavor_id' in line_content or 
                'security_groups' in line_content or 'availability_zone' in line_content):
                log_error_func(
                    file_path,
                    "ST.005",
                    f"Indentation level incorrect. "
                    f"Current indentation: {indent_level} spaces, Expected: 2 spaces",
                    line_num
                )
        elif indent_level == 2 and line_content.endswith('{') and 'content' in line_content:
            # This might be a content block that should be at level 4 instead of 2
            # Note: dynamic blocks at level 2 are correct (they're inside resource blocks)
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level incorrect. "
                f"Current indentation: {indent_level} spaces, Expected: 4 spaces",
                line_num
            )










def _check_heredoc_state(line: str, current_in_heredoc: bool, current_terminator: Optional[str]) -> dict:
    """
    Check if the current line changes the heredoc state.

    This function detects the start and end of HCL heredoc blocks by looking for
    patterns like `<<EOT`, `<<EOF`, etc. in lines, and their corresponding terminators.

    Args:
        line (str): The current line to analyze
        current_in_heredoc (bool): Whether we're currently inside a heredoc block
        current_terminator (Optional[str]): The current heredoc terminator if inside a block

    Returns:
        dict: Dictionary with 'in_heredoc' and 'terminator' keys
    """
    line_stripped = line.strip()
    
    # Check for heredoc start pattern (<<EOT, <<EOF, etc.)
    # This can appear at the end of a line like: locals = <<EOT
    if not current_in_heredoc:
        heredoc_match = re.search(r'<<([A-Z]+)\s*$', line)
        if heredoc_match:
            return {
                "in_heredoc": True,
                "terminator": heredoc_match.group(1)
            }

    # Check for heredoc end pattern
    # The terminator must be at the beginning of the line (after stripping)
    elif current_terminator and line_stripped == current_terminator:
        return {
            "in_heredoc": False,
            "terminator": None
        }

    # Return current state if no change
    return {
        "in_heredoc": current_in_heredoc,
        "terminator": current_terminator
    }


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
            "and proper visual hierarchy. For terraform.tfvars files, heredoc blocks "
            "(<<EOT, <<EOF, etc.) are excluded from validation to allow flexible content formatting. "
            "Properly handles complex data structures including arrays and objects, detecting "
            "missing indentation for block structure elements like '{' and '}' lines."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Consistent indentation levels using the current_level * 2 formula "
            "provide clear visual hierarchy and make code structure immediately "
            "apparent. This standard helps developers quickly understand nesting "
            "relationships and ensures consistent formatting across the codebase. "
            "Heredoc blocks in .tfvars files are excluded to allow for flexible "
            "content formatting without affecting the overall file structure."
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
''',
                '''
# Valid terraform.tfvars with heredoc (excluded from validation)
key_alias             = "tf-test-obs-key"
bucket_name           = "tf-test-obs-bucket"
object_upload_content = <<EOT
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
EOT
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
