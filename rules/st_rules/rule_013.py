#!/usr/bin/env python3
"""
ST.013 - Directory Naming Convention Check

This module implements the ST.013 rule which validates that all directory names
in the current directory and all subdirectories follow proper naming conventions.

Rule Specification:
- Directory names must contain only letters, numbers, and hyphens
- Directory names must start and end with a letter
- This applies to all directories at any depth from the current directory
- Helps maintain consistency in project structure and naming

Examples:
    Valid directory names:
        - my-project
        - terraform-modules
        - test-env-1
        - data-processing
        - api-gateway

    Invalid directory names:
        - _private-dir (starts with underscore)
        - my-project- (ends with hyphen)
        - 123-project (starts with number)
        - my_project (contains underscore)
        - my.project (contains dot)
        - my project (contains space)

Author: Lance
License: Apache 2.0
"""

import os
import re
from typing import Callable, List, Optional, Set
from pathlib import Path

# Global set to track checked directories to avoid duplicate checks
_checked_directories = set()


def check_st013_directory_naming(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if all directory names follow proper naming conventions.
    
    This function validates that all directory names in the current directory
    and all subdirectories follow the naming convention of:
    - Containing only letters, numbers, and hyphens
    - Starting and ending with a letter
    
    Args:
        file_path (str): Path to the file being checked (used to determine base directory)
        content (str): File content (not used for this rule)
        log_error_func (Callable): Function to log errors with signature (file_path, rule_id, message, line_num)
    """
    # Get the base directory from the file path
    base_dir = os.path.dirname(os.path.abspath(file_path))
    
    # Check if we've already checked this directory
    if base_dir in _checked_directories:
        return
    
    # Mark this directory as checked
    _checked_directories.add(base_dir)
    
    # Find all directories recursively
    directories = _find_all_directories(base_dir)
    
    # Check each directory name
    for dir_path in directories:
        dir_name = os.path.basename(dir_path)
        
        # Skip hidden directories and common system directories
        if _should_skip_directory(dir_name):
            continue
            
        # Check if directory name follows naming convention
        if not _is_valid_directory_name(dir_name):
            error_msg = f"Directory name '{dir_name}' does not follow naming convention. Must contain only letters, numbers, and hyphens, and start/end with a letter."
            log_error_func(dir_path, "ST.013", error_msg, None)


def _find_all_directories(base_dir: str) -> List[str]:
    """
    Find all directories recursively starting from the base directory.
    
    Args:
        base_dir (str): Base directory to start searching from
        
    Returns:
        List[str]: List of all directory paths found
    """
    directories = []
    
    try:
        # First, check the base directory itself
        base_dir_name = os.path.basename(base_dir)
        if not _should_skip_directory(base_dir_name):
            directories.append(base_dir)
        
        # Then, find all subdirectories recursively
        for root, dirs, files in os.walk(base_dir):
            # Filter out hidden directories from further traversal
            # This prevents os.walk from descending into hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and not _should_skip_directory(d)]
            
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                directories.append(dir_path)
    except (OSError, PermissionError) as e:
        # If we can't access a directory, skip it silently
        pass
    
    return directories


def _should_skip_directory(dir_name: str) -> bool:
    """
    Check if a directory should be skipped from naming convention checks.
    
    Args:
        dir_name (str): Directory name to check
        
    Returns:
        bool: True if directory should be skipped, False otherwise
    """
    # Skip hidden directories
    if dir_name.startswith('.'):
        return True
    
    # Skip common system directories
    skip_dirs = {
        '__pycache__',
        'node_modules',
        '.git',
        '.svn',
        '.hg',
        'venv',
        'env',
        '.venv',
        '.env',
        'build',
        'dist',
        'target',
        'bin',
        'obj',
        '.vs',
        '.vscode',
        '.idea',
        '.settings',
        'coverage',
        '.coverage',
        'htmlcov',
        '.pytest_cache',
        '.tox',
        '.mypy_cache',
        '.ruff_cache',
        # Terraform-specific directories
        '.terraform',
        'terraform.tfstate.d'
    }
    
    return dir_name.lower() in skip_dirs


def _is_valid_directory_name(dir_name: str) -> bool:
    """
    Check if a directory name follows the naming convention.
    
    Args:
        dir_name (str): Directory name to validate
        
    Returns:
        bool: True if directory name is valid, False otherwise
    """
    # Check if directory name is empty
    if not dir_name:
        return False
    
    # Check if directory name contains only letters, numbers, and hyphens
    if not re.match(r'^[a-zA-Z0-9-]+$', dir_name):
        return False
    
    # Check if directory name starts and ends with a letter
    if not re.match(r'^[a-zA-Z].*[a-zA-Z]$', dir_name):
        return False
    
    # Check for consecutive hyphens (not allowed)
    if '--' in dir_name:
        return False
    
    return True


def get_rule_description() -> dict:
    """
    Get the rule description for ST.013.
    
    Returns:
        dict: Rule description containing metadata and details
    """
    return {
        "rule_id": "ST.013",
        "title": "Directory Naming Convention Check",
        "category": "Style/Format",
        "severity": "warning",
        "description": "Validates that all directory names follow proper naming conventions",
        "rationale": "Ensures consistent directory naming across the project structure",
        "scope": ["directory_naming", "project_structure", "naming_conventions"],
        "implementation": "modular",
        "version": "1.0.0",
        "naming_pattern": {
            "allowed_characters": "letters (a-z, A-Z), numbers (0-9), hyphens (-)",
            "start_character": "must be a letter",
            "end_character": "must be a letter",
            "consecutive_hyphens": "not allowed"
        },
        "examples": {
            "valid": [
                "my-project",
                "terraform-modules", 
                "test-env-1",
                "data-processing",
                "api-gateway",
                "user-management",
                "config-files"
            ],
            "invalid": [
                "_private-dir (starts with underscore)",
                "my-project- (ends with hyphen)",
                "123-project (starts with number)",
                "my_project (contains underscore)",
                "my.project (contains dot)",
                "my project (contains space)",
                "my--project (consecutive hyphens)"
            ]
        },
        "fix_suggestions": [
            "Use only letters, numbers, and hyphens in directory names",
            "Ensure directory names start and end with a letter",
            "Avoid consecutive hyphens in directory names",
            "Use kebab-case naming convention (lowercase with hyphens)",
            "Make directory names descriptive and meaningful"
        ],
        "excluded_directories": [
            "Hidden directories (starting with .)",
            "System directories (__pycache__, node_modules, .git, etc.)",
            "Build and cache directories (build, dist, target, etc.)",
            "IDE and editor directories (.vscode, .idea, .settings, etc.)"
        ],
        "recursive_check": True,
        "max_depth": "unlimited"
    }
