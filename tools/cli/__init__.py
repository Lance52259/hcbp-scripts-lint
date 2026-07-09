"""CLI support modules for help rendering and version resolution."""

from .help import (
    LOCAL_INSTALL_TOOL_NAME,
    SCRIPT_TOOL_NAME,
    build_argument_parser_kwargs,
    render_cli_help_epilog,
    resolve_tool_context,
)
from .version import get_tool_version

__all__ = [
    "LOCAL_INSTALL_TOOL_NAME",
    "SCRIPT_TOOL_NAME",
    "build_argument_parser_kwargs",
    "get_tool_version",
    "render_cli_help_epilog",
    "resolve_tool_context",
]
