#!/usr/bin/env python3
"""
ST.008 - Different Named Parameter Block Spacing Check

This module implements the ST.008 rule which validates that there is exactly
one blank line between different-named parameter blocks within the same resource
or data source block.

Rule Specification:
- Exactly one blank line between different-named nested parameter blocks
- Different-named parameter blocks are nested structures with different names (e.g., data_disks vs network)
- This applies within the same resource (e.g., huaweicloud_compute_instance)
- Ensures consistent visual separation between different types of nested configuration

Examples:
    Valid spacing (exactly 1 blank line):
        resource "huaweicloud_compute_instance" "test" {
          name      = "tf_test_instance"
          flavor_id = "c6.2xlarge.4"
          image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

          data_disks {
            type = "SAS"
            size = 100
          }

          network {
            uuid = "12345678-1234-1234-1234-123456789012"
          }
        }

    Invalid spacing:
        # 0 blank lines between different-named parameter blocks
        resource "huaweicloud_compute_instance" "test" {
          name      = "tf_test_instance"
          flavor_id = "c6.2xlarge.4"
          image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

          data_disks {
            type = "SAS"
            size = 100
          }
          network {
            uuid = "12345678-1234-1234-1234-123456789012"
          }
        }

        # 2 blank lines (>1) between different-named parameter blocks
        resource "huaweicloud_compute_instance" "test" {
          name      = "tf_test_instance"
          flavor_id = "c6.2xlarge.4"
          image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

          data_disks {
            type = "SAS"
            size = 100
          }


          network {
            uuid = "12345678-1234-1234-1234-123456789012"
          }
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Dict


def check_st008_different_named_parameter_spacing(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate different-named parameter block spacing according to ST.008 rule specifications.

    This function scans through the provided Terraform file content and validates
    that there is exactly one blank line between different-named nested parameter
    blocks within the same resource or data source.

    The validation process:
    1. Parse content to identify all resource and data source blocks
    2. Within each block, identify nested parameter blocks with different names
    3. Check spacing between consecutive different-named parameter blocks
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
    resource_blocks = _extract_resource_blocks_with_nested_params(content)
    
    for resource_info in resource_blocks:
        resource_name = resource_info['name']
        nested_blocks = resource_info['nested_blocks']
        
        # Check spacing between consecutive different-named blocks
        spacing_errors = _check_different_named_block_spacing(
            nested_blocks, resource_name, content
        )
        
        for error_msg in spacing_errors:
            log_error_func(file_path, "ST.008", error_msg)


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


def _check_different_named_block_spacing(nested_blocks: List[Dict], resource_name: str, content: str) -> List[str]:
    """
    Check spacing between consecutive different-named nested parameter blocks.

    Args:
        nested_blocks (List[Dict]): List of nested blocks in order
        resource_name (str): The resource containing these blocks
        content (str): The full file content

    Returns:
        List[str]: List of error messages
    """
    errors = []
    lines = content.split('\n')
    
    # Sort blocks by their start line to check consecutive blocks
    sorted_blocks = sorted(nested_blocks, key=lambda x: x['start_line'])
    
    for i in range(len(sorted_blocks) - 1):
        current_block = sorted_blocks[i]
        next_block = sorted_blocks[i + 1]
        
        # Only check if blocks have different names
        if current_block['param_name'] != next_block['param_name']:
            # Calculate blank lines between blocks
            current_end = current_block['end_line'] - 1  # Convert to 0-based indexing
            next_start = next_block['start_line'] - 1    # Convert to 0-based indexing
            
            # Count blank lines between the blocks
            blank_lines = 0
            for line_idx in range(current_end, next_start):
                if line_idx < len(lines) and lines[line_idx].strip() == '':
                    blank_lines += 1
            
            # Check if blank lines are not exactly 1
            if blank_lines != 1:
                if blank_lines == 0:
                    errors.append(
                        f"Line {next_block['start_line']}: Missing blank line between "
                        f"different-named parameter blocks '{current_block['param_name']}' "
                        f"and '{next_block['param_name']}' in {resource_name}. "
                        f"Add exactly one blank line between different parameter blocks"
                    )
                else:
                    errors.append(
                        f"Lines {current_block['end_line']}-{next_block['start_line']}: "
                        f"Found {blank_lines} blank lines between different-named parameter blocks "
                        f"'{current_block['param_name']}' and '{next_block['param_name']}' "
                        f"in {resource_name}. Use exactly one blank line between different parameter blocks"
                    )
    
    return errors


def _analyze_different_named_block_spacing_patterns(content: str) -> dict:
    """
    Analyze spacing patterns between different-named nested blocks throughout the file.

    Args:
        content (str): The file content to analyze

    Returns:
        dict: Analysis results including spacing statistics
    """
    resource_blocks = _extract_resource_blocks_with_nested_params(content)
    
    total_different_block_pairs = 0
    pairs_with_correct_spacing = 0
    spacing_violations = []
    
    for resource_info in resource_blocks:
        resource_name = resource_info['name']
        nested_blocks = resource_info['nested_blocks']
        
        # Sort blocks by their start line
        sorted_blocks = sorted(nested_blocks, key=lambda x: x['start_line'])
        
        for i in range(len(sorted_blocks) - 1):
            current_block = sorted_blocks[i]
            next_block = sorted_blocks[i + 1]
            
            # Only analyze different-named blocks
            if current_block['param_name'] != next_block['param_name']:
                total_different_block_pairs += 1
                
                # Calculate spacing
                lines = content.split('\n')
                current_end = current_block['end_line'] - 1
                next_start = next_block['start_line'] - 1
                
                blank_lines = 0
                for line_idx in range(current_end, next_start):
                    if line_idx < len(lines) and lines[line_idx].strip() == '':
                        blank_lines += 1
                
                if blank_lines == 1:
                    pairs_with_correct_spacing += 1
                else:
                    spacing_violations.append({
                        'resource_name': resource_name,
                        'from_param': current_block['param_name'],
                        'to_param': next_block['param_name'],
                        'blank_lines': blank_lines,
                        'line_range': f"{current_block['end_line']}-{next_block['start_line']}"
                    })
    
    compliance_percentage = (
        (pairs_with_correct_spacing / total_different_block_pairs * 100)
        if total_different_block_pairs > 0 else 100
    )
    
    return {
        'total_different_block_pairs': total_different_block_pairs,
        'pairs_with_correct_spacing': pairs_with_correct_spacing,
        'compliance_percentage': compliance_percentage,
        'spacing_violations': spacing_violations,
        'total_resources': len(resource_blocks)
    }


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.008 rule.

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
        Different named parameter block spacing check
    """
    return {
        "id": "ST.008",
        "name": "Different named parameter block spacing check",
        "description": (
            "Validates that there is exactly one blank line between different-named "
            "nested parameter blocks within the same resource or data source "
            "(e.g., between 'data_disks' and 'network' blocks in huaweicloud_compute_instance). "
            "This ensures consistent visual separation between different types of nested configuration."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Requiring exactly one blank line between different-named parameter blocks "
            "creates clear visual separation between different types of nested configuration "
            "within the same resource. This improves readability by making it easy to "
            "distinguish between different structural components while maintaining consistency."
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

  network {
    uuid = "12345678-1234-1234-1234-123456789012"
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
  network {
    uuid = "12345678-1234-1234-1234-123456789012"
  }
}
''',
                '''
resource "huaweicloud_compute_instance" "test" {
  name      = "tf_test_instance"
  flavor_id = "c6.2xlarge.4"
  image_id  = "57818f98-06dd-2bc0-b41c-2b33144a76f0"

  data_disks {
    type = "SAS"
    size = 100
  }


  network {
    uuid = "12345678-1234-1234-1234-123456789012"
  }
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.006", "ST.007"],
        "configuration": {
            "required_blank_lines_between_different_named_blocks": 1,
            "strict_different_named_block_separation": True
        }
    }
