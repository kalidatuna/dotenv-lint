import unittest
from dotenv_lint.parser import parse
from dotenv_lint.rules import check


class RegressionTest(unittest.TestCase):
    def test_shell_syntax_and_variable_references_remain_literal(self):
        values = ["$(touch sentinel)", "`touch sentinel`", "${HOME}", "$HOME"]
        for value in values:
            with self.subTest(value=value):
                self.assertEqual(parse("KEY=" + value).entries[0].value, value)

    def test_diagnostics_do_not_include_secret_values(self):
        secret = "example-sensitive-token"
        result = parse("TOKEN=" + secret + "\nTOKEN=" + secret + "\n")
        self.assertTrue(check(result))
        self.assertTrue(all(secret not in issue.message for issue in check(result)))
