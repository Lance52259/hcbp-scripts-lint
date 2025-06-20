#!/usr/bin/env python3
"""
ST.011 - Trailing Whitespace Check

Validates that no lines contain trailing whitespace characters (spaces, tabs, or other whitespace)
at the end of lines.

Purpose:
- Prevents unnecessary diff noise in version control systems
- Maintains clean and consistent code formatting
- Follows general coding best practices for all languages
- Ensures compatibility with automated formatting tools
- Reduces merge conflicts caused by inconsistent whitespace

Rule Details:
- Checks all lines in Terraform files
- Detects trailing spaces, tabs, and other whitespace characters
- Reports each violation with specific line number and character details
- Provides detailed character type information in error messages

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, Optional


def check_st011_trailing_whitespace(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check for trailing whitespace characters at the end of lines.
    
    This function validates that no lines contain trailing whitespace characters
    including spaces, tabs, or other whitespace at the end of lines.
    
    Args:
        file_path (str): Path to the file being checked
        content (str): Content of the file to check
        log_error_func (Callable): Function to log errors with signature
                                 (file_path, rule_id, message, line_number)
    
    Returns:
        None
    
    Examples:
        Valid lines (no trailing whitespace):
        >>> content = '''resource "test" "example" {
        ...   name = "test"
        ... }'''
        >>> # No errors reported
        
        Invalid lines (with trailing whitespace):
        >>> content = '''resource "test" "example" { 
        ...   name = "test"\\t
        ... }'''
        >>> # Errors reported for lines with trailing space and tab
    """
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Check if line ends with whitespace characters
        if line and line != line.rstrip():
            # Get the trailing whitespace characters
            trailing_chars = line[len(line.rstrip()):]
            
            # Analyze the types of whitespace characters
            whitespace_types = []
            for char in trailing_chars:
                if char == ' ':
                    whitespace_types.append('space')
                elif char == '\t':
                    whitespace_types.append('tab')
                else:
                    whitespace_types.append(f'whitespace({ord(char)})')
            
            whitespace_desc = ', '.join(whitespace_types)
            error_msg = f"Line contains trailing whitespace characters: {whitespace_desc}"
            log_error_func(file_path, "ST.011", error_msg, line_num)


def get_rule_description() -> dict:
    """
    Get the rule description for ST.011.
    
    Returns:
        dict: Rule description containing metadata and details
    """
    return {
        "rule_id": "ST.011",
        "title": "Trailing Whitespace Check", 
        "category": "Style/Format",
        "severity": "warning",
        "description": "Validates that no lines contain trailing whitespace characters",
        "rationale": "Trailing whitespace can cause issues in version control and is generally considered poor practice",
        "scope": ["all_lines"],
        "implementation": "modular",
        "version": "1.0.0",
        "examples": {
            "valid": [
                'resource "huaweicloud_compute_instance" "test" {',
                '  name = "example"',
                '}'
            ],
            "invalid": [
                'resource "huaweicloud_compute_instance" "test" { ',
                '  name = "example"\t',
                '}  '
            ]
        },
        "fix_suggestions": [
            "Remove trailing spaces and tabs from the end of lines",
            "Configure your editor to automatically trim trailing whitespace",
            "Use a linter or formatter that handles trailing whitespace"
        ]
    }
