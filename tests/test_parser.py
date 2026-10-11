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


if __name__ == "__main__":
    unittest.main()
