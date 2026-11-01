import unittest
from dotenv_lint.parser import parse
from dotenv_lint.rules import check

class NulTests(unittest.TestCase):
    def test_nul_in_assignment_is_a_syntax_error_without_value_disclosure(self):
        for text in ('TOKEN=secret\0value', 'TO\0KEN=secret', 'TOKEN="secret\0value"'):
            with self.subTest(text=text):
                result = parse(text + '\nSAFE=1')
                self.assertEqual([e.key for e in result.entries], ['SAFE'])
                issues = check(result)
                self.assertEqual([(i.code, i.line) for i in issues], [('E001', 1)])
                self.assertNotIn('secret', issues[0].message)

    def test_literal_backslash_zero_is_preserved(self):
        self.assertEqual(parse(r'TOKEN=abc\0def').entries[0].value, r'abc\0def')
