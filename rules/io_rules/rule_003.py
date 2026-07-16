#!/usr/bin/env python3
"""
IO.003 - Required Variable Declaration Check in terraform.tfvars / *.auto.tfvars

This module implements the IO.003 rule which validates that all required variables
(variables without default values) are declared with values in Terraform's
auto-loaded tfvars sources in the same directory: ``terraform.tfvars`` and
sibling ``*.auto.tfvars`` files.

Rule Specification:
- Check all variables defined in the current file
- Required variables are those without default values (including ``default = null``,
  which counts as having a default and is therefore optional)
- All required variables must be declared in terraform.tfvars or *.auto.tfvars
- Variables with default values are optional and don't need tfvars entries
- Env-split files (e.g. ``dev.tfvars``) and ``*.tfvars.json`` are not loaded
- Provider-related variables are excluded from this check
  (shared list: ``region`` / ``region_*``, access_key, secret_key, domain_name,
  tenant/user/project identifiers; see rules.common.provider_variables)
- Report each missing variable declaration individually with precise line numbers
- Helps ensure all necessary input values are provided for deployment

Examples:
    Valid definition:
        # variables.tf
        variable "instance_name" {
          description = "Name of the ECS instance"
          type        = string
        }

        variable "tags" {
          description = "Optional tags"
          type        = map(string)
          default     = null
        }

        # defaults.auto.tfvars (or terraform.tfvars)
        instance_name = "my-instance"

    Invalid definition:
        # variables.tf
        variable "cpu_cores" {
          description = "Number of CPU cores"
          type        = number
        }

        # terraform.tfvars / *.auto.tfvars missing cpu_cores

Author: Lance
License: Apache 2.0
"""

import glob
import re
import os
from typing import Callable, List, Set, Optional, Tuple

from rules.common.provider_variables import is_provider_related_variable

_IO003_MSG = (
    "Required variable '{var_name}' (no default) must be declared in "
    "terraform.tfvars or *.auto.tfvars"
)


