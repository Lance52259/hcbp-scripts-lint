#!/usr/bin/env python3
"""
IO.002 - Output Definition File Organization Check

This module implements the IO.002 rule which checks that all output variables
(if any) in TF scripts within each directory are defined in the outputs.tf file
in the same directory level.

Rule Specification:
- All output definitions must be defined in the outputs.tf file in the same directory
- Output definitions in other TF files will be flagged as violations
- Helps maintain consistent project structure and organization
- Only applies when output definitions exist in the directory

Examples:
    Valid organization:
        # outputs.tf
        output "instance_id" {
          description = "The ID of the created ECS instance"
          value       = huaweicloud_compute_instance.test.id
        }

    Invalid organization:
        # main.tf (should not contain output definitions)
        output "instance_id" {
          description = "The ID of the created ECS instance"
          value       = huaweicloud_compute_instance.test.id
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, List, Dict, Any, Optional


def check_io002_output_file_location(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate output definition file organization according to IO.002 rule specifications.
    
    This function validates that all output definitions are properly organized 
    in outputs.tf files within their respective directories. It ensures that 
    outputs are defined in the correct location for better code organization 
    and maintainability.
    
    The validation process:
    1. Check if the current file contains output definitions
    2. Verify that output definitions are in the appropriate outputs.tf file
    3. Report violations for each misplaced output definition individually
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to check for output definitions.
        log_error_func (Callable[[str, str, str, Optional[int]], None]): 
                      Callback function for logging validation errors. The function
                      signature expects (file_path, rule_id, error_message, line_number).
                      The line_number parameter is optional and can be None.
    
    Returns:
        None: This function doesn't return any value. All validation results
              are communicated through the log_error_func callback.
    
    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    
    Example:
        >>> def sample_log_func(path, rule, msg, line_num):
        ...     print(f"{rule} at {path}: {msg}")
        >>> 
        >>> # Content with output definition in wrong file
        >>> content = '''
        ... output "example" {
        ...   value = var.example
        ... }
        ... '''
        >>> check_io002_output_file_location("main.tf", content, sample_log_func)
        IO.002 at main.tf: Output 'example' should be defined in 'outputs.tf'
    """
    outputs = _extract_outputs(content)
    
    # Check if non-outputs.tf files contain output definitions
    if outputs and not file_path.endswith('outputs.tf'):
        for output in outputs:
            log_error_func(
                file_path,
                "IO.002",
                f"Output '{output['name']}' should be defined in 'outputs.tf'",
                output['line_number']
            )


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from content for parsing, but preserve line structure.

    This helper function removes all comments from the Terraform content
    while maintaining the line structure for accurate parsing.

    Args:
        content (str): The original file content

    Returns:
        str: Content with comments removed
    """
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        # Remove comments but keep the line structure
        if '#' in line:
            # Find the first # that's not inside quotes
            in_quotes = False
            quote_char = None
            for i, char in enumerate(line):
                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                elif char == '#' and not in_quotes:
                    line = line[:i]
                    break
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def _extract_outputs(content: str) -> List[Dict[str, Any]]:
    """
    Extract output definitions with their metadata from the content.

    This function parses the content to find all output definitions and
    extracts relevant metadata for validation purposes.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[Dict[str, Any]]: List of output definitions with metadata including line numbers
    """
    outputs = []
    clean_content = _remove_comments_for_parsing(content)
    original_lines = content.split('\n')
    
    # Pattern to match output blocks - support quoted, single-quoted, and unquoted syntax
    output_pattern = r'output\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    
    # Find all output matches with their positions
    for match in re.finditer(output_pattern, clean_content, re.DOTALL):
        # Extract output name from quoted, single-quoted, or unquoted group
        output_name = match.group(1) if match.group(1) else (match.group(2) if match.group(2) else match.group(3))
        output_body = match.group(4)
        
        # Find the line number where this output starts
        # Count newlines before the match start to get line number
        preceding_text = clean_content[:match.start()]
        line_number = preceding_text.count('\n') + 1
        
        # Find the actual line number in original content by matching the output declaration
        actual_line_number = None
        for line_num, line in enumerate(original_lines, 1):
            if f'output "{output_name}"' in line or f'output \'{output_name}\'' in line or f'output {output_name}' in line:
                actual_line_number = line_num
                break
        
        output_info = {
            'name': output_name,
            'line_number': actual_line_number or line_number,
            'has_description': bool(re.search(r'description\s*=', output_body)),
            'body': output_body.strip()
        }
        outputs.append(output_info)
    
    return outputs


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.002 rule.

    This function provides metadata about the rule including its purpose,
    validation criteria, and examples. This information can be used for
    documentation generation, help systems, or configuration interfaces.

    Returns:
        dict: A dictionary containing comprehensive rule information including:
            - id: The unique rule identifier
            - name: Human-readable rule name
            - description: Detailed explanation of what the rule validates
            - category: The rule category (Input/Output)
            - severity: The severity level of violations
            - examples: Dictionary with valid and invalid examples

    Example:
        >>> info = get_rule_description()
        >>> print(info['name'])
        Output definition file organization check
    """
    return {
        "id": "IO.002",
        "name": "Output definition file organization check",
        "description": (
            "Validates that each output variable is properly defined in "
            "the outputs.tf file and not in other files. Each output "
            "definition found in non-outputs.tf files will be reported "
            "as a separate violation."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Organizing all output definitions in a dedicated outputs.tf file "
            "within the same directory improves project structure consistency, "
            "facilitates centralized output management, and enhances code "
            "maintainability. This follows Terraform community best practices "
            "for project organization."
        ),
        "examples": {
            "valid": [
                '''
# outputs.tf
output "instance_id" {
  description = "The ID of the created ECS instance"
  value       = huaweicloud_compute_instance.test.id
}

# main.tf
resource "huaweicloud_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}''',
                '''# outputs.tf
output "location" {
  description = "Location of the resource group"
  value       = huaweicloud_resource_group.test.location
}'''
            ],
            "invalid": [
                '''# main.tf (should not contain output definitions)
output "resource_group_name" {
  value       = huaweicloud_resource_group.test.id
}''',
                '''# variables.tf (should not contain output definitions)
output "location" {
  description = "Location of the resource group"
  value       = huaweicloud_resource_group.test.location
}'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal"
    }
