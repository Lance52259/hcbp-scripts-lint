#!/usr/bin/env python3
"""
ST.006 - Block Spacing Check

This module implements the ST.006 rule which validates that there is exactly
one blank line between different blocks (resources, data sources, variables, 
outputs, locals) in the Terraform file.

Rule Specification:
- Exactly one blank line between different blocks
- Blocks include: resource, data source, variable, output, locals
- Reports specific line numbers for violations
- Handles different scenarios with appropriate error messages

Examples:
    Valid block spacing:
        data "huaweicloud_availability_zones" "test" {
          region = var.region
        }

        resource "huaweicloud_vpc" "test" {
          name = "test-vpc"
          cidr = "10.0.0.0/16"
        }

        variable "vpc_name" {
          description = "VPC name"
          type        = string
        }

    Invalid block spacing:
        data "huaweicloud_availability_zones" "test" {
          region = var.region
        }
        resource "huaweicloud_vpc" "test" {    # Missing blank line
          name = "test-vpc"
          cidr = "10.0.0.0/16"
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Optional


def check_st006_resource_spacing(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate spacing between all types of blocks according to ST.006 rule specifications.

    This function scans through the provided Terraform file content and validates
    that all block types (resource, data source, variable, output, locals) maintain 
    proper spacing between them.

    Args:
        file_path (str): The path to the file being checked
        content (str): The complete content of the Terraform file
        log_error_func (Callable): Function to report rule violations

    Returns:
        None: Reports errors through the log_error_func callback
    """
    blocks = _extract_all_blocks(content)
    
    if len(blocks) < 2:
        return  # No spacing issues if there's only one or no blocks
    
    lines = content.split('\n')
    
    for i in range(len(blocks) - 1):
        current_block = blocks[i]
        next_block = blocks[i + 1]
        
        error_info = _check_block_spacing_detailed(current_block, next_block, lines)
        
        if error_info:
            error_line, error_msg = error_info
            log_error_func(file_path, "ST.006", error_msg, error_line)


