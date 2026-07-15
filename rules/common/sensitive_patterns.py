"""
Shared sensitive-name patterns and placeholder helpers for SC.005 / SC.006 / SC.007.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


NON_SENSITIVE_ALLOWLIST = frozenset({
    "auth_type",
    "authorization_mode",
    "oauth_scope",
    "certificate_name",
})

# Credential attribute / assignment LHS names used by SC.006
CREDENTIAL_ATTRIBUTE_NAMES = frozenset({
    "access_key",
    "secret_key",
    "security_token",
    "token",
    "api_key",
    "password",
    "private_key",
})

_PLACEHOLDER_EXACT = frozenset({
    "changeme",
    "replace_me",
    "xxx",
    "example",
    "placeholder",
    "todo",
    "fake",
    "dummy",
})

_REFERENCE_PREFIXES = (
    "var.",
    "local.",
    "data.",
    "module.",
    "file(",
    "env(",
)


def get_sensitive_variable_patterns() -> Dict[str, List[str]]:
    """
    Patterns for sensitive variable names.

    ``phone`` is segment-only (not contains) to avoid ``microphone`` false positives.
    """
    return {
        "exact": [
            "email",
            "age",
            "access_key",
            "secret_key",
            "sex",
            "signature",
            "api_key",
            "token",
            "private_key",
            "phone",
        ],
        "segment": [
            "auth",
            "token",
            "api_key",
            "phone",
        ],
        "contains": [
            "password",
            "pwd",
            "private_key",
            "credential",
        ],
    }


def split_segments(var_name: str) -> List[str]:
    """Split a snake_case variable name into lowercase segments."""
    return [segment for segment in var_name.lower().split("_") if segment]


def get_sensitive_match(
    var_name: str,
    patterns: Optional[Dict[str, List[str]]] = None,
) -> Optional[Tuple[str, str]]:
    """
    Determine whether a variable name matches a sensitive pattern.

    Matching priority: exact -> segment -> contains.
    Segment matches are skipped when the full variable name is allowlisted.
    """
    if patterns is None:
        patterns = get_sensitive_variable_patterns()

    var_name_lower = var_name.lower()

    for exact_pattern in patterns["exact"]:
        if var_name_lower == exact_pattern:
            return exact_pattern, "exact"

    segments = split_segments(var_name_lower)
    for segment_pattern in patterns["segment"]:
        if segment_pattern in segments:
            if var_name_lower in NON_SENSITIVE_ALLOWLIST:
                continue
            return segment_pattern, "segment"

    for contains_pattern in patterns["contains"]:
        if contains_pattern in var_name_lower:
            return contains_pattern, "contains"

    return None


def strip_line_comment(line: str) -> str:
    """Remove ``#`` comments outside of simple quoted segments (best-effort)."""
    in_single = False
    in_double = False
    result = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"' and not in_single and (i == 0 or line[i - 1] != "\\"):
            in_double = not in_double
            result.append(ch)
        elif ch == "'" and not in_double and (i == 0 or line[i - 1] != "\\"):
            in_single = not in_single
            result.append(ch)
        elif ch == "#" and not in_single and not in_double:
            break
        else:
            result.append(ch)
        i += 1
    return "".join(result).strip()


def is_placeholder_literal(value: str) -> bool:
    """Return True when *value* is an empty or documented placeholder string."""
    cleaned = value.strip().strip('"').strip("'").strip()
    if cleaned == "":
        return True
    lowered = cleaned.lower()
    if lowered in _PLACEHOLDER_EXACT:
        return True
    if lowered.startswith("your_") or lowered.startswith("your-"):
        return True
    if lowered.startswith("changeme") or lowered.startswith("replace_me"):
        return True
    return False


def is_reference_expression(value: str) -> bool:
    """Return True when RHS looks like a Terraform reference / function, not a literal."""
    stripped = value.strip()
    lowered = stripped.lower()
    return any(lowered.startswith(prefix) for prefix in _REFERENCE_PREFIXES)


def extract_default_assignment(var_content: str) -> Optional[Tuple[str, int]]:
    """
    Extract the first ``default`` assignment from a variable block.

    Returns:
        (rhs_text, line_number_1_based_within_file_content_start) or None.
        Line number is relative to the start of *var_content* (first line = 1).
    """
    for index, line in enumerate(var_content.split("\n"), 1):
        clean = strip_line_comment(line)
        match = re.match(r"default\s*=\s*(.+)$", clean, re.IGNORECASE)
        if match:
            return match.group(1).strip(), index
    return None


def is_dangerous_string_default(rhs: str) -> bool:
    """
    True when a variable default RHS is a non-empty non-placeholder string literal.

    Non-string defaults (numbers, bools, complex expressions) are ignored in MVP.
    ``null`` and empty string are safe.
    """
    stripped = rhs.strip()
    if re.match(r"^null\b", stripped, re.IGNORECASE):
        return False

    string_match = re.match(r'^"(.*)"\s*$', stripped) or re.match(r"^'(.*)'\s*$", stripped)
    if not string_match:
        return False

    value = string_match.group(1)
    if is_placeholder_literal(value):
        return False
    return True


# Compatibility aliases used by existing SC.005 tests
_get_sensitive_variable_patterns = get_sensitive_variable_patterns
_get_sensitive_match = get_sensitive_match
