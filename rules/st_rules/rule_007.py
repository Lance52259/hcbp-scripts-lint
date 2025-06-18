#!/usr/bin/env python3
"""
ST.007 - Same Parameter Block Spacing Check

This module implements the ST.007 rule which validates that blank lines
between same-name nested parameter blocks within the same resource
are less than or equal to 1.

Rule Specification:
- Same-name nested parameter blocks within a single resource must have ≤1 blank line between them
- This applies to repeated nested blocks like multiple "data_disks", "nic", "security_group" blocks
- Ensures consistent spacing without excessive whitespace within resource definitions
- Maintains readability while keeping related nested blocks visually grouped

Examples:
    Valid same parameter block spacing (≤1 blank line):
        resource "huaweicloud_compute_instance" "test" {
          name      = "tf_test_instance"
          flavor_id = "c6.2xlarge.4"
          image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

          data_disks {
            type = "SAS"
            size = 100
          }

          data_disks {
            type = "SSD"
            size = 200
          }
        }

    Invalid same parameter block spacing (>1 blank line):
        resource "huaweicloud_compute_instance" "test" {
          name      = "tf_test_instance"
          flavor_id = "c6.2xlarge.4"
          image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

          data_disks {
            type = "SAS"
            size = 100
          }


          data_disks {
            type = "SSD"
            size = 200
          }
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Dict


def check_st007_same_parameter_block_spacing(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate same parameter block spacing according to ST.007 rule specifications.

    This function scans through the provided Terraform file content and validates
    that blank lines between same-name nested parameter blocks within the same
    resource are less than or equal to 1.

    The validation process:
    1. Parse content to identify all resource and data source blocks
    2. Within each block, identify nested parameter blocks (like data_disks, nic, etc.)
    3. Group nested blocks by their parameter name
    4. Check spacing between consecutive blocks of the same parameter name
    5. Report violations through the error logging function

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
    resource_blocks = _extract_resource_blocks_with_nested_params(content)
    
    for resource_info in resource_blocks:
        resource_name = resource_info['name']
        nested_blocks = resource_info['nested_blocks']
        
        # Group nested blocks by parameter name
        grouped_blocks = _group_nested_blocks_by_name(nested_blocks)
        
        # Check spacing for each group of same-name blocks
        for param_name, blocks in grouped_blocks.items():
            if len(blocks) < 2:
                continue
                
            spacing_errors = _check_nested_block_spacing(
                blocks, param_name, resource_name, content
            )
            
            for error_msg in spacing_errors:
                log_error_func(file_path, "ST.007", error_msg)


def _extract_resource_blocks_with_nested_params(content: str) -> List[Dict]:
    """
    Extract all resource and data source blocks with their nested parameter blocks.

    Args:
        content (str): The Terraform file content

    Returns:
        List[Dict]: List of resource information with nested blocks
    """
    lines = content.split('\n')
    resources = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Match resource or data blocks
        resource_match = re.match(r'(resource|data)\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
        
        if resource_match:
            block_type = resource_match.group(1)
            resource_type = resource_match.group(2)
            resource_name = resource_match.group(3)
            full_name = f'{block_type} "{resource_type}" "{resource_name}"'
            
            resource_start = i + 1
            brace_count = 1
            i += 1
            
            # Find the end of the resource block
            resource_end = i
            while i < len(lines) and brace_count > 0:
                current_line = lines[i]
                for char in current_line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                i += 1
                if brace_count > 0:
                    resource_end = i
            
            # Extract nested parameter blocks within this resource
            nested_blocks = _extract_nested_blocks_from_resource(
                lines[resource_start-1:resource_end], resource_start
            )
            
            resources.append({
                'name': full_name,
                'start_line': resource_start,
                'end_line': resource_end,
                'nested_blocks': nested_blocks
            })
        else:
            i += 1
    
    return resources


def _extract_nested_blocks_from_resource(resource_lines: List[str], resource_start_line: int) -> List[Dict]:
    """
    Extract nested parameter blocks from within a resource.

    Args:
        resource_lines (List[str]): Lines of the resource block
        resource_start_line (int): Starting line number of the resource

    Returns:
        List[Dict]: List of nested block information
    """
    nested_blocks = []
    i = 1  # Skip the resource declaration line
    nesting_level = 0
    
    while i < len(resource_lines):
        line = resource_lines[i].strip()
        
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Look for nested parameter blocks (parameter_name {)
        nested_match = re.match(r'(\w+)\s*\{', line)
        
        if nested_match and nesting_level == 0:
            param_name = nested_match.group(1)
            block_start = resource_start_line + i
            
            # Find the end of this nested block
            brace_count = 1
            j = i + 1
            
            while j < len(resource_lines) and brace_count > 0:
                current_line = resource_lines[j]
                for char in current_line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                j += 1
            
            block_end = resource_start_line + j - 1
            
            nested_blocks.append({
                'param_name': param_name,
                'start_line': block_start,
                'end_line': block_end
            })
            
            i = j
        else:
            # Track nesting level for other blocks
            for char in line:
                if char == '{':
                    nesting_level += 1
                elif char == '}':
                    nesting_level -= 1
            i += 1
    
    return nested_blocks


def _group_nested_blocks_by_name(nested_blocks: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group nested blocks by their parameter name.

    Args:
        nested_blocks (List[Dict]): List of nested block information

    Returns:
        Dict[str, List[Dict]]: Blocks grouped by parameter name
    """
    grouped = {}
    
    for block in nested_blocks:
        param_name = block['param_name']
        if param_name not in grouped:
            grouped[param_name] = []
        grouped[param_name].append(block)
    
    # Sort blocks within each group by their start line
    for param_name in grouped:
        grouped[param_name].sort(key=lambda x: x['start_line'])
    
    return grouped


