#!/usr/bin/env python3
"""
IO (Input/Output) - Input and output definition rules
Contains all input and output definition related checking rules
"""

import os
import re
from typing import Dict, List, Set

class IORules:
    """IO type rule checker"""

    def __init__(self):
        self.rules = {
            "IO.001": {
                "name": "Variable definition file check",
                "description": (
                    "Check if all input variable definitions are in variables.tf file in the same directory"
                ),
                "category": "Input/Output"
            },
            "IO.002": {
                "name": "Output definition file check",
                "description": (
                    "Check if all output variable definitions are in outputs.tf file in the same directory"
                ),
                "category": "Input/Output"
            },
            "IO.003": {
                "name": "Required variable declaration check",
                "description": (
                    "Check if all required parameters used in resources are declared with input values in "
                    "terraform.tfvars file in the same directory"
                ),
                "category": "Input/Output"
            },
            "IO.004": {
                "name": "Variable naming convention check",
                "description": (
                    "Check if all variable names only contain lowercase letters and underscores, and do not "
                    "start with an underscore"
                ),
                "severity": "ERROR",
                "check_function": self.check_io004_variable_naming_convention
            },
            "IO.005": {
                "name": "Output naming convention check",
                "description": (
                    "Check if all output names only contain lowercase letters and underscores, and do not "
                    "start with an underscore"
                ),
                "severity": "ERROR",
                "check_function": self.check_io005_output_naming_convention
            },
            "IO.006": {
                "name": "Variable description check",
                "description": (
                    "Check if all input variables have a description field defined and not empty"
                ),
                "category": "Input/Output"
            },
            "IO.007": {
                "name": "Output description check",
                "description": (
                    "Check if all output variables have a description field defined and not empty"
                ),
                "category": "Input/Output"
            },
            "IO.008": {
                "name": "Variable type check",
                "description": (
                    "Check if all input variables have a type field defined"
                ),
                "category": "Input/Output"
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

    def extract_variables(self, content: str) -> List[str]:
        """
        Extract variable definitions from content
        """
        # Match variable "name" { ... }
        pattern = r'variable\s+"([^"]+)"\s*\{'
        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def extract_outputs(self, content: str) -> List[str]:
        """
        Extract output definitions from content
        """
        # Match output "name" { ... }
        pattern = r'output\s+"([^"]+)"\s*\{'
        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def extract_variable_references(self, content: str) -> Set[str]:
        """
        Extract variable references (var.xxx) from content
        """
        # Find all var.variable_name patterns
        pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(pattern, content)
        return set(matches)

    def parse_tfvars_file(self, file_path: str) -> Set[str]:
        """
        Parse terraform.tfvars file to extract declared variables
        """
        if not os.path.exists(file_path):
            return set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return set()

        declared_vars = set()
        # Find variable assignments
        pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                declared_vars.add(match.group(1))

        return declared_vars

    def is_valid_name(self, name: str) -> bool:
        """
        Check if name follows naming convention: only lowercase letters and underscores, not starting with underscore
        """
        # Check if starts with underscore
        if name.startswith('_'):
            return False

        # Check if only contains lowercase letters and underscores
        pattern = r'^[a-z][a-z0-9_]*$'
        return bool(re.match(pattern, name))

    def check_io001_variables_in_separate_file(self, file_path: str, content: str, log_error_func):
        """
        IO.001: Check if all input variable definitions are in variables.tf file in the same directory
        """
        # Skip check if current file is variables.tf
        if os.path.basename(file_path) == 'variables.tf':
            return

        clean_content = self.remove_comments_for_parsing(content)
        variables = self.extract_variables(clean_content)

        if variables:
            # Found variable definitions in non-variables.tf file
            log_error_func(
                file_path,
                "IO.001",
                f"Variables {variables} should be defined in variables.tf file, not in {os.path.basename(file_path)}"
            )

        # Check if variables.tf file exists (if directory has variable references)
        tf_dir = os.path.dirname(file_path)
        var_refs = self.extract_variable_references(clean_content)

        if var_refs:
            variables_tf_path = os.path.join(tf_dir, 'variables.tf')
            if not os.path.exists(variables_tf_path):
                log_error_func(
                    file_path,
                    "IO.001",
                    f"File uses variables {sorted(var_refs)} but variables.tf not found in same directory"
                )

    def check_io002_outputs_in_separate_file(self, file_path: str, content: str, log_error_func):
        """
        IO.002: Check if all output variable definitions are in outputs.tf file in the same directory
        """
        # Skip check if current file is outputs.tf
        if os.path.basename(file_path) == 'outputs.tf':
            return

        clean_content = self.remove_comments_for_parsing(content)
        outputs = self.extract_outputs(clean_content)

        if outputs:
            # Found output definitions in non-outputs.tf file
            log_error_func(
                file_path,
                "IO.002",
                f"Outputs {outputs} should be defined in outputs.tf file, not in {os.path.basename(file_path)}"
            )

    def check_io003_required_variables_in_tfvars(self, tf_file_path: str, content: str, log_error_func):
        """
        IO.003: Check if all required parameters used in resources are declared with input values in terraform.tfvars
        file in the same directory
        """
        clean_content = self.remove_comments_for_parsing(content)

        # Get variables used in resources
        required_vars = self.extract_variable_references(clean_content)

        if not required_vars:
            return

        # Find terraform.tfvars file in same directory
        tf_dir = os.path.dirname(tf_file_path)
        tfvars_path = os.path.join(tf_dir, 'terraform.tfvars')

        if not os.path.exists(tfvars_path):
            log_error_func(
                tf_file_path,
                "IO.003",
                f"terraform.tfvars not found in same directory, but resources use variables: "
                f"{', '.join(sorted(required_vars))}"
            )
            return

        # Parse tfvars file
        tfvars_variables = self.parse_tfvars_file(tfvars_path)

        # Check each required variable is declared in tfvars
        missing_vars = required_vars - tfvars_variables
        for var_name in sorted(missing_vars):
            log_error_func(
                tf_file_path,
                "IO.003",
                f"Required variable '{var_name}' used in resources but not declared in terraform.tfvars"
            )

    def check_io004_variable_naming_convention(self, file_path: str, content: str, log_error_func):
        """
        IO.004: Check if all variable names only contain lowercase letters and underscores, and do not start with an
        underscore
        """
        clean_content = self.remove_comments_for_parsing(content)
        variable_names = self.extract_variables(clean_content)

        for var_name in variable_names:
            if not self.is_valid_name(var_name):
                if var_name.startswith('_'):
                    log_error_func(
                        file_path,
                        "IO.004",
                        f"Variable name '{var_name}' should not start with underscore"
                    )
                else:
                    log_error_func(
                        file_path,
                        "IO.004",
                        f"Variable name '{var_name}' should only contain lowercase letters and underscores"
                    )

    def check_io005_output_naming_convention(self, file_path: str, content: str, log_error_func):
        """
        IO.005: Check if all output names only contain lowercase letters and underscores, and do not start with an
        underscore
        """
        clean_content = self.remove_comments_for_parsing(content)
        output_names = self.extract_outputs(clean_content)

        for output_name in output_names:
            if not self.is_valid_name(output_name):
                if output_name.startswith('_'):
                    log_error_func(
                        file_path,
                        "IO.005",
                        f"Output name '{output_name}' should not start with underscore"
                    )
                else:
                    log_error_func(
                        file_path,
                        "IO.005",
                        f"Output name '{output_name}' should only contain lowercase letters and underscores"
                    )

    def check_io006_variable_description(self, file_path: str, content: str, log_error_func):
        """
        IO.006: Check if all input variables have a description field defined and not empty
        """
        clean_content = self.remove_comments_for_parsing(content)
        variables = self.extract_variable_details(clean_content)
        
        for var_name, var_info in variables.items():
            if var_info['description'] is None:
                log_error_func(
                    file_path,
                    "IO.006",
                    f"Variable '{var_name}' at line {var_info['line_number']} is missing description field"
                )
            elif var_info['description'].strip() == '':
                log_error_func(
                    file_path,
                    "IO.006",
                    f"Variable '{var_name}' at line {var_info['line_number']} has empty description"
                )

    def check_io007_output_description(self, file_path: str, content: str, log_error_func):
        """
        IO.007: Check if all output variables have a description field defined and not empty
        """
        clean_content = self.remove_comments_for_parsing(content)
        outputs = self.extract_output_details(clean_content)
        
        for output_name, output_info in outputs.items():
            if output_info['description'] is None:
                log_error_func(
                    file_path,
                    "IO.007",
                    f"Output '{output_name}' at line {output_info['line_number']} is missing description field"
                )
            elif output_info['description'].strip() == '':
                log_error_func(
                    file_path,
                    "IO.007",
                    f"Output '{output_name}' at line {output_info['line_number']} has empty description"
                )

    def check_io008_variable_type(self, file_path: str, content: str, log_error_func):
        """
        IO.008: Check if all input variables have a type field defined
        """
        clean_content = self.remove_comments_for_parsing(content)
        variables = self.extract_variable_details(clean_content)
        
        for var_name, var_info in variables.items():
            if var_info['type'] is None:
                log_error_func(
                    file_path,
                    "IO.008",
                    f"Variable '{var_name}' at line {var_info['line_number']} is missing type field"
                )

    def run_all_checks(self, file_path: str, content: str, log_error_func):
        """
        Run all IO rule checks
        """
        self.check_io001_variables_in_separate_file(file_path, content, log_error_func)
        self.check_io002_outputs_in_separate_file(file_path, content, log_error_func)
        self.check_io003_required_variables_in_tfvars(file_path, content, log_error_func)
        self.check_io004_variable_naming_convention(file_path, content, log_error_func)
        self.check_io005_output_naming_convention(file_path, content, log_error_func)
        self.check_io006_variable_description(file_path, content, log_error_func)
        self.check_io007_output_description(file_path, content, log_error_func)
        self.check_io008_variable_type(file_path, content, log_error_func)

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

    def extract_variable_details(self, content: str) -> Dict[str, Dict]:
        """
        Extract variable definitions with their details (description, type, default)
        Returns dict with variable_name -> {description, type, has_default, line_number}
        """
        variables = {}
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match variable block start
            var_match = re.match(r'variable\s+"([^"]+)"\s*\{', line)
            if var_match:
                var_name = var_match.group(1)
                var_info = {
                    'description': None,
                    'type': None,
                    'has_default': False,
                    'line_number': i + 1
                }
                
                # Parse variable block content
                brace_count = 1
                i += 1
                
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    stripped = current_line.strip()
                    
                    # Count braces
                    brace_count += stripped.count('{')
                    brace_count -= stripped.count('}')
                    
                    # Extract description
                    desc_match = re.match(r'description\s*=\s*"([^"]*)"', stripped)
                    if desc_match:
                        var_info['description'] = desc_match.group(1)
                    
                    # Extract type
                    type_match = re.match(r'type\s*=\s*(.+)', stripped)
                    if type_match:
                        var_info['type'] = type_match.group(1).strip()
                    
                    # Check for default
                    if re.match(r'default\s*=', stripped):
                        var_info['has_default'] = True
                    
                    i += 1
                
                variables[var_name] = var_info
            else:
                i += 1
        
        return variables

    def extract_output_details(self, content: str) -> Dict[str, Dict]:
        """
        Extract output definitions with their details (description, value)
        Returns dict with output_name -> {description, value, line_number}
        """
        outputs = {}
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match output block start
            output_match = re.match(r'output\s+"([^"]+)"\s*\{', line)
            if output_match:
                output_name = output_match.group(1)
                output_info = {
                    'description': None,
                    'value': None,
                    'line_number': i + 1
                }
                
                # Parse output block content
                brace_count = 1
                i += 1
                
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    stripped = current_line.strip()
                    
                    # Count braces
                    brace_count += stripped.count('{')
                    brace_count -= stripped.count('}')
                    
                    # Extract description
                    desc_match = re.match(r'description\s*=\s*"([^"]*)"', stripped)
                    if desc_match:
                        output_info['description'] = desc_match.group(1)
                    
                    # Extract value
                    value_match = re.match(r'value\s*=\s*(.+)', stripped)
                    if value_match:
                        output_info['value'] = value_match.group(1).strip()
                    
                    i += 1
                
                outputs[output_name] = output_info
            else:
                i += 1
        
        return outputs
