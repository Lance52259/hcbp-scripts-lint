#!/usr/bin/env python3
"""
ST.007 - Parameter Block Spacing Check

This module implements the ST.007 rule which validates parameter block spacing
within Terraform resource and data source blocks.

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
    parameter block spacing within resource, data source, provider, terraform, and locals blocks.

    The validation process:
    1. Parse content to identify all resource, data source, provider, terraform, and locals blocks
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
    block_list = _extract_resource_blocks_with_parameters(content)
    
    # Collect all errors first
    all_errors = []
    
    for block_info in block_list:
        block_name = block_info['name']
        parameters = block_info['parameters']
        
        # Check spacing between consecutive parameters
        spacing_errors = _check_parameter_spacing_rules(
            parameters, block_name, content
        )
        
        for error_msg, line_num in spacing_errors:
            all_errors.append((error_msg, line_num))
    
    # Sort errors by line number
    all_errors.sort(key=lambda x: x[1] if x[1] is not None else 0)
    
    # Report errors in sorted order
    for error_msg, line_num in all_errors:
        log_error_func(file_path, "ST.007", error_msg, line_num)


def _extract_resource_blocks_with_parameters(content: str) -> List[Dict]:
    """
    Extract all resource, data source, provider, terraform, and locals blocks with their parameters.

    Args:
        content (str): The Terraform file content

    Returns:
        List[Dict]: List of block information with parameters
    """
    lines = content.split('\n')
    resources = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Match resource, data, provider, terraform, or locals blocks (support quoted, single-quoted, and unquoted syntax)
        resource_match = re.match(r'(resource|data|provider|terraform|locals)\s*(?:(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))(?:\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*)))?)?\s*\{', line)
        
        if resource_match:
            block_type = resource_match.group(1)
            
            if block_type == 'provider':
                # Provider blocks have only one name (no separate type and name)
                provider_name = resource_match.group(2) if resource_match.group(2) else (resource_match.group(3) if resource_match.group(3) else resource_match.group(4))
                full_name = f'{block_type} "{provider_name}"'
            elif block_type == 'terraform':
                # Terraform blocks have no name
                full_name = f'{block_type}'
            elif block_type == 'locals':
                # Locals blocks have no name
                full_name = f'{block_type}'
            else:
                # Resource and data blocks have both type and name
                resource_type = resource_match.group(2) if resource_match.group(2) else (resource_match.group(3) if resource_match.group(3) else resource_match.group(4))
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
                lines[resource_start-1:resource_end], resource_start, block_type
            )
            
            # Also extract parameters from nested structure blocks
            nested_parameters = _extract_nested_parameters(
                lines[resource_start-1:resource_end], resource_start
            )
            parameters.extend(nested_parameters)
            
            resources.append({
                'name': full_name,
                'start_line': resource_start,
                'end_line': resource_end,
                'parameters': parameters
            })
        else:
            i += 1
    
    return resources


def _extract_parameters_from_resource(resource_lines: List[str], resource_start_line: int, block_type: str = None) -> List[Dict]:
    """
    Extract all types of parameters from within a resource.

    Args:
        resource_lines (List[str]): Lines of the resource block
        resource_start_line (int): Starting line number of the resource

    Returns:
        List[Dict]: List of parameter information
    """
    parameters = []
    i = 1  # Skip the block declaration line
    nesting_level = 0
    
    while i < len(resource_lines):
        line = resource_lines[i].strip()
        
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Look for dynamic blocks first (dynamic "name" { ... })
        dynamic_match = re.match(r'dynamic\s+"([^"]+)"\s*\{', line)
        
        if dynamic_match:
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
        else:
            # Look for structure blocks (parameter_name { ... }) at any nesting level
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
                
                # Determine parameter type based on context
                param_type = 'structure'
                if block_type == 'terraform' and param_name == 'required_providers':
                    param_type = 'required_provider'
                elif block_type == 'provider':
                    param_type = 'provider'
                
                parameters.append({
                    'type': param_type,
                    'name': param_name,
                    'start_line': block_start,
                    'end_line': block_end
                })
                
                i = j
            else:
                # Look for advanced parameter assignments (parameter_name = { ... }) first
                advanced_assignment_match = re.match(r'(\w+)\s*=\s*\{', line)
                
                if advanced_assignment_match:
                    # This is an advanced parameter assignment (map or array)
                    param_name = advanced_assignment_match.group(1)
                    param_line = resource_start_line + i
                    
                    # Find the end of this advanced parameter
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
                    
                    # Determine parameter type based on context
                    param_type = 'advanced'
                    # Check if we're in a terraform block and this is a provider assignment
                    if block_type == 'terraform':
                        # Look for required_providers in the current context
                        for k in range(max(0, i-10), i):
                            if k < len(resource_lines) and 'required_providers' in resource_lines[k]:
                                param_type = 'required_provider'
                                break
                    
                    parameters.append({
                        'type': param_type,
                        'name': param_name,
                        'start_line': param_line,
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
    
    return parameters


def _extract_nested_parameters(resource_lines: List[str], resource_start_line: int) -> List[Dict]:
    """
    Extract parameters from nested structure blocks like required_providers.
    
    Args:
        resource_lines (List[str]): Lines of the resource block
        resource_start_line (int): Starting line number of the resource
        
    Returns:
        List[Dict]: List of nested parameter information
    """
    nested_parameters = []
    i = 1  # Skip the resource declaration line
    
    while i < len(resource_lines):
        line = resource_lines[i].strip()
        
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Look for structure blocks (parameter_name { ... }) or structure block assignments (parameter_name = { ... })
        block_match = re.match(r'(\w+)\s*\{', line)
        structure_assignment_match = re.match(r'(\w+)\s*=\s*\{', line)
        
        if block_match or structure_assignment_match:
            param_name = block_match.group(1) if block_match else structure_assignment_match.group(1)
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
            
            # Add the structure block itself if it's a provider assignment within required_providers
            if structure_assignment_match:
                # Check if this is within a required_providers block by looking at the context
                # We need to determine if this is a provider assignment or a regular advanced parameter
                is_provider_assignment = False
                
                # Look backwards to see if we're inside a required_providers block
                for prev_param in reversed(nested_parameters):
                    if prev_param['name'] == 'required_providers' and prev_param['type'] == 'required_provider':
                        is_provider_assignment = True
                        break
                
                if is_provider_assignment:
                    # This is a provider assignment within required_providers
                    nested_parameters.append({
                        'type': 'required_provider',
                        'name': param_name,
                        'start_line': block_start,
                        'end_line': block_end
                    })
                    # Skip extracting parameters from within provider blocks
                    i = j
                    continue
            elif block_match and param_name == 'required_providers':
                # This is the required_providers block itself, process its children
                # Extract provider assignments from within this block
                for k in range(i + 1, j):
                    line = resource_lines[k].strip()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    # Look for provider assignments (provider_name = { ... })
                    provider_match = re.match(r'(\w+)\s*=\s*\{', line)
                    
                    if provider_match:
                        provider_name = provider_match.group(1)
                        provider_start = resource_start_line + k
                        
                        # Find the end of this provider assignment
                        brace_count = 1
                        l = k + 1
                        
                        while l < len(resource_lines) and brace_count > 0:
                            current_line = resource_lines[l]
                            for char in current_line:
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                            l += 1
                        
                        provider_end = resource_start_line + l - 1
                        
                        # Add the provider assignment as a required_provider parameter
                        nested_parameters.append({
                            'type': 'required_provider',
                            'name': provider_name,
                            'start_line': provider_start,
                            'end_line': provider_end
                        })
            
            # Extract parameters from within this structure block
            # Process each line within the structure block
            for k in range(i + 1, j):
                line = resource_lines[k].strip()
                
                if not line or line.startswith('#'):
                    continue
                
                # Look for parameter assignments (parameter_name = value or "parameter_name" = value)
                param_match = re.match(r'(\w+|"[^"]+"|\'[^\']+\')\s*=', line)
                
                if param_match:
                    param_name_inner = param_match.group(1)
                    param_line_inner = resource_start_line + k
                    
                    # Determine parameter type based on parent block
                    param_type = 'basic'
                    # Only direct children of required_providers should be required_provider type
                    # If parent is huaweicloud, kubernetes, etc., these are basic parameters within provider blocks
                    if param_name == 'required_providers':
                        # Skip adding parameters from within required_providers block
                        # as they are handled by the provider assignment logic above
                        continue
                    
                    nested_parameters.append({
                        'type': param_type,
                        'name': param_name_inner,
                        'start_line': param_line_inner,
                        'end_line': param_line_inner,
                        'parent_block': param_name
                    })
            
            i = j
        else:
            i += 1
    
    return nested_parameters


def _check_structure_block_end_spacing(parameters: List[Dict], block_name: str, content: str) -> List[Tuple[str, Optional[int]]]:
    """
    Check spacing rules after structure blocks end (when encountering closing braces).
    
    Args:
        parameters (List[Dict]): List of parameters in order
        block_name (str): The block containing these parameters
        content (str): The full file content
        
    Returns:
        List[Tuple[str, Optional[int]]]: List of error messages and optional line numbers
    """
    errors = []
    lines = content.split('\n')
    
    # Sort parameters by their start line
    sorted_params = sorted(parameters, key=lambda x: x['start_line'])
    
    # Find all top-level parameters (those without parent_block)
    top_level_params = [p for p in sorted_params if not p.get('parent_block')]
    
    for i in range(len(top_level_params) - 1):
        current_param = top_level_params[i]
        next_param = top_level_params[i + 1]
        
        # Only check spacing if at least one parameter is a structure block or dynamic block
        if current_param['type'] not in ['structure', 'dynamic'] and next_param['type'] not in ['structure', 'dynamic']:
            continue
        
        # Calculate blank lines between structure block end and next parameter
        current_end = current_param['end_line'] - 1  # Convert to 0-based indexing
        next_start = next_param['start_line'] - 1    # Convert to 0-based indexing
        
        # Count blank lines between the structure block end and next parameter
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
        # Skip spacing check for meta-parameters (these are handled by ST.008)
        meta_parameters = {'count', 'for_each', 'provider', 'lifecycle', 'depends_on'}
        if current_param['name'] in meta_parameters or next_param['name'] in meta_parameters:
            continue
            
        # Skip spacing check for dynamic blocks and their content blocks (these are handled by ST.008)
        # Only skip if the structure block is a content block within the dynamic block
        if (current_param['type'] == 'dynamic' and next_param['type'] == 'structure' and 
            next_param['name'] == 'content') or \
           (current_param['type'] == 'structure' and current_param['name'] == 'content' and 
            next_param['type'] == 'dynamic'):
            continue
        
        # Check spacing rules using the unified error message format
        if blank_lines != 1:
            error_msg = _format_error_message(current_param, next_param, blank_lines, block_name)
            if error_msg:
                errors.append((error_msg, next_param['start_line']))
                
        elif current_param['type'] == 'basic' and next_param['type'] == 'basic':
            # Basic parameter to basic parameter: at most 1 blank line
            if blank_lines > 1:
                error_msg = _format_error_message(current_param, next_param, blank_lines, block_name)
                if error_msg:
                    errors.append((error_msg, next_param['start_line']))
    
    return errors


def _check_parameter_spacing_rules(parameters: List[Dict], block_name: str, content: str) -> List[Tuple[str, Optional[int]]]:
    """
    Check spacing rules between consecutive parameters.

    Args:
        parameters (List[Dict]): List of parameters in order
        block_name (str): The block containing these parameters
        content (str): The full file content

    Returns:
        List[Tuple[str, Optional[int]]]: List of error messages and optional line numbers
    """
    errors = []
    
    # First, check structure block end spacing
    structure_errors = _check_structure_block_end_spacing(parameters, block_name, content)
    errors.extend(structure_errors)
    
    # Then check non-structure parameter spacing
    lines = content.split('\n')
    
    # Sort parameters by their start line to check consecutive parameters
    sorted_params = sorted(parameters, key=lambda x: x['start_line'])
    
    for i in range(len(sorted_params) - 1):
        current_param = sorted_params[i]
        next_param = sorted_params[i + 1]
        
        # Skip if either parameter is a structure block or dynamic block (handled by _check_structure_block_end_spacing)
        if current_param['type'] in ['structure', 'dynamic'] or next_param['type'] in ['structure', 'dynamic']:
            continue
        
        # Skip if either parameter is inside a structure block (has parent_block attribute)
        # But allow checking parameters within the same structure block
        if (current_param.get('parent_block') and not next_param.get('parent_block')) or \
           (next_param.get('parent_block') and not current_param.get('parent_block')):
            continue
        
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
        # Skip spacing check if one parameter is inside a structure block and the other is the structure block itself
        if (current_param.get('parent_block') and next_param['name'] == current_param['parent_block']) or \
           (next_param.get('parent_block') and current_param['name'] == next_param['parent_block']):
            continue
            
        # Skip spacing check for meta-parameters (these are handled by ST.008)
        meta_parameters = {'count', 'for_each', 'provider', 'lifecycle', 'depends_on'}
        if current_param['name'] in meta_parameters or next_param['name'] in meta_parameters:
            continue
            
        # Skip spacing check for dynamic blocks and their content (these are handled by ST.008)
        if (current_param['type'] == 'dynamic' and next_param['type'] == 'structure') or \
           (current_param['type'] == 'structure' and next_param['type'] == 'dynamic'):
            continue
            
        error_msg = _check_spacing_rule(current_param, next_param, blank_lines, block_name)
        if error_msg:
            # Find the first non-empty non-comment line after the problem for error reporting
            error_line = _find_error_reporting_line(lines, current_end, next_start)
            errors.append((error_msg, error_line))
    
    return errors


def _check_spacing_rule(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check specific spacing rules based on parameter types.
    
    This function serves as a unified entry point that delegates to specific
    scenario checking functions. Each scenario is handled independently to
    improve maintainability and testability.

    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name

    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Try each scenario check function in order of specificity
    # More specific rules are checked first to avoid conflicts
    
    # Scenario 1: Structure block and dynamic block with same name
    error_msg = _check_structure_dynamic_same_name_spacing(param1, param2, blank_lines, block_name)
    if error_msg:
        return error_msg
    
    # Scenario 2: Same-name structure blocks
    error_msg = _check_same_name_structure_spacing(param1, param2, blank_lines, block_name)
    if error_msg:
        return error_msg
    
    # Scenario 3: Adjacent dynamic blocks
    error_msg = _check_adjacent_dynamic_spacing(param1, param2, blank_lines, block_name)
    if error_msg:
        return error_msg
    
    # Scenario 4: Different-named structure blocks
    error_msg = _check_different_name_structure_spacing(param1, param2, blank_lines, block_name)
    if error_msg:
        return error_msg
    
    # Scenario 5: Different parameter types
    error_msg = _check_different_type_spacing(param1, param2, blank_lines, block_name)
    if error_msg:
        return error_msg
    
    # Scenario 6: Same-type basic parameters
    error_msg = _check_same_type_basic_spacing(param1, param2, blank_lines, block_name)
    if error_msg:
        return error_msg
    
    # Scenario 7: Same-type required provider blocks
    error_msg = _check_same_type_required_provider_spacing(param1, param2, blank_lines, block_name)
    if error_msg:
        return error_msg
    
    return None


def _check_structure_dynamic_same_name_spacing(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check spacing rule for structure block and dynamic block with same name.
    
    Rule: Structure block and dynamic block with same name must have exactly 1 blank line.
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Check if this is a structure block and dynamic block with same name
    if not ((param1['type'] == 'structure' and param2['type'] == 'dynamic' and param1['name'] == param2['name']) or
            (param1['type'] == 'dynamic' and param2['type'] == 'structure' and param1['name'] == param2['name'])):
        return None
    
    if blank_lines != 1:
        return _format_error_message(param1, param2, blank_lines, block_name)
    
    return None


def _check_same_name_structure_spacing(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check spacing rule for same-name structure blocks.
    
    Rule: Same-name structure blocks must have 0-1 blank lines.
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Check if this is same-name structure blocks
    if not (param1['type'] == 'structure' and param2['type'] == 'structure' and param1['name'] == param2['name']):
        return None
    
    if blank_lines > 1:
        return _format_error_message(param1, param2, blank_lines, block_name)
    
    return None


def _check_adjacent_dynamic_spacing(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check spacing rule for adjacent dynamic blocks.
    
    Rule: Adjacent dynamic blocks must have exactly 1 blank line.
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Check if this is adjacent dynamic blocks
    if not (param1['type'] == 'dynamic' and param2['type'] == 'dynamic'):
        return None
    
    if blank_lines != 1:
        return _format_error_message(param1, param2, blank_lines, block_name)
    
    return None


def _check_different_name_structure_spacing(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check spacing rule for different-named structure blocks.
    
    Rule: Different-named structure blocks must have exactly 1 blank line.
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Check if this is different-named structure blocks
    if not (param1['type'] == 'structure' and param2['type'] == 'structure' and param1['name'] != param2['name']):
        return None
    
    if blank_lines != 1:
        return _format_error_message(param1, param2, blank_lines, block_name)
    
    return None


def _check_different_type_spacing(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check spacing rule for different parameter types.
    
    Rule: Different parameter types must have exactly 1 blank line.
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Check if this is different parameter types
    if param1['type'] == param2['type']:
        return None
    
    if blank_lines != 1:
        return _format_error_message(param1, param2, blank_lines, block_name)
    
    return None


def _check_same_type_basic_spacing(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check spacing rule for same-type basic parameters.
    
    Rule: Same-type basic parameters should not have excessive blank lines (max 1).
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Check if this is same-type basic parameters
    if not (param1['type'] == 'basic' and param2['type'] == 'basic'):
        return None
    
    if blank_lines > 1:
        return _format_error_message(param1, param2, blank_lines, block_name)
    
    return None


def _check_same_type_required_provider_spacing(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> Optional[str]:
    """
    Check spacing rule for same-type required provider blocks.
    
    Rule: Same-type required provider blocks should not have excessive blank lines (max 1).
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        Optional[str]: Error message if violation found, None otherwise
    """
    # Check if this is same-type required provider blocks
    if not (param1['type'] == 'required_provider' and param2['type'] == 'required_provider'):
        return None
    
    if blank_lines > 1:
        return _format_error_message(param1, param2, blank_lines, block_name)
    
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
        'dynamic': 'dynamic block',
        'advanced': 'advanced parameter',
        'required_provider': 'required provider block',
        'provider': 'provider block'
    }
    
    type1_desc = type_map.get(param1['type'], param1['type'])
    type2_desc = type_map.get(param2['type'], param2['type'])
    
    if param1['type'] != param2['type']:
        return f"{type1_desc} and {type2_desc}"
    else:
        return f"{type1_desc}s"


def _get_parameter_type_name(param_type: str) -> str:
    """
    Get the parameter type name for error messages.
    
    Args:
        param_type (str): Parameter type
        
    Returns:
        str: Parameter type name
    """
    type_map = {
        'basic': 'basic parameter',
        'structure': 'structure block',
        'dynamic': 'dynamic block',
        'advanced': 'advanced parameter',
        'required_provider': 'required provider block',
        'provider': 'provider block'
    }
    
    return type_map.get(param_type, param_type)


def _get_recommended_spacing_message(param1: Dict, param2: Dict) -> str:
    """
    Get the recommended spacing message based on parameter types.
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        
    Returns:
        str: Recommended spacing message
    """
    # For basic parameters, same-name structure blocks, or same-type required provider blocks, recommend 0 or 1 blank line
    if (param1['type'] == 'basic' and param2['type'] == 'basic') or \
       (param1['type'] == 'structure' and param2['type'] == 'structure' and param1['name'] == param2['name']) or \
       (param1['type'] == 'required_provider' and param2['type'] == 'required_provider'):
        return "0 or 1 blank line is recommended."
    else:
        return "1 blank line is recommended."


def _format_error_message(param1: Dict, param2: Dict, blank_lines: int, block_name: str) -> str:
    """
    Format error message according to the new specification.
    
    Args:
        param1 (Dict): First parameter
        param2 (Dict): Second parameter
        blank_lines (int): Number of blank lines between parameters
        block_name (str): The block name
        
    Returns:
        str: Formatted error message
    """
    type1_name = _get_parameter_type_name(param1['type'])
    type2_name = _get_parameter_type_name(param2['type'])
    
    # Handle singular/plural for "line"
    line_text = "line" if blank_lines < 2 else "lines"
    
    # Get recommended spacing message
    recommended_msg = _get_recommended_spacing_message(param1, param2)
    
    return f"Found {blank_lines} blank {line_text} between {type1_name} '{param1['name']}' and {type2_name} '{param2['name']}'. {recommended_msg}"


def _find_error_reporting_line(lines: List[str], current_end: int, next_start: int) -> Optional[int]:
    """
    Find the appropriate line for error reporting.

    Args:
        lines (List[str]): File lines
        current_end (int): End line of current parameter (0-based)
        next_start (int): Start line of next parameter (0-based)

    Returns:
        Optional[int]: Line number for error reporting (1-based)
    """
    # For spacing issues, report the line where the next parameter starts
    # This is more intuitive as it points to where the spacing problem occurs
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
            "Validates parameter block spacing within Terraform resource, data source, provider, terraform, and locals blocks. "
            "This ensure consistent spacing between different types of parameters: basic parameters, structure "
            "blocks, and dynamic blocks."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Proper spacing between different parameter types improves code readability by creating "
            "clear visual separation between basic parameter definitions, structure blocks, and "
            "dynamic blocks. This makes it easier to scan through resource, data source, provider, "
            "terraform, and locals definitions and understand the logical organization of configuration parameters."
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