#!/usr/bin/env python3
"""
IO Rules Reference Coordinator

This module serves as the central coordinator for all IO (Input/Output) rules.
It provides a unified interface for accessing and executing input/output
validation rules for Terraform files.

The IORules class orchestrates the individual rule implementations and provides
methods for rule discovery, execution, and metadata retrieval.

Author: Lance
License: Apache 2.0
"""

from typing import Dict, List, Callable, Any, Optional
import importlib
import sys
import os

# Import individual rule modules
from .rule_001 import check_io001_variable_file_location, get_rule_description as get_io001_description
from .rule_002 import check_io002_output_file_location, get_rule_description as get_io002_description
from .rule_003 import check_io003_required_variables, get_rule_description as get_io003_description
from .rule_004 import check_io004_variable_naming, get_rule_description as get_io004_description
from .rule_005 import check_io005_output_naming, get_rule_description as get_io005_description
from .rule_006 import check_io006_variable_description, get_rule_description as get_io006_description
from .rule_007 import check_io007_output_description, get_rule_description as get_io007_description
from .rule_008 import check_io008_variable_type, get_rule_description as get_io008_description


class IORules:
    """
    Central coordinator for all IO (Input/Output) rules.
    
    This class provides a unified interface for accessing and executing
    input/output validation rules. It maintains a registry of all
    available rules and their corresponding check functions.
    """
    
    def __init__(self):
        """Initialize the IO rules coordinator."""
        self._rules_registry = self._build_rules_registry()
    
    def _build_rules_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build the registry of available IO rules.
        
        Returns:
            Dict[str, Dict[str, Any]]: Registry mapping rule IDs to rule information
        """
        return {
            "IO.001": {
                "check_function": check_io001_variable_file_location,
                "description_function": get_io001_description,
                "name": "Variable definition file location check",
                "status": "modular"
            },
            "IO.002": {
                "check_function": check_io002_output_file_location,
                "description_function": get_io002_description,
                "name": "Output definition file organization check",
                "description": "Validates that all output variables (if any) in TF scripts within each directory are defined in the outputs.tf file in the same directory level",
                "status": "modular"
            },
            "IO.003": {
                "check_function": check_io003_required_variables,
                "description_function": get_io003_description,
                "name": "Required variable declaration check in terraform.tfvars",
                "status": "modular"
            },
            "IO.004": {
                "check_function": check_io004_variable_naming,
                "description_function": get_io004_description,
                "name": "Variable naming convention check",
                "status": "modular"
            },
            "IO.005": {
                "check_function": check_io005_output_naming,
                "description_function": get_io005_description,
                "name": "Output naming convention check",
                "status": "modular"
            },
            "IO.006": {
                "check_function": check_io006_variable_description,
                "description_function": get_io006_description,
                "name": "Variable description check",
                "status": "modular"
            },
            "IO.007": {
                "check_function": check_io007_output_description,
                "description_function": get_io007_description,
                "name": "Output description check",
                "status": "modular"
            },
            "IO.008": {
                "check_function": check_io008_variable_type,
                "description_function": get_io008_description,
                "name": "Variable type check",
                "status": "modular"
            }
        }
    
    def get_available_rules(self) -> List[str]:
        """
        Get a list of all available IO rule IDs.
        
        Returns:
            List[str]: List of rule IDs (e.g., ['IO.001', 'IO.002', ...])
        """
        return list(self._rules_registry.keys())
    
    def get_rule_info(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific rule.
        
        Args:
            rule_id (str): The rule ID (e.g., 'IO.001')
            
        Returns:
            Optional[Dict[str, Any]]: Rule information dictionary or None if not found
        """
        if rule_id not in self._rules_registry:
            return None
            
        rule_info = self._rules_registry[rule_id].copy()
        
        # Get detailed description from the rule module
        try:
            description = rule_info["description_function"]()
            rule_info.update(description)
        except Exception as e:
            rule_info["error"] = f"Failed to get rule description: {str(e)}"
            
        return rule_info
    
    def execute_rule(self, rule_id: str, file_path: str, content: str,
                    log_error_func: Callable[[str, str, str, Optional[int]], None]) -> bool:
        """
        Execute a specific IO rule.
        
        Args:
            rule_id (str): The rule ID to execute
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            
        Returns:
            bool: True if rule executed successfully, False otherwise
        """
        if rule_id not in self._rules_registry:
            log_error_func(file_path, "SYSTEM", f"Unknown IO rule: {rule_id}", None)
            return False
            
        try:
            check_function = self._rules_registry[rule_id]["check_function"]
            check_function(file_path, content, log_error_func)
            return True
        except Exception as e:
            log_error_func(file_path, rule_id, f"Rule execution failed: {str(e)}", None)
            return False
    
    def execute_all_rules(self, file_path: str, content: str,
                         log_error_func: Callable[[str, str, str, Optional[int]], None],
                         excluded_rules: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Execute all available IO rules.
        
        Args:
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            excluded_rules (Optional[List[str]]): Rules to exclude from execution
            
        Returns:
            Dict[str, bool]: Mapping of rule IDs to execution success status
        """
        excluded_rules = excluded_rules or []
        results = {}
        
        for rule_id in self.get_available_rules():
            if rule_id not in excluded_rules:
                results[rule_id] = self.execute_rule(rule_id, file_path, content, log_error_func)
                
        return results
    
    def get_rules_by_category(self, category: str) -> List[str]:
        """
        Get rules filtered by category.
        
        Args:
            category (str): Category to filter by
            
        Returns:
            List[str]: List of rule IDs matching the category
        """
        matching_rules = []
        for rule_id in self.get_available_rules():
            rule_info = self.get_rule_info(rule_id)
            if rule_info and rule_info.get("category", "").lower() == category.lower():
                matching_rules.append(rule_id)
        return matching_rules
    
    def get_rules_by_severity(self, severity: str) -> List[str]:
        """
        Get rules filtered by severity level.
        
        Args:
            severity (str): Severity level to filter by (error, warning, info)
            
        Returns:
            List[str]: List of rule IDs matching the severity
        """
        matching_rules = []
        for rule_id in self.get_available_rules():
            rule_info = self.get_rule_info(rule_id)
            if rule_info and rule_info.get("severity", "").lower() == severity.lower():
                matching_rules.append(rule_id)
        return matching_rules
    
    def get_modular_rules(self) -> List[str]:
        """
        Get all modular rules.
        
        Returns:
            List[str]: List of modular rule IDs
        """
        return [rule_id for rule_id, info in self._rules_registry.items() 
                if info.get("status") == "modular"]
    
    def get_legacy_rules(self) -> List[str]:
        """
        Get all legacy rules.
        
        Returns:
            List[str]: List of legacy rule IDs
        """
        return [rule_id for rule_id, info in self._rules_registry.items() 
                if info.get("status") == "legacy"]
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all available rules.
        
        Returns:
            Dict[str, Any]: Summary information about all rules
        """
        total_rules = len(self._rules_registry)
        modular_rules = len(self.get_modular_rules())
        legacy_rules = len(self.get_legacy_rules())
        
        categories = {}
        severities = {}
        
        for rule_id in self.get_available_rules():
            rule_info = self.get_rule_info(rule_id)
            if rule_info:
                category = rule_info.get("category", "unknown")
                severity = rule_info.get("severity", "unknown")
                
                categories[category] = categories.get(category, 0) + 1
                severities[severity] = severities.get(severity, 0) + 1
        
        return {
            "total_rules": total_rules,
            "modular_rules": modular_rules,
            "legacy_rules": legacy_rules,
            "categories": categories,
            "severities": severities,
            "rule_list": self.get_available_rules()
        }

    # Legacy compatibility methods
    def check_all_rules(self, file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
        """
        Legacy method for backward compatibility.
        
        Args:
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
        """
        self.execute_all_rules(file_path, content, log_error_func)
    
    def get_rule(self, rule_id: str):
        """Legacy method - returns rule info."""
        return self.get_rule_info(rule_id)
    
    def get_all_rules(self):
        """Legacy method - returns rules registry."""
        return self._rules_registry
    
    def list_rule_ids(self):
        """Legacy method - returns available rule IDs."""
        return self.get_available_rules()
    
    def enable_rule(self, rule_id: str) -> bool:
        """Legacy method - rules are always enabled in new architecture."""
        return rule_id in self._rules_registry
    
    def disable_rule(self, rule_id: str) -> bool:
        """Legacy method - use excluded_rules parameter instead."""
        return rule_id in self._rules_registry
    
    def is_rule_enabled(self, rule_id: str) -> bool:
        """Legacy method - rules are always enabled in new architecture."""
        return rule_id in self._rules_registry
    
    def get_all_rule_info(self) -> Dict:
        """Legacy method - returns all rule information."""
        return {
            rule_id: self.get_rule_info(rule_id)
            for rule_id in self.get_available_rules()
        }


# Convenience functions for backward compatibility and ease of use
def get_available_io_rules() -> List[str]:
    """Get list of all available IO rule IDs."""
    return IORules().get_available_rules()

def execute_io_rule(rule_id: str, file_path: str, content: str,
                   log_error_func: Callable[[str, str, str, Optional[int]], None]) -> bool:
    """Execute a specific IO rule."""
    return IORules().execute_rule(rule_id, file_path, content, log_error_func)

def execute_all_io_rules(file_path: str, content: str,
                        log_error_func: Callable[[str, str, str, Optional[int]], None],
                        excluded_rules: Optional[List[str]] = None) -> Dict[str, bool]:
    """Execute all IO rules."""
    return IORules().execute_all_rules(file_path, content, log_error_func, excluded_rules)

def get_io_rule_info(rule_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific IO rule."""
    return IORules().get_rule_info(rule_id)
