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
            
            # For locals blocks, also check alignment of top-level parameters across sections
            # This is because empty lines can split sections, but top-level locals should still align
            if block_type.startswith('locals'):
                all_top_level_params = []
                for section in sections:
                    for line, rel_idx in section:
                        if '=' in line and not line.strip().startswith('#'):
                            indent = len(line) - len(line.lstrip())
                            if indent <= 2:  # Top-level parameters
                                all_top_level_params.append((line, rel_idx))
                
                # Check alignment of top-level parameters across sections for locals
                if len(all_top_level_params) > 1:
                    top_level_errors = _check_parameter_alignment_in_section(
                        all_top_level_params, block_type, start_line
                    )
                    all_errors.extend(top_level_errors)
            
            # Check alignment and spacing within each individual section
            for section in sections:
                errors = _check_parameter_alignment_in_section(section, block_type, start_line)
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

    for line_idx, line in enumerate(block_lines):
        stripped_line = line.strip()
        
        if stripped_line == '':
            # Empty line - only split section if we're at brace_level 0 (not inside objects)
            if brace_level == 0 and current_section:
                sections.append(current_section)
                current_section = []
            # Always add empty lines to current section to maintain alignment context
            if brace_level > 0:
                current_section.append((line, line_idx))
            continue
        elif stripped_line.startswith('#'):
            # Skip comment lines but don't split sections
            continue
        else:
            # Track brace levels before processing
            for char in line:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
            
            # Check if we're entering an object (like { key = value })
            if brace_level == 1 and stripped_line.endswith('{') and current_section:
                # Add the current line to the section first
                current_section.append((line, line_idx))
                # Then split the section
                sections.append(current_section)
                current_section = []
                continue
            
            # Check if we're exiting an object
            elif brace_level == 0 and stripped_line == '}' and current_section:
                # We're exiting an object - split current section
                sections.append(current_section)
                current_section = []
            
            # Add line to current section
            current_section.append((line, line_idx))

    # Add final section if exists
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
        if len(group_lines) > 1:  # Only check alignment for groups with multiple parameters
            group_errors = _check_group_alignment(group_lines, indent_level, block_type, block_start_line)
            errors.extend(group_errors)
        
        # Always check spacing for all parameters
        for line, relative_line_idx in group_lines:
            spacing_errors = _check_parameter_spacing(line, relative_line_idx, block_type, block_start_line)
            errors.extend(spacing_errors)

    return errors


