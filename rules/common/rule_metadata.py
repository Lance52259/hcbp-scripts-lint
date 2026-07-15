"""
Normalize and validate rule description metadata (D5).

Canonical keys after normalize: id, name, description, category, severity.
Legacy aliases rule_id / title are preserved when present and mirrored when missing.
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple


REQUIRED_KEYS = ("id", "name", "description", "category", "severity")


def normalize_rule_description(
    raw: Dict[str, Any],
    rule_id: str,
    registry_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Return a copy of *raw* with stable ``id`` / ``name`` fields.

    Preference order for id: ``id`` → ``rule_id`` → registry *rule_id*.
    Preference order for name: ``name`` → ``title`` → *registry_name* → *rule_id*.
    """
    out = dict(raw)

    resolved_id = out.get("id") or out.get("rule_id") or rule_id
    resolved_name = (
        out.get("name")
        or out.get("title")
        or registry_name
        or rule_id
    )

    out["id"] = resolved_id
    out["name"] = resolved_name

    # Keep legacy aliases in sync for older consumers
    if "rule_id" in out or "title" in out:
        out.setdefault("rule_id", resolved_id)
        out.setdefault("title", resolved_name)

    return out


def validate_rule_description(
    raw: Dict[str, Any],
    rule_id: str = "",
) -> Tuple[bool, List[str]]:
    """
    Validate that required metadata keys are present and non-empty.

    Does not raise; intended for tests / CI assertions.
    """
    normalized = normalize_rule_description(raw, rule_id=rule_id or str(raw.get("id", "")))
    errors: List[str] = []
    for key in REQUIRED_KEYS:
        value = normalized.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"missing or empty required key: {key}")
    return (len(errors) == 0, errors)


def assert_rules_have_canonical_metadata(
    rule_infos: Iterable[Dict[str, Any]],
) -> None:
    """Raise AssertionError if any rule info lacks canonical metadata."""
    problems: List[str] = []
    for info in rule_infos:
        rule_id = str(info.get("id") or info.get("rule_id") or "?")
        ok, errors = validate_rule_description(info, rule_id=rule_id)
        if not ok:
            problems.append(f"{rule_id}: {', '.join(errors)}")
        if info.get("name") == "Unknown rule":
            problems.append(f"{rule_id}: name is Unknown rule")
    if problems:
        raise AssertionError("Rule metadata validation failed:\n" + "\n".join(problems))
