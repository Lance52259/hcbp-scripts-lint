#!/usr/bin/env python3
"""
Unified Rules Package

This package provides a comprehensive linting system for Terraform files
with rules organized into four main categories:

- ST (Style/Format): Code style and formatting rules
- IO (Input/Output): Variable and output definition rules  
- DC (Documentation/Comments): Documentation and comment rules
- SC (Security Code): Security code and safety rules

The package offers both unified management through RulesManager and
individual rule system access for specific use cases.

Main Components:
- RulesManager: Unified coordinator for all rule systems
- STRules: Style and format rules coordinator
- IORules: Input/output rules coordinator
- DCRules: Documentation and comment rules coordinator
- SCRules: Security code rules coordinator

Usage Examples:
    # Unified approach (recommended)
    from rules import RulesManager, validate_terraform_file
    
    manager = RulesManager()
    summary = manager.execute_all_rules(file_path, content, log_func)
    
    # Or use convenience function
    summary = validate_terraform_file(file_path, content, log_func)
    
    # Individual system access
    from rules import STRules, IORules, DCRules, SCRules
    
    st_rules = STRules()
    st_rules.execute_all_rules(file_path, content, log_func)

Author: Lance
License: Apache 2.0
"""

# Import unified management system
from .rules_manager import (
    RulesManager,
    RuleExecutionResult,
    BatchExecutionSummary,
    get_rules_manager,
    validate_terraform_file,
    get_all_available_rules,
    get_unified_rules_summary
)

# Import individual rule systems for direct access
from .st_rules.reference import STRules
from .io_rules.reference import IORules  
from .dc_rules.reference import DCRules
from .sc_rules.reference import SCRules

# Import convenience functions from individual systems
from .st_rules.reference import (
    get_available_st_rules,
    execute_st_rule,
    execute_all_st_rules,
    get_st_rule_info
)

from .io_rules.reference import (
    get_available_io_rules,
    execute_io_rule,
    execute_all_io_rules,
    get_io_rule_info
)

from .dc_rules.reference import (
    get_available_dc_rules,
    execute_dc_rule,
    execute_all_dc_rules,
    get_dc_rule_info
)

from .sc_rules.reference import (
    get_available_sc_rules,
    execute_sc_rule,
    execute_all_sc_rules,
    get_sc_rule_info
)

# Package metadata
__version__ = "1.0.0"
__author__ = "Lance"
__license__ = "Apache 2.0"

# Define public API
__all__ = [
    # Unified management (primary interface)
    "RulesManager",
    "RuleExecutionResult", 
    "BatchExecutionSummary",
    "get_rules_manager",
    "validate_terraform_file",
    "get_all_available_rules",
    "get_unified_rules_summary",
    
    # Individual rule systems
    "STRules",
    "IORules", 
    "DCRules",
    "SCRules",
    
    # ST rules convenience functions
    "get_available_st_rules",
    "execute_st_rule",
    "execute_all_st_rules", 
    "get_st_rule_info",
    
    # IO rules convenience functions
    "get_available_io_rules",
    "execute_io_rule",
    "execute_all_io_rules",
    "get_io_rule_info",
    
    # DC rules convenience functions
    "get_available_dc_rules",
    "execute_dc_rule", 
    "execute_all_dc_rules",
    "get_dc_rule_info",
    
    # SC rules convenience functions
    "get_available_sc_rules",
    "execute_sc_rule",
    "execute_all_sc_rules",
    "get_sc_rule_info"
]

# Backward compatibility aliases
# These maintain compatibility with existing code
def get_all_rules():
    """Legacy function - get all rules from unified manager."""
    return get_rules_manager().get_all_rules()

def check_all_rules(file_path: str, content: str, log_error_func):
    """Legacy function - execute all rules."""
    manager = get_rules_manager()
    manager.execute_all_rules(file_path, content, log_error_func)

# Package-level configuration
DEFAULT_CONFIG = {
    "enable_st_rules": True,
    "enable_io_rules": True, 
    "enable_dc_rules": True,
    "enable_sc_rules": True,
    "enable_performance_monitoring": True,
    "max_violations_per_file": 1000,
    "timeout_per_file": 60.0
}

def get_package_info():
    """Get comprehensive package information."""
    manager = get_rules_manager()
    summary = manager.get_rules_summary()
    
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "total_rules": summary["total_rules"],
        "rules_by_system": summary["rules_by_system"],
        "available_systems": ["ST", "IO", "DC", "SC"],
        "default_config": DEFAULT_CONFIG,
        "unified_interface": True
    } 