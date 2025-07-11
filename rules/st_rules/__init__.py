#!/usr/bin/env python3
"""
ST (Style/Format) Rules Package

This package contains all style and format related checking rules
for Terraform scripts. Each rule is implemented in a separate module for
better maintainability and extensibility.

Available Rules:
- ST.001: Resource and data source naming convention check
- ST.002: Variable default value check
- ST.003: Parameter alignment check
- ST.004: Indentation character check
- ST.005: Indentation level check
- ST.006: Resource and data source spacing check
- ST.007: Same parameter block spacing check
- ST.008: Different parameter block spacing check
- ST.009: Variable definition order check
- ST.010: Resource, data source, variable, and output quote check
- ST.011: Trailing whitespace check

Author: Lance
License: Apache 2.0
"""

from .reference import STRules
from .rule_008 import check_st008_different_named_parameter_spacing

__all__ = ['STRules']
