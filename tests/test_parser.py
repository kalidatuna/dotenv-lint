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


if __name__ == "__main__":
    unittest.main()
