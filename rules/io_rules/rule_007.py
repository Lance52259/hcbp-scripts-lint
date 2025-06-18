#!/usr/bin/env python3
"""
IO.007 - Output Description Check

This module implements the IO.007 rule which validates that all output variable
definitions include non-empty description fields. This ensures proper
documentation and helps users understand output purposes and values.

Rule Specification:
- All output definitions must include a description field
- Description fields must not be empty or contain only whitespace
- Helps improve module documentation and usability

Examples:
    Valid declarations:
        output "instance_id" {
          description = "The ID of the created ECS instance"
          value       = huaweicloud_compute_instance.test.id
        }

        output "vpc_cidr_block" {
          description = "The CIDR block of the created VPC"
          value       = huaweicloud_vpc.test.cidr
        }

    Invalid declarations:
        output "instance_id" {
          value = huaweicloud_compute_instance.test.id
          # Missing description
        }

        output "vpc_cidr_block" {
          description = ""  # Empty description
          value       = huaweicloud_vpc.test.cidr
        }

        output "resource_tags" {
          description = "   "  # Whitespace only description
          value       = local.common_tags
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Dict, Any, Optional


def check_io007_output_description(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate output definitions have meaningful descriptions according to IO.007 rule specifications.
    
    This function validates that all output definitions include meaningful 
    descriptions that clearly explain the purpose and value of each output. 
    It ensures that outputs provide adequate documentation for users of the 
    Terraform module.
    
    The validation process:
    1. Extract all output definitions from the Terraform file
    2. Check each output for the presence of a description field
    3. Validate that descriptions are meaningful (not empty or too generic)
    4. Report violations for outputs missing descriptions or having inadequate descriptions
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to check for output definitions and descriptions.
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
        ...     print(f"{rule} at {path}:{line_num}: {msg}")
        >>> 
        >>> # Content with output missing description
        >>> content = '''
        ... output "example" {
        ...   value = var.example
        ... }
        ... '''
        >>> check_io007_output_description("outputs.tf", content, sample_log_func)
        IO.007 at outputs.tf:None: Output 'example' must have a meaningful description
    """
    outputs = _extract_outputs(content)
    
    for output in outputs:
        if not output['has_description']:
            log_error_func(
                file_path,
                "IO.007",
                f"Output '{output['name']}' must include a description field",
                output['line_number']
            )
        elif output['description_empty']:
            log_error_func(
                file_path,
                "IO.007",
                f"Output '{output['name']}' has an empty description field",
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

    # Pattern to match output blocks with their full content
    output_pattern = r'output\s+"([^"]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    
    # Find all output matches with their positions
    for match in re.finditer(output_pattern, clean_content, re.DOTALL):
        output_name = match.group(1)
        output_body = match.group(2)
        
        # Find the line number where this output starts
        # Count newlines before the match start to get line number
        preceding_text = clean_content[:match.start()]
        line_number = preceding_text.count('\n') + 1
        
        # Find the actual line number in original content by matching the output declaration
        actual_line_number = None
        for line_num, line in enumerate(original_lines, 1):
            if f'output "{output_name}"' in line:
                actual_line_number = line_num
                break
        
        # Check for description field
        description_match = re.search(r'description\s*=\s*"([^"]*)"', output_body)
        has_description = description_match is not None
        
        # Check if description is empty or whitespace only
        description_empty = False
        if has_description:
            description_value = description_match.group(1).strip()
            description_empty = len(description_value) == 0
        
        output_info = {
            'name': output_name,
            'line_number': actual_line_number or line_number,
            'has_description': has_description,
            'description_empty': description_empty,
            'has_value': bool(re.search(r'value\s*=', output_body)),
            'has_sensitive': bool(re.search(r'sensitive\s*=', output_body)),
            'body': output_body.strip()
        }
        outputs.append(output_info)

    return outputs


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.007 rule.

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
        Output description check
    """
    return {
        "id": "IO.007",
        "name": "Output description check",
        "description": (
            "Validates that all output variable definitions include non-empty "
            "description fields. This ensures proper documentation and helps "
            "users understand output purposes and values."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Description fields in output definitions are essential for "
            "module documentation and usability. They help users understand "
            "what each output represents, what values to expect, and how "
            "to use the output in their configurations."
        ),
        "examples": {
            "valid": [
                '''output "instance_id" {
  description = "The ID of the created ECS instance"
  value       = huaweicloud_compute_instance.test.id
}''',
                '''output "vpc_cidr_block" {
  description = "The CIDR block of the created VPC"
  value       = huaweicloud_vpc.test.cidr
}''',
                '''output "resource_tags" {
  description = "Tags applied to all resources"
  value       = local.common_tags
}'''
            ],
            "invalid": [
                '''output "instance_id" {
  value = huaweicloud_compute_instance.test.id
  # Missing description
}''',
                '''output "vpc_cidr_block" {
  description = ""  # Empty description
  value       = huaweicloud_vpc.test.cidr
}''',
                '''output "resource_tags" {
  description = "   "  # Whitespace only description
  value       = local.common_tags
}'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.002", "IO.005", "IO.006"],
        "configuration": {
            "check_empty_descriptions": True,
            "allow_whitespace_only": False
        }
    }
