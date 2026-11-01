import unittest
from dotenv_lint.parser import parse


class RegressionTest(unittest.TestCase):
    def test_direct_parser_accepts_bom(self):
        self.assertEqual(parse("\ufeffPORT=8080").entries[0].key, "PORT")

    def test_bom_inside_value_is_preserved(self):
        self.assertEqual(parse("A=x\ufeffy").entries[0].value, "x\ufeffy")
