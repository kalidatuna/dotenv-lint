import unittest

from dotenv_lint.parser import parse


class ParseBasicsTest(unittest.TestCase):
    def test_simple_pairs(self):
        result = parse("A=1\nB=two\n")
        self.assertEqual([(e.key, e.value) for e in result.entries], [("A", "1"), ("B", "two")])
        self.assertEqual(result.errors, [])

    def test_skips_blank_lines_and_comments(self):
        result = parse("\n# comment\n   \nA=1\n")
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].line, 4)

    def test_missing_equals_is_error(self):
        result = parse("A=1\nNOT_A_PAIR\n")
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].line, 2)

    def test_value_may_contain_equals(self):
        result = parse("URL=postgres://u:p@h/db?a=b\n")
        self.assertEqual(result.entries[0].value, "postgres://u:p@h/db?a=b")

    def test_empty_value(self):
        result = parse("EMPTY=\n")
        self.assertEqual(result.entries[0].value, "")


class ParseQuotesTest(unittest.TestCase):
    def test_double_quotes_are_stripped(self):
        entry = parse('A="hello world"').entries[0]
        self.assertEqual(entry.value, "hello world")
        self.assertEqual(entry.quote, '"')

    def test_single_quotes_are_literal(self):
        entry = parse(r"A='a\nb'").entries[0]
        self.assertEqual(entry.value, r"a\nb")
        self.assertEqual(entry.quote, "'")

    def test_double_quote_escapes(self):
        entry = parse(r'A="line1\nline2 \"q\" \\"').entries[0]
        self.assertEqual(entry.value, 'line1\nline2 "q" \\')

    def test_unknown_escape_kept(self):
        entry = parse(r'A="\d"').entries[0]
        self.assertEqual(entry.value, r"\d")

    def test_unterminated_quote_is_error(self):
        result = parse('A="oops')
        self.assertEqual(result.entries, [])
        self.assertIn("unterminated", result.errors[0].message)

    def test_text_after_closing_quote_is_error(self):
        result = parse('A="x"y')
        self.assertIn("after closing quote", result.errors[0].message)

    def test_comment_after_closing_quote_is_allowed(self):
        result = parse('A="x # not a comment" # real comment')
        self.assertEqual(result.errors, [])
        self.assertEqual(result.entries[0].value, "x # not a comment")


class ParseExtrasTest(unittest.TestCase):
    def test_export_prefix(self):
        entry = parse("export API_KEY=abc").entries[0]
        self.assertEqual((entry.key, entry.value), ("API_KEY", "abc"))

    def test_inline_comment_on_unquoted_value(self):
        entry = parse("PORT=8080 # http port").entries[0]
        self.assertEqual(entry.value, "8080")

    def test_hash_without_space_is_part_of_value(self):
        entry = parse("COLOR=#ff0000").entries[0]
        self.assertEqual(entry.value, "#ff0000")
        entry = parse("URL=http://x/#frag").entries[0]
        self.assertEqual(entry.value, "http://x/#frag")

    def test_tab_after_export_prefix(self):
        entry = parse("export\tAPI_KEY=abc").entries[0]
        self.assertEqual((entry.key, entry.value), ("API_KEY", "abc"))
        self.assertEqual(parse("exported=1").entries[0].key, "exported")


if __name__ == "__main__":
    unittest.main()
