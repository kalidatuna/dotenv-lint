import unittest

from dotenv_lint.parser import parse
from dotenv_lint.rules import check


def codes(text):
    return [i.code for i in check(parse(text))]


class RulesTest(unittest.TestCase):
    def test_clean_file_has_no_issues(self):
        self.assertEqual(codes("A=1\nB_2=x\n_C=y\n"), [])

    def test_parse_errors_become_e001(self):
        self.assertEqual(codes("NOPE\n"), ["E001"])

    def test_invalid_key_names(self):
        self.assertEqual(codes("1A=x\nA-B=x\nA B=x\n=x\n"), ["E002"] * 4)

    def test_duplicate_key_reported_on_later_lines(self):
        issues = check(parse("A=1\nB=2\nA=3\nA=4\n"))
        self.assertEqual([(i.code, i.line) for i in issues], [("E003", 3), ("E003", 4)])
        self.assertIn("line 1", issues[0].message)


if __name__ == "__main__":
    unittest.main()
