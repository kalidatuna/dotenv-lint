"""Lint rules applied to parsed .env files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from .parser import ParseResult

ERROR = "error"
WARNING = "warning"
RULE_DESCRIPTIONS = {
    "E001": "Invalid assignment syntax",
    "E002": "Invalid variable name",
    "E003": "Duplicate variable name",
    "E004": "Variable missing from the input but present in the example",
    "W001": "Empty unquoted value",
    "W002": "Whitespace in an unquoted value",
    "W003": "Variable absent from the example",
}
RULE_CODES = frozenset(RULE_DESCRIPTIONS)

KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class Issue:
    code: str
    severity: str
    line: int
    message: str
    key: Optional[str] = None


def check(result: ParseResult) -> List[Issue]:
    """Run every single-file rule and return issues sorted by line."""
    issues: List[Issue] = []
    for err in result.errors:
        issues.append(Issue("E001", ERROR, err.line, err.message))
    issues.extend(_invalid_keys(result))
    issues.extend(_duplicate_keys(result))
    issues.extend(_empty_values(result))
    issues.extend(_unquoted_whitespace(result))
    return sorted(issues, key=lambda i: (i.line, i.code))


def _invalid_keys(result: ParseResult) -> List[Issue]:
    return [
        Issue("E002", ERROR, e.line, f"invalid key name {e.key!r}", e.key)
        for e in result.entries
        if not KEY_PATTERN.match(e.key)
    ]


def _duplicate_keys(result: ParseResult) -> List[Issue]:
    first_seen = {}
    issues = []
    for e in result.entries:
        if e.key in first_seen:
            msg = f"duplicate key {e.key!r} (first defined on line {first_seen[e.key]})"
            issues.append(Issue("E003", ERROR, e.line, msg, e.key))
        else:
            first_seen[e.key] = e.line
    return issues


def _empty_values(result: ParseResult) -> List[Issue]:
    return [
        Issue("W001", WARNING, e.line, f"{e.key} has an empty value", e.key)
        for e in result.entries
        if e.value == "" and e.quote is None
    ]


def _unquoted_whitespace(result: ParseResult) -> List[Issue]:
    """Shells split unquoted values on whitespace, so `source .env` breaks."""
    return [
        Issue("W002", WARNING, e.line, f"{e.key} value contains whitespace; wrap it in quotes", e.key)
        for e in result.entries
        if e.quote is None and any(ch.isspace() for ch in e.value)
    ]


def compare(env: ParseResult, example: ParseResult) -> List[Issue]:
    """Report keys missing from env (E004) and keys not documented in example (W003)."""
    env_keys = {e.key: e.line for e in env.entries}
    example_keys = {e.key for e in example.entries}
    issues = [
        Issue("E004", ERROR, 0, f"{key} is defined in the example but missing", key)
        for key in sorted(example_keys - set(env_keys))
    ]
    issues.extend(
        Issue("W003", WARNING, line, f"{key} is not listed in the example", key)
        for key, line in env_keys.items()
        if key not in example_keys
    )
    return sorted(issues, key=lambda i: (i.line, i.code))
