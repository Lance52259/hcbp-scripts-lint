#!/usr/bin/env python3
"""
SC.004 - HuaweiCloud Provider Version Validity Check

Validates huaweicloud provider version constraints by executing terraform validate
with the current version and the previous version to ensure proper version boundaries.

This rule performs the following checks:
1. Parses huaweicloud provider version constraints from Terraform files
2. Fetches available versions from GitHub releases
3. Finds the previous available version (excluding known problematic versions)
4. Executes terraform validate with current version (should pass)
5. Executes terraform validate with previous version (should fail)

Purpose:
- Ensures huaweicloud provider version constraints are properly set
- Validates that the minimum version is actually required (not too permissive)
- Prevents configuration failures due to version mismatches
- Promotes use of appropriate version constraints

Rule Details:
- Detects huaweicloud provider version constraints in required_providers blocks
- Fetches real version data from GitHub releases
- Executes terraform validate with different provider versions
- Reports violations when version constraints are not properly set

Common Scenarios:
1. Version constraint is too permissive (previous version also works)
2. Version constraint is too restrictive (current version doesn't work)
3. Version constraint points to non-existent version
4. Version constraint syntax is invalid

Author: Lance
License: Apache 2.0
"""

import re
import os
import subprocess
import tempfile
import shutil
import json
import urllib.request
import urllib.error
from typing import Callable, Optional, List, Dict, Tuple, Set, Any


def _compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    
    Args:
        version1 (str): First version string
        version2 (str): Second version string
        
    Returns:
        int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    def version_tuple(v):
        return tuple(map(int, v.split('.')))
    
    try:
        v1_tuple = version_tuple(version1)
        v2_tuple = version_tuple(version2)
        
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        else:
            return 0
    except (ValueError, AttributeError):
        # If version parsing fails, treat as equal
        return 0


def _is_valid_version(version_str: str) -> bool:
    """
    Check if a version string is valid.
    
    Args:
        version_str (str): Version string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        parts = version_str.split('.')
        if len(parts) != 3:
            return False
        
        for part in parts:
            int(part)
        return True
    except (ValueError, AttributeError):
        return False


def check_sc004_provider_version_validity(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check huaweicloud provider version validity by testing with current and previous versions.
    
    This rule validates that huaweicloud provider version constraints are properly set
    by executing terraform validate with the current version (should pass) and the
    previous version (should fail).
    
    Args:
        file_path (str): Path to the Terraform file being checked
        content (str): Content of the Terraform file
        log_error_func (Callable): Function to log errors with signature (file_path, rule_id, message, line_num)
    """
    # Extract provider version constraints from the file
    provider_constraints = _extract_provider_constraints(content)
    
    if not provider_constraints:
        return  # No provider constraints found
    
    # Filter for huaweicloud provider only
    huaweicloud_constraints = [
        constraint for constraint in provider_constraints 
        if constraint[0] == 'huaweicloud'
    ]
    
    if not huaweicloud_constraints:
        return  # No huaweicloud provider constraints found
    
    # Get the directory containing the Terraform file
    terraform_dir = os.path.dirname(file_path)
    
    # Get available versions from GitHub
    try:
        available_versions = _get_github_versions()
    except Exception as e:
        error_msg = f"Failed to fetch huaweicloud provider versions from GitHub: {str(e)}"
        log_error_func(file_path, "SC.004", error_msg, None)
        return
    
    # Check each huaweicloud provider constraint
    for constraint_info in huaweicloud_constraints:
        provider_name, version_constraint, line_num = constraint_info
        
        # Extract minimum version from constraint
        min_version = _extract_minimum_version(version_constraint)
        if not min_version:
            error_msg = f"Invalid huaweicloud provider version constraint: '{version_constraint}'"
            log_error_func(file_path, "SC.004", error_msg, line_num)
            continue
        
        # Check if minimum version exists in available versions
        if min_version not in available_versions:
            error_msg = f"HuaweiCloud provider version '{min_version}' is not available in GitHub releases"
            log_error_func(file_path, "SC.004", error_msg, line_num)
            continue
        
        # Find the previous available version
        previous_version = _find_previous_available_version(min_version, available_versions)
        if not previous_version:
            error_msg = f"No previous available version found for huaweicloud provider version '{min_version}'"
            log_error_func(file_path, "SC.004", error_msg, line_num)
            continue
        
        # Test with current version (should pass)
        current_result = _test_terraform_validate_with_version(terraform_dir, min_version)
        if not current_result['success']:
            error_msg = f"Terraform validate failed with huaweicloud provider version '{min_version}': {current_result['error']}"
            log_error_func(file_path, "SC.004", error_msg, line_num)
            continue
        
        # Test with previous version (should fail)
        previous_result = _test_terraform_validate_with_version(terraform_dir, previous_version)
        if previous_result['success']:
            # Find the actual minimum required version
            actual_min_version = _find_actual_minimum_version(terraform_dir, available_versions, min_version)
            if actual_min_version and actual_min_version != min_version:
                error_msg = f"Version constraint '{version_constraint}' is too permissive. Previous version '{previous_version}' also works. Consider using '>= {actual_min_version}' instead."
            else:
                error_msg = f"Version constraint '{version_constraint}' is too permissive. Previous version '{previous_version}' also works. Consider using a more restrictive version constraint."
            log_error_func(file_path, "SC.004", error_msg, line_num)
        # If previous version fails, that's expected and good


