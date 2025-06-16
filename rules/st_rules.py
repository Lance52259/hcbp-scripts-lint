#!/usr/bin/env python3
"""
ST (Style/Format) - Code formatting rules
Contains all code format-related checking rules
"""

import re
from typing import Dict, List, Tuple, Set

class STRules:
    """ST type rule checker"""

    def __init__(self):
        self.rules = {
            "ST.001": {
                "name": "Resource and data source naming convention check",
                "description": (
                    "Check if all data source (data) and resource (resource) code block instance names "
                    "are 'test'"
                ),
                "category": "Style/Format"
            },
            "ST.002": {
                "name": "Variable default value check",
                "description": (
                    "Check if all HCL input parameters (variable) are designed as optional parameters, "
                    "i.e., must have default values"
                ),
                "category": "Style/Format"
            },
            "ST.003": {
                "name": "Parameter alignment check",
                "description": (
                    "Check if parameter assignments in resource and data blocks have proper spacing "
                    "around equals sign"
                ),
                "category": "Style/Format"
            },
            "ST.004": {
                "name": "Indentation character check",
                "description": (
                    "Check if all indentation uses spaces only, not tabs"
                ),
                "category": "Style/Format"
            },
            "ST.005": {
                "name": "Indentation level check",
                "description": (
                    "Check if indentation follows the rule of current_level * 2 spaces"
                ),
                "category": "Style/Format"
            },
            "ST.006": {
                "name": "Resource and data source spacing check",
                "description": (
                    "Check if there is exactly one empty line between resource and data source blocks"
                ),
                "category": "Style/Format"
            },
            "ST.007": {
                "name": "Same parameter block spacing check",
                "description": (
                    "Check if empty lines between same-name parameter blocks are less than or equal to 1"
                ),
                "category": "Style/Format"
            },
            "ST.008": {
                "name": "Different parameter block spacing check",
                "description": (
                    "Check if there is exactly one empty line between different-name parameter blocks"
                ),
                "category": "Style/Format"
            },
            "ST.009": {
                "name": "Variable definition order check",
                "description": (
                    "Check if variable definition order in variables.tf matches usage order in main.tf"
                ),
                "category": "Style/Format"
            }
        }

    def remove_comments_for_parsing(self, content: str) -> str:
        """
        Remove comments from content for parsing, but preserve line structure
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

    def extract_data_sources(self, content: str) -> List[Tuple[str, str]]:
        """
        Extract data source definitions
        """
        # Match data "type" "name" { ... }
        pattern = r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{'
        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def extract_resources(self, content: str) -> List[Tuple[str, str]]:
        """
        Extract resource definitions
        """
        # Match resource "type" "name" { ... }
        pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'
        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def extract_variables(self, content: str) -> Dict[str, bool]:
        """
        Extract variable definitions, return variable name and whether it has default value
        """
        variables = {}

        # Match variable blocks
        var_pattern = r'variable\s+"([^"]+)"\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        var_matches = re.findall(var_pattern, content, re.DOTALL)

        for var_name, var_body in var_matches:
            # Check if it has default field
            has_default = bool(re.search(r'default\s*=', var_body))
            variables[var_name] = has_default

        return variables

    def extract_code_blocks(self, content: str) -> List[Tuple[str, int, List[str]]]:
        """
        Extract data source and resource code blocks, return (block_type, start_line_number, code_lines_list)
        """
        lines = content.split('\n')
        blocks = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Match data source or resource start
            data_match = re.match(r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
            resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)

            if data_match or resource_match:
                block_type = (
                    f"data.{data_match.group(1)}.{data_match.group(2)}" if data_match
                    else f"resource.{resource_match.group(1)}.{resource_match.group(2)}"
                )
                start_line = i + 1  # 1-indexed
                block_lines = []

                # Find matching closing brace
                brace_count = 1
                i += 1

                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    block_lines.append(current_line)

                    # Count braces (simple handling, doesn't consider braces inside strings)
                    for char in current_line:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1

                    i += 1

                # Remove the last closing brace line
                if block_lines and '}' in block_lines[-1]:
                    block_lines = block_lines[:-1]

                blocks.append((block_type, start_line, block_lines))
            else:
                i += 1

        return blocks

    def split_into_code_sections(self, block_lines: List[str]) -> List[List[Tuple[str, int]]]:
        """
        Split code block by empty lines into multiple sections, return list of (line_content, relative_line_number) for
        each section
        """
        sections = []
        current_section = []

        for line_idx, line in enumerate(block_lines):
            if line.strip() == '':
                # Empty line, end current section
                if current_section:
                    sections.append(current_section)
                    current_section = []
            else:
                current_section.append((line, line_idx))

        # Add the last section
        if current_section:
            sections.append(current_section)

        return sections

    def check_parameter_alignment_in_section(
        self, section: List[Tuple[str, int]], block_type: str, block_start_line: int
    ) -> List[Tuple[int, str]]:
        """
        Check parameter alignment in a code section, return error list (line_number, error_message)
        """
        errors = []
        parameter_lines = []
        base_indent = None

        # Extract parameter lines containing equals sign, only check parameters at the same indentation level
        for line_content, relative_line_idx in section:
            line = line_content.rstrip()
            if '=' in line and not line.strip().startswith('#'):
                # Check if it's a parameter assignment line (not nested block definition)
                if not re.match(r'^\s*(data|resource|variable|output|locals|module)\s+', line):
                    # Calculate indentation level
                    indent_level = len(line) - len(line.lstrip())

                    # Set base indentation level (use first parameter line's indentation)
                    if base_indent is None:
                        base_indent = indent_level
                        parameter_lines.append((line, relative_line_idx))
                    elif indent_level == base_indent:
                        # Only check parameters at the same indentation level
                        parameter_lines.append((line, relative_line_idx))
                    # Parameters at different indentation levels don't participate in alignment check

        if len(parameter_lines) <= 1:
            # Only one line or no parameter lines, no need to check alignment
            return errors

        # Check format and alignment of each line
        equals_positions = []

        for line, relative_line_idx in parameter_lines:
            actual_line_num = block_start_line + relative_line_idx + 1

            # Find equals sign position
            equals_pos = line.find('=')
            if equals_pos == -1:
                continue

            # Check spaces before and after equals sign
            before_equals = line[:equals_pos]
            after_equals = line[equals_pos + 1:]

            # Check if there's at least one space before equals sign
            if not before_equals.endswith(' '):
                errors.append((
                    actual_line_num,
                    f"Parameter assignment should have at least one space before '=' in {block_type}"
                ))
                continue

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
                    f"Parameter assignment should have exactly one space after '=' in {block_type}, "
                    f"found multiple spaces"
                ))
                continue

            # Record equals sign position for alignment check
            equals_positions.append(equals_pos)

        # Check if all equals signs are aligned (same position)
        if len(set(equals_positions)) > 1:
            # Not aligned, find the most common position or suggest alignment
            for line, relative_line_idx in parameter_lines:
                actual_line_num = block_start_line + relative_line_idx + 1
                equals_pos = line.find('=')
                if equals_pos != -1 and equals_pos != max(equals_positions):
                    errors.append((
                        actual_line_num,
                        f"Parameter assignment not aligned with other parameters in {block_type}"
                    ))

        return errors

    def check_st001_naming_convention(self, file_path: str, content: str, log_error_func):
        """
        ST.001: Check resource and data source naming convention
        """
        clean_content = self.remove_comments_for_parsing(content)

        # Check data sources
        data_sources = self.extract_data_sources(clean_content)
        for data_type, instance_name in data_sources:
            if instance_name != 'test':
                log_error_func(
                    file_path,
                    "ST.001",
                    f"Data source '{data_type}' instance name '{instance_name}' should be 'test'"
                )

        # Check resources
        resources = self.extract_resources(clean_content)
        for resource_type, instance_name in resources:
            if instance_name != 'test':
                log_error_func(
                    file_path,
                    "ST.001",
                    f"Resource '{resource_type}' instance name '{instance_name}' should be 'test'"
                )

    def check_st002_variable_defaults(self, file_path: str, content: str, log_error_func):
        """
        ST.002: Check variable default values
        """
        clean_content = self.remove_comments_for_parsing(content)
        variables = self.extract_variables(clean_content)

        for var_name, has_default in variables.items():
            if not has_default:
                log_error_func(
                    file_path,
                    "ST.002",
                    f"Variable '{var_name}' must have a default value (even if null or empty)"
                )

    def check_st003_parameter_alignment(self, file_path: str, content: str, log_error_func):
        """
        ST.003: Check parameter alignment
        """
        clean_content = self.remove_comments_for_parsing(content)

        # Extract code blocks
        blocks = self.extract_code_blocks(clean_content)

        for block_type, start_line, block_lines in blocks:
            # Split into sections by empty lines
            sections = self.split_into_code_sections(block_lines)

            for section in sections:
                errors = self.check_parameter_alignment_in_section(section, block_type, start_line)
                for line_num, error_msg in errors:
                    log_error_func(file_path, "ST.003", f"Line {line_num}: {error_msg}")

    def check_st004_indentation_character(self, file_path: str, content: str, log_error_func):
        """
        ST.004: Check if all indentation uses spaces only, not tabs
        """
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if self.has_tabs(line):
                log_error_func(
                    file_path,
                    "ST.004",
                    f"Line {line_num}: Indentation should use spaces only, not tabs"
                )

    def check_st005_indentation_level(self, file_path: str, content: str, log_error_func):
        """
        ST.005: Check if indentation follows the rule of current_level * 2 spaces
        """
        lines = content.split('\n')
        context_stack = []  # Stack to track nesting levels
        
        for line_num, line in enumerate(lines, 1):
            if line.strip() == '' or line.strip().startswith('#'):
                continue
                
            current_indent = self.get_indentation_level(line)
            
            # Track opening and closing braces to determine context level
            stripped_line = line.strip()
            
            # Handle closing braces - pop from stack
            if stripped_line == '}' and context_stack:
                context_stack.pop()
                expected_indent = self.calculate_expected_indentation(len(context_stack))
                if current_indent != expected_indent:
                    log_error_func(
                        file_path,
                        "ST.005",
                        f"Line {line_num}: Expected {expected_indent} spaces indentation, found {current_indent}"
                    )
                continue
            
            # Check current line indentation
            expected_indent = self.calculate_expected_indentation(len(context_stack))
            if current_indent != expected_indent:
                log_error_func(
                    file_path,
                    "ST.005",
                    f"Line {line_num}: Expected {expected_indent} spaces indentation, found {current_indent}"
                )
            
            # Handle opening braces - push to stack
            if stripped_line.endswith('{'):
                context_stack.append('block')

    def check_st006_resource_data_spacing(self, file_path: str, content: str, log_error_func):
        """
        ST.006: Check if there is exactly one empty line between resource and data source blocks
        """
        clean_content = self.remove_comments_for_parsing(content)
        blocks = self.extract_resource_data_blocks_with_positions(clean_content)
        lines = content.split('\n')
        
        for i in range(len(blocks) - 1):
            current_block = blocks[i]
            next_block = blocks[i + 1]
            
            current_end = current_block[2] - 1  # Convert to 0-indexed, this is the line after the closing brace
            next_start = next_block[1] - 1  # Convert to 0-indexed, this is the line with the block start
            
            # Count empty lines between blocks (excluding the closing brace line and block start line)
            empty_lines = 0
            for line_idx in range(current_end, next_start):
                if line_idx < len(lines) and lines[line_idx].strip() == '':
                    empty_lines += 1
            
            if empty_lines != 1:
                log_error_func(
                    file_path,
                    "ST.006",
                    f"Expected exactly 1 empty line between {current_block[0]} and {next_block[0]} blocks, found {empty_lines} at line {current_end + 1}"
                )

    def check_st007_same_parameter_spacing(self, file_path: str, content: str, log_error_func):
        """
        ST.007: Check if empty lines between same-name parameter blocks are less than or equal to 1
        """
        clean_content = self.remove_comments_for_parsing(content)
        blocks = self.extract_code_blocks(clean_content)
        lines = content.split('\n')
        
        for block_type, block_start_line, block_lines in blocks:
            param_blocks = self.extract_parameter_blocks_in_resource(block_lines)
            
            # Group parameter blocks by name
            param_groups = {}
            for param_name, start_line, end_line in param_blocks:
                if param_name not in param_groups:
                    param_groups[param_name] = []
                param_groups[param_name].append((start_line, end_line))
            
            # Check spacing between same-name parameter blocks
            for param_name, positions in param_groups.items():
                if len(positions) > 1:
                    for i in range(len(positions) - 1):
                        current_end = block_start_line + positions[i][1] - 2  # Adjust for 0-indexed
                        next_start = block_start_line + positions[i + 1][0] - 2  # Adjust for 0-indexed
                        
                        # Count empty lines between same-name parameter blocks
                        empty_lines = 0
                        for line_idx in range(current_end, next_start):
                            if line_idx < len(lines) and lines[line_idx].strip() == '':
                                empty_lines += 1
                        
                        if empty_lines > 1:
                            log_error_func(
                                file_path,
                                "ST.007",
                                f"Too many empty lines ({empty_lines}) between same-name parameter blocks '{param_name}' at line {current_end + 1}"
                            )

    def check_st008_different_parameter_spacing(self, file_path: str, content: str, log_error_func):
        """
        ST.008: Check if there is exactly one empty line between different-name parameter blocks
        """
        clean_content = self.remove_comments_for_parsing(content)
        blocks = self.extract_code_blocks(clean_content)
        lines = content.split('\n')
        
        for block_type, block_start_line, block_lines in blocks:
            param_blocks = self.extract_parameter_blocks_in_resource(block_lines)
            
            # Check spacing between consecutive different-name parameter blocks
            for i in range(len(param_blocks) - 1):
                current_param = param_blocks[i]
                next_param = param_blocks[i + 1]
                
                # Skip if same parameter name
                if current_param[0] == next_param[0]:
                    continue
                
                current_end = block_start_line + current_param[2] - 2  # Adjust for 0-indexed
                next_start = block_start_line + next_param[1] - 2  # Adjust for 0-indexed
                
                # Count empty lines between different-name parameter blocks
                empty_lines = 0
                for line_idx in range(current_end, next_start):
                    if line_idx < len(lines) and lines[line_idx].strip() == '':
                        empty_lines += 1
                
                if empty_lines != 1:
                    log_error_func(
                        file_path,
                        "ST.008",
                        f"Expected exactly 1 empty line between different parameter blocks '{current_param[0]}' and '{next_param[0]}', found {empty_lines} at line {current_end + 1}"
                    )

    def run_all_checks(self, file_path: str, content: str, log_error_func):
        """
        Run all ST rule checks
        """
        self.check_st001_naming_convention(file_path, content, log_error_func)
        self.check_st002_variable_defaults(file_path, content, log_error_func)
        self.check_st003_parameter_alignment(file_path, content, log_error_func)
        self.check_st004_indentation_character(file_path, content, log_error_func)
        self.check_st005_indentation_level(file_path, content, log_error_func)
        self.check_st006_resource_data_spacing(file_path, content, log_error_func)
        self.check_st007_same_parameter_spacing(file_path, content, log_error_func)
        self.check_st008_different_parameter_spacing(file_path, content, log_error_func)
        
        # ST.009 requires cross-file analysis, handle separately in main linter
        # This is called from terraform_lint.py when both variables.tf and main.tf are available

    def get_rule_info(self, rule_id: str) -> Dict:
        """
        Get rule information
        """
        return self.rules.get(rule_id, {})

    def get_all_rules(self) -> Dict:
        """
        Get all rule information
        """
        return self.rules

    def extract_resource_data_blocks_with_positions(self, content: str) -> List[Tuple[str, int, int]]:
        """
        Extract resource and data source blocks with their line positions
        Returns list of (block_type, start_line, end_line)
        """
        lines = content.split('\n')
        blocks = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match data source or resource start
            data_match = re.match(r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
            resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', line)
            
            if data_match or resource_match:
                block_type = "data" if data_match else "resource"
                start_line = i + 1  # 1-indexed
                
                # Find matching closing brace
                brace_count = 1
                i += 1
                
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    for char in current_line:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                    i += 1
                
                end_line = i  # 1-indexed
                blocks.append((block_type, start_line, end_line))
            else:
                i += 1
        
        return blocks

    def extract_parameter_blocks_in_resource(self, block_lines: List[str]) -> List[Tuple[str, int, int]]:
        """
        Extract parameter blocks within a resource or data source block
        Returns list of (parameter_name, start_line, end_line) relative to block start
        """
        parameter_blocks = []
        i = 0
        
        while i < len(block_lines):
            line = block_lines[i].strip()
            
            # Look for parameter block patterns like "tags {", "lifecycle {", etc.
            param_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\{', line)
            if param_match and not line.strip().startswith('#'):
                param_name = param_match.group(1)
                start_line = i + 1  # 1-indexed relative to block
                
                # Find matching closing brace
                brace_count = 1
                i += 1
                
                while i < len(block_lines) and brace_count > 0:
                    current_line = block_lines[i]
                    for char in current_line:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                    i += 1
                
                end_line = i  # 1-indexed relative to block
                parameter_blocks.append((param_name, start_line, end_line))
            else:
                i += 1
        
        return parameter_blocks

    def get_indentation_level(self, line: str) -> int:
        """
        Calculate the indentation level of a line based on leading spaces
        """
        return len(line) - len(line.lstrip(' '))

    def has_tabs(self, line: str) -> bool:
        """
        Check if a line contains tab characters for indentation
        """
        leading_whitespace = line[:len(line) - len(line.lstrip())]
        return '\t' in leading_whitespace

    def calculate_expected_indentation(self, context_level: int) -> int:
        """
        Calculate expected indentation based on context level
        Formula: context_level * 2 (standard 2 spaces per level)
        """
        return context_level * 2

    def check_variable_order(self, variables_content: str, main_content: str, variables_file: str, main_file: str) -> List[Dict]:
        """
        ST.009: Check if variable definition order in variables.tf matches usage order in main.tf
        
        Args:
            variables_content: Content of variables.tf file
            main_content: Content of main.tf file
            variables_file: Path to variables.tf file
            main_file: Path to main.tf file
            
        Returns:
            List of error dictionaries with 'file', 'rule', and 'message' keys
        """
        errors = []
        
        # Extract variable definitions in order from variables.tf
        variable_definitions = self.extract_variable_definitions_in_order(variables_content)
        
        # Extract variable references in order from main.tf
        variable_references = self.extract_variable_references_in_order(main_content)
        
        # Filter variable definitions to only include those referenced in main.tf
        referenced_variables = [var for var in variable_definitions if var in variable_references]
        
        # Check if the order matches
        if referenced_variables != variable_references:
            # Find the first mismatch
            mismatch_found = False
            for i, (expected, actual) in enumerate(zip(variable_references, referenced_variables)):
                if expected != actual:
                    errors.append({
                        'file': variables_file,
                        'rule': 'ST.009',
                        'message': f"Variable definition order mismatch: expected '{expected}' at position {i+1}, but found '{actual}'. Variables should be defined in the same order as they are used in main.tf"
                    })
                    mismatch_found = True
                    break
            
            # If no specific mismatch found but lengths differ, report general order issue
            if not mismatch_found:
                errors.append({
                    'file': variables_file,
                    'rule': 'ST.009',
                    'message': f"Variable definition order does not match usage order in main.tf. Expected order: {variable_references}, but found: {referenced_variables}"
                })
        
        return errors

    def extract_variable_definitions_in_order(self, content: str) -> List[str]:
        """
        Extract variable names in the order they are defined in variables.tf
        
        Args:
            content: Content of the variables.tf file
            
        Returns:
            List of variable names in definition order
        """
        variable_names = []
        clean_content = self.remove_comments_for_parsing(content)
        
        # Match variable blocks and extract names in order
        pattern = r'variable\s+"([^"]+)"\s*\{'
        matches = re.finditer(pattern, clean_content, re.MULTILINE)
        
        for match in matches:
            variable_names.append(match.group(1))
        
        return variable_names

    def extract_variable_references_in_order(self, content: str) -> List[str]:
        """
        Extract variable references in the order they first appear in main.tf
        
        Args:
            content: Content of the main.tf file
            
        Returns:
            List of variable names in first usage order
        """
        variable_references = []
        seen_variables = set()
        clean_content = self.remove_comments_for_parsing(content)
        
        # Match var.variable_name patterns and extract in order of first appearance
        pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(pattern, clean_content, re.MULTILINE)
        
        for match in matches:
            var_name = match.group(1)
            if var_name not in seen_variables:
                variable_references.append(var_name)
                seen_variables.add(var_name)
        
        return variable_references
