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

Alignment Calculation Formula:
- Expected equals location = indent_spaces + param_name_length + quote_chars + 1
- Where:
  - indent_spaces = indent_level * 2 (Terraform uses 2 spaces per indent level)
  - param_name_length = length of parameter name without quotes
  - quote_chars = 2 if parameter name is quoted, 0 otherwise
  - 1 = standard space before equals sign

Code Block Sectioning Rules:
- Sections are split on empty lines
- Comment lines are ignored for sectioning (do not split sections)
- Object boundaries ({ and }) create new sections
- Parameters within the same section must align with each other

Special Cases:
- Lines containing tab characters are excluded from alignment calculations
- If all lines in a group contain tabs, no alignment errors are reported
- Parameters with quotes (e.g., "Environment") are handled correctly
- Nested objects maintain their own alignment groups

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
import sys
from typing import Callable, List, Tuple, Optional, Dict


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
    
    # Check if this is a terraform.tfvars file
    if file_path.endswith('.tfvars'):
        _check_tfvars_parameter_alignment(file_path, clean_content, log_error_func)
    else:
        blocks = _extract_code_blocks(clean_content)
        all_errors = []

        for block_type, start_line, block_lines in blocks:
            sections = _split_into_code_sections(block_lines)
            
            
            # Check alignment and spacing within each individual section
            for section in sections:
                errors = _check_parameter_alignment_in_section(section, block_type, start_line, block_lines)
                all_errors.extend(errors)
        
        # Sort errors by line number
        all_errors.sort(key=lambda x: x[0])
        
        # Deduplicate errors (same line number and error message)
        seen = set()
        unique_errors = []
        for line_num, error_msg in all_errors:
            key = (line_num, error_msg)
            if key not in seen:
                seen.add(key)
                unique_errors.append((line_num, error_msg))
        
        # Report sorted and deduplicated errors
        for line_num, error_msg in unique_errors:
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
                    # If the line is only a comment (after stripping), keep the original line
                    # to preserve line structure
                    stripped_before_comment = line[:i].strip()
                    if not stripped_before_comment:
                        line = line  # Keep original line (comment line)
                    else:
                        line = line[:i].rstrip()  # Remove comment but keep content
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
        # Quoted: data "type" "name" { ... } or resource "type" "name" { ... } or provider "type" { ... } or locals { ... }
        # Single-quoted: data 'type' 'name' { ... } or resource 'type' 'name' { ... } or provider 'type' { ... } or locals { ... }
        # Unquoted: data type name { ... } or resource type name { ... } or provider type { ... } or locals { ... }
        data_match = re.match(r'data\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        resource_match = re.match(r'resource\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        provider_match = re.match(r'provider\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        locals_match = re.match(r'locals\s*\{', line)
        terraform_match = re.match(r'terraform\s*\{', line)
        variable_match = re.match(r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        output_match = re.match(r'output\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)

        if data_match or resource_match or provider_match or locals_match or terraform_match or variable_match or output_match:
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
            elif provider_match:
                # Get provider type from quoted, single-quoted, or unquoted groups
                provider_type = provider_match.group(1) if provider_match.group(1) else (provider_match.group(2) if provider_match.group(2) else provider_match.group(3))
                block_type = f"provider.{provider_type}"
            elif locals_match:
                block_type = "locals"
            elif terraform_match:
                block_type = "terraform"
            elif variable_match:
                # Get variable name from quoted, single-quoted, or unquoted groups
                variable_name = variable_match.group(1) if variable_match.group(1) else (variable_match.group(2) if variable_match.group(2) else variable_match.group(3))
                block_type = f"variable.{variable_name}"
            else:  # output_match
                # Get output name from quoted, single-quoted, or unquoted groups
                output_name = output_match.group(1) if output_match.group(1) else (output_match.group(2) if output_match.group(2) else output_match.group(3))
                block_type = f"output.{output_name}"
                
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
    Split code block by empty lines and object boundaries into multiple sections.

    Args:
        block_lines (List[str]): Lines within a code block

    Returns:
        List[List[Tuple[str, int]]]: Sections with (line_content, line_index) tuples
    """
    sections = []
    current_section = []
    brace_level = 0
    bracket_level = 0

    for line_idx, line in enumerate(block_lines):
        stripped_line = line.strip()
        
        if stripped_line == '':
            # Empty line always splits sections, regardless of brace/bracket level
            if current_section:
                sections.append(current_section)
                current_section = []
            continue
        elif stripped_line.startswith('#'):
            # Skip comment lines but don't split sections
            continue
        else:
            # Track brace and bracket levels before processing
            for char in line:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
                elif char == '[':
                    bracket_level += 1
                elif char == ']':
                    bracket_level -= 1
            
            # Check if we're entering an object (parameter = { form)
            # When encountering '{', enter a new grouping
            if brace_level == 1 and stripped_line.endswith('{'):
                # Check if this is a simple "parameter = {" form
                if '=' in stripped_line:
                    after_equals = stripped_line.split('=', 1)[1].strip()
                    if after_equals == '{':
                        # Entering object grouping
                        current_section.append((line, line_idx))
                        sections.append(current_section)
                        current_section = []
                        continue
            
            # Check if we're entering an array (parameter = [ form)
            # When encountering '[', enter a new grouping
            if bracket_level == 1 and stripped_line.endswith('['):
                # Check if this is a simple "parameter = [" form
                if '=' in stripped_line:
                    after_equals = stripped_line.split('=', 1)[1].strip()
                    if after_equals == '[':
                        # Entering array grouping
                        current_section.append((line, line_idx))
                        sections.append(current_section)
                        current_section = []
                        continue
            
            # Check if we're in an array and encountering a standalone '{' (new object element)
            # This happens in structures like: default = [ { ... }, { ... } ]
            if bracket_level >= 1 and stripped_line == '{' and '=' not in stripped_line:
                # Starting a new object within an array
                if current_section:
                    sections.append(current_section)
                    current_section = []
            
            # Check if we're exiting an object
            if brace_level == 0 and stripped_line == '}':
                # Exiting object grouping
                if current_section:
                    sections.append(current_section)
                    current_section = []
            
            # Check if we're exiting an array
            if bracket_level == 0 and stripped_line == ']':
                # Exiting array grouping
                if current_section:
                    sections.append(current_section)
                    current_section = []
            
            # Add line to current section
            current_section.append((line, line_idx))

    # Add final section if exists
    if current_section:
        sections.append(current_section)
    
    return sections


def _check_parameter_alignment_in_section(
    section: List[Tuple[str, int]], block_type: str, block_start_line: int, block_lines: List[str] = None
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

    # Extract parameter lines from section
    for line_content, relative_line_idx in section:
        line = line_content.rstrip()
        if '=' in line and not line.strip().startswith('#'):
            # Skip block declarations
            if not re.match(r'^\s*(data|resource|variable|output|locals|module)\s+', line):
                # Skip provider declarations in required_providers blocks
                if (re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\{', line) and
                    any('required_providers' in prev_line for prev_line, _ in section)):
                    continue
                
                parameter_lines.append((line, relative_line_idx))

    if len(parameter_lines) == 0:
        return errors

    # Group parameters by indentation level
    indent_groups = {}
    for line, relative_line_idx in parameter_lines:
        line_with_spaces = line.expandtabs(2)
        indent_spaces = len(line_with_spaces) - len(line_with_spaces.lstrip())
        indent_level = indent_spaces // 2  # Terraform uses 2 spaces per indent level
        
        if indent_level not in indent_groups:
            indent_groups[indent_level] = []
        indent_groups[indent_level].append((line, relative_line_idx))

    # Check each indentation group
    for indent_level, group_lines in indent_groups.items():
        # Check alignment for all groups (including single-parameter groups)
        # Even single parameters should have proper spacing before '='
        group_errors = _check_group_alignment(group_lines, indent_level, block_type, block_start_line, block_lines)
        errors.extend(group_errors)
        
        # Always check spacing for all parameters
        for line, relative_line_idx in group_lines:
            spacing_errors = _check_parameter_spacing(line, relative_line_idx, block_type, block_start_line)
            errors.extend(spacing_errors)

    return errors


def _has_st004_issue(line: str) -> bool:
    """Check if line has ST.004 issue (tab character)."""
    return '\t' in line


def _has_st005_issue(line: str, indent_level: int, relative_line_idx: int = 0, block_lines: List[str] = None) -> bool:
    """Check if line has ST.005 issue (incorrect indentation)."""
    actual_indent = len(line) - len(line.lstrip())
    # Check if indentation is not a multiple of 2
    if actual_indent % 2 != 0:
        return True
    # Additional check: if actual indentation is 4 spaces, check if previous line mentions ST.005
    if actual_indent == 4 and block_lines and relative_line_idx > 0:
        # Check the previous line in original content for ST.005 comment
        prev_line = block_lines[relative_line_idx - 1]
        if "ST.005" in prev_line:
            return True
    return False


def _has_st008_issue(param_name: str, relative_line_idx: int, block_lines: List[str], 
                     meta_parameters: List[str]) -> bool:
    """
    Check if line has ST.008 issue.
    ST.008 issue occurs ONLY when the parameter is a meta-parameter itself.
    Note: Multiple blank lines are handled by ST.007 and don't cause ST.003 to skip.
    """
    # If it's a meta-parameter itself, skip ST.003 for it
    return param_name in meta_parameters


def _should_skip_alignment_check(line: str, param_name: str, relative_line_idx: int,
                                  indent_level: int, block_lines: List[str] = None) -> bool:
    """Determine if alignment check should be skipped due to other rule issues."""
    meta_parameters = ['count', 'for_each', 'provider', 'depends_on', 'lifecycle']
    
    # Check ST.004 (tab character)
    if _has_st004_issue(line):
        return True
    
    # Check ST.005 (incorrect indentation)
    if _has_st005_issue(line, indent_level, relative_line_idx, block_lines):
        return True
    
    # Check ST.008 (meta-parameter or multiple blank lines)
    if _has_st008_issue(param_name, relative_line_idx, block_lines, meta_parameters):
        return True
    
    return False


def _check_equals_after_spacing(line: str, relative_line_idx: int, block_type: str, 
                                block_start_line: int) -> List[Tuple[int, str]]:
    """Check space after equals sign (must be exactly 1 space)."""
    errors = []
    actual_line_num = block_start_line + relative_line_idx + 1
    
    equals_pos = line.find('=')
    if equals_pos == -1:
        return errors
    
    after_equals = line[equals_pos + 1:]
    
    # Check space after equals sign
    if not after_equals.startswith(' '):
        errors.append((
            actual_line_num,
            f"Parameter assignment should have exactly one space after '=' in {block_type}"
        ))
    elif after_equals.startswith('  '):
        errors.append((
            actual_line_num,
            f"Parameter assignment should have exactly one space after '=' in {block_type}, found multiple spaces"
        ))
    
    return errors


def _check_group_alignment(
    group_lines: List[Tuple[str, int]], 
    indent_level: int, 
    block_type: str, 
    block_start_line: int,
    block_lines: List[str] = None
) -> List[Tuple[int, str]]:
    """Check alignment within a group of parameters."""
    errors = []
    
    # Extract parameter names and find longest
    param_data = []
    for line, relative_line_idx in group_lines:
        equals_pos = line.find('=')
        if equals_pos == -1:
            continue
        
        # Skip array/list declarations
        before_equals = line[:equals_pos]
        if before_equals.strip().startswith('[') or (before_equals.strip() == '' and line.strip().startswith('[')):
            continue
        
        # Check if this is a nested block declaration (e.g., "extend_param = {")
        after_equals = line[equals_pos + 1:].strip()
        is_nested_block = after_equals.startswith('{')
        
        param_name_match = re.match(r'^\s*(["\']?)([^"\'=\s]+)\1\s*$', before_equals)
        if param_name_match:
            param_name = param_name_match.group(2)
            # Include nested blocks for alignment checking
            # Don't skip them, they should still be aligned with other parameters
            param_data.append((param_name, line, relative_line_idx, equals_pos, is_nested_block))
    
    if len(param_data) < 1:
        return errors
    
    # Find longest parameter name
    longest_param_name_length = max(len(param_name) for param_name, _, _, _, _ in param_data) if param_data else 0
    
    indent_spaces = indent_level * 2  # Convert indent level back to spaces
    
    # For tfvars files, check if most parameters are already aligned
    # If so, use the aligned position as expected location
    unique_equals_positions = {}
    for param_name, line, relative_line_idx, equals_pos, is_nested_block in param_data:
        if equals_pos not in unique_equals_positions:
            unique_equals_positions[equals_pos] = []
        unique_equals_positions[equals_pos].append((param_name, line, relative_line_idx, equals_pos))
    
    # For tfvars files, use actual alignment if parameters are already aligned
    if block_type == "tfvars":
        # If all parameters are already aligned at one position, use that position
        if len(unique_equals_positions) == 1:
            expected_equals_location = list(unique_equals_positions.keys())[0]
        elif len(unique_equals_positions) > 1:
            # More than one position, find the most common one
            most_common_pos = max(unique_equals_positions.keys(), 
                                key=lambda pos: len(unique_equals_positions[pos]))
            most_common_count = len(unique_equals_positions[most_common_pos])
            total_params = len(param_data)
            
            # If most parameters (> 50% and at least 2 params) are aligned at one position, use that position
            if most_common_count > total_params * 0.5 and most_common_count >= 2:
                expected_equals_location = most_common_pos
            else:
                # Calculate based on longest parameter name
                longest_param_data = max(param_data, key=lambda x: len(x[0]))
                longest_line = longest_param_data[1]
                longest_equals_pos = longest_param_data[3]
                longest_before_equals = longest_line[:longest_equals_pos]
                longest_quote_chars = 2 if longest_before_equals.strip().startswith('"') else 0
                expected_equals_location = indent_spaces + longest_param_name_length + longest_quote_chars + 1
        else:
            # Calculate based on longest parameter name
            longest_param_data = max(param_data, key=lambda x: len(x[0]))
            longest_line = longest_param_data[1]
            longest_equals_pos = longest_param_data[3]
            longest_before_equals = longest_line[:longest_equals_pos]
            longest_quote_chars = 2 if longest_before_equals.strip().startswith('"') else 0
            expected_equals_location = indent_spaces + longest_param_name_length + longest_quote_chars + 1
    else:
        # Calculate expected equals location based on longest parameter name
        # Formula: indent_spaces + param_name_length + quote_chars + 1 (standard space before equals)
        longest_param_data = max(param_data, key=lambda x: len(x[0]))
        longest_line = longest_param_data[1]
        longest_equals_pos = longest_param_data[3]
        longest_before_equals = longest_line[:longest_equals_pos]
        
        # Check if ANY parameter in the group has quotes
        # This ensures we use correct quote_chars even if longest param doesn't have quotes
        has_quoted_params = any(
            line[:line.find('=')].strip().startswith('"') 
            for _, line, _, _, _ in param_data
        )
        longest_quote_chars = 2 if has_quoted_params else 0
        
        expected_equals_location = indent_spaces + longest_param_name_length + longest_quote_chars + 1
    
    # Check alignment for each parameter
    for param_name, line, relative_line_idx, equals_pos, is_nested_block in param_data:
        actual_line_num = block_start_line + relative_line_idx + 1
        
        # Skip alignment check if equals position matches expected location
        if equals_pos == expected_equals_location:
            continue
        
        # Check if should skip due to ST.004, ST.005, or ST.008 issues
        if _should_skip_alignment_check(line, param_name, relative_line_idx, indent_level, block_lines):
            continue
            
        required_spaces_before_equals = expected_equals_location - indent_spaces - len(param_name)
        
        if equals_pos < expected_equals_location:
            errors.append((
                actual_line_num,
                f"Parameter assignment equals sign not aligned in {block_type}. "
                f"Expected {required_spaces_before_equals} spaces between parameter name and '=', "
                f"equals sign should be at column {expected_equals_location + 1}"
            ))
        elif equals_pos > expected_equals_location:
            errors.append((
                actual_line_num,
                f"Parameter assignment equals sign not aligned in {block_type}. "
                f"Too many spaces before '=', equals sign should be at column {expected_equals_location + 1}"
            ))
    
    return errors


def _check_parameter_spacing(
    line: str, 
    relative_line_idx: int, 
    block_type: str, 
    block_start_line: int
) -> List[Tuple[int, str]]:
    """Check spacing around equals sign - only check space after equals sign."""
    # Use the dedicated function for checking space after equals
    return _check_equals_after_spacing(line, relative_line_idx, block_type, block_start_line)


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
            "Validates that parameter assignments in resource, data, provider, locals, terraform, and variable blocks "
            "have equals signs aligned, with aligned equals signs maintaining one space "
            "from the longest parameter name in the code block and one space "
            "between the equals sign and parameter value. Also supports terraform.tfvars files "
            "for variable assignment alignment checking. This ensures code readability and "
            "follows Terraform formatting standards across all supported file types."
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

locals {
  is_available = true
  environment = "dev"
  tags        = {
    "Environment" = "Development"
  }
}

terraform {
  required_version = ">= 1.0"
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.0"
    }
  }
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
  default     = "test-instance"
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
  region = var.region_name               # Equals signs not aligned
  access_key= var.access_key             # No space before equals
  secret_key =var.secret_key             # No space after equals
}

locals {
  is_available=true                      # No space before equals
  environment =  "dev"                   # Multiple spaces after equals
  tags         =  {                      # Multiple spaces after equals
    "Environment" = "Development"
  }
}

terraform {
  required_version= ">= 1.0"             # No space before equals
  required_providers {
    huaweicloud = {
      source= "huaweicloud/huaweicloud"  # No space before equals
      version =  ">= 1.0"                # Multiple spaces after equals
    }
  }
}

variable "instance_name" {
  description= "The name of the ECS instance"  # No space before equals
  type =  string                              # Multiple spaces after equals
  default = "test-instance"
}
'''
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal"
    }


def _has_blank_line_between(lines: List[str], start_line_idx: int, end_line_idx: int) -> bool:
    """
    Check if there's a blank line between two line indices in the original content.
    Only counts truly empty lines, ignores comment-only lines.
    
    Args:
        lines: Original content lines
        start_line_idx: Start line index (0-based)
        end_line_idx: End line index (0-based)
    
    Returns:
        bool: True if there's a blank line between the two indices
    """
    for i in range(start_line_idx + 1, end_line_idx):
        if i >= len(lines):
            break
        stripped = lines[i].strip()
        # True blank line: empty string
        if stripped == '':
            return True
    return False


def _check_tfvars_parameter_alignment(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check parameter alignment in terraform.tfvars files.
    
    This function handles variable assignments in .tfvars files, which don't follow
    the same block structure as .tf files. It groups consecutive variable assignments
    and checks their alignment.
    
    Args:
        file_path (str): Path to the file being checked
        content (str): Cleaned file content (comments removed)
        log_error_func (Callable): Error logging function
    """
    lines = content.split('\n')
    
    # Find all variable assignment lines and boundary markers
    assignment_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and '=' in stripped:
            # Include all assignment lines (comments already removed)
            assignment_lines.append((i + 1, line))
        elif stripped.rstrip(',') in ['{', '}', '[', ']']:
            # Include brace and bracket lines as boundary markers (allow trailing commas)
            assignment_lines.append((i + 1, line))
    
    if not assignment_lines:
        return
    
    # Group assignment lines by structural boundaries
    # This handles nested structures like arrays and objects in tfvars files
    sections = []
    current_section = []
    brace_level = 0
    bracket_level = 0
    top_level_indent = 0  # Track the indent of the current top-level section
    
    for idx, (line_num, line) in enumerate(assignment_lines):
        stripped_line = line.strip()
        # Also strip trailing comma for boundary checks
        stripped_for_boundary = stripped_line.rstrip(',')
        
        # Save levels BEFORE updating them
        prev_brace_level_saved = brace_level
        prev_bracket_level_saved = bracket_level
        
        # Track brace and bracket levels to detect nested structures
        # Ensure levels don't go negative (defensive programming)
        for char in stripped_line:
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level = max(0, brace_level - 1)
            elif char == '[':
                bracket_level += 1
            elif char == ']':
                bracket_level = max(0, bracket_level - 1)
        
        # Check if we're entering an array (line ends with [)
        if stripped_line.endswith('[') and bracket_level == 1 and '=' in stripped_line:
            after_equals = stripped_line.split('=', 1)[1].strip()
            if after_equals == '[':
                # Array declaration line - check if we should split based on blank lines
                line_indent = len(line) - len(line.lstrip())
                prev_brace_level = prev_brace_level_saved
                prev_bracket_level = prev_bracket_level_saved
                
                # For top-level array declarations, check blank lines before splitting
                is_top_level_array = (line_indent == 0 and 
                                    prev_brace_level == 0 and 
                                    prev_bracket_level == 0)
                
                if is_top_level_array and current_section:
                    # Check if there's a blank line before this array declaration
                    prev_line_num = current_section[-1][0]
                    has_gap = _has_blank_line_between(lines, prev_line_num - 1, line_num - 1)
                    
                    if has_gap:
                        # Blank line before top-level array - split section
                        sections.append(current_section)
                        current_section = [(line_num, line)]
                        continue
                
                # No gap or not top-level - add to current section but don't split
                current_section.append((line_num, line))
                continue
        
        # Check if we're entering an object (parameter = {)
        # But only if it's NOT a top-level parameter (top-level should be aligned first)
        if stripped_line.endswith('{') and '=' in stripped_line:
            after_equals = stripped_line.split('=', 1)[1].strip()
            if after_equals == '{':
                # Check if this is a top-level parameter
                # We need to use levels BEFORE this line updates them
                line_indent = len(line) - len(line.lstrip())
                prev_brace_level = prev_brace_level_saved
                prev_bracket_level = prev_bracket_level_saved
                
                is_top_level = (line_indent == 0 and 
                              prev_brace_level == 0 and 
                              prev_bracket_level == 0)
                
                if not is_top_level:
                    # Entering non-top-level object grouping
                    # Continue processing to check blank lines between
                    pass
        
        # Don't split section on ] or } - just exit the grouping level
        # Sections should only be split on blank lines or when entering new structures
        
        # Don't clear current_section when exiting array
        # This allows subsequent top-level params to join the same section
        # Check if we're starting a new object in an array (standalone {)
        # Only split if this is not at the top level
        if bracket_level >= 1 and stripped_for_boundary == '{' and '=' not in stripped_line:
            # Check if this is top-level (bracket_level was 1 AFTER this line's [, meaning we're in a top-level array)
            if bracket_level == 1:
                # Top-level array, don't split section
                pass
            else:
                # Non-top-level, split section
                if current_section:
                    sections.append(current_section)
                    current_section = []
        
        # Regular grouping logic (handles gaps between lines)
        # Check if we should process this line for regular grouping
        process_regular_grouping = True
        if stripped_for_boundary in ['{', '}', '[', ']'] and '=' not in stripped_line:
            # Standalone braces/brackets are handled above, skip regular grouping
            process_regular_grouping = False
        
        if process_regular_grouping:
            # Calculate current line's indent
            line_indent = len(line) - len(line.lstrip())
            
            if not current_section:
                # First line
                top_level_indent = line_indent
                current_section.append((line_num, line))
            else:
                # Check if this is a top-level parameter
                # A parameter is top-level if:
                # 1. It has the same indent as the current section's top-level indent
                # 2. It's not inside any nested structures (we check BEFORE this line increases the levels)
                # 3. We need to use the PREVIOUS brace_level and bracket_level (before this line increases them)
                prev_brace_level = prev_brace_level_saved
                prev_bracket_level = prev_bracket_level_saved
                
                # For top-level parameters (prev_brace_level == 0 and prev_bracket_level == 0),
                # we should align them even if they contain { or [
                # Also include parameters inside array objects that have the same indent level
                # For tfvars, top-level parameters have indent level 0
                is_top_level = (line_indent == top_level_indent and 
                              '=' in stripped_line and
                              ((prev_brace_level == 0 and prev_bracket_level == 0) or line_indent == 0))
                
                # Check if this is a parameter inside an object (regardless of indent level)
                # This handles cases where parameters have different indentation within the same object
                # For tfvars, parameters in the same object should be grouped together
                is_object_param = ('=' in stripped_line and
                                 prev_brace_level >= 1 and
                                 not stripped_line.strip().startswith('#'))
                
                if is_top_level or is_object_param:
                    # This is another top-level parameter, array object parameter, or object parameter
                    prev_line_num = current_section[-1][0]
                    has_gap = _has_blank_line_between(lines, prev_line_num - 1, line_num - 1)
                    
                    # For tfvars, split on blank lines unless they're inside arrays/objects
                    # If there's a blank line and we're both at the top level, always split
                    if has_gap and prev_brace_level == 0 and prev_bracket_level == 0:
                        # Both are top-level parameters separated by a blank line
                        # Split into separate sections
                        sections.append(current_section)
                        current_section = [(line_num, line)]
                        
                    else:
                        # Same top-level group, add to current section
                        current_section.append((line_num, line))
                else:
                    # Not a top-level parameter, check gap from previous line
                    prev_line_num = current_section[-1][0]
                    has_gap = _has_blank_line_between(lines, prev_line_num - 1, line_num - 1)
                    if has_gap:
                        # Blank line separates sections
                        sections.append(current_section)
                        current_section = [(line_num, line)]
                    else:
                        # Same line group, add to current section
                        current_section.append((line_num, line))
    
    if current_section:
        sections.append(current_section)
    
    # Check alignment in each section
    all_errors = []
    processed_lines = set()  # Track processed lines to avoid duplicates
    
    for section_idx, section in enumerate(sections):
        # Convert (line_num, line) to (line, relative_line_idx) format
        # For tfvars, we need to preserve original line numbers
        converted_section = [(line, line_num) for line_num, line in section]
        # Use the first line number minus 1 as the base line number
        # because _check_parameter_alignment_in_section adds 1 to the line number
        base_line_num = section[0][0] - 1
        
        errors = _check_tfvars_parameter_alignment_in_section(converted_section, "tfvars")
        
        # Only add errors for lines that haven't been processed yet
        for line_num, msg in errors:
            if line_num not in processed_lines:
                all_errors.append((line_num, msg))
                processed_lines.add(line_num)
    
    # Sort errors by line number
    all_errors.sort(key=lambda x: x[0])
    
    # Report sorted errors
    for line_num, error_msg in all_errors:
        log_error_func(file_path, "ST.003", error_msg, line_num)


def _check_tfvars_parameter_alignment_in_section(section: List[Tuple[str, int]], block_type: str) -> List[Tuple[int, str]]:
    """
    Check parameter alignment in a tfvars section.
    
    This is a wrapper that directly uses actual line numbers from tfvars.
    
    Args:
        section: List of (line_content, actual_line_num) tuples
        block_type: Type of the block being checked
    
    Returns:
        List[Tuple[int, str]]: List of (line_number, error_message) tuples
    """
    errors = []
    parameter_lines = []
    
    # Extract parameter lines from section
    for line_content, actual_line_num in section:
        line = line_content.rstrip()
        if '=' in line and not line.strip().startswith('#'):
            # Skip block declarations
            if not re.match(r'^\s*(data|resource|variable|output|locals|module)\s+', line):
                parameter_lines.append((line, actual_line_num))
    
    if len(parameter_lines) == 0:
        return errors
    
    # Group by indentation level
    groups = {}
    for line, actual_line_num in parameter_lines:
        indent = len(line) - len(line.lstrip())
        indent_level = indent // 2
        # Skip odd indent (indent not multiple of 2) - these are ST.005 issues
        if indent % 2 != 0:
            continue
        if indent_level not in groups:
            groups[indent_level] = []
        groups[indent_level].append((actual_line_num, line))
    
    # Check alignment and spacing for each group
    for indent_level, group_lines in groups.items():
        # Sort by line number to maintain order
        group_lines.sort()
        alignment_errors = _check_group_alignment_tfvars(group_lines, indent_level, block_type)
        errors.extend(alignment_errors)
        
        # Check spacing for each line in the group
        for actual_line_num, line in group_lines:
            spacing_errors = _check_parameter_spacing_tfvars(line, actual_line_num, block_type)
            errors.extend(spacing_errors)
    
    return errors


def _check_group_alignment_tfvars(group_lines: List[Tuple[int, str]], indent_level: int, block_type: str) -> List[Tuple[int, str]]:
    """Check alignment within a group of tfvars parameters, using actual line numbers."""
    errors = []
    
    # Deduplicate group_lines to avoid processing the same line multiple times
    seen_lines = set()
    unique_group_lines = []
    for line_num, line in group_lines:
        if line_num not in seen_lines:
            seen_lines.add(line_num)
            unique_group_lines.append((line_num, line))
    
    group_lines = unique_group_lines
    
    # Extract parameter names and find longest
    param_data = []
    for actual_line_num, line in group_lines:
        display_line = line.expandtabs(2)
        equals_pos = display_line.find('=')
        if equals_pos == -1:
            continue
        
        before_equals = display_line[:equals_pos]
        if before_equals.strip().startswith('[') or (before_equals.strip() == '' and line.strip().startswith('[')):
            continue
        
        # Check if this is an array/object declaration line (e.g., "param = [" or "param = {")
        # For top-level declarations (indent=0), we should check alignment
        # For nested declarations, we should skip them from expected position calculation only
        after_equals = display_line[equals_pos + 1:].strip()
        is_object_or_array_decl = after_equals.startswith('[') or after_equals.startswith('{')
        
        # Skip object/array declarations from expected position calculation if they're nested
        # But still check their alignment if they're top-level
        actual_indent = len(line) - len(line.lstrip())
        should_skip_from_expected_calc = is_object_or_array_decl and actual_indent > 0
            
        # Match parameter name, optionally with quotes
        # For quoted params like "format", we need to handle the quotes
        # For unquoted params like type, we just need the name
        if before_equals.strip().startswith('"') or before_equals.strip().startswith("'"):
            param_name_match = re.match(r'^\s*(["\'])([^"\'=\s]+)\1', before_equals)
            if param_name_match:
                param_name = param_name_match.group(2)
            else:
                param_name_match = None
        else:
            param_name_match = re.match(r'^\s*([^"\'=\s]+)', before_equals)
            if param_name_match:
                param_name = param_name_match.group(1)
            else:
                param_name_match = None
        
        if param_name_match:
            # Store original line for later skip checks, but equals_pos based on expanded tabs
            # Also store whether this should be skipped from expected position calculation
            param_data.append((param_name, line, actual_line_num, equals_pos, should_skip_from_expected_calc))
    
    if len(param_data) < 2:
        return errors
    
    # Find longest parameter name
    # First get longest from non-skipped and non-tab parameters (for expected position calculation)
    # Parameters with tabs (ST.004) should not influence expected position
    non_skipped_non_tab_params_len = [
        len(p[0]) for p in param_data 
        if not p[4] and '\t' not in p[1]  # p[4] is should_skip, p[1] is line
    ]
    if non_skipped_non_tab_params_len:
        longest_param_name_length = max(non_skipped_non_tab_params_len)
        # If we have skipped parameters (object/array declarations) that are significantly longer,
        # use them for alignment calculation
        # This ensures parameters can align with object declarations when appropriate
        skipped_params_len = [len(p[0]) for p in param_data if p[4] and '\t' not in p[1]]
        if skipped_params_len:
            longest_skipped_len = max(skipped_params_len)
            # If the longest skipped parameter is significantly longer than non-skipped ones,
            # use it for expected position calculation
            # This handles cases where multiple simple params (like size, type) should align
            # with a longer object declaration parameter (like extend_param)
            if longest_skipped_len > longest_param_name_length and longest_skipped_len - longest_param_name_length >= 4:
                # Skip parameter is significantly longer (at least 4 chars), use it
                longest_param_name_length = longest_skipped_len
    else:
        # All parameters are skipped or have tabs, use all non-tab params
        non_tab_params_len = [len(p[0]) for p in param_data if '\t' not in p[1]]
        if non_tab_params_len:
            longest_param_name_length = max(non_tab_params_len)
        else:
            # All have tabs, use all params
            longest_param_name_length = max(len(p[0]) for p in param_data)
    indent_spaces = indent_level * 2
    
    # For tfvars files, check if most parameters are already aligned
    # Exclude tab lines from alignment position counting
    unique_equals_positions = {}
    for param_name, line, actual_line_num, equals_pos, _ in param_data:
        # Skip tab lines from counting (ST.004 issues should not influence alignment expectations)
        if '\t' in line:
            continue
        if equals_pos not in unique_equals_positions:
            unique_equals_positions[equals_pos] = 0
        unique_equals_positions[equals_pos] += 1
    
    # If all params are already aligned at one position, still check spacing after equals
    # and skip lines with tabs (ST.004) - but still check alignment based on longest param
    if len(unique_equals_positions) == 1:
        # Check if the aligned position matches the expected position based on longest parameter
        longest_param_len = max(len(param_name) for param_name, _, _, _, _ in param_data)
        # Check if any parameter has quotes and add quote length
        has_quoted_params = any(
            line[:line.find('=')].strip().startswith('"') or line[:line.find('=')].strip().startswith("'")
            for _, line, _, _, _ in param_data
        )
        quote_chars = 2 if has_quoted_params else 0
        expected_equals_location = indent_spaces + longest_param_len + quote_chars + 1
        
        # If the aligned position doesn't match the expected position, they need realignment
        aligned_position = list(unique_equals_positions.keys())[0]
        
        if aligned_position != expected_equals_location:
            # Parameters are aligned but not to the longest parameter
            # Check alignment for all parameters
            for param_name, line, actual_line_num, equals_pos, should_skip in param_data:
                # Skip nested object/array declaration lines from alignment check
                if should_skip:
                    continue
                
                # Skip lines with tabs (ST.004)
                if '\t' in line:
                    continue
                
                if equals_pos != expected_equals_location:
                    required_spaces_before_equals = expected_equals_location - indent_spaces - len(param_name)
                    if equals_pos < expected_equals_location:
                        errors.append((
                            actual_line_num,
                            f"Parameter assignment equals sign not aligned in {block_type}. "
                            f"Expected {required_spaces_before_equals} spaces between parameter name and '=', "
                            f"equals sign should be at column {expected_equals_location + 1}"
                        ))
                    elif equals_pos > expected_equals_location:
                        errors.append((
                            actual_line_num,
                            f"Parameter assignment equals sign not aligned in {block_type}. "
                            f"Too many spaces before '=', equals sign should be at column {expected_equals_location + 1}"
                        ))
        
        # Also check spacing after equals for all parameters
        for param_name, line, actual_line_num, equals_pos, should_skip in param_data:
            # Skip nested object/array declaration lines
            if should_skip:
                continue
            
            # Skip lines with tabs (ST.004)
            if '\t' in line:
                continue
            
            # Use the original line to find equals and check spacing
            original_equals_pos = line.find('=')
            if original_equals_pos == -1:
                continue
                
            after_equals = line[original_equals_pos + 1:]
            if len(after_equals) == 0 or not after_equals[0] == ' ':
                errors.append((
                    actual_line_num,
                    f"Parameter assignment should have at least one space after '=' in {block_type}"
                ))
        
        return errors
    
    # Check if there are multiple alignment groups
    # If most parameters are aligned at one position, use that position
    # Note: unique_equals_positions already excludes tab lines, so count only non-tab params
    if unique_equals_positions:
        most_common_pos = max(unique_equals_positions.items(), key=lambda x: x[1])
        most_common_count = most_common_pos[1]
        # Count only non-tab parameters for total_params (to match unique_equals_positions)
        total_params = sum(1 for p in param_data if '\t' not in p[1])
    else:
        # All params have tabs (shouldn't happen, but handle it)
        most_common_pos = (0, 0)
        most_common_count = 0
        total_params = sum(1 for p in param_data if '\t' not in p[1])
        if total_params == 0:
            total_params = len(param_data)
    
    # Calculate expected position based on longest parameter
    # First try to get longest from non-skipped and non-tab parameters
    # Parameters with tabs (ST.004) should not influence expected position
    non_skipped_non_tab_params = [p for p in param_data if not p[4] and '\t' not in p[1]]  # p[4] is should_skip, p[1] is line
    if non_skipped_non_tab_params:
        longest_param_len = max(len(p[0]) for p in non_skipped_non_tab_params)  # p[0] is param_name
        # If we have skipped parameters (object/array declarations) that are longer,
        # consider using them for alignment calculation
        # This ensures parameters can align with object declarations when appropriate
        skipped_non_tab_params = [p for p in param_data if p[4] and '\t' not in p[1]]
        if skipped_non_tab_params:
            longest_skipped_len = max(len(p[0]) for p in skipped_non_tab_params)
            # If the longest skipped parameter is significantly longer than non-skipped ones,
            # use it for expected position calculation
            # This handles cases where multiple simple params (like size, type) should align
            # with a longer object declaration parameter (like extend_param)
            if longest_skipped_len > longest_param_len and longest_skipped_len - longest_param_len >= 4:
                # Skip parameter is significantly longer (at least 4 chars), use it
                longest_param_len = longest_skipped_len
    else:
        # All parameters are skipped or have tabs, use all non-tab params
        non_tab_params = [p for p in param_data if '\t' not in p[1]]
        if non_tab_params:
            longest_param_len = max(len(p[0]) for p in non_tab_params)
        else:
            # All have tabs, use all params
            longest_param_len = max(len(p[0]) for p in param_data)
    # Check if any parameter has quotes and add quote length
    has_quoted_params = any(
        line[:line.find('=')].strip().startswith('"') or line[:line.find('=')].strip().startswith("'")
        for _, line, _, _, _ in param_data
    )
    quote_chars = 2 if has_quoted_params else 0
    # The equals position is calculated as: indent + param_name_length + quote_chars + 1 space between param and =
    expected_equals_location = indent_spaces + longest_param_len + quote_chars + 1
    
    # If more than half of parameters are already aligned at a specific position,
    # use that position (they're already aligned, so it's valid)
    # Use the most common position if most parameters are aligned there
    # This respects existing alignment patterns
    # However, if the expected location based on longest parameter (including object declarations)
    # differs significantly from the most_common position, we should use the longest-based position
    # This ensures parameters correctly align with their object declarations
    use_most_common = False
    expected_based_on_longest = indent_spaces + longest_param_len + quote_chars + 1
    
    if most_common_count > total_params / 2 or (total_params == 2 and most_common_count == 2):
        # Check if most_common position is close to the expected position based on longest parameter
        # If they differ significantly (>2 columns), use the longest-based position instead
        # This prevents cases where a majority of parameters from different objects are aligned
        # but we need to align with an object declaration in the same group
        if abs(most_common_pos[0] - expected_based_on_longest) > 2:
            # Most common position differs significantly from expected - use expected position
            # This handles cases like: multiple size params at position 9, but extend_param at 17
            use_most_common = False
        else:
            expected_equals_location = most_common_pos[0]
            use_most_common = True
        
        # Only execute this branch if we're actually using most_common position
        # Otherwise, fall through to the normal alignment check loop below
        if use_most_common:
            # Only check spacing after equals, not alignment
            # Skip alignment checks for parameters that are already aligned
            for param_name, line, actual_line_num, equals_pos, should_skip in param_data:
                # Skip nested object/array declaration lines from alignment check
                if should_skip:
                    continue
                
                if equals_pos != expected_equals_location:
                    # Check if this parameter is already aligned with other parameters
                    # If most params are aligned at a different position, this might be a different alignment group
                    if most_common_count > 1:
                        # Check if this parameter is aligned with the majority
                        if equals_pos == most_common_pos[0]:
                            # This parameter is aligned with the majority, skip check
                            continue
                    
                    # Check if it's close enough to be considered aligned
                    if abs(equals_pos - expected_equals_location) <= 1:
                        # Close enough, skip alignment check
                        continue
                    
                    # Too far off, report alignment error
                    required_spaces_before_equals = expected_equals_location - indent_spaces - len(param_name)
                    if equals_pos < expected_equals_location:
                        errors.append((
                            actual_line_num,
                            f"Parameter assignment equals sign not aligned in {block_type}. "
                            f"Expected {required_spaces_before_equals} spaces between parameter name and '=', "
                            f"equals sign should be at column {expected_equals_location + 1}"
                        ))
                    elif equals_pos > expected_equals_location:
                        errors.append((
                            actual_line_num,
                            f"Parameter assignment equals sign not aligned in {block_type}. "
                            f"Too many spaces before '=', equals sign should be at column {expected_equals_location + 1}"
                        ))
            
            # Check spacing after equals for all parameters
            for param_name, line, actual_line_num, equals_pos, should_skip in param_data:
                # Skip nested object/array declaration lines
                if should_skip:
                    continue
                
                after_equals = line[equals_pos + 1:]
                if len(after_equals) == 0 or not after_equals[0] == ' ':
                    errors.append((
                        actual_line_num,
                        f"Parameter assignment should have at least one space after '=' in {block_type}"
                    ))
            
            return errors
    
    # Calculate expected equals location based on longest parameter name
    # For tfvars files, always align to longest parameter name
    # Check if any parameter has quotes
    has_quoted_params = any(
        line[:line.find('=')].strip().startswith('"') or line[:line.find('=')].strip().startswith("'")
        for _, line, _, _, _ in param_data
    )
    quote_chars = 2 if has_quoted_params else 0
    # Calculate expected location based on longest parameter
    # Use longest_param_len which is already calculated above (at line 1249-1265)
    # and includes the logic to consider object/array declarations when appropriate
    expected_equals_location_base = indent_spaces + longest_param_len + quote_chars + 1
    
    # If we already determined to use most common position, keep it
    # Otherwise use the base calculation
    if not use_most_common:
        expected_equals_location = expected_equals_location_base
    
    # Check alignment for each parameter
    for param_name, line, actual_line_num, equals_pos, should_skip in param_data:
        # Skip alignment check for nested object/array declaration lines
        if should_skip:
            continue
        
        # Skip alignment check if equals position matches expected location
        if equals_pos == expected_equals_location:
            continue
        
        # If most params are already aligned, respect that alignment
        if use_most_common:
            if equals_pos == most_common_pos[0]:
                # This parameter is aligned with the majority, skip check
                continue
        
        # Skip emitting alignment error on lines with tabs (ST.004), but still allow them to influence expected position
        if '\t' in line:
            continue

        # Check if indentation is incorrect
        actual_indent = len(line) - len(line.lstrip())
        if actual_indent % 2 != 0:
            continue
        
        # For parameters with quotes, add quote characters to length
        param_display_length = len(param_name)
        before_eq_for_quote = line[: line.find('=')]
        if before_eq_for_quote.strip().startswith('"') or before_eq_for_quote.strip().startswith("'"):
            param_display_length += 2  # Add quotes length
        
        # Check if this parameter is already aligned with at least 2 other NON-TAB parameters
        # Tab lines (ST.004) should not count for alignment - we only want to skip if aligned with valid parameters
        # However, we should only skip if the alignment position matches the expected location
        # or if it matches the most_common position and the difference from expected is small
        non_tab_aligned_count = sum(1 for p in param_data if p[3] == equals_pos and '\t' not in p[1])
        if non_tab_aligned_count >= 2:
            # Check if this alignment position is acceptable
            # If it matches expected location, or matches most_common and is close to expected, skip
            if equals_pos == expected_equals_location:
                # Aligned at expected location, skip
                continue
            elif use_most_common and equals_pos == most_common_pos[0]:
                # Aligned with most_common and we're using most_common, skip
                continue
            elif abs(equals_pos - expected_equals_location) <= 1:
                # Close to expected location (within 1 column), skip
                continue
            # Check if this parameter is aligned with the majority position
            # If most parameters are already aligned at a different position (most_common_pos),
            # and this parameter is at that position, skip the check
            # This handles cases where multiple parameters form a valid alignment group,
            # but the expected position is based on an object declaration in a different context
            # However, don't skip if this parameter should align with an object declaration
            # (i.e., if it's immediately followed by an object declaration parameter)
            elif not use_most_common and unique_equals_positions and equals_pos == most_common_pos[0]:
                # Check if this parameter should align with an object declaration
                # Find the index of current parameter in param_data
                current_idx = None
                for idx, (_, _, ln, _, _) in enumerate(param_data):
                    if ln == actual_line_num:
                        current_idx = idx
                        break
                
                # Check if next parameter is an object declaration and should be used for alignment
                should_align_with_next_decl = False
                if current_idx is not None and current_idx + 1 < len(param_data):
                    next_param = param_data[current_idx + 1]
                    if next_param[4]:  # next_param[4] is should_skip (object declaration)
                        # Check if there's a blank line between current and next parameter
                        # Find the line numbers from group_lines
                        next_line_num = next_param[2]  # next_param[2] is actual_line_num
                        current_line_num = actual_line_num
                        
                        # If line numbers differ by more than 1, there might be blank lines
                        # But we need to check group_lines to see the actual lines
                        # For now, if next_line_num - current_line_num == 1, they're adjacent
                        if next_line_num - current_line_num == 1:
                            # Adjacent lines, check if object declaration length was used for expected position
                            skipped_params_len = [len(p[0]) for p in param_data if p[4] and '\t' not in p[1]]
                            if skipped_params_len:
                                longest_skipped_len = max(skipped_params_len)
                                non_skipped_params = [p for p in param_data if not p[4] and '\t' not in p[1]]
                                non_skipped_len = max(len(p[0]) for p in non_skipped_params) if non_skipped_params else 0
                                if longest_skipped_len > non_skipped_len and longest_skipped_len - non_skipped_len >= 4:
                                    # Object declaration length was used, and this param is immediately before it
                                    should_align_with_next_decl = True
                        # If line numbers differ by more than 1, they're not adjacent, don't align
                
                if not should_align_with_next_decl:
                    # Most parameters are aligned at a position different from expected
                    # This parameter is aligned with the majority, skip check
                    continue
                # Otherwise, should align with next declaration, continue to report error
            # Otherwise, this parameter is aligned incorrectly with other parameters
            # Report the error instead of skipping
        
        required_spaces_before_equals = expected_equals_location - indent_spaces - param_display_length
        
        if equals_pos < expected_equals_location:
            errors.append((
                actual_line_num,
                f"Parameter assignment equals sign not aligned in {block_type}. "
                f"Expected {required_spaces_before_equals} spaces between parameter name and '=', "
                f"equals sign should be at column {expected_equals_location + 1}"
            ))
        elif equals_pos > expected_equals_location:
            errors.append((
                actual_line_num,
                f"Parameter assignment equals sign not aligned in {block_type}. "
                f"Too many spaces before '=', equals sign should be at column {expected_equals_location + 1}"
            ))
    
    return errors


def _check_parameter_spacing_tfvars(line: str, actual_line_num: int, block_type: str) -> List[Tuple[int, str]]:
    """Check spacing around equals sign for tfvars, using actual line number."""
    errors = []
    equals_pos = line.find('=')
    
    if equals_pos == -1:
        return errors
    
    # Check space before equals
    before_equals_raw = line[:equals_pos]
    if not before_equals_raw.strip() or not before_equals_raw.endswith(' '):
        errors.append((
            actual_line_num,
            f"Parameter assignment should have at least one space before '=' in {block_type}"
        ))
    
    # Check space after equals
    after_equals = line[equals_pos + 1:]
    if len(after_equals) == 0 or not after_equals[0] == ' ':
        errors.append((
            actual_line_num,
            f"Parameter assignment should have at least one space after '=' in {block_type}"
        ))
    elif len(after_equals) > 1 and after_equals[:2] == '  ':
        errors.append((
            actual_line_num,
            f"Parameter assignment should have exactly one space after '=' in {block_type}, found multiple spaces"
        ))
    
    return errors


def _is_inside_block_structure_tfvars(current_line: str, all_lines: List[str], current_line_num: int) -> bool:
    """
    Check if the current line is inside a block structure in terraform.tfvars files.
    
    This is similar to the function in rule_005.py but adapted for .tfvars files.
    
    Args:
        current_line (str): The current line being checked
        all_lines (List[str]): All lines in the file
        current_line_num (int): Current line number (1-indexed)
        
    Returns:
        bool: True if the line is inside a block structure, False otherwise
    """
    # Check if this line is inside a block structure (including lines with =, {, or })
    if (('=' in current_line.strip() or current_line.strip().startswith('{') or current_line.strip().startswith('}')) 
        and not current_line.strip().startswith('#')):
        # Look backwards to see if we're inside a block structure
        brace_count = 0
        bracket_count = 0
        
        for i in range(current_line_num - 2, -1, -1):  # Start from 2 lines before current
            if i >= len(all_lines):
                continue
                
            line = all_lines[i].strip()
            if not line:
                continue
                
            # Count braces and brackets to track block structure
            for char in line:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
            
            # If we have unmatched opening braces/brackets, we're inside a block
            if brace_count > 0 or bracket_count > 0:
                return True
                
            # If we find a line that ends with { or [, check if it's part of a block structure
            if line.endswith('{') or line.endswith('['):
                # Check if this is a block structure (not just a simple assignment)
                if '=' in line and ('{' in line or '[' in line):
                    return True
                break
        return False
    else:
        return False


