# Changelog

## 0.1.0 - 2026-10-11

First release.

- Parser for `KEY=VALUE` lines with `export` prefix, inline comments,
  single quotes, and double quotes with `\n \t \r \" \\` escapes
- Rules E001-E004 and W001-W003 (see README)
- Comparison against an example file with `--example`
- `--strict`, `--ignore`, and `--format json` options
- UTF-8 BOM and CRLF line endings accepted
- pre-commit hook definition
