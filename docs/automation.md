# Automating dotenv checks

Run from the repository root with explicit input and template paths:

```sh
dotenv-lint .env --example .env.example --strict
```

The command returns 0 on success, 1 for lint failures, or 2 when the inputs or
arguments cannot be used. Warnings fail only with `--strict`. Choose `--quiet`
when an automation only needs the exit status; argument and input failures still
appear on stderr.

To check only assignment syntax and duplicate keys:

```sh
dotenv-lint .env --select E001,E003
```

To collect individual diagnostic records:

```sh
dotenv-lint .env --format jsonl > diagnostics.jsonl
```

Preserve the command's exit status when using shell pipelines. A downstream
consumer can succeed even when the linter returned 1 or 2. JSON Lines has no
records for clean files, while `--format json` prints an empty array.

Input paths are deduplicated by their exact spelling, not by filesystem identity.
Use `--` before a filename beginning with a hyphen:

```sh
dotenv-lint -- -production.env
```

To read configuration from another process, use `dotenv-lint -`. Stdin can also
provide the example with `--example -`, but cannot supply both sides of the same
comparison. The linter reads values without evaluating or expanding them.