def _check_nested_block_spacing(blocks: List[Dict], param_name: str, resource_name: str, content: str) -> List[str]:
    """
    Check spacing between consecutive nested blocks of the same parameter name.

    Args:
        blocks (List[Dict]): List of nested blocks with the same parameter name
        param_name (str): The parameter name being checked
        resource_name (str): The resource containing these blocks
        content (str): The full file content

    Returns:
        List[str]: List of error messages
    """
    errors = []
    lines = content.split('\n')
    
    for i in range(len(blocks) - 1):
        current_block = blocks[i]
        next_block = blocks[i + 1]
        
        # Calculate blank lines between blocks
        current_end = current_block['end_line'] - 1  # Convert to 0-based indexing
        next_start = next_block['start_line'] - 1    # Convert to 0-based indexing
        
        # Count blank lines between the blocks
        blank_lines = 0
        for line_idx in range(current_end, next_start):
            if line_idx < len(lines) and lines[line_idx].strip() == '':
                blank_lines += 1
        
        # Check if blank lines exceed 1
        if blank_lines > 1:
            errors.append(
                f"Lines {current_block['end_line']}-{next_block['start_line']}: "
                f"Found {blank_lines} blank lines between same-name parameter blocks "
                f"'{param_name}' within {resource_name}. "
                f"Use ≤1 blank line between same parameter blocks"
            )
    
    return errors


def _analyze_nested_block_spacing_patterns(content: str) -> dict:
    """
    Analyze spacing patterns between same-name nested blocks throughout the file.

    Args:
        content (str): The file content to analyze

    Returns:
        dict: Analysis results including spacing statistics
    """
    resource_blocks = _extract_resource_blocks_with_nested_params(content)
    
    total_block_pairs = 0
    pairs_with_violations = 0
    spacing_violations = []
    
    for resource_info in resource_blocks:
        resource_name = resource_info['name']
        nested_blocks = resource_info['nested_blocks']
        grouped_blocks = _group_nested_blocks_by_name(nested_blocks)
        
        for param_name, blocks in grouped_blocks.items():
            if len(blocks) < 2:
                continue
                
            for i in range(len(blocks) - 1):
                current_block = blocks[i]
                next_block = blocks[i + 1]
                total_block_pairs += 1
                
                # Calculate spacing
                lines = content.split('\n')
                current_end = current_block['end_line'] - 1
                next_start = next_block['start_line'] - 1
                
                blank_lines = 0
                for line_idx in range(current_end, next_start):
                    if line_idx < len(lines) and lines[line_idx].strip() == '':
                        blank_lines += 1
                
                if blank_lines > 1:
                    pairs_with_violations += 1
                    spacing_violations.append({
                        'resource_name': resource_name,
                        'param_name': param_name,
                        'blank_lines': blank_lines,
                        'line_range': f"{current_block['end_line']}-{next_block['start_line']}"
                    })
    
    compliance_percentage = (
        ((total_block_pairs - pairs_with_violations) / total_block_pairs * 100)
        if total_block_pairs > 0 else 100
    )
    
    return {
        'total_block_pairs': total_block_pairs,
        'pairs_with_violations': pairs_with_violations,
        'compliance_percentage': compliance_percentage,
        'spacing_violations': spacing_violations,
        'total_resources': len(resource_blocks)
    }


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.007 rule.

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
        Same parameter block spacing check
    """
    return {
        "id": "ST.007",
        "name": "Same parameter block spacing check",
        "description": (
            "Validates that blank lines between same-name nested parameter blocks "
            "within the same resource (such as multiple 'data_disks' blocks) "
            "are less than or equal to 1. This ensures consistent spacing without "
            "excessive whitespace within resource definitions."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Limiting blank lines between same-name nested blocks to ≤1 maintains "
            "readability while preventing excessive whitespace within resources. "
            "This creates consistent visual grouping of related nested parameters "
            "and keeps resource definitions compact and easy to scan."
        ),
        "examples": {
            "valid": [
                '''
resource "huaweicloud_compute_instance" "test" {
  name      = "tf_test_instance"
  flavor_id = "c6.2xlarge.4"
  image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

  data_disks {
    type = "SAS"
    size = 100
  }

  data_disks {
    type = "SSD"
    size = 200
  }
}
'''
            ],
            "invalid": [
                '''
resource "huaweicloud_compute_instance" "test" {
  name      = "tf_test_instance"
  flavor_id = "c6.2xlarge.4"
  image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

  data_disks {
    type = "SAS"
    size = 100
  }


  data_disks {
    type = "SSD"
    size = 200
  }
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.006", "ST.008"],
        "configuration": {
            "max_blank_lines_between_same_nested_blocks": 1,
            "strict_nested_block_grouping": True
        }
    }
