"""
Shared provider-related variable identity helpers.

These names are commonly injected via environment variables, providers.tf, or
external tfvars, and should be treated specially by IO.003 / IO.009 / ST.009.

Exclusion semantics (same name set, different rules):
- IO.003: skip terraform.tfvars required-declaration check
- IO.009: skip unused-variable check only (undeclared references still report)
- ST.009: skip usage/definition order comparison

Region matching uses exact ``region`` or the ``region_`` prefix so names like
``regional_vpc`` are not treated as provider variables.
"""

from typing import FrozenSet

# Exact name "region", or any name starting with "region_" (region_name, region_id, …)
PROVIDER_REGION_EXACT: str = "region"
PROVIDER_REGION_PREFIX: str = "region_"

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

# Backwards-compatible alias used by docs / configuration dumps
PROVIDER_VARIABLE_PREFIXES: FrozenSet[str] = frozenset({PROVIDER_REGION_PREFIX.rstrip("_")})


def is_provider_related_variable(var_name: str) -> bool:
    """Return True if *var_name* is a known provider/auth/region variable."""
    if not var_name:
        return False
    if var_name in PROVIDER_VARIABLE_NAMES:
        return True
    if var_name == PROVIDER_REGION_EXACT:
        return True
    if var_name.startswith(PROVIDER_REGION_PREFIX):
        return True
    return False
