#!/usr/bin/env python3
"""
DC Rules Reference Coordinator

This module serves as the central coordinator for all DC (Documentation/Comments) rules.
It provides a unified interface for accessing and executing documentation and comment
validation rules for Terraform files.

The DCRules class orchestrates the individual rule implementations and provides
methods for rule discovery, execution, and metadata retrieval.

Author: Lance
License: Apache 2.0
"""

from typing import Dict, List, Callable, Any, Optional
import importlib
import sys
import os

# Import individual rule modules
from .rule_001 import check_dc001_comment_format, get_rule_description as get_dc001_description


class DCRules:
    """
    Central coordinator for all DC (Documentation/Comments) rules.
    
    This class provides a unified interface for accessing and executing
    documentation and comment validation rules. It maintains a registry of all
    available rules and their corresponding check functions.
    """
    
    def __init__(self):
        """Initialize the DC rules coordinator."""
        self._rules_registry = self._build_rules_registry()
    
    def _build_rules_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build the registry of available DC rules.
        
        Returns:
            Dict[str, Dict[str, Any]]: Registry mapping rule IDs to rule information
        """
        return {
            "DC.001": {
                "check_function": check_dc001_comment_format,
                "description_function": get_dc001_description,
                "name": "Comment format check",
                "status": "modular"
            }
        }
    
    def get_available_rules(self) -> List[str]:
        """
        Get a list of all available DC rule IDs.
        
        Returns:
            List[str]: List of rule IDs (e.g., ['DC.001'])
        """
        return list(self._rules_registry.keys())
    
    def get_rule_info(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific rule.
        
        Args:
            rule_id (str): The rule ID (e.g., 'DC.001')
            
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
        Execute a specific DC rule.
        
        Args:
            rule_id (str): The rule ID to execute
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            
        Returns:
            bool: True if rule executed successfully, False otherwise
        """
        if rule_id not in self._rules_registry:
            log_error_func(file_path, "SYSTEM", f"Unknown DC rule: {rule_id}", None)
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
        Execute all available DC rules.
        
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
    def run_all_checks(self, file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
        """
        Legacy method for backward compatibility.
        
        Args:
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
        """
        self.execute_all_rules(file_path, content, log_error_func)
    
    def get_file_lines(self, content: str) -> List[str]:
        """
        Legacy utility method - split file content into lines.
        
        Args:
            content (str): File content to split
            
        Returns:
            List[str]: List of lines
        """
        return content.split('\n')
    
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


# Convenience functions for backward compatibility and ease of use
def get_available_dc_rules() -> List[str]:
    """Get list of all available DC rule IDs."""
    return DCRules().get_available_rules()

def execute_dc_rule(rule_id: str, file_path: str, content: str,
                   log_error_func: Callable[[str, str, str, Optional[int]], None]) -> bool:
    """Execute a specific DC rule."""
    return DCRules().execute_rule(rule_id, file_path, content, log_error_func)

def execute_all_dc_rules(file_path: str, content: str,
                        log_error_func: Callable[[str, str, str, Optional[int]], None],
                        excluded_rules: Optional[List[str]] = None) -> Dict[str, bool]:
    """Execute all DC rules."""
    return DCRules().execute_all_rules(file_path, content, log_error_func, excluded_rules)

def get_dc_rule_info(rule_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific DC rule."""
    return DCRules().get_rule_info(rule_id)
