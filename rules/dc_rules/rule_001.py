#!/usr/bin/env python3
"""
DC.001 - Comment Format Validation Rule

This module implements the DC.001 rule which validates comment formatting
in Terraform files. The rule ensures that all comments follow consistent
formatting standards for better code readability and maintainability.

Rule Specifications:
- All comments must start with the '#' character
- There must be exactly one space between '#' and the comment text
- Empty comments (only '#') are allowed and considered valid
- Multiple spaces or tabs after '#' are considered violations
- Comments within string literals are not validated (Terraform-specific)

Valid Examples:
    # This is a properly formatted comment
    # TODO: Add validation logic
    # Variable description for input parameters
    #

Invalid Examples:
    #This comment has no space after #
    #  This comment has multiple spaces after #
    #	This comment has a tab after #

Author: Lance
License: Apache 2.0
"""

import re
from typing import Callable, List, Tuple, Optional, Dict, Any


def check_dc001_comment_format(file_path: str, content: str, 
                              log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate comment formatting according to DC.001 rule specifications.

    This function scans through all lines in the provided Terraform file content
    and validates that comments follow the proper formatting standards. It checks
    for the presence of exactly one space after the '#' character and reports
    violations through the provided error logging function.

    The validation process includes:
    1. Line-by-line analysis of file content
    2. Comment pattern identification using regex
    3. Spacing validation after '#' character
    4. Error reporting with specific line numbers and messages
    5. Handling of edge cases (empty comments, string literals)

    Args:
        file_path (str): The path to the file being checked. Used for error reporting
                        to help developers identify the location of violations.
        content (str): The complete content of the Terraform file as a string.
                      This includes all lines, comments, and code blocks.
        log_error_func (Callable[[str, str, str, Optional[int]], None]): A callback function used
                      to report rule violations. The function should accept four
                      parameters: file_path, rule_id, error_message, and line_number.
                      The line_number parameter is optional and can be None.

    Returns:
        None: This function doesn't return a value but reports errors through
              the log_error_func callback.

    Raises:
        No exceptions are raised by this function. All errors are handled
        gracefully and reported through the logging mechanism.

    Example:
        >>> def mock_logger(path, rule, msg, line_number):
        ...     print(f"{rule}: {msg} (line {line_number})")
        >>> content = "# Good comment\\n#Bad comment\\n#  Multiple spaces"
        >>> check_dc001_comment_format("test.tf", content, mock_logger)
        DC.001: Comment should have one space after '#' character (line 2)
        DC.001: Comment should have exactly one space after '#' character (line 3)

    Note:
        This function focuses on comment formatting within Terraform files and
        may not handle all edge cases such as comments within complex string
        literals or heredoc blocks. However, it provides reliable validation
        for typical Terraform file structures and coding patterns.
    """
    # Split content into individual lines for line-by-line analysis
    lines = content.split('\n')
    
    # Track comment violations for potential batch reporting
    violations = _analyze_comment_formatting(lines)
    
    # Report each violation through the error logging function
    for line_num, violation_type, message in violations:
        log_error_func(file_path, "DC.001", message, line_num)


def _analyze_comment_formatting(lines: List[str]) -> List[Tuple[int, str, str]]:
    """
    Analyze comment formatting across all lines and identify violations.
    
    Args:
        lines (List[str]): List of file lines to analyze
        
    Returns:
        List[Tuple[int, str, str]]: List of violations with line number, type, and message
    """
    violations = []
    
    # Process each line with its corresponding line number (1-indexed)
    for line_num, line in enumerate(lines, 1):
        # Skip empty lines or lines without comments
        if not line.strip() or '#' not in line:
            continue
            
        # Use regex to find comment patterns in the current line
        comment_match = re.search(r'#(.*)$', line)
        
        if comment_match:
            comment_text = comment_match.group(1)
            violation = _validate_comment_spacing(comment_text)
            
            if violation:
                violations.append((line_num, violation["type"], violation["message"]))
    
    return violations


def _validate_comment_spacing(comment_text: str) -> Optional[Dict[str, str]]:
    """
    Validate spacing requirements for a single comment.
    
    Args:
        comment_text (str): The text portion after the '#' character
        
    Returns:
        Optional[Dict[str, str]]: Violation information or None if valid
    """
    # Skip validation for empty comments (only '#' with no text)
    if not comment_text:
        return None
    
    # Check for proper spacing after '#' character
    if not comment_text.startswith(' '):
        return {
            "type": "no_space",
            "message": "Comment should have one space after '#' character"
        }
    elif comment_text.startswith('  ') or comment_text.startswith('\t'):
        return {
            "type": "multiple_spaces",
            "message": "Comment should have exactly one space after '#' character"
        }
    
    return None


def _remove_comments_for_parsing(content: str) -> str:
    """
    Remove comments from content for parsing purposes.
    
    This is a utility function that can be used by other validation
    functions that need to parse Terraform syntax without comments.
    
    Args:
        content (str): Original file content
        
    Returns:
        str: Content with comments removed
    """
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Find comment start position
        comment_pos = line.find('#')
        if comment_pos != -1:
            # Keep everything before the comment
            cleaned_lines.append(line[:comment_pos].rstrip())
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def _get_comment_statistics(content: str) -> Dict[str, Any]:
    """
    Generate statistics about comment usage in the file.
    
    Args:
        content (str): File content to analyze
        
    Returns:
        Dict[str, Any]: Statistics about comments
    """
    lines = content.split('\n')
    total_lines = len(lines)
    comment_lines = 0
    empty_comments = 0
    properly_formatted = 0
    violations = 0
    
    for line in lines:
        if '#' in line:
            comment_lines += 1
            comment_match = re.search(r'#(.*)$', line)
            if comment_match:
                comment_text = comment_match.group(1)
                if not comment_text:
                    empty_comments += 1
                elif comment_text.startswith(' ') and not comment_text.startswith('  '):
                    properly_formatted += 1
                else:
                    violations += 1
    
    return {
        "total_lines": total_lines,
        "comment_lines": comment_lines,
        "empty_comments": empty_comments,
        "properly_formatted": properly_formatted,
        "violations": violations,
        "comment_ratio": comment_lines / total_lines if total_lines > 0 else 0
    }


def get_rule_description() -> Dict[str, Any]:
    """
    Retrieve detailed information about the DC.001 rule.

    This function provides comprehensive metadata about the rule including its
    purpose, validation criteria, examples, and configuration options. This
    information is used for documentation generation, help systems, and
    configuration interfaces.

    Returns:
        Dict[str, Any]: A dictionary containing comprehensive rule information with
                       standardized fields for integration with the linting system.

    Example:
        >>> info = get_rule_description()
        >>> print(info['name'])
        Comment format check
        >>> print(info['severity'])
        error
    """
    return {
        "id": "DC.001",
        "name": "Comment format check",
        "description": (
            "Validates that all comments in Terraform files follow consistent formatting "
            "standards. Comments must start with '#' followed by exactly one space before "
            "the comment text. This ensures uniform comment styling across the codebase "
            "and improves readability for both humans and automated tools."
        ),
        "category": "Documentation/Comments",
        "severity": "error",
        "rationale": (
            "Consistent comment formatting improves code readability and maintains "
            "professional coding standards. It ensures that automated documentation "
            "tools can properly parse and process comments, and helps maintain "
            "consistency across team members and projects."
        ),
        "specifications": [
            "All comments must start with the '#' character",
            "Exactly one space must follow the '#' character",
            "Empty comments (only '#') are allowed",
            "Multiple spaces or tabs after '#' are violations",
            "Comments within string literals are not validated"
        ],
        "examples": {
            "valid": [
                "# This is a properly formatted comment",
                "# TODO: Implement error handling",
                "# Variable description for input parameters", 
                "#"
            ],
            "invalid": [
                "#This comment has no space after hash",
                "#  This comment has multiple spaces after hash",
                "#\tThis comment has a tab character after hash"
            ]
        },
        "auto_fixable": True,
        "performance_impact": "minimal",
        "related_rules": [],
        "configuration": {
            "allow_empty_comments": True,
            "require_space_after_hash": True,
            "allow_multiple_spaces": False
        }
    }
