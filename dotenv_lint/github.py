"""Render lint findings as GitHub Actions workflow annotations."""

from .rules import Issue


def _escape(value: str, *, property_value: bool = False) -> str:
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if property_value:
        value = value.replace(":", "%3A").replace(",", "%2C")
    return value


def annotation(filename: str, issue: Issue) -> str:
    """Return one workflow command, escaping data separately from properties."""
    properties = [f"file={_escape(filename, property_value=True)}"]
    if issue.line > 0:
        properties.append(f"line={issue.line}")
    properties.append(f"title={_escape(issue.code, property_value=True)}")
    return f"::{issue.severity} {','.join(properties)}::{_escape(issue.message)}"
