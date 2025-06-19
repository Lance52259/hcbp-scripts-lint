#!/usr/bin/env python3
"""
ST.003 - Parameter Alignment Check

This module implements the ST.003 rule which validates that parameter assignments
in resource and data blocks have proper spacing around equals signs and maintain
consistent alignment within code blocks.

Rule Specification:
- At least one space before the equals sign
- Exactly one space after the equals sign
- Consistent parameter alignment within the same code block

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
          # Parameter equal signs are not aligned
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
        data_match = re.match(r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
        resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)

        if data_match or resource_match:
            block_type = (
                f"data.{data_match.group(1)}.{data_match.group(2)}" if data_match
                else f"resource.{resource_match.group(1)}.{resource_match.group(2)}"
            )
            start_line = i + 1
            block_lines = []
            brace_count = 1
            i += 1

            while i < len(lines) and brace_count > 0:
                current_line = lines[i]
                block_lines.append(current_line)
                for char in current_line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                i += 1

            if block_lines and '}' in block_lines[-1]:
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
                indent_level = len(line) - len(line.lstrip())

                if base_indent is None:
                    base_indent = indent_level
                    parameter_lines.append((line, relative_line_idx))
                elif indent_level == base_indent:
                    parameter_lines.append((line, relative_line_idx))

    if len(parameter_lines) <= 1:
        return errors

    equals_positions = []

    for line, relative_line_idx in parameter_lines:
        actual_line_num = block_start_line + relative_line_idx + 1
        equals_pos = line.find('=')
        if equals_pos == -1:
            continue

        before_equals = line[:equals_pos]
        after_equals = line[equals_pos + 1:]

        if not before_equals.endswith(' '):
            errors.append((
                actual_line_num,
                f"Parameter assignment should have at least one space before '=' in {block_type}"
            ))
            continue

        if not after_equals.startswith(' '):
            errors.append((
                actual_line_num,
                f"Parameter assignment should have exactly one space after '=' in {block_type}"
            ))
            continue
        elif after_equals.startswith('  '):
            errors.append((
                actual_line_num,
                f"Parameter assignment should have exactly one space after '=' in {block_type}, "
                f"found multiple spaces"
            ))
            continue

        equals_positions.append(equals_pos)

    if len(set(equals_positions)) > 1:
        for line, relative_line_idx in parameter_lines:
            actual_line_num = block_start_line + relative_line_idx + 1
            equals_pos = line.find('=')
            if equals_pos != -1 and equals_pos != max(equals_positions):
                errors.append((
                    actual_line_num,
                    f"Parameter assignment not aligned with other parameters in {block_type}"
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
            "Validates that parameter assignments in resource and data blocks "
            "have proper spacing around equals signs and maintain consistent "
            "alignment within code blocks. This ensures code readability and "
            "follows Terraform formatting standards."
        ),
        "category": "Style/Format",
        "severity": "error",
        "rationale": (
            "Proper parameter alignment improves code readability and maintains "
            "consistent formatting standards. It makes it easier to scan through "
            "configuration parameters and understand the structure at a glance."
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
  # Parameter equal signs are not aligned
  name = "tf_test_instance"
  flavor_id = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")
  security_group_ids = [huaweicloud_networking_secgroup.test.id]
  # ...
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal"
    }
