#!/usr/bin/env python3
"""
SC.003 - Terraform Version Compatibility Check

This module implements the SC.003 rule which validates that the declared
Terraform required_version in providers.tf is compatible with the features
used in the Terraform configuration.

Rule Specification:
- Analyzes Terraform configuration to determine minimum required version
- Validates that declared required_version meets the actual version requirements
- Prevents runtime errors from version incompatibilities

Version Requirements:
1. variable/output sensitive = "true" requires >= 0.14.0
2. variable nullable = "true" requires >= 1.1.0  
3. variable type with optional() requires >= 1.3.0
4. resource lifecycle precondition requires >= 1.2.0
5. variable validation with other variable references requires >= 1.9.0
6. import block with for_each requires >= 1.7.0
7. Default minimum version: 0.12.0

Examples:
    Valid providers.tf with correct version:
        terraform {
          required_version = ">= 1.3.0"  # Correct for optional() usage
        }
        
        variable "example" {
          type = optional(string)
        }

    Invalid providers.tf with incorrect version:
        terraform {
          required_version = ">= 0.14.0"  # Too low for optional() usage
        }
        
        variable "example" {
          type = optional(string)  # Requires >= 1.3.0
        }

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, Optional, List, Dict, Set, Tuple


def check_sc003_terraform_version_compatibility(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if the declared Terraform required_version is compatible with used features.
    
    This function analyzes the Terraform configuration to determine the minimum
    required version based on the features used, then validates that the declared
    required_version in providers.tf meets these requirements.
    
    The function specifically checks:
    - Variable/output sensitive attribute (requires >= 0.14.0)
    - Variable nullable attribute (requires >= 1.1.0)
    - Variable type with optional() function (requires >= 1.3.0)
    - Resource lifecycle precondition (requires >= 1.2.0)
    - Variable validation with other variable references (requires >= 1.9.0)
    - Import block with for_each (requires >= 1.7.0)
    - Default minimum version: 0.12.0
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to extract and validate version requirements.
        log_error_func (Callable[[str, str, str, Optional[int]], None]):
                      Callback function for logging validation errors. The function
                      signature expects (file_path, rule_id, error_message, line_number).
                      The line_number parameter is optional and can be None.
    
    Returns:
        None: This function doesn't return any value. All validation results
              are communicated through the log_error_func callback.
    
    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.
    
    Example:
        >>> def sample_log_func(path, rule, msg, line_num):
        ...     print(f"{rule} at {path}:{line_num}: {msg}")
        >>>
        >>> content = '''
        ... terraform {
        ...   required_version = ">= 0.14.0"
        ... }
        ... 
        ... variable "example" {
        ...   type = optional(string)
        ... }
        ... '''
        >>> check_sc003_terraform_version_compatibility("providers.tf", content, sample_log_func)
        SC.003 at providers.tf:2: Declared version '>= 0.14.0' is too low. Required: '>= 1.3.0' (for optional() usage)
    """
    # Get the directory to analyze all .tf files
    file_dir = os.path.dirname(file_path)
    
    # Analyze all .tf files in the directory to determine minimum required version
    min_required_version, used_features = _determine_minimum_required_version(file_dir)
    
    # Extract declared version from providers.tf
    declared_version = _extract_declared_version(content)
    
    if declared_version and min_required_version:
        # Compare versions
        if not _is_version_compatible(declared_version, min_required_version):
            # Generate feature description
            feature_description = _generate_feature_description(used_features)
            log_error_func(
                file_path,
                "SC.003",
                f"Declared version '{declared_version}' is too low. Required: '{min_required_version}' {feature_description}",
                1
            )