def check_io003_required_variables(file_path: str, content: str, 
                                  log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate that all required variables are declared in auto-loaded tfvars sources.

    Required variables (no ``default`` attribute) in the current file must appear as
    top-level assignments in sibling ``terraform.tfvars`` and/or ``*.auto.tfvars``.
    Each missing declaration is reported individually with a precise line number.
    
    Args:
        file_path (str): The path to the Terraform file being validated.
        content (str): The complete content of the Terraform file as a string.
        log_error_func (Callable): Callback ``(file_path, rule_id, message, line_number)``.
    """
    file_dir = os.path.dirname(file_path)
    required_variables = _extract_required_variables_with_lines(content)
    
    if not required_variables:
        return
    
    declared_variables = _collect_declared_variables_from_dir(file_dir)
    
    for var_name, line_number in required_variables:
        if var_name not in declared_variables:
            log_error_func(
                file_path,
                "IO.003",
                _IO003_MSG.format(var_name=var_name),
                line_number
            )


def _collect_declared_variables_from_dir(file_dir: str) -> Set[str]:
    """
    Union declared keys from Terraform auto-loaded HCL tfvars in ``file_dir``.

    Sources (existence-only union; no override-precedence check):
    - ``terraform.tfvars``
    - sibling ``*.auto.tfvars`` (sorted for deterministic reads)

    Does not include env-split ``*.tfvars`` or ``*.tfvars.json``.
    """
    declared: Set[str] = set()
    paths: List[str] = []

    terraform_tfvars = os.path.join(file_dir, "terraform.tfvars")
    if os.path.isfile(terraform_tfvars):
        paths.append(terraform_tfvars)

    paths.extend(sorted(glob.glob(os.path.join(file_dir, "*.auto.tfvars"))))

    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                declared |= _extract_declared_variables(handle.read())
        except Exception:
            # Unreadable file contributes nothing
            pass

    return declared


def _extract_required_variables_with_lines(content: str) -> List[Tuple[str, int]]:
    """
    Extract required variables (variables without defaults) with their line numbers.

    Excludes shared provider-related variables (see rules.common.provider_variables).

    Args:
        content (str): The Terraform file content

    Returns:
        List[Tuple[str, int]]: List of tuples containing (variable_name, line_number)
    """
    required_vars = []
    lines = content.split('\n')

    # Pattern to match variable definitions - support quoted, single-quoted, and unquoted syntax
    var_pattern = r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z][a-zA-Z0-9_]*[a-zA-Z]|[a-zA-Z]))\s*\{'

    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.search(var_pattern, line)
        if match:
            # Extract variable name from quoted, single-quoted, or unquoted group
            var_name = match.group(1) if match.group(1) else (match.group(2) if match.group(2) else match.group(3))
            line_number = i + 1  # Convert to 1-indexed

            # Find the end of this variable block
            brace_count = line.count('{') - line.count('}')
            j = i + 1
            var_content = line

            while j < len(lines) and brace_count > 0:
                var_content += '\n' + lines[j]
                brace_count += lines[j].count('{') - lines[j].count('}')
                j += 1

            # Check if variable has a default value and should not be excluded
            if not re.search(r'default\s*=', var_content) and not is_provider_related_variable(var_name):
                required_vars.append((var_name, line_number))

            i = j
        else:
            i += 1

    return required_vars


def _extract_declared_variables(content: str) -> Set[str]:
    """
    Extract top-level assignment names from a tfvars file body.

    Args:
        content (str): Content of terraform.tfvars or *.auto.tfvars

    Returns:
        Set[str]: Set of declared variable names
    """
    declared_vars = set()
    clean_content = _remove_comments_for_parsing(content)
    
    # Pattern to match variable declarations in tfvars
    # Matches: variable_name = value
    var_decl_pattern = r'^([a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]|[a-zA-Z])\s*='
    
    for line in clean_content.split('\n'):
        line = line.strip()
        if line:
            match = re.match(var_decl_pattern, line)
            if match:
                declared_vars.add(match.group(1))
    
    return declared_vars


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


def get_rule_description() -> dict:
    """
    Retrieve detailed information about the IO.003 rule.

    Returns:
        dict: A dictionary containing comprehensive rule information
    """
    return {
        "id": "IO.003",
        "name": "Required variable declaration check in terraform.tfvars",
        "description": (
            "Validates that variables without default values are declared in "
            "terraform.tfvars or sibling *.auto.tfvars (Terraform auto-load set). "
            "A default attribute — including default = null — makes the variable "
            "optional for this rule. Does not verify whether variables are referenced "
            "as var.<name> in module code (see IO.009). Does not load env-split "
            "*.tfvars or *.tfvars.json. Each missing declaration is reported with a "
            "precise line number. Provider-related variables (region / region_*, "
            "access_key, secret_key, domain_name, tenant/user/project identifiers) "
            "are excluded."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Variables without defaults need values from auto-loaded tfvars for "
            "non-interactive applies. This rule enforces that declaration contract; "
            "it is independent of whether the variable is referenced in .tf files. "
            "Provider-related variables are excluded because they are often supplied "
            "via environment variables or provider configuration."
        ),
        "examples": {
            "valid": [
                '''
# variables.tf
variable "region_name" {          # Excluded from IO.003 check
  description = "The region where resources are located"
  type        = string
}

variable "instance_name" {
  description = "Name of the ECS instance"
  type        = string
}

variable "tags" {
  description = "Optional tags"
  type        = map(string)
  default     = null              # Has default - optional for IO.003
}

# defaults.auto.tfvars (or terraform.tfvars)
instance_name = "my-instance"
'''
            ],
            "invalid": [
                '''
# variables.tf
variable "cpu_cores" {
  description = "Number of CPU cores"
  type        = number
}

# terraform.tfvars / *.auto.tfvars
# Missing cpu_cores

# Expected error:
# [IO.003] Required variable 'cpu_cores' (no default) must be declared in terraform.tfvars or *.auto.tfvars
'''
            ]
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.002"],
        "configuration": {
            "check_all_required_variables": True,
            "require_tfvars_file": True,
            "auto_tfvars_included": True,
            "report_individual_violations": True,
            "excluded_provider_variables": "shared via rules.common.provider_variables",
        }
    }
