#!/usr/bin/env python3
"""
ST.008 - Different Named Parameter Block Spacing Check

This module implements the ST.008 rule which validates that there is exactly
one blank line between different types of parameters within the same resource
or data source block.

Rule Specification:
- Exactly one blank line between different-named nested parameter blocks
- Exactly one blank line between basic parameter definitions and parameter blocks
- Different-named parameter blocks are nested structures with different names (e.g., data_disks vs network)
- Basic parameters are simple key-value assignments (e.g., name = "value")
- Parameter blocks are nested structures with braces (e.g., data_disks { ... })
- This applies within the same resource (e.g., huaweicloud_compute_instance)
- Ensures consistent visual separation between different types of configuration

Examples:
    Valid spacing (exactly 1 blank line):
        resource "huaweicloud_compute_instance" "test" {
          name              = var.instance_name
          flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
          system_disk_type  = "SAS"
          system_disk_size  = 40

          data_disks {
            size = 40
            type = "SAS"
          }

          tags = {
            "key" = "value"
          }
        }

    Invalid spacing:
        # Missing blank line between basic parameters and parameter block
        resource "huaweicloud_compute_instance" "test" {
          name              = var.instance_name
          flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
          system_disk_type  = "SAS"
          system_disk_size  = 40
          data_disks {
            size = 40
            type = "SAS"
          }

          tags = {
            "key" = "value"
          }
        }

        # Missing blank line between parameter block and basic parameters
        resource "huaweicloud_compute_instance" "test" {
          name              = var.instance_name
          flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
          system_disk_type  = "SAS"
          system_disk_size  = 40

          data_disks {
            size = 40
            type = "SAS"
          }
          tags = {
            "key" = "value"
          }
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Dict, Optional


def check_st008_different_named_parameter_spacing(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate different-named parameter block spacing according to ST.008 rule specifications.

    This function scans through the provided Terraform file content and validates
    that there is exactly one blank line between different types of parameters
    within the same resource or data source.

    The validation process:
    1. Parse content to identify all resource and data source blocks
    2. Within each block, identify both basic parameters and parameter blocks
    3. Check spacing between consecutive different types of parameters
    4. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all resource and data source definitions.

        log_error_func (Callable[[str, str, str, Optional[int]], None]): A callback function used
                      to report rule violations. The function should accept four
                      parameters: file_path, rule_id, error_message, and optional line_number.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    """
    resource_blocks = _extract_resource_blocks_with_parameters(content)
    
    for resource_info in resource_blocks:
        resource_name = resource_info['name']
        parameters = resource_info['parameters']
        
        # Check spacing between consecutive different types of parameters
        spacing_errors = _check_parameter_spacing(
            parameters, resource_name, content
        )
        
        for error_msg, line_num in spacing_errors:
            log_error_func(file_path, "ST.008", error_msg, line_num)


def _extract_resource_blocks_with_parameters(content: str) -> List[Dict]:
    """
    Extract all resource and data source blocks with their parameters (both basic and blocks).

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
    Extract both basic parameters and parameter blocks from within a resource.

    Args:
        resource_lines (List[str]): Lines of the resource block
        resource_start_line (int): Starting line number of the resource

    Returns:
        List[Dict]: List of parameter information (both basic and blocks)
    """
    parameters = []
    i = 1  # Skip the resource declaration line
    nesting_level = 0
    
    while i < len(resource_lines):
        line = resource_lines[i].strip()
        
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Look for parameter blocks (parameter_name { ... })
        block_match = re.match(r'(\w+)\s*\{', line)
        
        if block_match and nesting_level == 0:
            param_name = block_match.group(1)
            block_start = resource_start_line + i
            
            # Find the end of this parameter block
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
                'type': 'block',
                'name': param_name,
                'start_line': block_start,
                'end_line': block_end
            })
            
            i = j
        elif nesting_level == 0:
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


