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
from .rules import ERROR, RULE_CODES, RULE_DESCRIPTIONS, check, compare


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="dotenv-lint", description="Lint .env files.")
    ap.add_argument("files", nargs="*", default=[".env"], help="files to lint (default: .env)")
    ap.add_argument("-e", "--example", help="compare keys against this example file")
    ap.add_argument("-f", "--format", choices=["text", "json", "jsonl"], default="text")
    ap.add_argument("-q", "--quiet", action="store_true", help="suppress text diagnostics; keep exit status")
    ap.add_argument("--select", metavar="CODES", help="only report these comma-separated rule codes")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument(
        "--ignore",
        default="",
        metavar="CODES",
        help="comma-separated rule codes to skip, e.g. W001,W003",
    )
    ap.add_argument("--list-rules", action="store_true", help="list supported rules without reading inputs")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    ignored = {c.strip().upper() for c in args.ignore.split(",") if c.strip()}
    if args.quiet and args.format != "text":
        ap.error("--quiet cannot be combined with machine-readable output")
    selected = RULE_CODES if args.select is None else {
        c.strip().upper() for c in args.select.split(",") if c.strip()
    }
    if not selected:
        ap.error("--select requires at least one rule code")
    unknown = (ignored | selected) - RULE_CODES
    if unknown:
        ap.error("unknown rule codes: " + ", ".join(sorted(unknown)))
    if args.list_rules:
        rules = [dict(code=code, severity="error" if code.startswith("E") else "warning",
                      description=RULE_DESCRIPTIONS[code]) for code in sorted(RULE_CODES)]
        if args.format == "json":
            print(json.dumps(rules, indent=2))
        elif args.format == "jsonl":
            for rule in rules:
                print(json.dumps(rule))
        else:
            for rule in rules:
                print(f"{rule['code']} {rule['severity']}: {rule['description']}")
        return 0
    if args.example == "-" and "-" in args.files:
        ap.error("stdin cannot be both an input file and the example")
    try:
        example = parse(_read(args.example)) if args.example else None
        texts = [(name, _read(name)) for name in dict.fromkeys(args.files)]
    except UnicodeError:
        print("dotenv-lint: input is not valid UTF-8", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"dotenv-lint: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 2
    except ValueError:
        print("dotenv-lint: invalid input path", file=sys.stderr)
        return 2

    if example is not None:
        invalid = [issue for issue in check(example) if issue.severity == ERROR]
        if invalid:
            for issue in invalid:
                print(f"{args.example}:{issue.line}: {issue.code} error: {issue.message}", file=sys.stderr)
            return 2

    failed = False
    report = []
    for name, text in texts:
        result = parse(text)
        issues = check(result)
        if example is not None:
            issues = sorted(issues + compare(result, example), key=lambda i: (i.line, i.code))
        issues = [i for i in issues if i.code in selected and i.code not in ignored]
        if args.format == "json":
            report.extend(dict(asdict(i), file=name) for i in issues)
        elif args.format == "jsonl":
            for issue in issues:
                print(json.dumps(dict(asdict(issue), file=name)))
        elif not args.quiet:
            for issue in issues:
                print(f"{name}:{issue.line}: {issue.code} {issue.severity}: {issue.message}")
        failed = failed or any(args.strict or i.severity == ERROR for i in issues)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    return 1 if failed else 0


def _read(name: str) -> str:
    if name == "-":
        # Decode the original bytes, independent of locale or PYTHONIOENCODING.
        # String-only streams remain supported by callers embedding the CLI.
        if hasattr(sys.stdin, "buffer"):
            return sys.stdin.buffer.read().decode("utf-8-sig")
        return sys.stdin.read()
    # utf-8-sig drops the BOM that some Windows editors prepend.
    return Path(name).read_text(encoding="utf-8-sig")


if __name__ == "__main__":
    sys.exit(main())
