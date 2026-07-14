"""
Shared provider-related variable identity helpers.

These names are commonly injected via environment variables, providers.tf, or
external tfvars, and should be treated specially by IO.003 / IO.009 / ST.009.

Exclusion semantics (same name set, different rules):
- IO.003: skip terraform.tfvars required-declaration check
- IO.009: skip unused-variable check only (undeclared references still report)
- ST.009: skip usage/definition order comparison
"""

from typing import FrozenSet

PROVIDER_VARIABLE_PREFIXES: FrozenSet[str] = frozenset({"region"})

PROVIDER_VARIABLE_NAMES: FrozenSet[str] = frozenset(
    {
        "access_key",
        "secret_key",
        "domain_name",
        "tenant_name",
        "tenant_id",
        "user_name",
        "user_id",
        "project_name",
        "project_id",
    }
)


def is_provider_related_variable(var_name: str) -> bool:
    """Return True if *var_name* is a known provider/auth/region variable."""
    if not var_name:
        return False
    if var_name in PROVIDER_VARIABLE_NAMES:
        return True
    return any(var_name.startswith(prefix) for prefix in PROVIDER_VARIABLE_PREFIXES)
