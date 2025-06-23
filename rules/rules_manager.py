#!/usr/bin/env python3
"""
Unified Rules Manager

This module provides a centralized interface for managing and executing all
linting rules across different categories: ST (Style/Format), IO (Input/Output),
DC (Documentation/Comments), and SC (Security Code).

The RulesManager class serves as the main coordinator that orchestrates
individual rule systems and provides unified functionality for:
- Rule discovery and metadata retrieval
- Batch rule execution across categories
- Configuration management
- Performance monitoring and statistics
- Error reporting and logging

Author: Lance
License: Apache 2.0
"""

from typing import Dict, List, Callable, Any, Optional, Set, Union
import time
import os

# Import individual rule system coordinators
from .st_rules.reference import STRules
from .io_rules.reference import IORules
from .dc_rules.reference import DCRules
from .sc_rules.reference import SCRules


class RuleExecutionResult:
    """Result of rule execution with metadata."""
    
    def __init__(self, rule_id: str, success: bool, execution_time: float, 
                 error_message: Optional[str] = None, violations_count: int = 0):
        self.rule_id = rule_id
        self.success = success
        self.execution_time = execution_time
        self.error_message = error_message
        self.violations_count = violations_count


class BatchExecutionSummary:
    """Summary of batch rule execution."""
    
    def __init__(self, total_rules: int, successful_rules: int, failed_rules: int,
                 total_violations: int, total_execution_time: float, 
                 results_by_category: Dict[str, List[RuleExecutionResult]]):
        self.total_rules = total_rules
        self.successful_rules = successful_rules
        self.failed_rules = failed_rules
        self.total_violations = total_violations
        self.total_execution_time = total_execution_time
        self.results_by_category = results_by_category


