#!/usr/bin/env python3
"""
SC Rules Reference Coordinator

This module serves as the central coordinator for all SC (Security Code) rules.
It provides a unified interface for accessing and executing security code
validation rules for Terraform files.

The SCRules class orchestrates the individual rule implementations and provides
methods for rule discovery, execution, and metadata retrieval.

Author: Lance
License: Apache 2.0
"""

from typing import Dict, List, Callable, Any, Optional
import importlib
import sys
import os

# Import individual rule modules
from .rule_001 import check_sc001_array_index_safety, get_rule_description as get_sc001_description
from .rule_002 import check_sc002_terraform_version_declaration, get_rule_description as get_sc002_description
from .rule_003 import check_sc003_terraform_version_compatibility, get_rule_description as get_sc003_description
from .rule_004 import check_sc004_provider_version_validity, get_rule_description as get_sc004_description
from .rule_005 import check_sc005_sensitive_variable_declaration, get_rule_description as get_sc005_description


class SCRules:
    """
    Central coordinator for all SC (Security Code) rules.
    
    This class provides a unified interface for accessing and executing
    security code validation rules. It maintains a registry of all
    available rules and their corresponding check functions.
    """
    
    def __init__(self):
        """Initialize the SC rules coordinator."""
        self._rules_registry = self._build_rules_registry()
    
    def _build_rules_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build the registry of available SC rules.
        
        Returns:
            Dict[str, Dict[str, Any]]: Registry mapping rule IDs to rule information
        """
        return {
            "SC.001": {
                "check_function": check_sc001_array_index_safety,
                "description_function": get_sc001_description,
                "name": "Array index access safety check",
                "status": "modular"
            },
            "SC.002": {
                "check_function": check_sc002_terraform_version_declaration,
                "description_function": get_sc002_description,
                "name": "Terraform required version declaration check",
                "status": "modular"
            },
            "SC.003": {
                "check_function": check_sc003_terraform_version_compatibility,
                "description_function": get_sc003_description,
                "name": "Terraform version compatibility check",
                "status": "modular"
            },
            "SC.004": {
                "check_function": check_sc004_provider_version_validity,
                "description_function": get_sc004_description,
                "name": "Provider minimum version validity check",
                "status": "modular"
            },
            "SC.005": {
                "check_function": check_sc005_sensitive_variable_declaration,
                "description_function": get_sc005_description,
                "name": "Sensitive variable declaration check",
                "status": "modular"
            }
        }
    
    def get_available_rules(self) -> List[str]:
        """
        Get a list of all available SC rule IDs.
        
        Returns:
            List[str]: List of rule IDs (e.g., ['SC.001'])
        """
        return list(self._rules_registry.keys())
    
    def get_rule_info(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific rule.
        
        Args:
            rule_id (str): The rule ID (e.g., 'SC.001')
            
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
        Execute a specific SC rule.
        
        Args:
            rule_id (str): The rule ID to execute
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            
        Returns:
            bool: True if rule executed successfully, False otherwise
        """
        if rule_id not in self._rules_registry:
            log_error_func(file_path, "SYSTEM", f"Unknown SC rule: {rule_id}", None)
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
        Execute all available SC rules.
        
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
        
        for rule_id in self._rules_registry:
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
        
        for rule_id in self._rules_registry:
            try:
                rule_info = self.get_rule_info(rule_id)
                if rule_info and rule_info.get("category", "").lower() == category.lower():
                    matching_rules.append(rule_id)
            except Exception:
                continue
                
        return matching_rules
    
    def get_rules_by_severity(self, severity: str) -> List[str]:
        """
        Get rules filtered by severity level.
        
        Args:
            severity (str): Severity level to filter by
            
        Returns:
            List[str]: List of rule IDs matching the severity
        """
        matching_rules = []
        
        for rule_id in self._rules_registry:
            try:
                rule_info = self.get_rule_info(rule_id)
                if rule_info and rule_info.get("severity", "").lower() == severity.lower():
                    matching_rules.append(rule_id)
            except Exception:
                continue
                
        return matching_rules
    
    def get_modular_rules(self) -> List[str]:
        """
        Get all modular (new architecture) rules.
        
        Returns:
            List[str]: List of modular rule IDs
        """
        return [rule_id for rule_id, info in self._rules_registry.items() 
                if info.get("status") == "modular"]
    
    def get_legacy_rules(self) -> List[str]:
        """
        Get all legacy (old architecture) rules.
        
        Returns:
            List[str]: List of legacy rule IDs
        """
        return [rule_id for rule_id, info in self._rules_registry.items() 
                if info.get("status") == "legacy"]
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all available rules.
        
        Returns:
            Dict[str, Any]: Summary information about rules
        """
        total_rules = len(self._rules_registry)
        modular_rules = len(self.get_modular_rules())
        legacy_rules = len(self.get_legacy_rules())
        
        # Group by category and severity
        categories = {}
        severities = {}
        
        for rule_id in self._rules_registry:
            try:
                rule_info = self.get_rule_info(rule_id)
                if rule_info:
                    category = rule_info.get("category", "Unknown")
                    severity = rule_info.get("severity", "Unknown")
                    
                    categories[category] = categories.get(category, 0) + 1
                    severities[severity] = severities.get(severity, 0) + 1
            except Exception:
                continue
        
        return {
            "total_rules": total_rules,
            "modular_rules": modular_rules,
            "legacy_rules": legacy_rules,
            "categories": categories,
            "severities": severities,
            "rule_list": list(self._rules_registry.keys())
        }


# Convenience functions for backward compatibility
def get_available_sc_rules() -> List[str]:
    """Get list of available SC rule IDs."""
    sc_rules = SCRules()
    return sc_rules.get_available_rules()

def execute_sc_rule(rule_id: str, file_path: str, content: str,
                   log_error_func: Callable[[str, str, str, Optional[int]], None]) -> bool:
    """Execute a specific SC rule."""
    sc_rules = SCRules()
    return sc_rules.execute_rule(rule_id, file_path, content, log_error_func)

def execute_all_sc_rules(file_path: str, content: str,
                        log_error_func: Callable[[str, str, str, Optional[int]], None],
                        excluded_rules: Optional[List[str]] = None) -> Dict[str, bool]:
    """Execute all SC rules."""
    sc_rules = SCRules()
    return sc_rules.execute_all_rules(file_path, content, log_error_func, excluded_rules)

def get_sc_rule_info(rule_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific SC rule."""
    sc_rules = SCRules()
    return sc_rules.get_rule_info(rule_id) 