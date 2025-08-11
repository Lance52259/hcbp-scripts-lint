#!/usr/bin/env python3
"""
SC.002 - Terraform Required Version Declaration Check

This module implements the SC.002 rule which validates that providers.tf files
contain proper Terraform required version declarations.

Rule Specification:
- providers.tf files should contain a terraform block with required_version declaration
- This ensures consistent Terraform version usage across the project
- Prevents version compatibility issues and improves deployment reliability

Examples:
    Valid providers.tf:
        terraform {
          required_version = ">= 1.3.0"
          
          required_providers {
            huaweicloud = {
              source  = "huaweicloud/huaweicloud"
              version = ">=1.70.1"
            }
          }
        }

    Invalid providers.tf:
        # Missing terraform block with required_version
        required_providers {
          huaweicloud = {
            source  = "huaweicloud/huaweicloud"
            version = ">=1.70.1"
          }
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, Optional


def check_sc002_terraform_version_declaration(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if providers.tf files contain proper Terraform required version declarations.
    
    This function validates that providers.tf files include a terraform block
    with required_version declaration to ensure consistent Terraform version usage
    across the project and prevent version compatibility issues.
    
    The function specifically checks:
    - File is named providers.tf
    - File contains a terraform block
    - terraform block contains required_version declaration
    - required_version has a valid version constraint format
    
    Valid declarations:
    - terraform { required_version = ">= 1.3.0" }
    - terraform { required_version = "~> 1.0" }
    - terraform { required_version = ">= 0.14.0, < 2.0.0" }
    
    Args:
        file_path (str): The path to the Terraform file being validated.
                        Used for error reporting to identify the source file.
        content (str): The complete content of the Terraform file as a string.
                      This content is parsed to extract and validate terraform blocks.
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
        ... required_providers {
        ...   huaweicloud = {
        ...     source  = "huaweicloud/huaweicloud"
        ...     version = ">=1.70.1"
        ...   }
        ... }
        ... '''
        >>> check_sc002_terraform_version_declaration("providers.tf", content, sample_log_func)
        SC.002 at providers.tf:1: Missing terraform block with required_version declaration
    """
    # Only check providers.tf files
    if not file_path.endswith('providers.tf'):
        return
    
    lines = content.split('\n')
    
    # Check if file contains terraform block
    terraform_block_found = False
    required_version_found = False
    terraform_block_start_line = None
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check for terraform block start
        if line == 'terraform {' or line.startswith('terraform {') or line.startswith('terraform{'):
            terraform_block_found = True
            terraform_block_start_line = line_num
            continue
        
        # If we're inside a terraform block, look for required_version
        if terraform_block_found:
            # Check for required_version declaration
            if 'required_version' in line and '=' in line:
                required_version_found = True
                # Validate version constraint format
                version_match = re.search(r'required_version\s*=\s*["\']([^"\']+)["\']', line)
                if version_match:
                    version_constraint = version_match.group(1)
                    if not _is_valid_version_constraint(version_constraint):
                        log_error_func(
                            file_path,
                            "SC.002",
                            f"Invalid version constraint format: '{version_constraint}'. Use format like '>= 1.3.0' or '~> 1.0'",
                            line_num
                        )
                break
            
            # Check for terraform block end
            if line == '}' or line.endswith('}'):
                break
    
    # Report errors
    if not terraform_block_found:
        log_error_func(
            file_path,
            "SC.002",
            "Missing terraform block with required_version declaration",
            1
        )
    elif not required_version_found:
        log_error_func(
            file_path,
            "SC.002",
            "terraform block found but missing required_version declaration",
            terraform_block_start_line or 1
        )


def _is_valid_version_constraint(constraint: str) -> bool:
    """
    Validate if the version constraint format is correct.
    
    Args:
        constraint (str): Version constraint string
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic validation for common version constraint patterns
    valid_patterns = [
        r'^\s*>=?\s*\d+\.\d+(?:\.\d+)?\s*$',  # >= 1.3.0, > 1.3.0
        r'^\s*<=?\s*\d+\.\d+(?:\.\d+)?\s*$',  # <= 1.3.0, < 1.3.0
        r'^\s*~\s*>\s*\d+\.\d+\s*$',          # ~> 1.0
        r'^\s*=\s*\d+\.\d+(?:\.\d+)?\s*$',    # = 1.3.0
        r'^\s*>=?\s*\d+\.\d+(?:\.\d+)?\s*,\s*<=?\s*\d+\.\d+(?:\.\d+)?\s*$',  # >= 0.14.0, < 2.0.0
    ]
    
    constraint = constraint.strip()
    return any(re.match(pattern, constraint) for pattern in valid_patterns)


def get_rule_description() -> dict:
    """
    Get the rule description for SC.002.
    
    Returns:
        dict: Rule description with name, description, and examples
    """
    return {
        "name": "Terraform required version declaration check",
        "description": "Validates that providers.tf files contain a terraform block with required_version declaration to ensure consistent Terraform version usage across the project.",
        "category": "Security Code",
        "severity": "warning",
        "examples": {
            "valid": [
                'terraform {\\n  required_version = ">= 1.3.0"\\n  \\n  required_providers {\\n    huaweicloud = {\\n      source  = "huaweicloud/huaweicloud"\\n      version = ">=1.70.1"\\n    }\\n  }\\n}',
                'terraform {\\n  required_version = "~> 1.0"\\n  \\n  required_providers {\\n    huaweicloud = {\\n      source  = "huaweicloud/huaweicloud"\\n      version = ">=1.70.1"\\n    }\\n  }\\n}'
            ],
            "invalid": [
                'required_providers {\\n  huaweicloud = {\\n    source  = "huaweicloud/huaweicloud"\\n    version = ">=1.70.1"\\n  }\\n}',
                'terraform {\\n  required_providers {\\n    huaweicloud = {\\n      source  = "huaweicloud/huaweicloud"\\n      version = ">=1.70.1"\\n    }\\n  }\\n}'
            ]
        },
        "fix_suggestions": [
            "Add terraform block with required_version declaration",
            "Use proper version constraint format (e.g., '>= 1.3.0', '~> 1.0')",
            "Ensure required_version is declared before required_providers"
        ]
    } 