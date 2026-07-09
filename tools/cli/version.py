#!/usr/bin/env python3
"""Tool release version helpers."""

import os
import re

from ._project import get_project_root

CHANGELOG_RELATIVE_PATH = ("CHANGELOG.md",)
CHANGELOG_VERSION_PATTERN = re.compile(r"^## \[([^\]]+)\]", re.MULTILINE)


def get_tool_version():
    """Return the latest tool release version from CHANGELOG.md."""
    changelog_path = os.path.join(get_project_root(), *CHANGELOG_RELATIVE_PATH)
    if not os.path.isfile(changelog_path):
        return "unknown"

    with open(changelog_path, "r", encoding="utf-8") as changelog_file:
        content = changelog_file.read()

    match = CHANGELOG_VERSION_PATTERN.search(content)
    if not match:
        return "unknown"

    return match.group(1).strip()
