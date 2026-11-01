# Parsing behavior

`parse(text)` returns entries and syntax errors without reading files, evaluating
shell commands, expanding variables, or changing the process environment.

- An optional leading UTF-8 BOM is ignored. A BOM inside a value is preserved.
- LF and CRLF separate physical lines. Unicode separators inside quoted values
  remain content. Actual multiline quoted values are unsupported.
- `export` followed by a space or tab is accepted. `export=value` is an ordinary
  key named `export`.
- `A= # comment` has an empty value. `COLOR=#fff` preserves the hash value.
- Single quotes preserve literal text. Double quotes decode the documented
  escapes; unknown escapes keep their backslash.
- Text after a closing quote must be whitespace or a comment.

Assignments containing actual NUL bytes are syntax errors (E001). A literal
backslash followed by `0` remains text; it is not a supported escape.

The CLI reads files and piped input as UTF-8 with an optional BOM, independently
of the Python stream's locale encoding. Invalid encoding returns 2. Invalid
filesystem paths also return 2 without a traceback.
Comparison templates must have valid syntax, valid key names, and unique keys.
Empty placeholder values in templates are allowed. Diagnostics include key names
and line numbers, without copying values.
