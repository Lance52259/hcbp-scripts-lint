#!/usr/bin/env python3
"""
ST.014 - File Naming Convention Check

This module implements the ST.014 rule which validates that all file names
in the current directory and all subdirectories follow proper naming conventions.

Rule Specification:
- File names must contain only letters, numbers, and underscores
- File names must start and end with a letter
- This applies to all files at any depth from the current directory
- Helps maintain consistency in project structure and naming

Examples:
    Valid file names:
        - main.tf
        - variables.tf
        - terraform_config.tf
        - test_file.tfvars
        - data_processing.py

    Invalid file names:
        - _private.tf (starts with underscore)
        - config-.tf (ends with underscore)
        - 123_config.tf (starts with number)
        - my-file.tf (contains hyphen)
        - my.file.tf (contains dot in name)
        - my file.tf (contains space)

Author: Lance
License: Apache 2.0
"""

import os
import re
from typing import Callable, List, Optional, Set
from pathlib import Path


def check_st014_file_naming(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check if all file names follow proper naming conventions.
    
    This function validates that all file names in the current directory
    and all subdirectories follow the naming convention of:
    - Containing only letters, numbers, and underscores
    - Starting and ending with a letter
    
    Args:
        file_path (str): Path to the file being checked (used to determine base directory)
        content (str): File content (not used for this rule)
        log_error_func (Callable): Function to log errors with signature (file_path, rule_id, message, line_num)
    """
    # Get the base directory from the file path
    base_dir = os.path.dirname(os.path.abspath(file_path))
    
    # Find all files recursively
    files = _find_all_files(base_dir)
    
    # Check each file name
    for file_path in files:
        file_name = os.path.basename(file_path)
        
        # Skip hidden files and common system files
        if _should_skip_file(file_name):
            continue
            
        # Check if file name follows naming convention
        if not _is_valid_file_name(file_name):
            error_msg = f"File name '{file_name}' does not follow naming convention. Must contain only letters, numbers, and underscores, and start/end with a letter."
            log_error_func(file_path, "ST.014", error_msg, None)


def _find_all_files(base_dir: str) -> List[str]:
    """
    Find all files recursively starting from the base directory.
    
    Args:
        base_dir (str): Base directory to start searching from
        
    Returns:
        List[str]: List of all file paths found
    """
    files = []
    
    try:
        for root, dirs, filenames in os.walk(base_dir):
            # Filter out hidden directories from further traversal
            # This prevents os.walk from descending into hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and not _should_skip_directory(d)]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
    except (OSError, PermissionError) as e:
        # If we can't access a directory, skip it silently
        pass
    
    return files


def _should_skip_directory(dir_name: str) -> bool:
    """
    Check if a directory should be skipped from traversal.
    
    Args:
        dir_name (str): Directory name to check
        
    Returns:
        bool: True if directory should be skipped, False otherwise
    """
    # Skip hidden directories
    if dir_name.startswith('.'):
        return True
    
    # Skip common system directories and Terraform-specific directories
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
        'tmp',
        'temp',
        'vendor',
        'examples',
        'test',
        'tests',
        # Terraform-specific directories
        '.terraform',
        'terraform.tfstate.d'
    }
    
    return dir_name.lower() in skip_dirs


def _should_skip_file(file_name: str) -> bool:
    """
    Check if a file should be skipped from naming convention checks.
    
    Args:
        file_name (str): File name to check
        
    Returns:
        bool: True if file should be skipped, False otherwise
    """
    # Skip hidden files
    if file_name.startswith('.'):
        return True
    
    # Skip Terraform auto.tfvars files (xxx.auto.tfvars format)
    if file_name.endswith('.auto.tfvars'):
        return True
    
    # Skip Terraform state files (terraform.tfstate and variations)
    if file_name.startswith('terraform.tfstate'):
        return True
    
    # Skip log files
    if file_name.endswith('.log'):
        return True
    
    # Skip common system files
    skip_files = {
        'Thumbs.db',
        'desktop.ini',
        '.DS_Store',
        '.gitkeep',
        '.gitignore',
        '.gitattributes',
        '.editorconfig',
        '.eslintrc',
        '.prettierrc',
        '.prettierignore',
        '.dockerignore',
        'Dockerfile',
        'docker-compose.yml',
        'docker-compose.yaml',
        'Makefile',
        'Rakefile',
        'Gemfile',
        'Gemfile.lock',
        'package.json',
        'package-lock.json',
        'yarn.lock',
        'requirements.txt',
        'Pipfile',
        'Pipfile.lock',
        'poetry.lock',
        'pyproject.toml',
        'setup.py',
        'setup.cfg',
        'tox.ini',
        'pytest.ini',
        '.pytest_cache',
        'coverage.xml',
        '.coverage',
        'htmlcov',
        '.mypy_cache',
        '.ruff_cache',
        'node_modules',
        'venv',
        'env',
        '.venv',
        '.env',
        '__pycache__',
        '.pytest_cache',
        '.tox',
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
        # Terraform-specific files
        'terraform.tfstate',
        'terraform.tfstate.backup',
        '.terraform.lock.hcl',
        '.terraform.tfstate.lock.info'
    }
    
    return file_name.lower() in skip_files


def _is_valid_file_name(file_name: str) -> bool:
    """
    Check if a file name follows the naming convention.
    
    Args:
        file_name (str): File name to validate
        
    Returns:
        bool: True if file name is valid, False otherwise
    """
    # Check if file name is empty
    if not file_name:
        return False
    
    # Split file name and extension
    name_part, ext_part = os.path.splitext(file_name)
    
    # Check if name part contains only letters, numbers, and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', name_part):
        return False
    
    # Check if name part starts and ends with a letter
    if not re.match(r'^[a-zA-Z].*[a-zA-Z]$', name_part):
        return False
    
    # Check for consecutive underscores (not allowed)
    if '__' in name_part:
        return False
    
    return True


def get_rule_description() -> dict:
    """
    Get the rule description for ST.014.
    
    Returns:
        dict: Rule description containing metadata and details
    """
    return {
        "rule_id": "ST.014",
        "title": "File Naming Convention Check",
        "category": "Style/Format",
        "severity": "warning",
        "description": "Validates that all file names follow proper naming conventions",
        "rationale": "Ensures consistent file naming across the project structure",
        "scope": ["file_naming", "project_structure", "naming_conventions"],
        "implementation": "modular",
        "version": "1.0.0",
        "naming_pattern": {
            "allowed_characters": "letters (a-z, A-Z), numbers (0-9), underscores (_)",
            "start_character": "must be a letter",
            "end_character": "must be a letter",
            "consecutive_underscores": "not allowed"
        },
        "examples": {
            "valid": [
                "main.tf",
                "variables.tf",
                "terraform_config.tf",
                "test_file.tfvars",
                "data_processing.py",
                "user_management.tf",
                "config_files.tf"
            ],
            "invalid": [
                "_private.tf (starts with underscore)",
                "config-.tf (ends with underscore)",
                "123_config.tf (starts with number)",
                "my-file.tf (contains hyphen)",
                "my.file.tf (contains dot in name)",
                "my file.tf (contains space)",
                "my__file.tf (consecutive underscores)"
            ]
        },
        "fix_suggestions": [
            "Use only letters, numbers, and underscores in file names",
            "Ensure file names start and end with a letter",
            "Avoid consecutive underscores in file names",
            "Use snake_case naming convention (lowercase with underscores)",
            "Make file names descriptive and meaningful"
        ],
        "excluded_files": [
            "Hidden files (starting with .)",
            "Terraform auto.tfvars files (xxx.auto.tfvars format)",
            "Terraform state files (terraform.tfstate and variations like terraform.tfstate.1754040310.backup)",
            "Log files (*.log)",
            "System files (Thumbs.db, desktop.ini, .DS_Store, etc.)",
            "Configuration files (.gitignore, .editorconfig, etc.)",
            "Build and cache files (build, dist, target, etc.)",
            "IDE and editor files (.vscode, .idea, .settings, etc.)",
            "Package manager files (package.json, requirements.txt, etc.)"
        ],
        "recursive_check": True,
        "max_depth": "unlimited"
    }
