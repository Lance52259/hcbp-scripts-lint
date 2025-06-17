#!/usr/bin/env python3
"""
DC (Documentation/Comments) Rules Package

This package contains all documentation and comment related checking rules
for Terraform scripts. Each rule is implemented in a separate module for
better maintainability and extensibility.

Available Rules:
- DC.001: Comment format validation

Author: Lance
License: Apache 2.0
"""

from .reference import DCRules

__all__ = ['DCRules']
