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
```

Example output:

```text
.env:0: E004 error: REDIS_URL is defined in the example but missing
.env:4: E003 error: duplicate key 'PORT' (first defined on line 2)
.env:7: W002 warning: GREETING value contains whitespace; wrap it in quotes
```

Line `0` means the issue concerns the whole file rather than one line.

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
| 2    | A file could not be read |

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
