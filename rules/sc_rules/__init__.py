#!/usr/bin/env python3
"""
SC (Security Code) Rules Package

This package contains all security code related checking rules
for Terraform scripts. Each rule is implemented in a separate module for
better maintainability and extensibility.

Available Rules:
- SC.001: Array index access safety check

Author: Lance
License: Apache 2.0
"""

from .reference import SCRules

__all__ = ['SCRules'] 