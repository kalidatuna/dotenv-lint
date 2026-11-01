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
    for lineno, raw in enumerate(text.removeprefix("\ufeff").split("\n"), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\0" in line:
            result.errors.append(ParseError(lineno, "NUL bytes are not allowed in assignments"))
            continue
        if "=" not in line:
            result.errors.append(ParseError(lineno, "expected KEY=VALUE"))
            continue
        if line.startswith(("export ", "export\t")):
            line = line[len("export ") :].lstrip()
        key, rest = line.split("=", 1)
        # Strip comments before trimming assignment whitespace.
        if rest.lstrip().startswith("#") and rest[:1] in (" ", "\t"):
            rest = ""
        rest = rest.strip()
        try:
            value, quote = _parse_value(rest)
        except ValueError as exc:
            result.errors.append(ParseError(lineno, str(exc)))
            continue
        result.entries.append(Entry(key.strip(), value, lineno, quote))
    return result


_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}


def _parse_value(rest: str):
    """Return (value, quote_char) for the text after '='."""
    if not rest or rest[0] not in ("'", '"'):
        return _strip_inline_comment(rest), None
    quote = rest[0]
    chars = []
    i = 1
    while i < len(rest):
        ch = rest[i]
        if quote == '"' and ch == "\\" and i + 1 < len(rest):
            nxt = rest[i + 1]
            chars.append(_ESCAPES.get(nxt, "\\" + nxt))
            i += 2
            continue
        if ch == quote:
            trailing = rest[i + 1 :].strip()
            if trailing and not trailing.startswith("#"):
                raise ValueError("unexpected text after closing quote")
            return "".join(chars), quote
        chars.append(ch)
        i += 1
    raise ValueError("unterminated quoted value")


def _strip_inline_comment(value: str) -> str:
    """Drop a ' #...' comment from an unquoted value; '#' without a space is kept."""
    for i, ch in enumerate(value):
        if ch == "#" and i > 0 and value[i - 1] in " \t":
            return value[:i].rstrip()
    return value
