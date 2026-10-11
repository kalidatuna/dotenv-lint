"""Parse .env files into entries without evaluating them."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Entry:
    key: str
    value: str
    line: int
    quote: Optional[str] = None


@dataclass
class ParseError:
    line: int
    message: str


@dataclass
class ParseResult:
    entries: List[Entry] = field(default_factory=list)
    errors: List[ParseError] = field(default_factory=list)


def parse(text: str) -> ParseResult:
    """Parse the contents of a .env file."""
    result = ParseResult()
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            result.errors.append(ParseError(lineno, "expected KEY=VALUE"))
            continue
        key, value = line.split("=", 1)
        result.entries.append(Entry(key.strip(), value.strip(), lineno))
    return result
