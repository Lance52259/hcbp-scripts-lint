#!/usr/bin/env python3
"""
SC.001 - Array Index Access Safety Check

Validates that array index access operations use safe wrappers to prevent
index out of bounds errors in specific scenarios:

1. Data source list attribute references
2. Collection-typed input variables (list / set / tuple)
3. Risky local values (for-expression results or direct data.* aliases)

Safe same-line wrappers: try(), element(), one(), can(), and length(...) > 0 ? ... : ...

Author: Lance
License: Apache 2.0
"""

import re
import os
from typing import Callable, Dict, Optional, List, Tuple, Set


_DATA_ATTR_RE = re.compile(r'data\.\w+\.\w+\.\w+')
_FOR_EXPR_RE = re.compile(r'\[for\b|\bfor\s+\w+\s+in\b')
_COLLECTION_TYPE_RE = re.compile(r'type\s*=\s*(?:list|set|tuple)\s*\(')
_SAFE_WRAP_FUNCS = ('try', 'element', 'one', 'can')


def check_sc001_array_index_safety(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Check for unsafe array index access in Terraform files.
    """
    file_dir = os.path.dirname(file_path)
    list_variables = _extract_list_variables_from_directory(file_dir)
    risky_locals = _extract_risky_locals_from_directory(file_dir)

    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        if not line.strip() or line.strip().startswith('#'):
            continue

        unsafe_patterns = []
        unsafe_patterns.extend(_find_data_source_index_access(line))
        unsafe_patterns.extend(_find_variable_index_access(line, list_variables))
        unsafe_patterns.extend(_find_local_index_access(line, risky_locals))

        for pattern, start_pos, suggestion, scenario in unsafe_patterns:
            if _is_safely_wrapped(line, start_pos):
                continue
            error_msg = (
                f"Unsafe array index access detected in {scenario}: '{pattern}'. "
                f"Use try()/element()/one()/can() or a length guard to prevent "
                f"index out of bounds errors. Suggestion: {suggestion}"
            )
            log_error_func(file_path, "SC.001", error_msg, line_num)


def _extract_list_variables_from_directory(directory: str) -> Set[str]:
    """Extract variable names typed as list/set/tuple from sibling *.tf files."""
    list_variables: Set[str] = set()
    if not os.path.exists(directory):
        return list_variables

    for filename in os.listdir(directory):
        if not filename.endswith('.tf'):
            continue
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as handle:
                list_variables.update(_extract_list_variables(handle.read()))
        except (OSError, UnicodeDecodeError):
            continue
    return list_variables


def _extract_list_variables(content: str) -> Set[str]:
    """Extract variable names defined as list, set, or tuple types."""
    list_variables: Set[str] = set()
    in_variable_block = False
    current_variable: Optional[str] = None
    var_header = re.compile(
        r'variable\s+(?:"([^"]+)"|\'([^\']+)\'|([a-zA-Z_][a-zA-Z0-9_]*))\s*\{'
    )

    for line in content.split('\n'):
        stripped = line.strip()
        variable_match = var_header.match(stripped)
        if variable_match:
            current_variable = (
                variable_match.group(1)
                or variable_match.group(2)
                or variable_match.group(3)
            )
            in_variable_block = True
            continue

        if in_variable_block and stripped == '}':
            in_variable_block = False
            current_variable = None
            continue

        if in_variable_block and current_variable and _COLLECTION_TYPE_RE.match(stripped):
            list_variables.add(current_variable)

    return list_variables


def _extract_risky_locals_from_directory(directory: str) -> Set[str]:
    """Collect local names whose RHS is a for-expression or a data.* attribute."""
    risky: Set[str] = set()
    if not os.path.exists(directory):
        return risky

    for filename in os.listdir(directory):
        if not filename.endswith('.tf'):
            continue
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as handle:
                risky.update(_extract_risky_locals(handle.read()))
        except (OSError, UnicodeDecodeError):
            continue
    return risky


def _extract_risky_locals(content: str) -> Set[str]:
    """Parse locals blocks and return names whose RHS is considered risky."""
    risky: Set[str] = set()
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        if re.match(r'locals\s*\{', lines[i].strip()):
            brace_depth = lines[i].count('{') - lines[i].count('}')
            i += 1
            assignments: Dict[str, List[str]] = {}
            current_name: Optional[str] = None

            while i < len(lines) and brace_depth > 0:
                line = lines[i]
                stripped = line.strip()
                brace_depth += line.count('{') - line.count('}')

                assign_match = re.match(
                    r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$',
                    stripped,
                )
                if assign_match and brace_depth >= 1:
                    current_name = assign_match.group(1)
                    assignments[current_name] = [assign_match.group(2)]
                elif current_name is not None:
                    assignments[current_name].append(stripped)

                i += 1

            for name, rhs_parts in assignments.items():
                rhs = ' '.join(rhs_parts)
                if _is_risky_local_rhs(rhs):
                    risky.add(name)
            continue
        i += 1

    return risky


def _is_risky_local_rhs(rhs: str) -> bool:
    """True when local RHS is a for-expression result or a direct data.* attribute."""
    if _FOR_EXPR_RE.search(rhs):
        return True
    if _DATA_ATTR_RE.search(rhs):
        return True
    return False


def _find_data_source_index_access(line: str) -> List[Tuple[str, int, str, str]]:
    """Find data source array index access patterns."""
    patterns = []
    data_pattern = r'data\.[\w_]+\.[\w_]+\.[\w_]+\[\d+\](?:\.[\w_]+)*'

    for match in re.finditer(data_pattern, line):
        pattern = match.group(0)
        suggestion = f'try({pattern}, "default_value")'
        patterns.append((pattern, match.start(), suggestion, "data source list attribute"))
    return patterns


def _find_variable_index_access(line: str, list_variables: Set[str]) -> List[Tuple[str, int, str, str]]:
    """Find collection-typed input variable index access patterns."""
    patterns = []
    var_pattern = r'var\.([\w_]+)\[\d+\](?:\.[\w_]+)*'

    for match in re.finditer(var_pattern, line):
        variable_name = match.group(1)
        if variable_name not in list_variables:
            continue
        pattern = match.group(0)
        suggestion = f'try({pattern}, "default_value")'
        patterns.append((pattern, match.start(), suggestion, "optional list parameter"))
    return patterns


def _find_local_index_access(line: str, risky_locals: Set[str]) -> List[Tuple[str, int, str, str]]:
    """Find index access on locals attributed as for-results or data aliases."""
    patterns = []
    local_pattern = r'local\.([\w_]+)\[\d+\](?:\.[\w_]+)*'

    for match in re.finditer(local_pattern, line):
        local_name = match.group(1)
        if local_name not in risky_locals:
            continue
        pattern = match.group(0)
        suggestion = f'try({pattern}, "default_value")'
        scenario = "for expression / data-alias local"
        patterns.append((pattern, match.start(), suggestion, scenario))
    return patterns


def _is_safely_wrapped(line: str, index_pos: int) -> bool:
    """True if index access sits inside try/element/one/can or a length ternary guard."""
    if _is_wrapped_in_functions(line, index_pos, _SAFE_WRAP_FUNCS):
        return True
    if _is_length_guarded(line, index_pos):
        return True
    return False


def _is_wrapped_in_functions(line: str, index_pos: int, func_names: Tuple[str, ...]) -> bool:
    """Check whether index_pos is inside one of the given call parentheses."""
    line_before = line[:index_pos]
    for func_name in func_names:
        pattern = rf'{func_name}\s*\('
        for match in re.finditer(pattern, line_before):
            paren_start = match.end() - 1
            paren_count = 1
            pos = paren_start + 1
            while pos < len(line) and paren_count > 0:
                if line[pos] == '(':
                    paren_count += 1
                elif line[pos] == ')':
                    paren_count -= 1
                pos += 1
            if paren_count == 0 and pos > index_pos:
                return True
    return False


def _is_length_guarded(line: str, index_pos: int) -> bool:
    """Heuristic: same-line `length(...) > 0 ? ...[N] : ...`."""
    before = line[:index_pos]
    return bool(re.search(r'length\s*\(.+\)\s*>\s*0\s*\?', before))


def get_rule_description() -> dict:
    """Get the rule description for SC.001."""
    return {
        "rule_id": "SC.001",
        "title": "Array Index Access Safety Check",
        "category": "Security Code",
        "severity": "warning",
        "description": (
            "Validates that risky array index access uses try()/element()/one()/can() "
            "or a same-line length guard. Flags data.*[N], collection-typed var.*[N], "
            "and locals derived from for-expressions or data.* aliases. Literal local "
            "lists are not flagged."
        ),
        "rationale": (
            "Array index access can fail when data sources return empty results, "
            "variables are empty collections, or for expressions produce empty results"
        ),
        "scope": ["data_source_access", "variable_access", "for_expression_access"],
        "implementation": "modular",
        "version": "2.1.0",
        "scenarios": {
            "data_source": "Data source list attribute references that might return empty results",
            "input_variables": "Collection-typed input variable element references",
            "for_expressions": "Locals attributed to for-expressions or data.* aliases",
        },
        "examples": {
            "valid": [
                'flavor_id = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")',
                'subnet_id = try(var.subnet_ids[0], "default_subnet")',
                'zone = local.zones[0]  # locals { zones = ["cn-north-1a"] }',
                'item = element(var.items, 0)',
            ],
            "invalid": [
                'flavor_id = data.huaweicloud_compute_flavors.test.flavors[0].id',
                'subnet_id = var.subnet_ids[0]',
                'first = local.filtered[0]  # locals { filtered = [for x in var.x : x] }',
            ],
        },
        "fix_suggestions": [
            "Wrap risky index access in try()/element()/one()/can()",
            "Use length(list) > 0 ? list[0] : default on the same line",
            "Prefer element() when a default index into a list is intended",
        ],
    }
