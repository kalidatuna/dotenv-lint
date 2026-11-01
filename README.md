# dotenv-lint

Zero-dependency linter for `.env` files. Catches syntax errors, duplicate keys,
and drift between `.env` and `.env.example` before they reach production.

- Pure Python standard library, no runtime dependencies
- Never evaluates or expands values
- Text output for humans, JSON for tooling
- Exit codes that work in CI and pre-commit hooks

## Install

```bash
pip install git+https://github.com/kalidatuna/dotenv-lint
```

Or run from a checkout without installing:

```bash
python -m dotenv_lint .env
```

## Usage

```bash
dotenv-lint                         # lint ./.env
dotenv-lint .env .env.local         # lint several files
dotenv-lint -e .env.example         # also compare keys with the example
dotenv-lint --strict                # fail on warnings too
dotenv-lint --ignore W001,W003      # skip specific rules
dotenv-lint --format json           # machine-readable output
dotenv-lint --quiet                 # exit status without text diagnostics
cat .env | dotenv-lint -            # read standard input
```

Example output:

```text
.env:0: E004 error: REDIS_URL is defined in the example but missing
.env:4: E003 error: duplicate key 'PORT' (first defined on line 2)
.env:7: W002 warning: GREETING value contains whitespace; wrap it in quotes
```

Use `-` as the input path or `--example -` to read standard input. Stdin can
supply one side of a comparison, never both. Repeated identical input paths
are checked once, in their first specified order.

`--quiet` suppresses text lint findings while preserving the exit code. Input
and argument errors still go to stderr. It cannot be combined with JSON output.
Unknown codes passed to `--ignore` are argument errors, including typos.

Line `0` means the issue concerns the whole file rather than one line.

## pre-commit

```yaml
repos:
  - repo: https://github.com/kalidatuna/dotenv-lint
    rev: v0.1.0
    hooks:
      - id: dotenv-lint
```

The hook runs on files named `.env` or `.env.*`. Most projects do not commit
real `.env` files, so this is mainly useful for `.env.example` and templates.

## Rules

| Code | Severity | Description |
|------|----------|-------------|
| E001 | error    | Line cannot be parsed (missing `=`, unterminated quote, text after closing quote) |
| E002 | error    | Key is not a valid variable name (`[A-Za-z_][A-Za-z0-9_]*`) |
| E003 | error    | Key is defined more than once |
| E004 | error    | Key exists in the example file but not in the linted file |
| W001 | warning  | Value is empty and unquoted (use `KEY=""` if empty is intended) |
| W002 | warning  | Unquoted value contains whitespace |
| W003 | warning  | Key is not listed in the example file |

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | No errors (warnings allowed unless `--strict`) |
| 1    | At least one error, or any warning with `--strict` |
| 2    | Invalid arguments, unreadable or invalid UTF-8 input, or malformed example file |

## Supported syntax

```sh
# comments and blank lines are ignored
export API_URL=https://api.example.com   # `export` prefix is allowed
PORT=8080 # inline comment after whitespace
COLOR=#ff0000                            # '#' without a preceding space is kept
NAME="double quoted, supports \n \t \" \\ escapes"
RAW='single quoted, taken literally'
```

Multi-line values are not supported yet.

## Development

```bash
python -m unittest -v
```

## License

MIT
