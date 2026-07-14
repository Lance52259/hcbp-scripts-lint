#!/usr/bin/env python3
"""
IO.009 - Variable Usage Check

This module implements the IO.009 rule which validates variable definitions and
references within a Terraform module directory.

Rule Specification:
- Detect variables defined in variables.tf but never referenced (unused)
- Detect variables referenced as var.<name> but not declared in variables.tf (undeclared)
- Operates at directory scope when variables.tf is linted
- Excludes provider-related variables from the unused-variable check only

Author: Lance
License: Apache 2.0
"""

import re
import os
import glob
from typing import Callable, List, Set, Optional, Tuple


def check_io009_unused_variables(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate variable usage in a Terraform module directory.

    Performs bidirectional checks when processing variables.tf:
    1. Defined but never used
    2. Referenced but not declared in variables.tf

    Args:
        file_path (str): Path to the Terraform file being validated
        content (str): Content of the Terraform file
        log_error_func (Callable): Error logging callback
    """
    if not file_path.endswith('variables.tf'):
        return

    file_dir = os.path.dirname(file_path)
    defined_variables = _extract_variables_with_lines(content)

    if not defined_variables:
        defined_names: Set[str] = set()
    else:
        defined_names = {var_name for var_name, _ in defined_variables}

    used_variables = _get_used_variables_in_directory(file_dir)

    for var_name, line_number in defined_variables:
        if _should_exclude_from_unused_check(var_name):
            continue

        if var_name not in used_variables:
            log_error_func(
                file_path,
                "IO.009",
                f"Variable '{var_name}' is defined but never used",
                line_number
            )

    _check_undeclared_variable_references(file_dir, defined_names, log_error_func)


def _check_undeclared_variable_references(
    directory: str,
    defined_names: Set[str],
    log_error_func: Callable[[str, str, str, Optional[int]], None],
) -> None:
    """Report var.<name> references that are not declared in variables.tf."""
    reported: Set[str] = set()
    tf_files = sorted(glob.glob(os.path.join(directory, "*.tf")))

    for tf_file in tf_files:
        if os.path.basename(tf_file) == 'variables.tf':
            continue

        try:
            with open(tf_file, 'r', encoding='utf-8') as handle:
                tf_content = handle.read()
        except OSError:
            continue

        clean_content = _remove_comments_for_parsing(tf_content)
        for var_name, line_number in _extract_variable_references_with_lines(clean_content):
            if var_name in defined_names or var_name in reported:
                continue

            log_error_func(
                tf_file,
                "IO.009",
                f"Variable '{var_name}' is referenced but not declared in variables.tf",
                line_number
            )
            reported.add(var_name)


def _extract_variables_with_lines(content: str) -> List[Tuple[str, int]]:
    """Extract variable definitions with line numbers from variables.tf content."""
    variables = []
    lines = content.split('\n')
    var_pattern = r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{'

    for index, line in enumerate(lines, 1):
        match = re.match(var_pattern, line.strip())
        if match:
            var_name = match.group(1) or match.group(2) or match.group(3)
            variables.append((var_name, index))

    return variables


def _get_used_variables_in_directory(directory: str) -> Set[str]:
    """Collect all var.<name> references from .tf files in the directory."""
    used_variables: Set[str] = set()
    tf_files = glob.glob(os.path.join(directory, "*.tf"))

    for tf_file in tf_files:
        if os.path.basename(tf_file) == 'variables.tf':
            continue

        try:
            with open(tf_file, 'r', encoding='utf-8') as handle:
                tf_content = handle.read()
        except OSError:
            continue

        clean_content = _remove_comments_for_parsing(tf_content)
        used_variables.update(_extract_variable_usage(clean_content))

    return used_variables


def _extract_variable_usage(content: str) -> Set[str]:
    """Extract unique variable names referenced as var.<name>."""
    return {var_name for var_name, _ in _extract_variable_references_with_lines(content)}


def _extract_variable_references_with_lines(content: str) -> List[Tuple[str, int]]:
    """Extract variable references with their line numbers."""
    references: List[Tuple[str, int]] = []
    var_pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'

    for line_number, line in enumerate(content.split('\n'), 1):
        for match in re.finditer(var_pattern, line):
            references.append((match.group(1), line_number))

    return references


def _should_exclude_from_unused_check(var_name: str) -> bool:
    """
    Exclude provider-related variables from the unused-variable check.

    These variables may only be consumed in providers.tf or external tfvars.
    They are still required to be declared when referenced.
    """
    if var_name.startswith('region'):
        return True
    if var_name in ['access_key', 'secret_key', 'domain_name']:
        return True
    if var_name in ['tenant_name', 'tenant_id', 'user_name', 'user_id', 'project_name', 'project_id']:
        return True
    return False


def _remove_comments_for_parsing(content: str) -> str:
    """Remove comments from Terraform content for cleaner parsing."""
    lines = content.split('\n')
    clean_lines = []

    for line in lines:
        in_string = False
        quote_char = None
        clean_line = ""
        index = 0

        while index < len(line):
            char = line[index]

            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    quote_char = char
                    clean_line += char
                elif char == '#' or (char == '/' and index + 1 < len(line) and line[index + 1] == '/'):
                    break
                else:
                    clean_line += char
            else:
                clean_line += char
                if char == quote_char and (index == 0 or line[index - 1] != '\\'):
                    in_string = False
                    quote_char = None

            index += 1

        clean_lines.append(clean_line)

    return '\n'.join(clean_lines)


def get_rule_description() -> dict:
    """Retrieve detailed information about the IO.009 rule."""
    return {
        "id": "IO.009",
        "name": "Variable usage check",
        "description": (
            "Validates variable definitions and references within a module directory. "
            "Reports variables defined in variables.tf but never used, and variables "
            "referenced as var.<name> but not declared in variables.tf."
        ),
        "category": "Input/Output",
        "severity": "warning",
        "rationale": (
            "Unused variables add unnecessary complexity, while undeclared references "
            "indicate missing module inputs or stale configuration. Bidirectional "
            "checking keeps variables.tf aligned with actual module usage."
        ),
        "examples": {
            "valid": [
                '''
# variables.tf
variable "instance_name" {
  type = string
}

# main.tf
resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name
}
'''
            ],
            "invalid": [
                '''
# variables.tf
variable "unused_var" {
  type = string
}

# main.tf
resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name
}

# Expected:
# variables.tf: Variable 'unused_var' is defined but never used
# main.tf: Variable 'instance_name' is referenced but not declared in variables.tf
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.003", "ST.009"],
        "configuration": {
            "check_unused_variables": True,
            "check_undeclared_references": True,
            "exclude_provider_variables_from_unused_check": True,
            "search_current_directory_only": True,
            "excluded_variable_prefixes": ["region"],
            "excluded_variable_names": [
                "access_key",
                "secret_key",
                "domain_name",
                "tenant_name",
                "tenant_id",
                "user_name",
                "user_id",
                "project_name",
                "project_id"
            ]
        }
    }
