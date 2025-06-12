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

    def run_all_checks(self, file_path: str, content: str, log_error_func):
        """
        Run all ST rule checks
        """
        self.check_st001_naming_convention(file_path, content, log_error_func)
        self.check_st002_variable_defaults(file_path, content, log_error_func)
        self.check_st003_parameter_alignment(file_path, content, log_error_func)

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
