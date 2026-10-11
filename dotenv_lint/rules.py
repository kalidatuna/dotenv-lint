"""Lint rules applied to parsed .env files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from .parser import ParseResult

ERROR = "error"
WARNING = "warning"

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
