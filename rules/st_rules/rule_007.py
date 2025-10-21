#!/usr/bin/env python3
"""
ST.007 - Parameter Block Spacing Check

This module implements the ST.007 rule which validates parameter block spacing
within Terraform resource and data source blocks. This rule combines the functionality
of the original ST.007 and ST.008 rules.

Rule Specification:
1. Different parameter blocks (basic parameters, structure blocks, dynamic blocks) 
   must have exactly 1 blank line between them
2. Same-name structure blocks must have 0-1 blank lines between them (compact or single spacing)
3. Adjacent dynamic blocks must have exactly 1 blank line between them

Parameter Types:
- a. Basic parameter definitions (e.g., name = "value")
- b. Structure parameter blocks (e.g., data_disks { ... }, network { ... })
- c. Dynamic code blocks (e.g., dynamic "data_disks" { ... })

Examples:
    Valid spacing:
        resource "huaweicloud_compute_instance" "test" {
          name = var.instance_name
          flavor_id = data.huaweicloud_compute_flavors.test.flavors[0].id

          data_disks {
            type = "SSD"
            size = 20
          }

          data_disks {
            type = "SAS"
            size = 40
          }

          dynamic "data_disks" {
            for_each = var.data_disks_configurations
            content {
              type = data_disks.value.type
              size = data_disks.value.size
            }
          }

          network {
            uuid = huaweicloud_vpc_subnet.test.id
          }

          tags = merge(local.system_tags, var.custom_tags)
        }

    Invalid spacing:
        resource "huaweicloud_compute_instance" "test" {
          name = var.instance_name
          flavor_id = data.huaweicloud_compute_flavors.test.flavors[0].id
          data_disks {  # Missing blank line between basic parameter and structure block
            type = "SSD"
            size = 20
          }

          data_disks {  # Too many blank lines between same-name structure blocks
            type = "SAS"
            size = 40
          }

          dynamic "data_disks" {  # Missing blank line between structure and dynamic blocks
            for_each = var.data_disks_configurations
            content {
              type = data_disks.value.type
              size = data_disks.value.size
            }
          }
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Dict, Optional


def check_st007_parameter_block_spacing(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate parameter block spacing according to ST.007 rule specifications.

    This function scans through the provided Terraform file content and validates
    parameter block spacing within resource and data source blocks.

    The validation process:
    1. Parse content to identify all resource and data source blocks
    2. Within each block, identify different types of parameters:
       - Basic parameters (name = value)
       - Structure blocks (name { ... })
       - Dynamic blocks (dynamic "name" { ... })
    3. Check spacing rules:
       - Different parameter types: exactly 1 blank line
       - Same-name structure blocks: 0-1 blank lines
       - Adjacent dynamic blocks: exactly 1 blank line
    4. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked
        content (str): The complete content of the Terraform file
        log_error_func (Callable): Function to report rule violations

    Returns:
        None: Reports errors through the log_error_func callback
    """
    resource_blocks = _extract_resource_blocks_with_parameters(content)
    
    for resource_info in resource_blocks:
        resource_name = resource_info['name']
        parameters = resource_info['parameters']
        
        # Check spacing between consecutive parameters
        spacing_errors = _check_parameter_spacing_rules(
            parameters, resource_name, content
        )
        
        for error_msg, line_num in spacing_errors:
            log_error_func(file_path, "ST.007", error_msg, line_num)


