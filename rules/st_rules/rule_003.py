#!/usr/bin/env python3
"""
ST.003 - Parameter Alignment Check

This module implements the ST.003 rule which validates that parameter assignments
in resource and data blocks have proper spacing around equals signs and maintain
consistent alignment within code blocks.

Rule Specification:
- Equals signs must be aligned within the same code block
- Aligned equals signs should maintain one space from the longest parameter name in the code block
- Exactly one space after the equals sign and parameter value

Examples:
    Valid declarations:
        data "huaweicloud_compute_flavors" "test" {
          performance_type = "normal"
          cpu_core_count   = 4
          memory_size      = 8
        }

        resource "huaweicloud_compute_instance" "test" {
          name               = "tf_test_instance"
          flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
          security_group_ids = [huaweicloud_networking_secgroup.test.id]
          # ...
        }

    Invalid declarations:
        data "huaweicloud_compute_flavors" "test" {
          performance_type="normal"    # No spaces around equals
          cpu_core_count= 4            # No space before equals
          memory_size =8               # No space after equals
        }

        resource "huaweicloud_compute_instance" "test" {
          # Parameter equal signs are not aligned or not properly spaced
          name = "tf_test_instance"
          flavor_id = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
          security_group_ids = [huaweicloud_networking_secgroup.test.id]
          # ...
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Optional


def check_st003_parameter_alignment(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate parameter alignment in data sources and resource blocks according to ST.003 rule specifications.

    This function scans through the provided Terraform file content and validates
    that parameter assignments within data source and resource blocks are properly
    aligned. This ensures consistent code formatting and improves readability
    across the entire codebase.

    The validation process:
    1. Remove comments from content for accurate parsing
    2. Extract all data source and resource blocks
    3. Split each block into sections separated by blank lines
    4. Check parameter alignment within each section
    5. Report violations through the error logging function

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.

        content (str): The complete content of the Terraform file as a string.
                      This includes all data source and resource blocks.

        log_error_func (Callable[[str, str, str, Optional[int]], None]): A callback function used
                      to report rule violations. The function should accept four
                      parameters: file_path, rule_id, error_message, and line_number.
                      The line_number parameter is optional and can be None.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    """
    clean_content = _remove_comments_for_parsing(content)
    blocks = _extract_code_blocks(clean_content)

    for block_type, start_line, block_lines in blocks:
        sections = _split_into_code_sections(block_lines)
        for section in sections:
            errors = _check_parameter_alignment_in_section(section, block_type, start_line)
            for line_num, error_msg in errors:
                log_error_func(file_path, "ST.003", error_msg, line_num)


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from content for parsing, but preserve line structure.

    Args:
        content (str): The original file content

    Returns:
        str: Content with comments removed
    """
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        if '#' in line:
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


def _extract_code_blocks(content: str) -> List[Tuple[str, int, List[str]]]:
    """
    Extract data source and resource code blocks.

    Args:
        content (str): The cleaned Terraform content

    Returns:
        List[Tuple[str, int, List[str]]]: List of (block_type, start_line, block_lines)
    """
    lines = content.split('\n')
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Support quoted, single-quoted, and unquoted syntax
        # Quoted: data "type" "name" { ... } or resource "type" "name" { ... } or provider "type" { ... }
        # Single-quoted: data 'type' 'name' { ... } or resource 'type' 'name' { ... } or provider 'type' { ... }
        # Unquoted: data type name { ... } or resource type name { ... } or provider type { ... }
        data_match = re.match(r'data\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        resource_match = re.match(r'resource\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        provider_match = re.match(r'provider\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)

        if data_match or resource_match or provider_match:
            if data_match:
                # Get data type and name from quoted, single-quoted, or unquoted groups
                data_type = data_match.group(1) if data_match.group(1) else (data_match.group(2) if data_match.group(2) else data_match.group(3))
                data_name = data_match.group(4) if data_match.group(4) else (data_match.group(5) if data_match.group(5) else data_match.group(6))
                block_type = f"data.{data_type}.{data_name}"
            elif resource_match:
                # Get resource type and name from quoted, single-quoted, or unquoted groups
                resource_type = resource_match.group(1) if resource_match.group(1) else (resource_match.group(2) if resource_match.group(2) else resource_match.group(3))
                resource_name = resource_match.group(4) if resource_match.group(4) else (resource_match.group(5) if resource_match.group(5) else resource_match.group(6))
                block_type = f"resource.{resource_type}.{resource_name}"
            else:  # provider_match
                # Get provider type from quoted, single-quoted, or unquoted groups
                provider_type = provider_match.group(1) if provider_match.group(1) else (provider_match.group(2) if provider_match.group(2) else provider_match.group(3))
                block_type = f"provider.{provider_type}"
                
            start_line = i + 1
            block_lines = []
            brace_count = 1
            i += 1

            # Check if the opening brace is on the same line as the declaration
            if '{' in line and '}' in line:
                # Single line block like: data "type" "name" { }
                # No additional lines to process
                pass
            else:
                # Multi-line block, process until we find the closing brace
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    block_lines.append(current_line)
                    for char in current_line:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                    i += 1

                # Remove the last line if it contains only the closing brace
                if block_lines and block_lines[-1].strip() == '}':
                    block_lines = block_lines[:-1]

            blocks.append((block_type, start_line, block_lines))
        else:
            i += 1

    return blocks


def _split_into_code_sections(block_lines: List[str]) -> List[List[Tuple[str, int]]]:
    """
    Split code block by empty lines into multiple sections.

    Args:
        block_lines (List[str]): Lines within a code block

    Returns:
        List[List[Tuple[str, int]]]: Sections with (line_content, line_index) tuples
    """
    sections = []
    current_section = []

    for line_idx, line in enumerate(block_lines):
        if line.strip() == '':
            if current_section:
                sections.append(current_section)
                current_section = []
        else:
            current_section.append((line, line_idx))

    if current_section:
        sections.append(current_section)

    return sections


def _check_parameter_alignment_in_section(
    section: List[Tuple[str, int]], block_type: str, block_start_line: int
) -> List[Tuple[int, str]]:
    """
    Check parameter alignment in a code section.

    Args:
        section: List of (line_content, relative_line_idx) tuples
        block_type: Type of the block being checked
        block_start_line: Starting line number of the block

    Returns:
        List[Tuple[int, str]]: List of (line_number, error_message) tuples
    """
    errors = []
    parameter_lines = []
    base_indent = None

    for line_content, relative_line_idx in section:
        line = line_content.rstrip()
        if '=' in line and not line.strip().startswith('#'):
            if not re.match(r'^\s*(data|resource|variable|output|locals|module)\s+', line):
                # Calculate indentation level, treating tabs as equivalent to spaces
                # Convert tabs to spaces for consistent indentation calculation
                line_with_spaces = line.expandtabs(2)  # Convert tabs to 2 spaces
                indent_level = len(line_with_spaces) - len(line_with_spaces.lstrip())

                if base_indent is None:
                    base_indent = indent_level
                    parameter_lines.append((line, relative_line_idx))
                elif indent_level == base_indent:
                    parameter_lines.append((line, relative_line_idx))

    # Even with single parameter, we can check for basic spacing issues
    if len(parameter_lines) == 0:
        return errors

    # First, find the longest parameter name and calculate expected equals position
    longest_param_name_length = 0
    param_names = []
    
    for line, relative_line_idx in parameter_lines:
        equals_pos = line.find('=')
        if equals_pos == -1:
            continue
            
        before_equals = line[:equals_pos]
        param_name_part = before_equals.strip()
        
        # Extract parameter name (remove indentation and quotes if any)
        param_name_match = re.match(r'^\s*(["\']?)([^"\'=\s]+)\1\s*$', before_equals)
        if param_name_match:
            param_name = param_name_match.group(2)
            param_names.append((param_name, line, relative_line_idx))
            longest_param_name_length = max(longest_param_name_length, len(param_name))

    if not param_names:
        return errors

    # Calculate expected equals position: base_indent + longest_param_name + 1 space
    expected_equals_pos = base_indent + longest_param_name_length + 1

    # Check each parameter line
    for param_name, line, relative_line_idx in param_names:
        actual_line_num = block_start_line + relative_line_idx + 1
        equals_pos = line.find('=')
        
        if equals_pos == -1:
            continue

        before_equals = line[:equals_pos]
        after_equals = line[equals_pos + 1:]

        # Check if there's exactly one space after equals sign
        if not after_equals.startswith(' '):
            errors.append((
                actual_line_num,
                f"Parameter assignment should have exactly one space after '=' in {block_type}"
            ))
            continue
        elif after_equals.startswith('  '):
            errors.append((
                actual_line_num,
                f"Parameter assignment should have exactly one space after '=' in {block_type}, found multiple spaces"
            ))
            continue

        # Check if there's at least one space before equals sign
        if not before_equals.endswith(' '):
            errors.append((
                actual_line_num,
                f"Parameter assignment should have at least one space before '=' in {block_type}"
            ))

        # Only check alignment if we have multiple parameters
        if len(param_names) > 1:
            # Check if equals sign is at the expected position
            if equals_pos != expected_equals_pos:
                # Calculate how many spaces should be between parameter name and equals sign
                required_spaces_before_equals = expected_equals_pos - base_indent - len(param_name)
                
                if equals_pos < expected_equals_pos:
                    errors.append((
                        actual_line_num,
                        f"Parameter assignment equals sign not aligned in {block_type}. "
                        f"Expected {required_spaces_before_equals} spaces between parameter name and '=', "
                        f"equals sign should be at column {expected_equals_pos + 1}"
                    ))
                elif equals_pos > expected_equals_pos:
                    errors.append((
                        actual_line_num,
                        f"Parameter assignment equals sign not aligned in {block_type}. "
                        f"Too many spaces before '=', equals sign should be at column {expected_equals_pos + 1}"
                    ))

    return errors


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the ST.003 rule.

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
        Parameter alignment check
    """
    return {
        "id": "ST.003",
        "name": "Parameter alignment check",
        "description": (
            "Validates that parameter assignments in resource, data, and provider blocks "
            "have equals signs aligned, with aligned equals signs maintaining one space "
            "from the longest parameter name in the code block and one space "
            "between the equals sign and parameter value. This ensures code readability and "
            "follows Terraform formatting standards."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Proper parameter alignment with consistent spacing improves code readability and maintains "
            "consistent formatting standards. Aligning equals signs with proper spacing from the longest "
            "parameter name makes it easier to scan through configuration parameters and understand "
            "the structure at a glance."
        ),
        "examples": {
            "valid": [
                '''
data "huaweicloud_compute_flavors" "test" {
  performance_type = "normal"
  cpu_core_count   = 4
  memory_size      = 8
}

resource "huaweicloud_compute_instance" "test" {
  name               = "tf_test_instance"
  flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
  security_group_ids = [huaweicloud_networking_secgroup.test.id]
  # ...
}

provider "huaweicloud" {
  region     = var.region_name
  access_key = var.access_key
  secret_key = var.secret_key
}
'''
            ],
            "invalid": [
                '''
data "huaweicloud_compute_flavors" "test" {
  performance_type="normal"    # No spaces around equals
  cpu_core_count= 4            # No space before equals
  memory_size =8               # No space after equals
}

resource "huaweicloud_compute_instance" "test" {
  # Parameter equal signs are not aligned or properly spaced
  name = "tf_test_instance"
  flavor_id = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
  security_group_ids = [huaweicloud_networking_secgroup.test.id]
  # ...
}

provider "huaweicloud" {
  region = var.region_name      # Equals signs not aligned
  access_key= var.access_key    # No space before equals
  secret_key =var.secret_key    # No space after equals
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal"
    }