def _determine_minimum_required_version(directory: str) -> Tuple[str, List[str]]:
    """
    Determine the minimum required Terraform version based on features used.
    
    Args:
        directory (str): Directory path to analyze
        
    Returns:
        Tuple[str, List[str]]: (Minimum required version, List of used features)
    """
    required_versions = []
    used_features = []
    
    # Find all .tf files in the directory
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.tf'):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_versions, file_features = _analyze_file_for_version_requirements(content)
                        required_versions.extend(file_versions)
                        used_features.extend(file_features)
                except Exception:
                    continue
    
    # Return the highest required version, or default to 0.12.0
    if required_versions:
        # Sort versions and return the highest
        sorted_versions = sorted(required_versions, key=lambda x: _parse_version(x))
        return sorted_versions[-1], used_features
    else:
        return ">= 0.12.0", []


def _analyze_file_for_version_requirements(content: str) -> Tuple[List[str], List[str]]:
    """
    Analyze file content to determine version requirements.
    
    Args:
        content (str): File content to analyze
        
    Returns:
        Tuple[List[str], List[str]]: (List of required versions, List of used features)
    """
    required_versions = []
    used_features = []
    lines = content.split('\n')
    
    in_variable_block = False
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check for variable block start
        if line.startswith('variable '):
            in_variable_block = True
            continue
        
        # Check for variable block end
        if in_variable_block and line == '}':
            in_variable_block = False
            continue
        
        # Check for sensitive attribute in variable/output
        if 'sensitive' in line and in_variable_block:
            if '= "true"' in line or '= true' in line:
                required_versions.append(">= 0.14.0")
                used_features.append("sensitive")
        
        # Check for nullable attribute in variable
        if 'nullable' in line and in_variable_block:
            if '=' in line:  # Check if nullable attribute is used (regardless of value)
                required_versions.append(">= 1.1.0")
                used_features.append("nullable")
        
        # Check for optional() function in variable type (inside variable block)
        if 'optional(' in line and in_variable_block:
            required_versions.append(">= 1.3.0")
            used_features.append("optional()")
        
        # Check for lifecycle precondition
        if 'lifecycle' in line:
            # Look for precondition in the next few lines within the lifecycle block
            for i in range(line_num, min(line_num + 10, len(lines))):
                if 'precondition' in lines[i]:
                    required_versions.append(">= 1.2.0")
                    used_features.append("lifecycle.precondition")
                    break
                if lines[i].strip() == '}':
                    break
        
        # Check for variable validation with other variable references
        if 'validation' in line and in_variable_block:
            # Look for var. references in the next few lines and analyze if they reference other variables
            current_variable_name = None
            for i in range(line_num - 1, max(-1, line_num - 10), -1):
                # Find the current variable name by looking backwards
                if i >= 0 and lines[i].strip().startswith('variable '):
                    match = re.search(r'variable\s+"([^"]+)"', lines[i])
                    if match:
                        current_variable_name = match.group(1)
                        break
            
            if current_variable_name:
                # Look for var. references in the validation block
                for i in range(line_num, min(line_num + 10, len(lines))):
                    if 'var.' in lines[i]:
                        # Check if this var. reference is to a different variable
                        var_matches = re.findall(r'var\.([a-zA-Z0-9_-]+)', lines[i])
                        for var_name in var_matches:
                            if var_name != current_variable_name:
                                # Found reference to another variable
                                required_versions.append(">= 1.9.0")
                                used_features.append("other variables are referenced in validation.condition")
                                break
                        if ">= 1.9.0" in required_versions:
                            break
                    if lines[i].strip() == '}':
                        break
        
        # Check for import block with for_each
        if 'import' in line:
            # Look for for_each in the next few lines within the import block
            in_import_block = True
            for i in range(line_num, min(line_num + 10, len(lines))):
                if 'for_each' in lines[i]:
                    required_versions.append(">= 1.7.0")
                    used_features.append("import.for_each")
                    break
                if lines[i].strip() == '}':
                    break
    
    return required_versions, used_features


