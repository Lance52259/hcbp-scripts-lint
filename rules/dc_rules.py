#!/usr/bin/env python3
"""
DC (Documentation/Comments) - Documentation and comment rules
Contains all documentation and comment related checking rules
"""

import re
from typing import Dict, List

class DCRules:
    """DC type rule checker"""

    def __init__(self):
        self.rules = {
            "DC.001": {
                "name": "Comment format check",
                "description": (
                    "Check if all comments start with # character and maintain one space between # and "
                    "comment text"
                ),
                "category": "Documentation/Comments"
            }
        }

    def get_file_lines(self, content: str) -> List[str]:
        """
        Get all lines of the file
        """
        return content.split('\n')

    def check_dc001_comment_format(self, file_path: str, content: str, log_error_func):
        """
        DC.001: Check comment format - all comments should start with # and have one space after #
        """
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Find comments
            comment_match = re.search(r'#(.*)$', line)
            if comment_match:
                comment_text = comment_match.group(1)

                # Skip empty comments (only #)
                if not comment_text:
                    continue

                # Check if it starts with a space
                if not comment_text.startswith(' '):
                    log_error_func(
                        file_path,
                        "DC.001",
                        f"Line {line_num}: Comment should have one space after '#' character"
                    )
                elif comment_text.startswith('  '):
                    # Check for multiple spaces
                    log_error_func(
                        file_path,
                        "DC.001",
                        f"Line {line_num}: Comment should have exactly one space after '#' character, "
                        f"found multiple spaces"
                    )

    def run_all_checks(self, file_path: str, content: str, log_error_func):
        """
        Run all DC rule checks
        """
        self.check_dc001_comment_format(file_path, content, log_error_func)

    def get_rule_info(self, rule_id: str) -> Dict:
        """
        Get rule information
        """
        return self.rules.get(rule_id, {})

    def get_all_rules(self) -> Dict:
        """
        Get all rule information
        """
        return self.rules
