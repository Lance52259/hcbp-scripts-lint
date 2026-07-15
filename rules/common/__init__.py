"""Shared helpers used across ST / IO / SC / DC rules."""

from .provider_variables import (
    PROVIDER_REGION_EXACT,
    PROVIDER_REGION_PREFIX,
    PROVIDER_VARIABLE_NAMES,
    PROVIDER_VARIABLE_PREFIXES,
    is_provider_related_variable,
)
from .rule_metadata import (
    REQUIRED_KEYS,
    assert_rules_have_canonical_metadata,
    normalize_rule_description,
    validate_rule_description,
)
from .sensitive_patterns import (
    CREDENTIAL_ATTRIBUTE_NAMES,
    NON_SENSITIVE_ALLOWLIST,
    get_sensitive_match,
    get_sensitive_variable_patterns,
    is_dangerous_string_default,
    is_placeholder_literal,
)

__all__ = [
    "PROVIDER_REGION_EXACT",
    "PROVIDER_REGION_PREFIX",
    "PROVIDER_VARIABLE_NAMES",
    "PROVIDER_VARIABLE_PREFIXES",
    "is_provider_related_variable",
    "REQUIRED_KEYS",
    "assert_rules_have_canonical_metadata",
    "normalize_rule_description",
    "validate_rule_description",
    "CREDENTIAL_ATTRIBUTE_NAMES",
    "NON_SENSITIVE_ALLOWLIST",
    "get_sensitive_match",
    "get_sensitive_variable_patterns",
    "is_dangerous_string_default",
    "is_placeholder_literal",
]
