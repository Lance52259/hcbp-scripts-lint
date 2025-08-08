#!/usr/bin/env python3
"""
Comment Control Module

This module provides functionality to control rule execution through comments
in Terraform files. It supports enabling and disabling specific rules using
comment directives.

Supported Comment Formats:
- # ST.001 Disable  - Disables ST.001 rule from this line onwards in the current file
- # ST.001 Enable   - Re-enables ST.001 rule from this line onwards in the current file

Features:
- File-scoped control (comments only affect the current file)
- Line-based control (rules are disabled/enabled from the comment line onwards)
- Support for all rule categories (ST, IO, DC, SC)
- Robust parsing with error handling

Author: Lance
License: Apache 2.0
"""

import re
from typing import Dict, Set, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RuleControlState:
    """Represents the state of rule control for a specific rule."""
    rule_id: str
    is_enabled: bool
    control_line: int
    control_type: str  # "Enable" or "Disable"


class CommentController:
    """
    Manages rule execution control through comments in Terraform files.
    
    This class parses comment directives and maintains the state of which
    rules are enabled or disabled for each line in a file.
    """
    
    def __init__(self):
        """Initialize the comment controller."""
        self._control_pattern = re.compile(r'^\s*#\s*([A-Z]{2}\.\d{3})\s+(Enable|Disable)\s*$')
    
    def parse_control_comments(self, content: str) -> Dict[int, RuleControlState]:
        """
        Parse control comments from file content and return control states.
        
        Args:
            content (str): The complete file content to parse
            
        Returns:
            Dict[int, RuleControlState]: Mapping of line numbers to control states
        """
        lines = content.split('\n')
        control_states = {}
        
        for line_num, line in enumerate(lines, 1):
            match = self._control_pattern.match(line.strip())
            if match:
                rule_id = match.group(1)
                control_type = match.group(2)
                is_enabled = control_type == "Enable"
                
                control_states[line_num] = RuleControlState(
                    rule_id=rule_id,
                    is_enabled=is_enabled,
                    control_line=line_num,
                    control_type=control_type
                )
        
        return control_states
    
    def get_rule_state_at_line(self, rule_id: str, line_number: int, 
                              control_states: Dict[int, RuleControlState]) -> bool:
        """
        Determine if a rule is enabled at a specific line number.
        
        Args:
            rule_id (str): The rule ID to check (e.g., "ST.001")
            line_number (int): The line number to check
            control_states (Dict[int, RuleControlState]): Parsed control states
            
        Returns:
            bool: True if the rule is enabled at this line, False if disabled
        """
        # Rules are enabled by default
        is_enabled = True
        
        # Check all control directives that affect this rule
        for control_line, state in control_states.items():
            if state.rule_id == rule_id and control_line <= line_number:
                is_enabled = state.is_enabled
        
        return is_enabled
    
    def get_disabled_rules_at_line(self, line_number: int, 
                                  control_states: Dict[int, RuleControlState]) -> Set[str]:
        """
        Get all disabled rules at a specific line number.
        
        Args:
            line_number (int): The line number to check
            control_states (Dict[int, RuleControlState]): Parsed control states
            
        Returns:
            Set[str]: Set of rule IDs that are disabled at this line
        """
        disabled_rules = set()
        
        for control_line, state in control_states.items():
            if control_line <= line_number and not state.is_enabled:
                disabled_rules.add(state.rule_id)
        
        return disabled_rules
    
    def validate_control_comments(self, content: str) -> List[str]:
        """
        Validate control comments and return any errors.
        
        Args:
            content (str): The file content to validate
            
        Returns:
            List[str]: List of validation error messages
        """
        errors = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Check for comment control patterns
            if stripped_line.startswith('#'):
                # Check if it looks like a control comment but doesn't match the pattern
                if re.search(r'[A-Z]{2}\.\d{3}\s+(Enable|Disable)', stripped_line):
                    if not self._control_pattern.match(stripped_line):
                        errors.append(f"Line {line_num}: Invalid control comment format. "
                                   f"Expected: '# RULE_ID Enable' or '# RULE_ID Disable'")
        
        return errors
    
    def get_control_summary(self, control_states: Dict[int, RuleControlState]) -> Dict[str, List[int]]:
        """
        Get a summary of control directives by rule ID.
        
        Args:
            control_states (Dict[int, RuleControlState]): Parsed control states
            
        Returns:
            Dict[str, List[int]]: Mapping of rule IDs to line numbers where they are controlled
        """
        summary = {}
        
        for line_num, state in control_states.items():
            if state.rule_id not in summary:
                summary[state.rule_id] = []
            summary[state.rule_id].append(line_num)
        
        return summary


def create_comment_controller() -> CommentController:
    """
    Create a new comment controller instance.
    
    Returns:
        CommentController: A new comment controller instance
    """
    return CommentController()


def parse_file_control_states(content: str) -> Dict[int, RuleControlState]:
    """
    Parse control states from file content.
    
    Args:
        content (str): The file content to parse
        
    Returns:
        Dict[int, RuleControlState]: Mapping of line numbers to control states
    """
    controller = create_comment_controller()
    return controller.parse_control_comments(content)


def is_rule_enabled_at_line(rule_id: str, line_number: int, 
                           control_states: Dict[int, RuleControlState]) -> bool:
    """
    Check if a rule is enabled at a specific line.
    
    Args:
        rule_id (str): The rule ID to check
        line_number (int): The line number to check
        control_states (Dict[int, RuleControlState]): Parsed control states
        
    Returns:
        bool: True if the rule is enabled, False if disabled
    """
    controller = create_comment_controller()
    return controller.get_rule_state_at_line(rule_id, line_number, control_states) 