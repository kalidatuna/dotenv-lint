"""Command-line interface for dotenv-lint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .parser import parse
from .rules import ERROR, check, compare


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="dotenv-lint", description="Lint .env files.")
    ap.add_argument("files", nargs="*", default=[".env"], help="files to lint (default: .env)")
    ap.add_argument("-e", "--example", help="compare keys against this example file")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        example = parse(_read(args.example)) if args.example else None
        texts = [(name, _read(name)) for name in args.files]
    except OSError as exc:
        print(f"dotenv-lint: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 2

    failed = False
    for name, text in texts:
        result = parse(text)
        issues = check(result)
        if example is not None:
            issues = sorted(issues + compare(result, example), key=lambda i: (i.line, i.code))
        for issue in issues:
            print(f"{name}:{issue.line}: {issue.code} {issue.severity}: {issue.message}")
        failed = failed or any(i.severity == ERROR for i in issues)
    return 1 if failed else 0


def _read(name: str) -> str:
    return Path(name).read_text(encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