def _extract_provider_constraints(content: str) -> List[Tuple[str, str, int]]:
    """
    Extract provider version constraints from Terraform file content.
    
    Args:
        content (str): File content to analyze
        
    Returns:
        List[Tuple[str, str, int]]: List of (provider_name, version_constraint, line_number) tuples
    """
    constraints = []
    lines = content.split('\n')
    
    in_required_providers = False
    current_provider = None
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Check for terraform block with required_providers
        if re.match(r'terraform\s*\{', stripped):
            in_required_providers = False
            continue
        
        # Check for required_providers block
        if re.match(r'required_providers\s*\{', stripped):
            in_required_providers = True
            continue
        
        # End of required_providers block
        if in_required_providers and stripped == '}':
            in_required_providers = False
            current_provider = None
            continue
        
        # End of terraform block
        if not in_required_providers and stripped == '}':
            continue
        
        # Provider constraint within required_providers
        if in_required_providers:
            # Pattern: provider_name = { version = ">= 1.0.0" }
            provider_match = re.match(r'(\w+)\s*=\s*\{', stripped)
            if provider_match:
                current_provider = provider_match.group(1)
                continue
            
            # Version constraint
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', stripped)
            if version_match and current_provider:
                version_constraint = version_match.group(1)
                constraints.append((current_provider, version_constraint, line_num))
                # Reset current_provider after finding version
                current_provider = None
                continue
        
        # Provider constraint outside required_providers (legacy format)
        # Pattern: provider "provider_name" { version = ">= 1.0.0" }
        legacy_match = re.match(r'provider\s+["\'](\w+)["\']\s*\{', stripped)
        if legacy_match:
            current_provider = legacy_match.group(1)
            continue
        
        # Version constraint in legacy provider block
        if current_provider and 'version' in stripped:
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', stripped)
            if version_match:
                version_constraint = version_match.group(1)
                constraints.append((current_provider, version_constraint, line_num))
                current_provider = None
                continue
        
        # End of provider block
        if current_provider and stripped == '}':
            current_provider = None
    
    return constraints


