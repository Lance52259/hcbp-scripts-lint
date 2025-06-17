#!/usr/bin/env python3
"""
IO (Input/Output) Rules Package

This package contains all input/output related checking rules for Terraform scripts.
It provides modular, maintainable implementations of IO rules that validate
variable definitions, output declarations, and file organization.

Available Rules:
- IO.001: Variable definition file location check
- IO.002: Output definition file location check
- IO.003: Required variable declaration check in terraform.tfvars
- IO.004: Variable naming convention check
- IO.005: Output naming convention check
- IO.006: Variable description field check
- IO.007: Output description field check
- IO.008: Variable type definition check

Each rule is implemented as a separate module for better maintainability
and easier testing. The rules are coordinated by the IORules class in
the reference module.

Author: Lance
License: Apache 2.0
"""

from .reference import IORules

__all__ = ['IORules']
