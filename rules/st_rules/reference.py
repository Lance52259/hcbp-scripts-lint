#!/usr/bin/env python3
"""
ST Rules Reference Coordinator

This module serves as the central coordinator for all ST (Style/Format) rules.
It provides a unified interface for accessing and executing style and format
validation rules for Terraform files.

The STRules class orchestrates the individual rule implementations and provides
methods for rule discovery, execution, and metadata retrieval.

Author: Lance
License: Apache 2.0
"""

from typing import Dict, List, Callable, Any, Optional
import importlib
import sys
import os

# Import individual rule modules
from .rule_001 import check_st001_naming_convention, get_rule_description as get_st001_description
from .rule_002 import check_st002_variable_defaults, get_rule_description as get_st002_description
from .rule_003 import check_st003_parameter_alignment, get_rule_description as get_st003_description
from .rule_004 import check_st004_indentation_character, get_rule_description as get_st004_description
from .rule_005 import check_st005_indentation_level, get_rule_description as get_st005_description
from .rule_006 import check_st006_resource_spacing, get_rule_description as get_st006_description
from .rule_007 import check_st007_same_parameter_block_spacing, get_rule_description as get_st007_description
from .rule_008 import check_st008_different_named_parameter_spacing, get_rule_description as get_st008_description
from .rule_009 import check_st009_variable_order, get_rule_description as get_st009_description
from .rule_010 import check_st010_quote_usage, get_rule_description as get_st010_description