def _extract_all_blocks(content: str) -> List[Tuple[str, int, int, str, str]]:
    """
    Extract all blocks (resource, data, variable, output, locals) from content.

    Args:
        content (str): The Terraform file content

    Returns:
        List[Tuple[str, int, int, str, str]]: List of (block_type, start_line, end_line, type_name, instance_name)
    """
    lines = content.split('\n')
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Match different block types
        resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
        data_match = re.match(r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
        # Also match data blocks without quotes around type name (ST.010 violation)
        data_match_no_quotes = re.match(r'data\s+([a-zA-Z0-9_]+)\s+"([^"]+)"\s*\{', line)
        # Also match data blocks with quotes around type but not name (ST.010 violation)
        data_match_mixed_quotes = re.match(r'data\s+"([^"]+)"\s+([a-zA-Z0-9_]+)\s*\{', line)
        # Also match resource blocks without quotes around type name (ST.010 violation)
        resource_match_no_quotes = re.match(r'resource\s+([a-zA-Z0-9_]+)\s+"([^"]+)"\s*\{', line)
        # Also match resource blocks with quotes around type but not name (ST.010 violation)
        resource_match_mixed_quotes = re.match(r'resource\s+"([^"]+)"\s+([a-zA-Z0-9_]+)\s*\{', line)
        variable_match = re.match(r'variable\s+"([^"]+)"\s*\{', line)
        output_match = re.match(r'output\s+"([^"]+)"\s*\{', line)
        locals_match = re.match(r'locals\s*\{', line)
        
        if resource_match:
            block_type = "resource"
            type_name = resource_match.group(1)
            instance_name = resource_match.group(2)
        elif resource_match_no_quotes:
            block_type = "resource"
            type_name = resource_match_no_quotes.group(1)
            instance_name = resource_match_no_quotes.group(2)
        elif resource_match_mixed_quotes:
            block_type = "resource"
            type_name = resource_match_mixed_quotes.group(1)
            instance_name = resource_match_mixed_quotes.group(2)
        elif data_match:
            block_type = "data source"
            type_name = data_match.group(1)
            instance_name = data_match.group(2)
        elif data_match_no_quotes:
            block_type = "data source"
            type_name = data_match_no_quotes.group(1)
            instance_name = data_match_no_quotes.group(2)
        elif data_match_mixed_quotes:
            block_type = "data source"
            type_name = data_match_mixed_quotes.group(1)
            instance_name = data_match_mixed_quotes.group(2)
        elif variable_match:
            block_type = "variable"
            type_name = ""
            instance_name = variable_match.group(1)
        elif output_match:
            block_type = "output"
            type_name = ""
            instance_name = output_match.group(1)
        elif locals_match:
            block_type = "locals"
            type_name = ""
            instance_name = ""
        else:
            i += 1
            continue
        
        start_line = i + 1
        start_line_content = lines[i]
        
        # Special handling for single-line blocks like "data "..." "..." {}"
        if start_line_content.strip().endswith('{}'):
            end_line = i + 1
            blocks.append((block_type, start_line, end_line, type_name, instance_name))
            i += 1
            continue
        
        # Count braces for multi-line blocks
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
        blocks.append((block_type, start_line, end_line, type_name, instance_name))
        i += 1
    
    return blocks


def _check_block_spacing_detailed(
    current_block: Tuple[str, int, int, str, str],
    next_block: Tuple[str, int, int, str, str],
    lines: List[str]
) -> Optional[Tuple[int, str]]:
    """
    Check spacing between two consecutive blocks with detailed error reporting.

    Args:
        current_block: Tuple of (block_type, start_line, end_line, type_name, instance_name)
        next_block: Tuple of (block_type, start_line, end_line, type_name, instance_name)
        lines: List of file lines

    Returns:
        Optional[Tuple[int, str]]: (error_line, error_message) if violation found, None otherwise
    """
    current_type, current_start, current_end, current_type_name, current_instance = current_block
    next_type, next_start, next_end, next_type_name, next_instance = next_block
    
    # Count blank lines between the end of current block and start of next block
    blank_lines = 0
    first_blank_line = None
    comment_lines = 0
    
    for line_idx in range(current_end, next_start - 1):
        if line_idx < len(lines):
            line = lines[line_idx].strip()
            if line == '':
                blank_lines += 1
                if first_blank_line is None:
                    first_blank_line = line_idx + 1
            elif line.startswith('#'):
                comment_lines += 1
    
    # Generate block identifiers for error messages
    current_block_id = _format_block_identifier(current_type, current_type_name, current_instance)
    next_block_id = _format_block_identifier(next_type, next_type_name, next_instance)
    
    if blank_lines == 0:
        # Missing blank line - report at the start of next block
        if comment_lines > 0:
            error_msg = f"Missing blank line between {current_block_id} and {next_block_id}, the number of blank line should be 1."
        else:
            error_msg = f"Missing blank line between {current_block_id} and {next_block_id}, the number of blank line should be 1."
        return next_start, error_msg
    elif blank_lines > 1:
        # Too many blank lines - report at the first extra blank line
        if first_blank_line is not None:
            # Find the line after the first required blank line
            error_line = current_end + 2  # current_end + 1 (first blank line) + 1 (second blank line)
            error_msg = f"Too many blank lines between {current_block_id} and {next_block_id}, the number of blank line should be 1."
            return error_line, error_msg
    
    return None


def _format_block_identifier(block_type: str, type_name: str, instance_name: str) -> str:
    """
    Format block identifier for error messages.

    Args:
        block_type: Type of block (resource, data source, variable, output, locals)
        type_name: Resource/data source type name
        instance_name: Instance name

    Returns:
        str: Formatted block identifier
    """
    if block_type == "resource":
        return f"resource '{type_name}'"
    elif block_type == "data source":
        return f"data source '{type_name}'"
    elif block_type == "variable":
        return f"variable '{instance_name}'"
    elif block_type == "output":
        return f"output '{instance_name}'"
    elif block_type == "locals":
        return "locals"
    else:
        return f"{block_type} '{instance_name}'"


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.006 rule.

    Returns:
        dict: A dictionary containing comprehensive rule information
    """
    return {
        "id": "ST.006",
        "name": "Block spacing check",
        "description": (
            "Validates that there is exactly one blank line between different "
            "blocks (resources, data sources, variables, outputs, locals) to "
            "improve code readability and organization."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Proper spacing between blocks improves code readability by creating "
            "clear visual separation between different infrastructure components. "
            "This makes it easier to scan through large configuration files and "
            "understand the logical organization."
        ),
        "examples": {
            "valid": [
                '''
data "huaweicloud_availability_zones" "test" {
  region = var.region
}

resource "huaweicloud_vpc" "test" {
  name = "test-vpc"
  cidr = "10.0.0.0/16"
}

variable "vpc_name" {
  description = "VPC name"
  type        = string
}
'''
            ],
            "invalid": [
                '''
data "huaweicloud_availability_zones" "test" {
  region = var.region
}
resource "huaweicloud_vpc" "test" {    # Missing blank line
  name = "test-vpc"
  cidr = "10.0.0.0/16"
}


variable "vpc_name" {    # Too many blank lines
  description = "VPC name"
  type        = string
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": ["ST.007", "ST.008"]
    }
