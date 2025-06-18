#!/usr/bin/env python3
"""
ST.006 - Resource Block Spacing Check

This module implements the ST.006 rule which validates that there is exactly
one blank line between different resource blocks in the Terraform file.

Rule Specification:
- Exactly one blank line between different resource blocks
- Resource blocks include both resource and data source blocks
- No blank lines within the same resource block
- This improves readability by visually separating different resources

Examples:
    Valid resource block spacing:
        data "huaweicloud_compute_flavors" "test" {
          performance_type = "normal"
          cpu_core_count   = 4
          memory_size      = 8
        }

        resource "huaweicloud_networking_secgroup" "test" {
          name                 = "tf_test_secgroup"
          delete_default_rules = true
        }

        resource "huaweicloud_compute_instance" "test" {
          name               = "tf_test_instance"
          flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
          security_group_ids = [huaweicloud_networking_secgroup.test.id]
          ...
        }

    Invalid resource block spacing:
        data "huaweicloud_compute_flavors" "test" {
          performance_type = "normal"
          cpu_core_count   = 4
          memory_size      = 8
        }
        resource "huaweicloud_networking_secgroup" "test" {    # Missing blank line
          name                 = "tf_test_secgroup"
          delete_default_rules = true
        }


        resource "huaweicloud_compute_instance" "test" {    # Too many blank lines
          name               = "tf_test_instance"
          flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
          security_group_ids = [huaweicloud_networking_secgroup.test.id]
          ...
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Optional


def check_st006_resource_spacing(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate resource and data source spacing according to ST.006 rule specifications.

    This function scans through the provided Terraform file content and validates
    that there is exactly one blank line between different resource and data source
    blocks, improving code readability and organization.

    The validation process:
    1. Parse content to identify all resource and data source blocks
    2. Check spacing between consecutive blocks
    3. Validate that spacing follows the one-blank-line rule
    4. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all resource and data source definitions.

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
    blocks = _extract_resource_blocks(content)
    
    if len(blocks) < 2:
        return  # No spacing issues if there's only one or no blocks
    
    for i in range(len(blocks) - 1):
        current_block = blocks[i]
        next_block = blocks[i + 1]
        
        spacing_errors = _check_block_spacing_with_content(current_block, next_block, content)
        
        for error_msg in spacing_errors:
            log_error_func(file_path, "ST.006", error_msg)


def _extract_resource_blocks(content: str) -> List[Tuple[str, int, int, str]]:
    """
    Extract all resource and data source blocks from content.

    Args:
        content (str): The Terraform file content

    Returns:
        List[Tuple[str, int, int, str]]: List of (block_type, start_line, end_line, block_name)
    """
    lines = content.split('\n')
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Match resource or data blocks
        resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
        data_match = re.match(r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
        
        if resource_match or data_match:
            if resource_match:
                block_type = "resource"
                block_name = f'resource "{resource_match.group(1)}" "{resource_match.group(2)}"'
            else:
                block_type = "data"
                block_name = f'data "{data_match.group(1)}" "{data_match.group(2)}"'
            
            start_line = i + 1
            brace_count = 1
            i += 1
            
            # Find the end of the block
            while i < len(lines) and brace_count > 0:
                current_line = lines[i]
                for char in current_line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                if brace_count == 0:
                    break
                i += 1
            
            end_line = i + 1  # Current line is the closing brace line
            blocks.append((block_type, start_line, end_line, block_name))
            i += 1
        else:
            i += 1
    
    return blocks


def _check_block_spacing(
    current_block: Tuple[str, int, int, str],
    next_block: Tuple[str, int, int, str]
) -> List[str]:
    """
    Check spacing between two consecutive blocks.

    Args:
        current_block: Tuple of (block_type, start_line, end_line, block_name)
        next_block: Tuple of (block_type, start_line, end_line, block_name)

    Returns:
        List[str]: List of error messages
    """
    errors = []
    
    current_type, current_start, current_end, current_name = current_block
    next_type, next_start, next_end, next_name = next_block
    
    # Calculate the number of blank lines between blocks
    # We need to count actual blank lines, not just line differences
    blank_lines = next_start - current_end - 1
    
    # For now, we expect exactly 1 line between blocks (which could be empty or comment)
    # The rule should be: exactly one blank line between blocks
    if blank_lines < 1:
        errors.append(
            f"Line {next_start}: Missing blank line between {current_name} "
            f"and {next_name}. Add exactly one blank line between blocks"
        )
    elif blank_lines > 1:
        errors.append(
            f"Line {next_start}: Too many blank lines ({blank_lines}) between "
            f"{current_name} and {next_name}. Use exactly one blank line between blocks"
        )
    
    return errors


def _check_block_spacing_with_content(
    current_block: Tuple[str, int, int, str],
    next_block: Tuple[str, int, int, str],
    content: str
) -> List[str]:
    """
    Check spacing between two consecutive blocks by analyzing actual content.

    Args:
        current_block: Tuple of (block_type, start_line, end_line, block_name)
        next_block: Tuple of (block_type, start_line, end_line, block_name)
        content: The file content

    Returns:
        List[str]: List of error messages
    """
    errors = []
    lines = content.split('\n')
    
    current_type, current_start, current_end, current_name = current_block
    next_type, next_start, next_end, next_name = next_block
    
    # Count actual blank lines between the blocks
    blank_line_count = 0
    for line_idx in range(current_end, next_start - 1):
        line = lines[line_idx].strip()
        if line == '':
            blank_line_count += 1
    
    if blank_line_count < 1:
        errors.append(
            f"Line {next_start}: Missing blank line between {current_name} "
            f"and {next_name}. Add exactly one blank line between blocks"
        )
    elif blank_line_count > 1:
        errors.append(
            f"Line {next_start}: Too many blank lines ({blank_line_count}) between "
            f"{current_name} and {next_name}. Use exactly one blank line between blocks"
        )
    
    return errors


def _analyze_spacing_patterns(content: str) -> dict:
    """
    Analyze spacing patterns throughout the file.

    Args:
        content (str): The file content to analyze

    Returns:
        dict: Analysis results including spacing statistics
    """
    blocks = _extract_resource_blocks(content)
    
    if len(blocks) < 2:
        return {
            'total_blocks': len(blocks),
            'spacing_violations': 0,
            'proper_spacing_count': 0,
            'spacing_consistency': 100.0
        }
    
    spacing_violations = 0
    proper_spacing_count = 0
    spacing_details = []
    
    for i in range(len(blocks) - 1):
        current_block = blocks[i]
        next_block = blocks[i + 1]
        
        current_end = current_block[2]
        next_start = next_block[1]
        blank_lines = next_start - current_end - 1
        
        spacing_details.append({
            'between_blocks': f"{current_block[3]} -> {next_block[3]}",
            'blank_lines': blank_lines,
            'is_correct': blank_lines == 1
        })
        
        if blank_lines == 1:
            proper_spacing_count += 1
        else:
            spacing_violations += 1
    
    total_spacings = len(spacing_details)
    consistency_percentage = (proper_spacing_count / total_spacings * 100) if total_spacings > 0 else 100
    
    return {
        'total_blocks': len(blocks),
        'total_spacings_checked': total_spacings,
        'spacing_violations': spacing_violations,
        'proper_spacing_count': proper_spacing_count,
        'spacing_consistency': consistency_percentage,
        'spacing_details': spacing_details
    }


def _get_block_context(content: str, line_num: int, context_lines: int = 3) -> str:
    """
    Get context around a specific line for better error reporting.

    Args:
        content (str): The file content
        line_num (int): Line number to get context for
        context_lines (int): Number of lines before and after to include

    Returns:
        str: Context string with line numbers
    """
    lines = content.split('\n')
    start_line = max(0, line_num - context_lines - 1)
    end_line = min(len(lines), line_num + context_lines)
    
    context_lines_list = []
    for i in range(start_line, end_line):
        line_marker = ">>>" if i == line_num - 1 else "   "
        context_lines_list.append(f"{line_marker} {i + 1:3d}: {lines[i]}")
    
    return '\n'.join(context_lines_list)


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.006 rule.

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
        Resource and data source spacing check
    """
    return {
        "id": "ST.006",
        "name": "Resource and data source spacing check",
        "description": (
            "Validates that there is exactly one blank line between different "
            "resource and data source blocks to improve code readability and "
            "organization. This rule ensures consistent visual separation "
            "between logical units of infrastructure configuration."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Proper spacing between resource and data source blocks improves "
            "code readability by creating clear visual separation between "
            "different infrastructure components. This makes it easier to "
            "scan through large configuration files and understand the "
            "logical organization of resources."
        ),
        "examples": {
            "valid": [
                '''
 data "huaweicloud_compute_flavors" "test" {
   performance_type = "normal"
   cpu_core_count   = 4
   memory_size      = 8
 }

resource "huaweicloud_networking_secgroup" "test" {
  name                 = "tf_test_secgroup"
  delete_default_rules = true
}

resource "huaweicloud_compute_instance" "test" {
  name               = "tf_test_instance"
  flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
  security_group_ids = [huaweicloud_networking_secgroup.test.id]
  ...
}
'''
            ],
            "invalid": [
                '''
data "huaweicloud_compute_flavors" "test" {
  performance_type = "normal"
  cpu_core_count   = 4
  memory_size      = 8
}
resource "huaweicloud_networking_secgroup" "test" {    # Missing blank line
  name                 = "tf_test_secgroup"
  delete_default_rules = true
}


resource "huaweicloud_compute_instance" "test" {    # Too many blank lines
  name               = "tf_test_instance"
  flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
  security_group_ids = [huaweicloud_networking_secgroup.test.id]
  ...
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.007", "ST.008"],
        "configuration": {
            "required_blank_lines": 1,
            "apply_to_all_blocks": True
        }
    }