def _check_parameter_spacing(parameters: List[Dict], resource_name: str, content: str) -> List[Tuple[str, Optional[int]]]:
    """
    Check spacing between consecutive parameters of different types.

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
        
        # Check spacing between different types of parameters
        if _should_check_spacing_between_params(current_param, next_param):
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
            
            # Check if blank lines are not exactly 1
            if blank_lines != 1:
                error_description = _get_parameter_type_description(current_param, next_param)
                
                if blank_lines == 0:
                    errors.append((
                        f"Missing blank line between {error_description} "
                        f"'{current_param['name']}' and '{next_param['name']}' "
                        f"in {resource_name} (1 blank line is expected)",
                        next_param['start_line']
                    ))
                else:
                    errors.append((
                        f"Found {blank_lines} blank lines between {error_description} "
                        f"'{current_param['name']}' and '{next_param['name']}' "
                        f"in {resource_name}. Use exactly one blank line between different parameter types",
                        next_param['start_line']
                    ))
    
    return errors


def _should_check_spacing_between_params(param1: Dict, param2: Dict) -> bool:
    """
    Determine if spacing should be checked between two parameters.

    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter

    Returns:
        bool: True if spacing should be checked
    """
    # Check spacing if:
    # 1. Different types (basic vs block)
    # 2. Same type but different names (for blocks)
    if param1['type'] != param2['type']:
        return True
    elif param1['type'] == 'block' and param1['name'] != param2['name']:
        return True
    else:
        return False


def _get_parameter_type_description(param1: Dict, param2: Dict) -> str:
    """
    Get a description of the parameter types for error messages.

    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter

    Returns:
        str: Description of parameter types
    """
    if param1['type'] != param2['type']:
        if param1['type'] == 'basic' and param2['type'] == 'block':
            return "basic parameter and parameter block"
        elif param1['type'] == 'block' and param2['type'] == 'basic':
            return "parameter block and basic parameter"
    elif param1['type'] == 'block' and param1['name'] != param2['name']:
        return "different-named parameter blocks"
    
    return "parameters"


def _analyze_different_named_block_spacing_patterns(content: str) -> dict:
    """
    Analyze spacing patterns between different types of parameters throughout the file.

    Args:
        content (str): The file content to analyze

    Returns:
        dict: Analysis results including spacing statistics
    """
    resource_blocks = _extract_resource_blocks_with_parameters(content)
    
    total_different_param_pairs = 0
    pairs_with_correct_spacing = 0
    spacing_violations = []
    
    for resource_info in resource_blocks:
        resource_name = resource_info['name']
        parameters = resource_info['parameters']
        
        # Sort parameters by their start line
        sorted_params = sorted(parameters, key=lambda x: x['start_line'])
        
        for i in range(len(sorted_params) - 1):
            current_param = sorted_params[i]
            next_param = sorted_params[i + 1]
            
            # Only analyze parameters that should have spacing checked
            if _should_check_spacing_between_params(current_param, next_param):
                total_different_param_pairs += 1
                
                # Calculate spacing
                lines = content.split('\n')
                current_end = current_param['end_line'] - 1
                next_start = next_param['start_line'] - 1
                
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
                
                if blank_lines == 1:
                    pairs_with_correct_spacing += 1
                else:
                    spacing_violations.append({
                        'resource_name': resource_name,
                        'from_param': current_param['name'],
                        'from_type': current_param['type'],
                        'to_param': next_param['name'],
                        'to_type': next_param['type'],
                        'blank_lines': blank_lines,
                        'line_range': f"{current_param['end_line']}-{next_param['start_line']}"
                    })
    
    compliance_percentage = (
        (pairs_with_correct_spacing / total_different_param_pairs * 100)
        if total_different_param_pairs > 0 else 100
    )
    
    return {
        'total_different_param_pairs': total_different_param_pairs,
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
            - severity: Error level indicator
            - rationale: Explanation of why this rule is important
            - examples: Code examples showing valid and invalid patterns
            - auto_fixable: Whether violations can be automatically corrected
            - performance_impact: Expected impact on linting performance
            - related_rules: List of other rules that complement this one
            - configuration: Available configuration options
    """
    
    return {
        "id": "ST.008",
        "name": "Different parameter type spacing check",
        "description": (
            "Validates that there is exactly one blank line between different types "
            "of parameters within the same resource or data source. This includes "
            "spacing between basic parameter definitions and parameter blocks, as well as "
            "between different-named parameter blocks (e.g., between 'system_disk_size' "
            "basic parameter and 'data_disks' block, or between 'data_disks' and 'network' blocks). "
            "This ensures consistent visual separation between different types of configuration."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Requiring exactly one blank line between different types of parameters "
            "creates clear visual separation between basic parameter definitions and "
            "parameter blocks, as well as between different-named parameter blocks. "
            "This improves readability by making it easy to distinguish between "
            "different structural components while maintaining consistency."
        ),
        "examples": {
            "valid": [
                '''
resource "huaweicloud_compute_instance" "test" {
  name              = var.instance_name
  flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  system_disk_type  = "SAS"
  system_disk_size  = 40

  data_disks {
    size = 40
    type = "SAS"
  }

  tags = {
    "key" = "value"
  }
}
'''
            ],
            "invalid": [
                '''
resource "huaweicloud_compute_instance" "test" {
  name              = var.instance_name
  flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  system_disk_type  = "SAS"
  system_disk_size  = 40
  data_disks {        # Missing blank line between basic parameter and parameter block
    size = 40
    type = "SAS"
  }

  tags = {
    "key" = "value"
  }
}
''',
                '''
resource "huaweicloud_compute_instance" "test" {
  name              = var.instance_name
  flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  system_disk_type  = "SAS"
  system_disk_size  = 40

  data_disks {
    size = 40
    type = "SAS"
  }
  tags = {            # Missing blank line between parameter block and basic parameter
    "key" = "value"
  }
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.006", "ST.007"],
        "configuration": {
            "required_blank_lines_between_different_parameter_types": 1,
            "strict_parameter_type_separation": True
        }
    }
