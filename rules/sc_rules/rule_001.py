#!/usr/bin/env python3
"""
SC.001 - Array Index Access Safety Check

Validates that array index access operations use try() function to prevent
index out of bounds errors in specific scenarios:

1. Data source list attribute references
2. Optional list parameter (input variables) element references  
3. For expressions in local variables or resource parameter expressions

Purpose:
- Prevents runtime errors from array index out of bounds
- Ensures safe handling of data source query results
- Promotes defensive programming practices for list variable access
- Validates safe usage of HCL for expressions with array indexing
- Improves Terraform configuration reliability

Rule Details:
- Detects unsafe array index access in data source references
- Validates safe access to optional input variable list elements
- Checks for expression list access patterns in locals and resources
- Reports violations with specific line numbers and safety suggestions

Common Scenarios:
1. Data source returns empty list when no matching resources found
2. Optional input variables might be empty lists
3. For expressions generating dynamic lists that could be empty

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, Optional, List, Tuple, Set


def check_sc001_array_index_safety(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check for unsafe array index access in Terraform files.
    
    This rule validates safe array index access in three scenarios:
    1. Data source list attribute references (data.xxx.yyy.list[0])
    2. Optional list parameter element references (var.list_variable[0])
    3. For expressions in local variables or resource parameter expressions (local.for_result[0])
    
    Args:
        file_path (str): Path to the Terraform file being checked
        content (str): Content of the Terraform file
        log_error_func (Callable): Function to log errors with signature (file_path, rule_id, message, line_num)
    """
    # Extract list variables from all .tf files in the same directory
    file_dir = os.path.dirname(file_path)
    list_variables = _extract_list_variables_from_directory(file_dir)
    
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Find all unsafe array index access patterns
        unsafe_patterns = []
        
        # 1. Data source list attribute references
        unsafe_patterns.extend(_find_data_source_index_access(line))
        
        # 2. Optional list parameter element references
        unsafe_patterns.extend(_find_variable_index_access(line, list_variables))
        
        # 3. For expressions in local variables or resource parameter expressions
        unsafe_patterns.extend(_find_for_expression_index_access(line))
        
        # Log errors for each unsafe pattern found
        for pattern_info in unsafe_patterns:
            pattern, start_pos, suggestion, scenario = pattern_info
            
            # Check if this index access is already wrapped in try()
            if not _is_wrapped_in_try(line, start_pos):
                error_msg = f"Unsafe array index access detected in {scenario}: '{pattern}'. Use try() function to prevent index out of bounds errors. Suggestion: {suggestion}"
                log_error_func(file_path, "SC.001", error_msg, line_num)


def _extract_list_variables_from_directory(directory: str) -> Set[str]:
    """
    Extract variable names that are defined as list types from all .tf files in the directory.
    
    Args:
        directory (str): Directory path to search for .tf files
        
    Returns:
        Set[str]: Set of variable names that are list types
    """
    list_variables = set()
    
    # Find all .tf files in the directory
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.tf'):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        list_variables.update(_extract_list_variables(content))
                except (IOError, UnicodeDecodeError):
                    # Skip files that can't be read
                    continue
    
    return list_variables


def _extract_list_variables(content: str) -> Set[str]:
    """
    Extract variable names that are defined as list types.
    
    Args:
        content (str): File content to analyze
        
    Returns:
        Set[str]: Set of variable names that are list types
    """
    list_variables = set()
    lines = content.split('\n')
    
    in_variable_block = False
    current_variable = None
    
    for line in lines:
        stripped = line.strip()
        
        # Start of variable block
        variable_match = re.match(r'variable\s+"([^"]+)"\s*\{', stripped)
        if variable_match:
            current_variable = variable_match.group(1)
            in_variable_block = True
            continue
        
        # End of variable block
        if in_variable_block and stripped == '}':
            in_variable_block = False
            current_variable = None
            continue
        
        # Type declaration within variable block
        if in_variable_block and current_variable:
            type_match = re.match(r'type\s*=\s*list\(', stripped)
            if type_match:
                list_variables.add(current_variable)
    
    return list_variables


def _find_data_source_index_access(line: str) -> List[Tuple[str, int, str, str]]:
    """
    Find unsafe data source array index access patterns.
    
    Args:
        line (str): Line to analyze
        
    Returns:
        List[Tuple[str, int, str, str]]: List of (pattern, position, suggestion, scenario) tuples
    """
    patterns = []
    
    # Pattern: data.source_type.name.attribute[index]
    # Matches: data.huaweicloud_compute_flavors.test.flavors[0].id
    data_pattern = r'data\.[\w_]+\.[\w_]+\.[\w_]+\[\d+\](?:\.[\w_]+)*'
    
    for match in re.finditer(data_pattern, line):
        pattern = match.group(0)
        start_pos = match.start()
        
        # Generate suggestion with try() wrapper
        suggestion = f"try({pattern}, \"default_value\")"
        scenario = "data source list attribute"
        
        patterns.append((pattern, start_pos, suggestion, scenario))
    
    return patterns


