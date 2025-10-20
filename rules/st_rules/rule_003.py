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
    
    # Check if this is a terraform.tfvars file
    if file_path.endswith('.tfvars'):
        _check_tfvars_parameter_alignment(file_path, clean_content, log_error_func)
    else:
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
        # Quoted: data "type" "name" { ... } or resource "type" "name" { ... } or provider "type" { ... } or locals { ... }
        # Single-quoted: data 'type' 'name' { ... } or resource 'type' 'name' { ... } or provider 'type' { ... } or locals { ... }
        # Unquoted: data type name { ... } or resource type name { ... } or provider type { ... } or locals { ... }
        data_match = re.match(r'data\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        resource_match = re.match(r'resource\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        provider_match = re.match(r'provider\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)
        locals_match = re.match(r'locals\s*\{', line)
        terraform_match = re.match(r'terraform\s*\{', line)
        variable_match = re.match(r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{', line)

        if data_match or resource_match or provider_match or locals_match or terraform_match or variable_match:
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
            else:  # variable_match
                # Get variable name from quoted, single-quoted, or unquoted groups
                variable_name = variable_match.group(1) if variable_match.group(1) else (variable_match.group(2) if variable_match.group(2) else variable_match.group(3))
                block_type = f"variable.{variable_name}"
                
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
    in_object_definition = False

    for line_idx, line in enumerate(block_lines):
        stripped_line = line.strip()
        
        if stripped_line == '':
            # Empty line - split section if we have content
            if current_section:
                sections.append(current_section)
                current_section = []
        else:
            # Track brace levels
            for char in line:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
            
            # Check if we're entering an object definition (like list(object({...})))
            if (brace_level == 1 and 
                'object(' in stripped_line and 
                stripped_line.endswith('{') and
                current_section):
                # We're entering an object definition - split current section
                sections.append(current_section)
                current_section = []
                in_object_definition = True
            
            # Check if we're inside an object definition and have parameter assignments
            elif (in_object_definition and 
                  '=' in stripped_line and 
                  not stripped_line.startswith('{') and
                  not stripped_line.startswith('}') and
                  current_section and
                  any('object(' in prev_line for prev_line, _ in current_section)):
                # We're inside object definition with parameters - split if current section has object definition line
                if any('object(' in prev_line for prev_line, _ in current_section):
                    sections.append(current_section)
                    current_section = []
            
            # Check if we're exiting an object definition
            elif (in_object_definition and 
                  brace_level == 0 and 
                  stripped_line == '})' and
                  current_section):
                # We're exiting the object definition - split current section
                sections.append(current_section)
                current_section = []
                in_object_definition = False
            
            # Check if we're starting a new object in a list
            elif (in_object_definition and 
                  stripped_line == '{' and 
                  current_section and
                  any('=' in prev_line for prev_line, _ in current_section)):
                # Start of a new object in the list - split current section
                sections.append(current_section)
                current_section = []
            
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
                # Skip provider declarations in required_providers blocks
                # These are provider names like "huaweicloud = {" not parameter assignments
                if re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\{', line):
                    continue
                
                # Calculate indentation level, treating tabs as equivalent to spaces
                # Convert tabs to spaces for consistent indentation calculation
                line_with_spaces = line.expandtabs(2)  # Convert tabs to 2 spaces
                indent_level = len(line_with_spaces) - len(line_with_spaces.lstrip())

                # Group parameters by indentation level
                if base_indent is None:
                    base_indent = indent_level
                    parameter_lines.append((line, relative_line_idx))
                elif indent_level == base_indent:
                    parameter_lines.append((line, relative_line_idx))
                # Also include parameters with deeper indentation (nested objects)
                elif indent_level > base_indent:
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
        elif after_equals.startswith('  '):
            errors.append((
                actual_line_num,
                f"Parameter assignment should have exactly one space after '=' in {block_type}, found multiple spaces"
            ))

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
    
    # Find all variable assignment lines
    assignment_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and '=' in stripped:
            # Include all assignment lines (comments already removed)
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
            # We're entering an array - split current section if it exists
            if current_section:
                sections.append(current_section)
                current_section = []
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
              current_section and
              any('=' in prev_line for prev_line, _ in current_section)):
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
            current_section.append((line_num, line))
    
    if current_section:
        sections.append(current_section)
    
    # Check alignment in each section
    for section in sections:
        # Convert (line_num, line) to (line, relative_line_idx) format
        converted_section = [(line, i) for i, (line_num, line) in enumerate(section)]
        # Use the first line number minus 1 as the base line number
        # because _check_parameter_alignment_in_section adds 1 to the line number
        base_line_num = section[0][0] - 1
        errors = _check_parameter_alignment_in_section(converted_section, "tfvars", base_line_num)
        for line_num, error_msg in errors:
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
