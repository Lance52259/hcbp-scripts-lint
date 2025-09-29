#!/usr/bin/env python3
"""
SC.005 - Sensitive Variable Declaration Check

This module implements the SC.005 rule which validates that sensitive variables
are properly declared with Sensitive=true in Terraform variable blocks.

Rule Specification:
- Variables with sensitive names must have Sensitive=true declaration
- Supports both exact matching and fuzzy matching for variable names
- Helps prevent sensitive data exposure in Terraform state and logs
- Ensures proper handling of sensitive configuration values

Sensitive Variable Patterns:
1. Exact match: email, age, access_key, secret_key, sex, signature
2. Fuzzy match: phone (contains "phone"), password (contains "password"), pwd (contains "pwd")

Examples:
    Valid variable declarations:
        variable "email" {
          type        = string
          description = "User email address"
          sensitive   = true
        }
        
        variable "user_password" {
          type        = string
          description = "User password"
          sensitive   = true
        }

    Invalid variable declarations:
        variable "email" {
          type        = string
          description = "User email address"
          # Missing sensitive = true
        }
        
        variable "user_password" {
          type        = string
          description = "User password"
          # Missing sensitive = true
        }

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, Optional, List, Set, Dict


def check_sc005_sensitive_variable_declaration(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if sensitive variables are properly declared with Sensitive=true.
    
    This function validates that variables with sensitive names have the
    Sensitive=true declaration in their variable blocks to prevent
    sensitive data exposure in Terraform state and logs.
    
    Args:
        file_path (str): Path to the Terraform file being checked
        content (str): Content of the Terraform file
        log_error_func (Callable): Function to log errors with signature (file_path, rule_id, message, line_num)
    """
    # Define sensitive variable patterns
    sensitive_patterns = _get_sensitive_variable_patterns()
    
    # Parse variable blocks and check for sensitive declarations
    variable_blocks = _parse_variable_blocks(content)
    
    for var_block in variable_blocks:
        var_name = var_block['name']
        var_line = var_block['line']
        var_content = var_block['content']
        
        # Check if this variable name matches any sensitive pattern
        is_sensitive = _is_sensitive_variable(var_name, sensitive_patterns)
        
        if is_sensitive:
            # Check if Sensitive=true is declared
            if not _has_sensitive_declaration(var_content):
                error_msg = f"Sensitive variable '{var_name}' must be declared with 'sensitive = true' to prevent data exposure in Terraform state and logs."
                log_error_func(file_path, "SC.005", error_msg, var_line)


def _get_sensitive_variable_patterns() -> Dict[str, List[str]]:
    """
    Get the patterns for sensitive variable names.
    
    Returns:
        Dict[str, List[str]]: Dictionary with 'exact' and 'fuzzy' pattern lists
    """
    return {
        'exact': [
            'email',
            'age', 
            'access_key',
            'secret_key',
            'sex',
            'signature'
        ],
        'fuzzy': [
            'phone',
            'password', 
            'pwd'
        ]
    }


def _is_sensitive_variable(var_name: str, patterns: Dict[str, List[str]]) -> bool:
    """
    Check if a variable name matches any sensitive pattern.
    
    Args:
        var_name (str): Variable name to check
        patterns (Dict[str, List[str]]): Sensitive patterns dictionary
        
    Returns:
        bool: True if variable is sensitive, False otherwise
    """
    var_name_lower = var_name.lower()
    
    # Check exact matches
    for exact_pattern in patterns['exact']:
        if var_name_lower == exact_pattern:
            return True
    
    # Check fuzzy matches (contains)
    for fuzzy_pattern in patterns['fuzzy']:
        if fuzzy_pattern in var_name_lower:
            return True
    
    return False


def _has_sensitive_declaration(var_content: str) -> bool:
    """
    Check if a variable block contains Sensitive=true declaration.
    
    Args:
        var_content (str): Variable block content
        
    Returns:
        bool: True if Sensitive=true is found, False otherwise
    """
    lines = var_content.split('\n')
    
    for line in lines:
        # Remove comments from line
        clean_line = re.sub(r'#.*$', '', line).strip()
        
        # Skip empty lines
        if not clean_line:
            continue
            
        # Look for sensitive = true (case insensitive)
        sensitive_pattern = r'sensitive\s*=\s*true'
        if re.search(sensitive_pattern, clean_line, re.IGNORECASE):
            return True
    
    return False


def _parse_variable_blocks(content: str) -> List[Dict[str, any]]:
    """
    Parse variable blocks from Terraform content.
    
    Args:
        content (str): Terraform file content
        
    Returns:
        List[Dict[str, any]]: List of variable block information
    """
    variable_blocks = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for variable block start
        var_match = re.match(r'variable\s+"([^"]+)"\s*\{', line.strip())
        if var_match:
            var_name = var_match.group(1)
            var_start_line = i + 1
            
            # Find the end of the variable block
            brace_count = 1
            var_content_lines = [line]
            i += 1
            
            while i < len(lines) and brace_count > 0:
                line = lines[i]
                var_content_lines.append(line)
                
                # Count braces to find block end
                for char in line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            break
                
                i += 1
            
            # Join content and store variable block info
            var_content = '\n'.join(var_content_lines)
            variable_blocks.append({
                'name': var_name,
                'line': var_start_line,
                'content': var_content
            })
        else:
            i += 1
    
    return variable_blocks


def get_rule_description() -> dict:
    """
    Get the rule description for SC.005.
    
    Returns:
        dict: Rule description containing metadata and details
    """
    return {
        "rule_id": "SC.005",
        "title": "Sensitive Variable Declaration Check",
        "category": "Security Code",
        "severity": "error",
        "description": "Validates that sensitive variables are properly declared with Sensitive=true",
        "rationale": "Sensitive variables without proper declaration can expose sensitive data in Terraform state files and logs, creating security risks",
        "scope": ["variable_declaration", "sensitive_data", "security_compliance"],
        "implementation": "modular",
        "version": "1.0.0",
        "sensitive_patterns": {
            "exact_match": [
                "email",
                "age",
                "access_key", 
                "secret_key",
                "sex",
                "signature"
            ],
            "fuzzy_match": [
                "phone (contains 'phone')",
                "password (contains 'password')",
                "pwd (contains 'pwd')"
            ]
        },
        "examples": {
            "valid": [
                'variable "email" {\n  type        = string\n  description = "User email address"\n  sensitive   = true\n}',
                'variable "user_password" {\n  type        = string\n  description = "User password"\n  sensitive   = true\n}',
                'variable "access_key" {\n  type        = string\n  description = "API access key"\n  sensitive   = true\n}'
            ],
            "invalid": [
                'variable "email" {\n  type        = string\n  description = "User email address"\n  # Missing sensitive = true\n}',
                'variable "user_password" {\n  type        = string\n  description = "User password"\n  # Missing sensitive = true\n}',
                'variable "access_key" {\n  type        = string\n  description = "API access key"\n  # Missing sensitive = true\n}'
            ]
        },
        "fix_suggestions": [
            "Add 'sensitive = true' to all sensitive variable declarations",
            "Review variable names against sensitive patterns list",
            "Ensure all variables containing sensitive data are properly marked",
            "Consider using more descriptive variable names for non-sensitive data",
            "Regularly audit variable declarations for sensitive data exposure"
        ],
        "security_impact": {
            "risk_level": "high",
            "exposure_points": [
                "Terraform state files",
                "Terraform plan output",
                "Terraform apply logs",
                "CI/CD pipeline logs"
            ],
            "mitigation": "Declaring sensitive variables prevents their values from being displayed in logs and state files"
        }
    }