def _find_variable_index_access(line: str, list_variables: set) -> List[Tuple[str, int, str, str]]:
    """
    Find unsafe input variable array index access patterns.
    
    Args:
        line (str): Line to analyze
        list_variables (set): Set of known list variable names
        
    Returns:
        List[Tuple[str, int, str, str]]: List of (pattern, position, suggestion, scenario) tuples
    """
    patterns = []
    
    # Pattern: var.variable_name[index]
    var_pattern = r'var\.([\w_]+)\[\d+\](?:\.[\w_]+)*'
    
    for match in re.finditer(var_pattern, line):
        variable_name = match.group(1)
        
        # Only check variables that are defined as list types
        if variable_name in list_variables:
            pattern = match.group(0)
            start_pos = match.start()
            
            # Generate suggestion with try() wrapper
            suggestion = f"try({pattern}, \"default_value\")"
            scenario = "optional list parameter"
            
            patterns.append((pattern, start_pos, suggestion, scenario))
    
    return patterns


def _find_for_expression_index_access(line: str) -> List[Tuple[str, int, str, str]]:
    """
    Find unsafe for expression result array index access patterns.
    
    Args:
        line (str): Line to analyze
        
    Returns:
        List[Tuple[str, int, str, str]]: List of (pattern, position, suggestion, scenario) tuples
    """
    patterns = []
    
    # Pattern 1: local.variable_name[index] (could be result of for expression)
    local_pattern = r'local\.([\w_]+)\[\d+\](?:\.[\w_]+)*'
    
    for match in re.finditer(local_pattern, line):
        pattern = match.group(0)
        start_pos = match.start()
        
        # Generate suggestion with try() wrapper
        suggestion = f"try({pattern}, \"default_value\")"
        scenario = "for expression result"
        
        patterns.append((pattern, start_pos, suggestion, scenario))
    
    # Pattern 2: Direct for expression with index access
    # This is more complex and would require multi-line analysis
    # For now, focus on the result access pattern above
    
    return patterns


def _is_wrapped_in_try(line: str, index_pos: int) -> bool:
    """
    Check if the array index access at given position is wrapped in try() function.
    
    Args:
        line (str): The line containing the index access
        index_pos (int): Position of the index access pattern
        
    Returns:
        bool: True if wrapped in try(), False otherwise
    """
    # Look for try( before the index access position
    try_pattern = r'try\s*\('
    
    # Search backwards from the index position
    line_before_index = line[:index_pos]
    
    # Find all try( occurrences before the index position
    try_matches = list(re.finditer(try_pattern, line_before_index))
    
    if not try_matches:
        return False
    
    # Check if any try( has a matching closing parenthesis after the index access
    for try_match in try_matches:
        try_start = try_match.end() - 1  # Position of the opening parenthesis
        
        # Count parentheses to find the matching closing parenthesis
        paren_count = 1
        pos = try_start + 1
        
        while pos < len(line) and paren_count > 0:
            if line[pos] == '(':
                paren_count += 1
            elif line[pos] == ')':
                paren_count -= 1
            pos += 1
        
        # If we found a matching closing parenthesis after the index access
        if paren_count == 0 and pos > index_pos:
            return True
    
    return False


def get_rule_description() -> dict:
    """
    Get the rule description for SC.001.
    
    Returns:
        dict: Rule description containing metadata and details
    """
    return {
        "rule_id": "SC.001",
        "title": "Array Index Access Safety Check",
        "category": "Security Code",
        "severity": "warning",
        "description": "Validates that array index access uses try() function to prevent index out of bounds errors in specific scenarios",
        "rationale": "Array index access can fail when data sources return empty results, variables are empty lists, or for expressions produce empty results",
        "scope": ["data_source_access", "variable_access", "for_expression_access"],
        "implementation": "modular",
        "version": "2.0.0",
        "scenarios": {
            "data_source": "Data source list attribute references that might return empty results",
            "input_variables": "Optional list parameter (input variables) element references", 
            "for_expressions": "For expressions in local variables or resource parameter expressions"
        },
        "examples": {
            "valid": [
                'flavor_id = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")',
                'subnet_id = try(var.subnet_ids[0], "default_subnet")',
                'first_ip = try(local.instance_ips[0], "10.0.0.1")'
            ],
            "invalid": [
                'flavor_id = data.huaweicloud_compute_flavors.test.flavors[0].id',
                'subnet_id = var.subnet_ids[0]',
                'first_ip = local.instance_ips[0]'
            ]
        },
        "fix_suggestions": [
            "Wrap data source array index access in try() function with appropriate default value",
            "Use try(var.list_variable[index], default_value) pattern for list variables",
            "Protect for expression result access with try() function",
            "Consider checking array length before accessing specific indices",
            "Provide meaningful default values based on your use case"
        ]
    } 