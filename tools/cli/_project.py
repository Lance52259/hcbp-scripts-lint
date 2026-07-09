"""Shared path helpers for CLI modules."""

import os


def get_project_root():
    """Return the repository root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current_dir))