def _generate_feature_description(used_features: List[str]) -> str:
    """
    Generate a description of the features that require the version.
    
    Args:
        used_features (List[str]): List of used features
        
    Returns:
        str: Feature description string
    """
    if not used_features:
        return "(no special feature used)"
    
    # Remove duplicates while preserving order
    unique_features = []
    for feature in used_features:
        if feature not in unique_features:
            unique_features.append(feature)
    
    if len(unique_features) == 1:
        return f"based on feature '{unique_features[0]}' used"
    else:
        # For multiple features, show them in a list
        feature_list = "', '".join(unique_features)
        return f"based on features '{feature_list}' used"


def _extract_declared_version(content: str) -> Optional[str]:
    """
    Extract the declared required_version from providers.tf content.
    
    Args:
        content (str): File content
        
    Returns:
        Optional[str]: Declared version or None if not found
    """
    lines = content.split('\n')
    in_terraform_block = False
    
    for line in lines:
        line = line.strip()
        
        # Check for terraform block start
        if line == 'terraform {' or line.startswith('terraform {') or line.startswith('terraform{'):
            in_terraform_block = True
            continue
        
        # If inside terraform block, look for required_version
        if in_terraform_block:
            if 'required_version' in line and '=' in line:
                match = re.search(r'required_version\s*=\s*["\']([^"\']+)["\']', line)
                if match:
                    return match.group(1)
            
            # Check for terraform block end
            if line == '}' or line.endswith('}'):
                break
    
    return None


def _is_version_compatible(declared_version: str, required_version: str) -> bool:
    """
    Check if declared version is compatible with required version.
    
    Args:
        declared_version (str): Version declared in providers.tf
        required_version (str): Version required by features
        
    Returns:
        bool: True if compatible, False otherwise
    """
    # Parse versions to compare
    declared_min = _parse_version(declared_version)
    required_min = _parse_version(required_version)
    
    return declared_min >= required_min


def _parse_version(version_constraint: str) -> List[int]:
    """
    Parse version constraint to get minimum version.
    
    Args:
        version_constraint (str): Version constraint (e.g., ">= 1.3.0")
        
    Returns:
        List[int]: Version as list of integers [major, minor, patch]
    """
    # Extract version number from constraint
    match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', version_constraint)
    if match:
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3)) if match.group(3) else 0
        return [major, minor, patch]
    else:
        return [0, 0, 0]


def get_rule_description() -> dict:
    """
    Get the rule description for SC.003.
    
    Returns:
        dict: Rule description with name, description, and examples
    """
    return {
        "name": "Terraform version compatibility check",
        "description": "Validates that the declared Terraform required_version in providers.tf is compatible with the features used in the Terraform configuration.",
        "category": "Security Code",
        "severity": "error",
        "examples": {
            "valid": [
                'terraform {\\n  required_version = ">= 1.3.0"\\n}\\n\\nvariable "example" {\\n  type = optional(string)\\n}',
                'terraform {\\n  required_version = ">= 1.9.0"\\n}\\n\\nvariable "example" {\\n  validation {\\n    condition = var.other_var != ""\\n  }\\n}'
            ],
            "invalid": [
                'terraform {\\n  required_version = ">= 0.14.0"\\n}\\n\\nvariable "example" {\\n  type = optional(string)\\n}',
                'terraform {\\n  required_version = ">= 1.1.0"\\n}\\n\\nvariable "example" {\\n  validation {\\n    condition = var.other_var != ""\\n  }\\n}'
            ]
        },
        "fix_suggestions": [
            "Update required_version to match the highest version requirement from used features",
            "Review all .tf files in the directory for version-dependent features",
            "Use version constraints that accommodate all used features"
        ],
        "version_requirements": {
            "sensitive attribute": ">= 0.14.0",
            "nullable attribute": ">= 1.1.0",
            "optional() function": ">= 1.3.0",
            "lifecycle precondition": ">= 1.2.0",
            "validation with var references": ">= 1.9.0",
            "import with for_each": ">= 1.7.0",
            "default minimum": ">= 0.12.0"
        }
    } 