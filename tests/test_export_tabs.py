import unittest
from dotenv_lint.parser import parse


class RegressionTest(unittest.TestCase):
    def test_tabbed_export_prefix(self):
        result = parse("export\tPORT=8080")
        self.assertEqual(result.entries[0].key, "PORT")
        self.assertEqual(result.errors, [])

    def test_export_named_key_is_preserved(self):
        self.assertEqual(parse("export=value").entries[0].key, "export")
