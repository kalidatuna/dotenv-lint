# Changelog

## Unreleased

- Accept tabbed `export` prefixes and BOM-prefixed direct parser input.
- Preserve Unicode separators in quoted values and parse comment-only values.
- Return input errors for invalid UTF-8 and malformed comparison templates.
- Validate ignored rule codes and deduplicate repeated input paths.
- Read stdin with `-` and add `--quiet` for text exit-status checks.
- Add regression tests for parser boundaries, literal values, secret-free
  diagnostics, and the executable module entry point.
- Document CLI input errors and exact parsing behavior.

## 0.1.0 - 2026-10-11

First release.

- Parser for `KEY=VALUE` lines with `export` prefix, inline comments,
  single quotes, and double quotes with `\n \t \r \" \\` escapes
- Rules E001-E004 and W001-W003 (see README)
- Comparison against an example file with `--example`
- `--strict`, `--ignore`, and `--format json` options
- UTF-8 BOM and CRLF line endings accepted
- pre-commit hook definition
