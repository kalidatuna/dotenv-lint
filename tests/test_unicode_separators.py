import unittest
from dotenv_lint.parser import parse


class RegressionTest(unittest.TestCase):
    def test_unicode_separators_are_value_content(self):
        for separator in ("\u2028", "\u2029", "\x85", "\v", "\f"):
            with self.subTest(separator=repr(separator)):
                result = parse('A="left' + separator + 'right"\nB=2\n')
                self.assertEqual(result.errors, [])
                self.assertEqual(result.entries[0].value, "left" + separator + "right")
                self.assertEqual(result.entries[1].line, 2)