class STRules:
    """
    Central coordinator for all ST (Style/Format) rules.
    
    This class provides a unified interface for accessing and executing
    style and format validation rules. It maintains a registry of all
    available rules and their corresponding check functions.
    """
    
    def __init__(self):
        """Initialize the ST rules coordinator."""
        self._rules_registry = self._build_rules_registry()
    
    def _build_rules_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build the registry of available ST rules.
        
        Returns:
            Dict[str, Dict[str, Any]]: Registry mapping rule IDs to rule information
        """
        return {
            "ST.001": {
                "check_function": check_st001_naming_convention,
                "description_function": get_st001_description,
                "name": "Naming convention check",
                "status": "modular"
            },
            "ST.002": {
                "check_function": check_st002_variable_defaults,
                "description_function": get_st002_description,
                "name": "Variable default value check",
                "status": "modular"
            },
            "ST.003": {
                "check_function": check_st003_parameter_alignment,
                "description_function": get_st003_description,
                "name": "Parameter alignment check",
                "status": "modular"
            },
            "ST.004": {
                "check_function": check_st004_indentation_character,
                "description_function": get_st004_description,
                "name": "Indentation character check",
                "status": "modular"
            },
            "ST.005": {
                "check_function": check_st005_indentation_level,
                "description_function": get_st005_description,
                "name": "Indentation level check",
                "status": "modular"
            },
            "ST.006": {
                "check_function": check_st006_resource_spacing,
                "description_function": get_st006_description,
                "name": "Resource and data source spacing check",
                "status": "modular"
            },
            "ST.007": {
                "check_function": check_st007_same_parameter_block_spacing,
                "description_function": get_st007_description,
                "name": "Same parameter block spacing check",
                "status": "modular"
            },
            "ST.008": {
                "check_function": check_st008_different_named_parameter_spacing,
                "description_function": get_st008_description,
                "name": "Different named parameter block spacing check",
                "status": "modular"
            },
            "ST.009": {
                "check_function": check_st009_variable_order,
                "description_function": get_st009_description,
                "name": "Variable definition order check",
                "status": "modular"
            },
            "ST.010": {
                "check_function": check_st010_quote_usage,
                "description_function": get_st010_description,
                "name": "Quote usage check",
                "status": "modular"
            }
        }
    
    def get_available_rules(self) -> List[str]:
        """
        Get a list of all available ST rule IDs.
        
        Returns:
            List[str]: List of rule IDs (e.g., ['ST.001', 'ST.002', ...])
        """
        return list(self._rules_registry.keys())
    
    def get_rule_info(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific rule.
        
        Args:
            rule_id (str): The rule ID (e.g., 'ST.001')
            
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
        Execute a specific ST rule.
        
        Args:
            rule_id (str): The rule ID to execute
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            
        Returns:
            bool: True if rule executed successfully, False otherwise
        """
        if rule_id not in self._rules_registry:
            log_error_func(file_path, "SYSTEM", f"Unknown ST rule: {rule_id}", None)
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
        Execute all available ST rules.
        
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
            category (str): Category to filter by (e.g., 'Style/Format')
            
        Returns:
            List[str]: List of rule IDs matching the category
        """
        matching_rules = []
        
        for rule_id in self.get_available_rules():
            rule_info = self.get_rule_info(rule_id)
            if rule_info and rule_info.get('category') == category:
                matching_rules.append(rule_id)
                
        return matching_rules
    
    def get_rules_by_severity(self, severity: str) -> List[str]:
        """
        Get rules filtered by severity level.
        
        Args:
            severity (str): Severity level to filter by (e.g., 'error', 'warning')
            
        Returns:
            List[str]: List of rule IDs matching the severity level
        """
        matching_rules = []
        
        for rule_id in self.get_available_rules():
            rule_info = self.get_rule_info(rule_id)
            if rule_info and rule_info.get('severity') == severity:
                matching_rules.append(rule_id)
                
        return matching_rules
    
    def get_modular_rules(self) -> List[str]:
        """
        Get all rules that have been migrated to modular format.
        
        Returns:
            List[str]: List of modular rule IDs
        """
        return [
            rule_id for rule_id, rule_info in self._rules_registry.items()
            if rule_info.get('status') == 'modular'
        ]
    
    def get_legacy_rules(self) -> List[str]:
        """
        Get all rules that are still in legacy format.
        
        Returns:
            List[str]: List of legacy rule IDs
        """
        return [
            rule_id for rule_id, rule_info in self._rules_registry.items()
            if rule_info.get('status') == 'legacy'
        ]
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all ST rules.
        
        Returns:
            Dict[str, Any]: Summary information about all rules
        """
        all_rules = self.get_available_rules()
        modular_rules = self.get_modular_rules()
        legacy_rules = self.get_legacy_rules()
        
        # Group rules by severity
        error_rules = self.get_rules_by_severity('error')
        warning_rules = self.get_rules_by_severity('warning')
        
        return {
            'total_rules': len(all_rules),
            'modular_rules': len(modular_rules),
            'legacy_rules': len(legacy_rules),
            'error_rules': len(error_rules),
            'warning_rules': len(warning_rules),
            'migration_progress': (len(modular_rules) / len(all_rules) * 100) if all_rules else 0,
            'rule_list': all_rules,
            'modular_rule_list': modular_rules,
            'legacy_rule_list': legacy_rules
        }


# Create a global instance for easy access
st_rules = STRules()


# Backward compatibility functions
def get_available_st_rules() -> List[str]:
    """Get list of available ST rules (backward compatibility)."""
    return st_rules.get_available_rules()


def execute_st_rule(rule_id: str, file_path: str, content: str,
                   log_error_func: Callable[[str, str, str, Optional[int]], None]) -> bool:
    """Execute a specific ST rule (backward compatibility)."""
    return st_rules.execute_rule(rule_id, file_path, content, log_error_func)


def execute_all_st_rules(file_path: str, content: str,
                        log_error_func: Callable[[str, str, str, Optional[int]], None],
                        excluded_rules: Optional[List[str]] = None) -> Dict[str, bool]:
    """Execute all ST rules (backward compatibility)."""
    return st_rules.execute_all_rules(file_path, content, log_error_func, excluded_rules)


def get_st_rule_info(rule_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific ST rule (backward compatibility)."""
    return st_rules.get_rule_info(rule_id)