class RulesManager:
    """
    Unified coordinator for all linting rules across ST, IO, DC, and SC categories.
    
    This class provides a centralized interface for managing and executing
    all available linting rules. It maintains connections to individual rule
    systems and provides unified functionality for rule discovery, execution,
    and management.
    """
    
    def __init__(self):
        """Initialize the unified rules manager."""
        self._st_rules = STRules()
        self._io_rules = IORules()
        self._dc_rules = DCRules()
        self._sc_rules = SCRules()
        
        # Build unified rule registry
        self._unified_registry = self._build_unified_registry()
        
        # Configuration settings
        self._config = {
            "enable_performance_monitoring": True,
            "enable_batch_reporting": True,
            "max_violations_per_rule": 100,
            "timeout_per_rule": 30.0
        }
    
    def _build_unified_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build a unified registry of all available rules across categories.
        
        Returns:
            Dict[str, Dict[str, Any]]: Unified registry with rule metadata
        """
        registry = {}
        
        # Add ST rules
        for rule_id in self._st_rules.get_available_rules():
            registry[rule_id] = {
                "category": "Style/Format",
                "coordinator": self._st_rules,
                "system": "ST"
            }
        
        # Add IO rules
        for rule_id in self._io_rules.get_available_rules():
            registry[rule_id] = {
                "category": "Input/Output",
                "coordinator": self._io_rules,
                "system": "IO"
            }
        
        # Add DC rules
        for rule_id in self._dc_rules.get_available_rules():
            registry[rule_id] = {
                "category": "Documentation/Comments",
                "coordinator": self._dc_rules,
                "system": "DC"
            }
        
        # Add SC rules
        for rule_id in self._sc_rules.get_available_rules():
            registry[rule_id] = {
                "category": "Security Code",
                "coordinator": self._sc_rules,
                "system": "SC"
            }
        
        return registry
    
    def get_all_available_rules(self) -> List[str]:
        """
        Get a list of all available rule IDs across all categories.
        
        Returns:
            List[str]: Complete list of rule IDs
        """
        return list(self._unified_registry.keys())
    
    def get_available_rules(self) -> List[str]:
        """
        Get a list of all available rule IDs across all categories.
        Alias for get_all_available_rules for backward compatibility.
        
        Returns:
            List[str]: Complete list of rule IDs
        """
        return self.get_all_available_rules()
    
    def get_rules_by_category(self, category: str) -> List[str]:
        """
        Get rules filtered by category.
        
        Args:
            category (str): Category to filter by (ST, IO, DC, SC, or full category name)
            
        Returns:
            List[str]: List of rule IDs in the specified category
        """
        category_mapping = {
            "ST": "Style/Format",
            "IO": "Input/Output", 
            "DC": "Documentation/Comments",
            "SC": "Security Code",
            "Style/Format": "Style/Format",
            "Input/Output": "Input/Output",
            "Documentation/Comments": "Documentation/Comments",
            "Security Code": "Security Code"
        }
        
        target_category = category_mapping.get(category, category)
        
        return [
            rule_id for rule_id, info in self._unified_registry.items()
            if info["category"] == target_category
        ]
    
    def get_rules_by_system(self, system: str) -> List[str]:
        """
        Get rules filtered by rule system.
        
        Args:
            system (str): Rule system (ST, IO, DC, SC)
            
        Returns:
            List[str]: List of rule IDs from the specified system
        """
        return [
            rule_id for rule_id, info in self._unified_registry.items()
            if info["system"] == system.upper()
        ]
    
    def get_rule_info(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about a specific rule.
        
        Args:
            rule_id (str): The rule ID to query
            
        Returns:
            Optional[Dict[str, Any]]: Rule information or None if not found
        """
        if rule_id not in self._unified_registry:
            return None
        
        rule_meta = self._unified_registry[rule_id]
        coordinator = rule_meta["coordinator"]
        
        # Get detailed info from the appropriate coordinator
        rule_info = coordinator.get_rule_info(rule_id)
        if rule_info:
            # Add unified manager metadata
            rule_info.update({
                "unified_category": rule_meta["category"],
                "rule_system": rule_meta["system"],
                "manager_version": "1.0.0"
            })
        
        return rule_info
    
    def execute_rule(self, rule_id: str, file_path: str, content: str,
                    log_error_func: Callable[[str, str, str, Optional[int]], None]) -> RuleExecutionResult:
        """
        Execute a specific rule with performance monitoring.
        
        Args:
            rule_id (str): The rule ID to execute
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            
        Returns:
            RuleExecutionResult: Execution result with metadata
        """
        start_time = time.time()
        
        if rule_id not in self._unified_registry:
            return RuleExecutionResult(
                rule_id=rule_id,
                success=False,
                execution_time=0.0,
                error_message=f"Unknown rule: {rule_id}"
            )
        
        rule_meta = self._unified_registry[rule_id]
        coordinator = rule_meta["coordinator"]
        
        # Track violations for this rule
        violations_count = 0
        original_log_func = log_error_func
        
        def counting_log_func(path: str, rule: str, message: str, line_number: Optional[int] = None):
            nonlocal violations_count
            violations_count += 1
            original_log_func(path, rule, message, line_number)
        
        try:
            success = coordinator.execute_rule(rule_id, file_path, content, counting_log_func)
            execution_time = time.time() - start_time
            
            return RuleExecutionResult(
                rule_id=rule_id,
                success=success,
                execution_time=execution_time,
                violations_count=violations_count
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return RuleExecutionResult(
                rule_id=rule_id,
                success=False,
                execution_time=execution_time,
                error_message=str(e),
                violations_count=violations_count
            )
    
    def execute_rules_by_category(self, category: str, file_path: str, content: str,
                                 log_error_func: Callable[[str, str, str, Optional[int]], None],
                                 excluded_rules: Optional[List[str]] = None) -> List[RuleExecutionResult]:
        """
        Execute all rules in a specific category.
        
        Args:
            category (str): Category to execute (ST, IO, DC, SC)
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            excluded_rules (Optional[List[str]]): Rules to exclude
            
        Returns:
            List[RuleExecutionResult]: Results for each rule executed
        """
        excluded_rules = excluded_rules or []
        rules_to_execute = [
            rule_id for rule_id in self.get_rules_by_category(category)
            if rule_id not in excluded_rules
        ]
        
        results = []
        for rule_id in rules_to_execute:
            result = self.execute_rule(rule_id, file_path, content, log_error_func)
            results.append(result)
        
        return results
    
    def execute_all_rules(self, file_path: str, content: str,
                         log_error_func: Callable[[str, str, str, Optional[int]], None],
                         excluded_rules: Optional[List[str]] = None,
                         excluded_categories: Optional[List[str]] = None) -> BatchExecutionSummary:
        """
        Execute all available rules with comprehensive reporting.
        
        Args:
            file_path (str): Path to the file being checked
            content (str): File content to check
            log_error_func (Callable): Function to log errors
            excluded_rules (Optional[List[str]]): Specific rules to exclude
            excluded_categories (Optional[List[str]]): Categories to exclude
            
        Returns:
            BatchExecutionSummary: Comprehensive execution summary
        """
        start_time = time.time()
        excluded_rules = excluded_rules or []
        excluded_categories = excluded_categories or []
        
        # Build list of rules to execute
        rules_to_execute = []
        for rule_id in self.get_all_available_rules():
            if rule_id in excluded_rules:
                continue
            
            rule_meta = self._unified_registry[rule_id]
            if rule_meta["system"] in excluded_categories:
                continue
                
            rules_to_execute.append(rule_id)
        
        # Execute rules and collect results
        results_by_category = {"ST": [], "IO": [], "DC": [], "SC": []}
        total_violations = 0
        successful_rules = 0
        failed_rules = 0
        
        for rule_id in rules_to_execute:
            result = self.execute_rule(rule_id, file_path, content, log_error_func)
            
            # Categorize result
            system = self._unified_registry[rule_id]["system"]
            results_by_category[system].append(result)
            
            # Update counters
            total_violations += result.violations_count
            if result.success:
                successful_rules += 1
            else:
                failed_rules += 1
        
        total_execution_time = time.time() - start_time
        
        return BatchExecutionSummary(
            total_rules=len(rules_to_execute),
            successful_rules=successful_rules,
            failed_rules=failed_rules,
            total_violations=total_violations,
            total_execution_time=total_execution_time,
            results_by_category=results_by_category
        )
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of all available rules.
        
        Returns:
            Dict[str, Any]: Complete rules summary with statistics
        """
        st_summary = self._st_rules.get_rules_summary()
        io_summary = self._io_rules.get_rules_summary()
        dc_summary = self._dc_rules.get_rules_summary()
        sc_summary = self._sc_rules.get_rules_summary()
        
        return {
            "total_rules": len(self._unified_registry),
            "rules_by_system": {
                "ST": st_summary["total_rules"],
                "IO": io_summary["total_rules"],
                "DC": dc_summary["total_rules"],
                "SC": sc_summary["total_rules"]
            },
            "rules_by_category": {
                "Style/Format": len(self.get_rules_by_category("ST")),
                "Input/Output": len(self.get_rules_by_category("IO")),
                "Documentation/Comments": len(self.get_rules_by_category("DC")),
                "Security Code": len(self.get_rules_by_category("SC"))
            },
            "system_summaries": {
                "ST": st_summary,
                "IO": io_summary,
                "DC": dc_summary,
                "SC": sc_summary
            },
            "configuration": self._config,
            "all_rule_ids": self.get_all_available_rules()
        }
    
    def validate_file(self, file_path: str, content: str,
                     log_error_func: Callable[[str, str, str, Optional[int]], None],
                     rule_filter: Optional[Dict[str, Any]] = None) -> BatchExecutionSummary:
        """
        Validate a file with flexible rule filtering.
        
        Args:
            file_path (str): Path to the file being validated
            content (str): File content to validate
            log_error_func (Callable): Function to log errors
            rule_filter (Optional[Dict[str, Any]]): Filtering options
            
        Returns:
            BatchExecutionSummary: Validation results
        """
        rule_filter = rule_filter or {}
        
        # Extract filter parameters
        included_systems = rule_filter.get("systems", ["ST", "IO", "DC", "SC"])
        excluded_rules = rule_filter.get("excluded_rules", [])
        included_severities = rule_filter.get("severities", ["error", "warning", "info"])
        
        # Filter rules based on criteria
        filtered_rules = []
        for rule_id in self.get_all_available_rules():
            rule_meta = self._unified_registry[rule_id]
            
            # Check system inclusion
            if rule_meta["system"] not in included_systems:
                continue
                
            # Check rule exclusion
            if rule_id in excluded_rules:
                continue
            
            # Check severity (if rule info is available)
            rule_info = self.get_rule_info(rule_id)
            if rule_info and rule_info.get("severity") not in included_severities:
                continue
            
            filtered_rules.append(rule_id)
        
        # Execute filtered rules
        start_time = time.time()
        results_by_category = {"ST": [], "IO": [], "DC": [], "SC": []}
        total_violations = 0
        successful_rules = 0
        failed_rules = 0
        
        for rule_id in filtered_rules:
            result = self.execute_rule(rule_id, file_path, content, log_error_func)
            
            system = self._unified_registry[rule_id]["system"]
            results_by_category[system].append(result)
            
            total_violations += result.violations_count
            if result.success:
                successful_rules += 1
            else:
                failed_rules += 1
        
        total_execution_time = time.time() - start_time
        
        return BatchExecutionSummary(
            total_rules=len(filtered_rules),
            successful_rules=successful_rules,
            failed_rules=failed_rules,
            total_violations=total_violations,
            total_execution_time=total_execution_time,
            results_by_category=results_by_category
        )
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration settings."""
        return self._config.copy()
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> None:
        """
        Update configuration settings.
        
        Args:
            config_updates (Dict[str, Any]): Configuration updates to apply
        """
        self._config.update(config_updates)
    
    # Legacy compatibility methods
    def check_all_rules(self, file_path: str, content: str,
                       log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
        """Legacy method for backward compatibility."""
        self.execute_all_rules(file_path, content, log_error_func)
    
    def get_all_rules(self) -> Dict[str, Any]:
        """Legacy method - returns unified registry."""
        return self._unified_registry
    
    def list_rule_ids(self) -> List[str]:
        """Legacy method - returns all available rule IDs."""
        return self.get_all_available_rules()


# Convenience functions for easy access
def get_rules_manager() -> RulesManager:
    """Get a configured rules manager instance."""
    return RulesManager()

def validate_terraform_file(file_path: str, content: str,
                           log_error_func: Callable[[str, str, str, Optional[int]], None],
                           rule_filter: Optional[Dict[str, Any]] = None) -> BatchExecutionSummary:
    """
    Validate a Terraform file using all available rules.
    
    Args:
        file_path (str): Path to the file being validated
        content (str): File content to validate
        log_error_func (Callable): Function to log errors
        rule_filter (Optional[Dict[str, Any]]): Rule filtering options
        
    Returns:
        BatchExecutionSummary: Validation results
    """
    manager = get_rules_manager()
    return manager.validate_file(file_path, content, log_error_func, rule_filter)

def get_all_available_rules() -> List[str]:
    """Get list of all available rule IDs across all systems."""
    return get_rules_manager().get_all_available_rules()

def get_unified_rules_summary() -> Dict[str, Any]:
    """Get comprehensive summary of all rules."""
    return get_rules_manager().get_rules_summary() 