def _extract_resource_blocks_with_parameters(content: str) -> List[Dict]:
    """
    Extract all resource and data source blocks with their parameters.

    Args:
        content (str): The Terraform file content

    Returns:
        List[Dict]: List of resource information with parameters
    """
    lines = content.split('\n')
    resources = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Match resource or data blocks (support quoted, single-quoted, and unquoted syntax)
        resource_match = re.match(r'(resource|data)\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        
        if resource_match:
            block_type = resource_match.group(1)
            # Extract resource type (quoted, single-quoted, or unquoted)
            resource_type = resource_match.group(2) if resource_match.group(2) else (resource_match.group(3) if resource_match.group(3) else resource_match.group(4))
            # Extract resource name (quoted, single-quoted, or unquoted)
            resource_name = resource_match.group(5) if resource_match.group(5) else (resource_match.group(6) if resource_match.group(6) else resource_match.group(7))
            full_name = f'{block_type} "{resource_type}" "{resource_name}"'
            
            resource_start = i + 1
            
            # Count braces in the resource declaration line first
            brace_count = line.count('{') - line.count('}')
            i += 1
            
            # Find the end of the resource block
            resource_end = i
            while i < len(lines) and brace_count > 0:
                current_line = lines[i]
                brace_count += current_line.count('{') - current_line.count('}')
                i += 1
                if brace_count > 0:
                    resource_end = i
            
            # Extract parameters within this resource
            parameters = _extract_parameters_from_resource(
                lines[resource_start-1:resource_end], resource_start
            )
            
            resources.append({
                'name': full_name,
                'start_line': resource_start,
                'end_line': resource_end,
                'parameters': parameters
            })
        else:
            i += 1
    
    return resources


def _extract_parameters_from_resource(resource_lines: List[str], resource_start_line: int) -> List[Dict]:
    """
    Extract all types of parameters from within a resource.

    Args:
        resource_lines (List[str]): Lines of the resource block
        resource_start_line (int): Starting line number of the resource

    Returns:
        List[Dict]: List of parameter information
    """
    parameters = []
    i = 1  # Skip the resource declaration line
    nesting_level = 0
    
    while i < len(resource_lines):
        line = resource_lines[i].strip()
        
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Look for dynamic blocks first (dynamic "name" { ... })
        dynamic_match = re.match(r'dynamic\s+"([^"]+)"\s*\{', line)
        
        if dynamic_match and nesting_level == 0:
            param_name = dynamic_match.group(1)
            block_start = resource_start_line + i
            
            # Find the end of this dynamic block
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
            
            parameters.append({
                'type': 'dynamic',
                'name': param_name,
                'start_line': block_start,
                'end_line': block_end
            })
            
            i = j
        elif nesting_level == 0:
            # Look for structure blocks (parameter_name { ... })
            block_match = re.match(r'(\w+)\s*\{', line)
            
            if block_match:
                param_name = block_match.group(1)
                block_start = resource_start_line + i
                
                # Find the end of this structure block
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
                
                parameters.append({
                    'type': 'structure',
                    'name': param_name,
                    'start_line': block_start,
                    'end_line': block_end
                })
                
                i = j
            else:
                # Look for basic parameter assignments (parameter_name = value)
                param_match = re.match(r'(\w+)\s*=', line)
                
                if param_match:
                    param_name = param_match.group(1)
                    param_line = resource_start_line + i
                    
                    parameters.append({
                        'type': 'basic',
                        'name': param_name,
                        'start_line': param_line,
                        'end_line': param_line
                    })
                
                # Track nesting level for other constructs
                for char in line:
                    if char == '{':
                        nesting_level += 1
                    elif char == '}':
                        nesting_level -= 1
                i += 1
        else:
            # Track nesting level for nested constructs
            for char in line:
                if char == '{':
                    nesting_level += 1
                elif char == '}':
                    nesting_level -= 1
            i += 1
    
    return parameters


def _check_parameter_spacing_rules(parameters: List[Dict], resource_name: str, content: str) -> List[Tuple[str, Optional[int]]]:
    """
    Check spacing rules between consecutive parameters.

    Args:
        parameters (List[Dict]): List of parameters in order
        resource_name (str): The resource containing these parameters
        content (str): The full file content

    Returns:
        List[Tuple[str, Optional[int]]]: List of error messages and optional line numbers
    """
    errors = []
    lines = content.split('\n')
    
    # Sort parameters by their start line to check consecutive parameters
    sorted_params = sorted(parameters, key=lambda x: x['start_line'])
    
    for i in range(len(sorted_params) - 1):
        current_param = sorted_params[i]
        next_param = sorted_params[i + 1]
        
        # Calculate blank lines between parameters
        current_end = current_param['end_line'] - 1  # Convert to 0-based indexing
        next_start = next_param['start_line'] - 1    # Convert to 0-based indexing
        
        # Count blank lines between the parameters (excluding comment lines)
        blank_lines = 0
        for line_idx in range(current_end + 1, next_start):
            if line_idx < len(lines):
                line_content = lines[line_idx].strip()
                if line_content == '':
                    blank_lines += 1
                elif line_content.startswith('#'):
                    # Comment lines don't count as blank lines but also don't reset the count
                    continue
                else:
                    # If there's any non-comment, non-blank content, reset blank line count
                    blank_lines = 0
        
        # Apply spacing rules based on parameter types
        error_msg = _check_spacing_rule(current_param, next_param, blank_lines, resource_name)
        if error_msg:
            # Find the first non-empty non-comment line after the problem for error reporting
            error_line = _find_error_reporting_line(lines, current_end, next_start)
            errors.append((error_msg, error_line))
    
    return errors


def _check_spacing_rule(param1: Dict, param2: Dict, blank_lines: int, resource_name: str) -> Optional[str]:
    """
    Check specific spacing rules based on parameter types.

    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        resource_name (str): The resource name

    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Rule 1: Structure block and dynamic block with same name must have exactly 1 blank line
    if ((param1['type'] == 'structure' and param2['type'] == 'dynamic' and param1['name'] == param2['name']) or
        (param1['type'] == 'dynamic' and param2['type'] == 'structure' and param1['name'] == param2['name'])):
        if blank_lines != 1:
            if blank_lines == 0:
                return f"Missing blank line between structure block and dynamic block '{param1['name']}' in {resource_name} (1 blank line is expected)"
            else:
                return f"Found {blank_lines} blank lines between structure block and dynamic block '{param1['name']}' in {resource_name}. Use exactly one blank line between structure and dynamic blocks"
    
    # Rule 2: Same-name structure blocks must have 0-1 blank lines
    elif param1['type'] == 'structure' and param2['type'] == 'structure' and param1['name'] == param2['name']:
        if blank_lines > 1:
            return f"Found {blank_lines} blank lines between same-name structure blocks '{param1['name']}' in {resource_name}. Use 0-1 blank lines between same-name structure blocks (Maximum 1 blank line)"
    
    # Rule 3: Adjacent dynamic blocks must have exactly 1 blank line
    elif param1['type'] == 'dynamic' and param2['type'] == 'dynamic':
        if blank_lines != 1:
            if blank_lines == 0:
                return f"Missing blank line between dynamic blocks '{param1['name']}' and '{param2['name']}' in {resource_name} (1 blank line is expected)"
            else:
                return f"Found {blank_lines} blank lines between dynamic blocks '{param1['name']}' and '{param2['name']}' in {resource_name}. Use exactly one blank line between dynamic blocks"
    
    # Rule 4: Different-named structure blocks must have exactly 1 blank line
    elif param1['type'] == 'structure' and param2['type'] == 'structure' and param1['name'] != param2['name']:
        if blank_lines != 1:
            if blank_lines == 0:
                return f"Missing blank line between different-named structure blocks '{param1['name']}' and '{param2['name']}' in {resource_name} (1 blank line is expected)"
            else:
                return f"Found {blank_lines} blank lines between different-named structure blocks '{param1['name']}' and '{param2['name']}' in {resource_name}. Use exactly one blank line between different-named structure blocks"
    
    # Rule 5: Different parameter types must have exactly 1 blank line
    elif param1['type'] != param2['type']:
        if blank_lines != 1:
            type_desc = _get_parameter_type_description(param1, param2)
            if blank_lines == 0:
                return f"Missing blank line between {type_desc} '{param1['name']}' and '{param2['name']}' in {resource_name} (1 blank line is expected)"
            else:
                return f"Found {blank_lines} blank lines between {type_desc} '{param1['name']}' and '{param2['name']}' in {resource_name}. Use exactly one blank line between different parameter types"
    
    # Rule 6: Same-type basic parameters should not have excessive blank lines (max 1)
    elif param1['type'] == 'basic' and param2['type'] == 'basic':
        if blank_lines > 1:
            return f"Found {blank_lines} blank lines between basic parameters '{param1['name']}' and '{param2['name']}' in {resource_name}. Use at most 1 blank line between basic parameters"
    
    return None


def _get_parameter_type_description(param1: Dict, param2: Dict) -> str:
    """
    Get a description of the parameter types for error messages.

    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter

    Returns:
        str: Description of parameter types
    """
    type_map = {
        'basic': 'basic parameter',
        'structure': 'structure block',
        'dynamic': 'dynamic block'
    }
    
    type1_desc = type_map.get(param1['type'], param1['type'])
    type2_desc = type_map.get(param2['type'], param2['type'])
    
    if param1['type'] != param2['type']:
        return f"{type1_desc} and {type2_desc}"
    else:
        return f"{type1_desc}s"


def _find_error_reporting_line(lines: List[str], current_end: int, next_start: int) -> Optional[int]:
    """
    Find the first non-empty non-comment line after the problem for error reporting.

    Args:
        lines (List[str]): File lines
        current_end (int): End line of current parameter (0-based)
        next_start (int): Start line of next parameter (0-based)

    Returns:
        Optional[int]: Line number for error reporting (1-based)
    """
    for line_idx in range(current_end + 1, next_start):
        if line_idx < len(lines):
            line = lines[line_idx].strip()
            # Skip empty lines and comment lines
            if line and not line.startswith('#'):
                return line_idx + 1  # Convert to 1-based indexing
    
    # If no non-empty non-comment line found, use the start of next parameter
    return next_start + 1 if next_start < len(lines) else None


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.007 rule.

    Returns:
        dict: A dictionary containing comprehensive rule information
    """
    return {
        "id": "ST.007",
        "name": "Parameter block spacing check",
        "description": (
            "Validates parameter block spacing within Terraform resource and data source blocks. "
            "This rule combines functionality from the original ST.007 and ST.008 rules to ensure "
            "consistent spacing between different types of parameters: basic parameters, structure "
            "blocks, and dynamic blocks."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Proper spacing between different parameter types improves code readability by creating "
            "clear visual separation between basic parameter definitions, structure blocks, and "
            "dynamic blocks. This makes it easier to scan through resource definitions and "
            "understand the logical organization of configuration parameters."
        ),
        "examples": {
            "valid": [
                '''
resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name
  flavor_id = data.huaweicloud_compute_flavors.test.flavors[0].id

  data_disks {
    type = "SSD"
    size = 20
  }

  data_disks {
    type = "SAS"
    size = 40
  }

  dynamic "data_disks" {
    for_each = var.data_disks_configurations
    content {
      type = data_disks.value.type
      size = data_disks.value.size
    }
  }

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }

  tags = merge(local.system_tags, var.custom_tags)
}
'''
            ],
            "invalid": [
                '''
resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name
  flavor_id = data.huaweicloud_compute_flavors.test.flavors[0].id
  data_disks {  # Missing blank line between basic parameter and structure block
    type = "SSD"
    size = 20
  }

  data_disks {  # Too many blank lines between same-name structure blocks
    type = "SAS"
    size = 40
  }

  dynamic "data_disks" {  # Missing blank line between structure and dynamic blocks
    for_each = var.data_disks_configurations
    content {
      type = data_disks.value.type
      size = data_disks.value.size
    }
  }
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.006"],
        "configuration": {
            "required_blank_lines_between_different_types": 1,
            "max_blank_lines_between_same_structure_blocks": 1,
            "required_blank_lines_between_dynamic_blocks": 1
        }
    }