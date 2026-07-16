#!/usr/bin/env python3
"""
IO.013 - Provider Definition File Location Check

Ensures top-level provider configuration blocks live in providers.tf,
mirroring IO.001 (variables.tf) and IO.002 (outputs.tf).

Rule Specification:
- Top-level ``provider … {`` blocks must be defined in ``providers.tf``
- Resource/module meta-argument ``provider = …`` is not a configuration block
- ``terraform { required_providers { … } }`` is out of scope (see SC.002)
- Quoted, single-quoted, and unquoted provider types are recognized

Author: Lance
License: Apache 2.0
"""

import os
import re
from typing import Callable, List, Optional, Tuple

_PROVIDER_HEADER = re.compile(
    r'\s*provider\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{'
)
_ALIAS_PATTERN = re.compile(r'alias\s*=\s*"([^"]+)"')


def check_io013_provider_file_location(
    file_path: str,
    content: str,
    log_error_func: Callable[[str, str, str, Optional[int]], None],
) -> None:
    """
    Validate that provider configuration blocks are defined in providers.tf.
    """
    providers = _extract_providers_with_lines(content)
    if not providers:
        return

    if os.path.basename(file_path) == "providers.tf":
        return

    for provider_type, line_number, alias in providers:
        if alias:
            message = (
                f"Provider '{provider_type}' (alias '{alias}') "
                f"should be defined in 'providers.tf'"
            )
        else:
            message = (
                f"Provider '{provider_type}' should be defined in 'providers.tf'"
            )
        log_error_func(file_path, "IO.013", message, line_number)


def _extract_providers_with_lines(content: str) -> List[Tuple[str, int, Optional[str]]]:
    """
    Extract provider configuration blocks as (type, line, alias).

    Only matches headers ending with ``{`` so resource meta-arguments
    like ``provider = huaweicloud.test`` are ignored.
    """
    providers: List[Tuple[str, int, Optional[str]]] = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]
        match = _PROVIDER_HEADER.match(line)
        if not match:
            i += 1
            continue

        provider_type = match.group(1) or match.group(2) or match.group(3)
        line_number = i + 1
        brace_count = line.count("{") - line.count("}")
        block_lines = [line]
        j = i + 1
        while j < len(lines) and brace_count > 0:
            block_lines.append(lines[j])
            brace_count += lines[j].count("{") - lines[j].count("}")
            j += 1

        alias_match = _ALIAS_PATTERN.search("\n".join(block_lines))
        alias = alias_match.group(1) if alias_match else None
        providers.append((provider_type, line_number, alias))
        i = j

    return providers


def get_rule_description() -> dict:
    """Retrieve detailed information about the IO.013 rule."""
    return {
        "id": "IO.013",
        "name": "Provider definition file location check",
        "description": (
            "Validates that top-level provider configuration blocks are defined "
            "in providers.tf and not in other .tf files. Does not flag resource "
            "or module provider meta-arguments, and does not police terraform {} "
            "or required_providers (see SC.002)."
        ),
        "category": "Input/Output",
        "severity": "error",
        "rationale": (
            "Huawei Cloud example modules keep provider configuration next to "
            "terraform required_providers in providers.tf. Enforcing that layout "
            "matches SC.002/SC.003/SC.004 and mirrors IO.001/IO.002 organization."
        ),
        "examples": {
            "valid": [
                '''
# providers.tf
terraform {
  required_providers {
    huaweicloud = {
      source = "huaweicloud/huaweicloud"
    }
  }
}

provider "huaweicloud" {
  region = var.region_name
}

# main.tf
resource "huaweicloud_vpc" "test" {
  name = var.vpc_name
  # provider = huaweicloud.test  # meta-arg OK
}
'''
            ],
            "invalid": [
                '''
# main.tf
provider "huaweicloud" {
  region = var.region_name
}
'''
            ],
        },
        "auto_fixable": False,
        "performance_impact": "minimal",
        "related_rules": ["IO.001", "IO.002", "SC.002", "SC.003", "SC.004"],
    }