def _extract_minimum_version(version_constraint: str) -> Optional[str]:
    """
    Extract the minimum version from a version constraint.
    
    Args:
        version_constraint (str): Version constraint string
        
    Returns:
        Optional[str]: Minimum version string or None if not found
    """
    constraint = version_constraint.strip()
    
    # Handle different constraint patterns
    patterns = [
        r'^(\d+\.\d+\.\d+)$',  # Exact version
        r'^>=\s*(\d+\.\d+\.\d+)$',  # >= version
        r'^>\s*(\d+\.\d+\.\d+)$',   # > version
        r'^~>\s*(\d+\.\d+\.\d+)$',  # ~> version
        r'^(\d+\.\d+\.\d+)\s*-\s*\d+\.\d+\.\d+$',  # Range (take first)
    ]
    
    for pattern in patterns:
        match = re.match(pattern, constraint)
        if match:
            return match.group(1)
    
    return None


def _check_version_availability(provider_name: str, version_constraint: str, terraform_dir: str) -> Dict[str, Any]:
    """
    Check if the provider version is available using terraform commands.
    
    Args:
        provider_name (str): Name of the provider
        version_constraint (str): Version constraint string
        terraform_dir (str): Directory containing Terraform files
        
    Returns:
        Dict[str, any]: Availability result with 'available', 'reason', and 'suggested_version' keys
    """
    try:
        # Create a temporary directory for terraform operations
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy terraform files to temp directory
            _copy_terraform_files(terraform_dir, temp_dir)
            
            # Execute terraform init
            init_result = _execute_terraform_command(['init'], temp_dir)
            if not init_result['success']:
                return {
                    'available': False,
                    'reason': f'terraform init failed: {init_result["error"]}',
                    'suggested_version': _get_latest_stable_version(provider_name)
                }
            
            # Execute terraform validate
            validate_result = _execute_terraform_command(['validate'], temp_dir)
            if not validate_result['success']:
                return {
                    'available': False,
                    'reason': f'terraform validate failed: {validate_result["error"]}',
                    'suggested_version': _get_latest_stable_version(provider_name)
                }
            
            # Execute terraform init -upgrade to check for newer versions
            upgrade_result = _execute_terraform_command(['init', '-upgrade'], temp_dir)
            if not upgrade_result['success']:
                return {
                    'available': False,
                    'reason': f'terraform init -upgrade failed: {upgrade_result["error"]}',
                    'suggested_version': _get_latest_stable_version(provider_name)
                }
            
            # Check if the minimum version is in the available versions list
            min_version = _extract_minimum_version(version_constraint)
            if min_version:
                available_versions = _get_available_versions(provider_name)
                if available_versions and min_version not in available_versions:
                    # Find the closest available version
                    suggested_version = _find_closest_version(min_version, available_versions)
                    return {
                        'available': False,
                        'reason': f'Minimum version {min_version} not found in available versions',
                        'suggested_version': suggested_version
                    }
            
            return {
                'available': True,
                'reason': 'Version is available and valid',
                'suggested_version': None
            }
            
    except Exception as e:
        return {
            'available': False,
            'reason': f'Error checking version availability: {str(e)}',
            'suggested_version': _get_latest_stable_version(provider_name)
        }


def _copy_terraform_files(source_dir: str, dest_dir: str) -> None:
    """
    Copy all .tf files from source directory to destination directory.
    
    Args:
        source_dir (str): Source directory path
        dest_dir (str): Destination directory path
    """
    if not os.path.exists(source_dir):
        return
    
    for filename in os.listdir(source_dir):
        if filename.endswith('.tf'):
            source_path = os.path.join(source_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            shutil.copy2(source_path, dest_path)


def _execute_terraform_command(args: List[str], working_dir: str) -> Dict[str, Any]:
    """
    Execute a terraform command and return the result.
    
    Args:
        args (List[str]): Terraform command arguments
        working_dir (str): Working directory for the command
        
    Returns:
        Dict[str, any]: Command result with 'success', 'output', and 'error' keys
    """
    try:
        # Add -no-color flag to avoid ANSI color codes in output
        cmd = ['terraform'] + args + ['-no-color']
        
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60  # 60 second timeout
        )
        
        # Decode output for older Python versions
        stdout = result.stdout.decode('utf-8') if result.stdout else ''
        stderr = result.stderr.decode('utf-8') if result.stderr else ''
        
        return {
            'success': result.returncode == 0,
            'output': stdout,
            'error': stderr if result.returncode != 0 else None
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Command timed out after 60 seconds'
        }
    except FileNotFoundError:
        return {
            'success': False,
            'output': '',
            'error': 'terraform command not found. Please ensure Terraform is installed and in PATH'
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': f'Command execution failed: {str(e)}'
        }