def _check_group_alignment(
    group_lines: List[Tuple[str, int]], 
    indent_level: int, 
    block_type: str, 
    block_start_line: int
) -> List[Tuple[int, str]]:
    """Check alignment within a group of parameters."""
    errors = []
    
    # Extract parameter names and find longest
    param_data = []
    for line, relative_line_idx in group_lines:
        equals_pos = line.find('=')
        if equals_pos == -1:
            continue
        
        # Skip array/list declarations only if before_equals is just [ or ends with ]
        # Don't skip lines that contain [ ] in the values
        before_equals = line[:equals_pos]
        if before_equals.strip().startswith('[') or (before_equals.strip() == '' and line.strip().startswith('[')):
            continue
        param_name_match = re.match(r'^\s*(["\']?)([^"\'=\s]+)\1\s*$', before_equals)
        if param_name_match:
            # Use parameter value without quotes for length calculation
            param_name = param_name_match.group(2)
            param_data.append((param_name, line, relative_line_idx, equals_pos))
    
    if len(param_data) < 2:
        return errors
    
    # Filter out lines with tab characters from alignment calculation
    param_data_no_tabs = [(param_name, line, relative_line_idx, equals_pos) 
                         for param_name, line, relative_line_idx, equals_pos in param_data 
                         if '\t' not in line]
    
    if len(param_data_no_tabs) < 2:
        # Not enough lines without tabs for alignment check
        return errors
    
    # Use only lines without tabs for alignment calculation
    param_data = param_data_no_tabs
    
    # Find longest parameter name
    longest_param_name_length = max(len(param_name) for param_name, _, _, _ in param_data)
    
    indent_spaces = indent_level * 2  # Convert indent level back to spaces
    
    # For tfvars files, check if most parameters are already aligned
    # If so, use the aligned position as expected location
    unique_equals_positions = {}
    for param_name, line, relative_line_idx, equals_pos in param_data:
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
            for _, line, _, _ in param_data
        )
        longest_quote_chars = 2 if has_quoted_params else 0
        
        expected_equals_location = indent_spaces + longest_param_name_length + longest_quote_chars + 1
    
    # Check alignment for each parameter
    for param_name, line, relative_line_idx, equals_pos in param_data:
        actual_line_num = block_start_line + relative_line_idx + 1
        
        # Skip alignment check if equals position matches expected location
        if equals_pos == expected_equals_location:
            continue
        
        # Check if indentation is incorrect (should be caught by ST.005)
        # If indentation is wrong, skip alignment error to prioritize ST.005
        actual_indent = len(line) - len(line.lstrip())
        
        # If indentation is not a multiple of 2, it's a ST.005 error
        # Skip alignment check to avoid confusion
        if actual_indent % 2 != 0:
            continue
        
        # Check if this line has ST.008 error (meta-parameter spacing)
        # If so, skip alignment error to prioritize ST.008
        # Note: Simple heuristic - if param is meta-parameter, skip alignment check
        # Full ST.008 error detection is done by rule_008 itself
        meta_parameters = ['count', 'for_each', 'provider', 'depends_on', 'lifecycle']
        if param_name in meta_parameters:
            # Skip ST.003 alignment error for meta-parameters
            # ST.008 will handle spacing errors for these
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
    """Check spacing around equals sign."""
    errors = []
    actual_line_num = block_start_line + relative_line_idx + 1
    
    equals_pos = line.find('=')
    if equals_pos == -1:
        return errors
    
    before_equals = line[:equals_pos]
    after_equals = line[equals_pos + 1:]
    
    # Check space before equals sign
    if not before_equals.endswith(' '):
        errors.append((
            actual_line_num,
            f"Parameter assignment should have at least one space before '=' in {block_type}"
        ))
    
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
        elif stripped in ['{', '}']:
            # Include brace lines as boundary markers
            assignment_lines.append((i + 1, line))
    
    if not assignment_lines:
        return
    
    # Group assignment lines by structural boundaries
    # This handles nested structures like arrays and objects in tfvars files
    sections = []
    current_section = []
    brace_level = 0
    in_array = False
    
    for line_num, line in assignment_lines:
        stripped_line = line.strip()
        
        # Track brace levels to detect nested structures
        for char in stripped_line:
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level -= 1
        
        # Check if we're entering an array (line ends with [)
        if stripped_line.endswith('[') and not in_array:
            # We're entering an array - add to current section instead of splitting
            # This ensures variable assignments before array are grouped together
            current_section.append((line_num, line))
            in_array = True
        
        # Check if we're exiting an array (line is just ])
        elif stripped_line == ']' and in_array:
            # We're exiting the array - split current section if it exists
            if current_section:
                sections.append(current_section)
                current_section = []
            in_array = False
        
        # Check if we're starting a new object in an array (line is just {)
        elif (in_array and 
              stripped_line == '{' and 
              current_section):
            # Start of a new object in the array - split current section
            sections.append(current_section)
            current_section = []
        
        # Check if we're ending an object in an array (line is just })
        elif (in_array and 
              stripped_line == '}' and 
              current_section):
            # End of an object in the array - split current section
            sections.append(current_section)
            current_section = []
        
        # Regular grouping for non-array assignments
        elif not in_array:
            if not current_section:
                # First line
                current_section.append((line_num, line))
            elif line_num - current_section[-1][0] <= 3:
                # Within 3 lines of previous assignment - same section
                current_section.append((line_num, line))
            else:
                # More than 3 lines away - start new section
                if current_section:
                    sections.append(current_section)
                current_section = [(line_num, line)]
        else:
            # Inside array structure - add to current section
            if stripped_line not in ['{', '}']:
                # Don't add standalone braces to sections, they're just markers
                current_section.append((line_num, line))
    
    if current_section:
        sections.append(current_section)
    
    # Check alignment in each section
    all_errors = []
    for section in sections:
        # Convert (line_num, line) to (line, relative_line_idx) format
        converted_section = [(line, i) for i, (line_num, line) in enumerate(section)]
        # Use the first line number minus 1 as the base line number
        # because _check_parameter_alignment_in_section adds 1 to the line number
        base_line_num = section[0][0] - 1
        errors = _check_parameter_alignment_in_section(converted_section, "tfvars", base_line_num)
        all_errors.extend(errors)
    
    # Sort errors by line number
    all_errors.sort(key=lambda x: x[0])
    
    # Report sorted errors
    for line_num, error_msg in all_errors:
        log_error_func(file_path, "ST.003", error_msg, line_num)


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


