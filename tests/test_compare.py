import unittest

from dotenv_lint.parser import parse
from dotenv_lint.rules import compare


class CompareTest(unittest.TestCase):
    def test_matching_keys(self):
        self.assertEqual(compare(parse("A=1\nB=2"), parse("B=\nA=")), [])

    def test_missing_key_is_error(self):
        issues = compare(parse("A=1"), parse("A=\nB=\n"))
        self.assertEqual([(i.code, i.key, i.line) for i in issues], [("E004", "B", 0)])

    def test_extra_key_is_warning_with_line(self):
        issues = compare(parse("A=1\nSECRET=x"), parse("A="))
        self.assertEqual([(i.code, i.key, i.line) for i in issues], [("W003", "SECRET", 2)])


if __name__ == "__main__":
    unittest.main()
