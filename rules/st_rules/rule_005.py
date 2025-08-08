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
    indentation_stack = []
    
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
        
        # Skip lines with no indentation (top-level declarations)
        if indent_level == 0:
            # Check if this line should have indentation based on context
            # Only check if we're inside a resource/data source block and this line looks like a parameter
            if (indentation_stack and 
                line.strip() and 
                not line.strip().startswith('#') and
                '=' in line.strip() and
                not line.strip().startswith('resource') and
                not line.strip().startswith('data') and
                not line.strip().startswith('variable') and
                not line.strip().startswith('output') and
                not line.strip().startswith('locals') and
                not line.strip().startswith('terraform') and
                not line.strip().startswith('provider') and
                not line.strip().startswith('}') and
                not line.strip().startswith('{') and
                len(indentation_stack) > 0 and
                indentation_stack[-1] > 0 and
                # For terraform.tfvars files, don't require indentation for top-level variable declarations
                not (is_tfvars_file and not _is_inside_block_structure(line, lines, line_num))):  # Only check if we're inside a block
                # This line should be indented but isn't
                log_error_func(
                    file_path,
                    "ST.005",
                    f"Line should be indented but has no indentation. "
                    f"Expected: {indentation_stack[-1] * 2} spaces",
                    line_num
                )
            
            # Update indentation stack for lines with no indentation
            # If this line ends with '{', it starts a new block, so add depth 1
            if line.strip().endswith('{'):
                indentation_stack = [1]
            # Reset stack for block starts/ends
            elif (line.strip().startswith('resource') or 
                line.strip().startswith('data') or 
                line.strip().startswith('variable') or 
                line.strip().startswith('output') or 
                line.strip().startswith('locals') or 
                line.strip().startswith('terraform') or 
                line.strip().startswith('provider') or
                line.strip() == '}'):
                indentation_stack = []
            continue
            
        # Check if indentation is a multiple of 2
        if indent_level % 2 != 0:
            log_error_func(
                file_path,
                "ST.005",
                f"Indentation level {indent_level} is not a multiple of 2 spaces. "
                f"Current indentation: {indent_level} spaces, "
                f"Expected: multiple of 2",
                line_num
            )
            continue
        
        # Validate proper nesting
        current_depth = indent_level // 2
        validation_errors = _validate_nesting_level(
            line_num, current_depth, indentation_stack, line.strip()
        )
        
        for error_msg in validation_errors:
            log_error_func(file_path, "ST.005", error_msg, line_num)
        
        # Update indentation stack
        _update_indentation_stack(indentation_stack, current_depth, line.strip())


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
                f"First indentation level should be 2 spaces, "
                f"found {current_depth * 2} spaces"
            )
        return errors
    
    last_depth = indentation_stack[-1]
    
    # Check for proper nesting increment/decrement
    if current_depth > last_depth:
        # Increasing indentation should only increase by 1 level
        if current_depth - last_depth > 1:
            errors.append(
                f"Indentation increased by {(current_depth - last_depth) * 2} spaces. "
                f"Increase indentation by 2 spaces only"
            )
    elif current_depth < last_depth:
        # Decreasing indentation should match a previous level
        if current_depth not in indentation_stack:
            errors.append(
                f"Indentation level {current_depth * 2} spaces "
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


def _is_inside_block_structure(current_line: str, all_lines: List[str], current_line_num: int) -> bool:
    """
    Check if the current line is inside a block structure (like arrays, objects, etc.).
    
    This function helps determine if a line should be indented by checking if it's
    inside a block structure that requires indentation.
    
    Args:
        current_line (str): The current line being checked
        all_lines (List[str]): All lines in the file
        current_line_num (int): Current line number (1-indexed)
        
    Returns:
        bool: True if the line is inside a block structure, False otherwise
    """
    # If this is a top-level variable declaration in terraform.tfvars, it's not inside a block
    if '=' in current_line.strip() and not current_line.strip().startswith('#'):
        # Look backwards to see if we're inside a block structure
        brace_count = 0
        bracket_count = 0
        
        for i in range(current_line_num - 2, -1, -1):  # Start from 2 lines before current
            if i >= len(all_lines):
                continue
                
            line = all_lines[i].strip()
            if not line:
                continue
                
            # Count braces and brackets to track block structure
            for char in line:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
            
            # If we have unmatched opening braces/brackets, we're inside a block
            if brace_count > 0 or bracket_count > 0:
                return True
                
            # If we find a line that ends with { or [, check if it's part of a block structure
            if line.endswith('{') or line.endswith('['):
                # Check if this is a block structure (not just a simple assignment)
                if '=' in line and ('{' in line or '[' in line):
                    return True
                break
            # If we find a line that doesn't end with { or [, and it's not empty,
            # and it's not a comment, then we're probably at the top level
            elif not line.startswith('#') and not line.endswith('{') and not line.endswith('['):
                break
    
    return False


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
            "(<<EOT, <<EOF, etc.) are excluded from validation to allow flexible content formatting."
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
