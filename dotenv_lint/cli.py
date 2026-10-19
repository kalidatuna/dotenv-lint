"""Command-line interface for dotenv-lint."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from . import __version__
from .parser import parse
from .rules import ERROR, check, compare


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="dotenv-lint", description="Lint .env files.")
    ap.add_argument("files", nargs="*", default=[".env"], help="files to lint; - reads stdin (default: .env)")
    ap.add_argument("-e", "--example", help="compare keys against this example file")
    ap.add_argument("-f", "--format", choices=["text", "json"], default="text")
    ap.add_argument("-q", "--quiet", action="store_true", help="suppress text diagnostics; keep exit status")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument(
        "--ignore",
        default="",
        metavar="CODES",
        help="comma-separated rule codes to skip, e.g. W001,W003",
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return ap


RULE_CODES = frozenset({"E001", "E002", "E003", "E004", "W001", "W002", "W003"})


def main(argv: Optional[List[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    ignored = {c.strip().upper() for c in args.ignore.split(",") if c.strip()}
    unknown = ignored - RULE_CODES
    if unknown:
        ap.error("unknown rule code(s): " + ", ".join(sorted(unknown)))
    if args.files.count("-") + int(args.example == "-") > 1:
        ap.error("stdin may only be read once")
    try:
        example = parse(_read(args.example)) if args.example else None
        texts = [(name, _read(name)) for name in args.files]
    except UnicodeError:
        print("dotenv-lint: input is not valid UTF-8", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"dotenv-lint: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 2

    failed = False
    report = []
    if example is not None:
        example_issues = [i for i in check(example) if i.severity == ERROR and i.code not in ignored]
        failed = bool(example_issues)
        for issue in example_issues:
            if args.format == "json":
                report.append(dict(asdict(issue), file=args.example))
            elif not args.quiet:
                print(f"{args.example}:{issue.line}: {issue.code} {issue.severity}: {issue.message}")
    for name, text in texts:
        result = parse(text)
        issues = check(result)
        if example is not None:
            issues = sorted(issues + compare(result, example), key=lambda i: (i.line, i.code))
        issues = [i for i in issues if i.code not in ignored]
        if args.format == "json":
            report.extend(dict(asdict(i), file=name) for i in issues)
        elif not args.quiet:
            for issue in issues:
                print(f"{name}:{issue.line}: {issue.code} {issue.severity}: {issue.message}")
        failed = failed or any(args.strict or i.severity == ERROR for i in issues)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    return 1 if failed else 0


def _read(name: str) -> str:
    if name == "-":
        return sys.stdin.read().removeprefix("\ufeff")
    # utf-8-sig drops the BOM that some Windows editors prepend.
    return Path(name).read_text(encoding="utf-8-sig")


if __name__ == "__main__":
    sys.exit(main())
