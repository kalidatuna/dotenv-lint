import unittest
from dotenv_lint.parser import parse


class RegressionTest(unittest.TestCase):
    def test_comment_only_value_is_empty(self):
        for text in ("A= # comment", "A=\t# comment"):
            self.assertEqual(parse(text).entries[0].value, "")

    def test_hash_without_whitespace_is_a_value(self):
        self.assertEqual(parse("COLOR=#fff").entries[0].value, "#fff")