def _get_github_versions() -> List[str]:
    """
    Get available versions from GitHub releases with pagination.
    
    Returns:
        List[str]: List of available version strings
    """
    versions = []
    page = 1
    per_page = 100  # Maximum per page
    
    try:
        while True:
            url = f"https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases?page={page}&per_page={per_page}"
            
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            # If no more releases, break
            if not data:
                break
            
            page_versions = []
            for release in data:
                if not release.get('draft', False) and not release.get('prerelease', False):
                    tag_name = release['tag_name']
                    # Remove 'v' prefix if present
                    if tag_name.startswith('v'):
                        version = tag_name[1:]
                    else:
                        version = tag_name
                    
                    # Validate version format
                    if _is_valid_version(version):
                        page_versions.append(version)
            
            versions.extend(page_versions)
            
            # If we got less than per_page, we've reached the end
            if len(data) < per_page:
                break
                
            page += 1
            
            # Safety limit to prevent infinite loops
            if page > 50:  # Maximum 5000 releases
                break
        
        # Sort versions using semantic versioning
        versions.sort(key=lambda x: tuple(map(int, x.split('.'))))
        return versions
        
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        raise Exception(f"Failed to fetch versions from GitHub: {str(e)}")


def _find_actual_minimum_version(terraform_dir: str, available_versions: List[str], current_min_version: str) -> Optional[str]:
    """
    Find the actual minimum version required by testing with different versions.
    
    Args:
        terraform_dir (str): Directory containing Terraform files
        available_versions (List[str]): List of all available versions
        current_min_version (str): Current minimum version constraint
        
    Returns:
        Optional[str]: Actual minimum required version or None if not found
    """
    # Find versions less than current minimum version
    lower_versions = [v for v in available_versions if _compare_versions(v, current_min_version) < 0]
    
    if not lower_versions:
        return None
    
    # Sort versions in descending order (newest first)
    lower_versions.sort(key=lambda x: _compare_versions(x, "0.0.0"), reverse=True)
    
    # Test each version to find the highest one that still works
    last_working_version = None
    for version in lower_versions:
        result = _test_terraform_validate_with_version(terraform_dir, version)
        if result['success']:
            last_working_version = version
        else:
            # This version fails, so the last working version + 1 is the minimum required
            if last_working_version:
                # Find the next higher version after the last working version
                higher_versions = [v for v in available_versions if _compare_versions(v, last_working_version) > 0]
                if higher_versions:
                    higher_versions.sort(key=lambda x: _compare_versions(x, "0.0.0"))
                    return higher_versions[0]
            break
    
    # If all lower versions work, return the current minimum version
    return current_min_version


def _find_previous_available_version(current_version: str, available_versions: List[str]) -> Optional[str]:
    """
    Find the previous available version, excluding problematic versions.
    
    Args:
        current_version (str): Current version to find previous for
        available_versions (List[str]): List of all available versions
        
    Returns:
        Optional[str]: Previous available version or None if not found
    """
    # Known problematic versions to exclude
    problematic_versions = {
        "1.52.0",
        "1.63.0",
        "1.63.1",
        "1.63.2",
        "1.64.0",
        "1.64.1",
        "1.64.2",
        "1.75.4",
        "1.77.0"
    }
    
    # Filter out problematic versions
    valid_versions = [v for v in available_versions if v not in problematic_versions]
    
    # Find versions less than current version
    previous_versions = [v for v in valid_versions if _compare_versions(v, current_version) < 0]
    
    if not previous_versions:
        return None
    
    # Sort versions in ascending order and return the highest one
    previous_versions.sort(key=lambda x: _compare_versions(x, "0.0.0"))
    return previous_versions[-1]


def _test_terraform_validate_with_version(terraform_dir: str, provider_version: str) -> Dict[str, Any]:
    """
    Test terraform validate with a specific huaweicloud provider version.
    
    Args:
        terraform_dir (str): Directory containing Terraform files
        provider_version (str): Provider version to test
        
    Returns:
        Dict[str, Any]: Test result with 'success', 'output', and 'error' keys
    """
    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy terraform files to temp directory
            _copy_terraform_files(terraform_dir, temp_dir)
            
            # Create a temporary providers.tf with the specific version
            providers_content = f'''terraform {{
  required_providers {{
    huaweicloud = {{
      source  = "huaweicloud/huaweicloud"
      version = "= {provider_version}"
    }}
  }}
}}'''
            
            providers_file = os.path.join(temp_dir, "providers.tf")
            with open(providers_file, 'w', encoding='utf-8') as f:
                f.write(providers_content)
            
            # Execute terraform init
            init_result = _execute_terraform_command(['init'], temp_dir)
            if not init_result['success']:
                return {
                    'success': False,
                    'output': init_result['output'],
                    'error': f"terraform init failed: {init_result['error']}"
                }
            
            # Execute terraform validate
            validate_result = _execute_terraform_command(['validate'], temp_dir)
            return {
                'success': validate_result['success'],
                'output': validate_result['output'],
                'error': validate_result['error']
            }
            
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': f"Test execution failed: {str(e)}"
        }


def get_rule_description() -> dict:
    """
    Get the rule description for SC.004.
    
    Returns:
        dict: Rule description containing metadata and details
    """
    return {
        "rule_id": "SC.004",
        "title": "HuaweiCloud Provider Version Validity Check",
        "category": "Security Code",
        "severity": "error",
        "description": "Validates huaweicloud provider version constraints by testing with current and previous versions",
        "rationale": "Ensures version constraints are properly set by verifying current version works and previous version fails",
        "scope": ["huaweicloud_provider_version_constraints", "terraform_validation", "version_boundary_testing"],
        "implementation": "modular",
        "version": "2.0.0",
        "scenarios": {
            "too_permissive": "Version constraint is too permissive (previous version also works)",
            "too_restrictive": "Version constraint is too restrictive (current version doesn't work)",
            "invalid_version": "Version constraint points to non-existent version",
            "invalid_syntax": "Version constraint syntax is invalid"
        },
        "examples": {
            "valid": [
                'required_providers { huaweicloud = { version = ">= 1.77.1" } }  # Current version works, previous fails',
                'provider "huaweicloud" { version = ">= 1.40.0" }  # Properly set version constraint'
            ],
            "invalid": [
                'required_providers { huaweicloud = { version = ">= 1.52.1" } }  # Too permissive - previous version 1.51.0 also works, should use >= 1.52.2',
                'required_providers { huaweicloud = { version = ">= 99.0.0" } }  # Non-existent version',
                'required_providers { huaweicloud = { version = "invalid-version" } }  # Invalid syntax'
            ]
        },
        "fix_suggestions": [
            "Check that current version passes terraform validate",
            "Verify that previous version fails terraform validate",
            "Use GitHub releases to find available versions",
            "Exclude known problematic versions (1.52.0, 1.63.0-1.63.2, 1.64.0-1.64.2, 1.75.4, 1.77.0)",
            "Test version constraints in development environment",
            "Use the suggested minimum version from the error message",
            "Verify the actual minimum required version by testing with different provider versions"
        ],
        "terraform_commands": [
            "terraform init - initializes with specific provider version",
            "terraform validate - validates configuration with specific version"
        ],
        "version_source": "GitHub releases: https://github.com/huaweicloud/terraform-provider-huaweicloud/releases",
        "problematic_versions": ["1.52.0", "1.63.0", "1.63.1", "1.63.2", "1.64.0", "1.64.1", "1.64.2", "1.75.4", "1.77.0"],
        "target_provider": "huaweicloud"
    }
