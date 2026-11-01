import contextlib
import io
import json
import unittest
from unittest.mock import patch
from dotenv_lint.cli import main
from dotenv_lint.rules import RULE_CODES

class ListRulesTests(unittest.TestCase):
    def test_inventory_does_not_read_files(self):
        output = io.StringIO()
        with patch('dotenv_lint.cli._read', side_effect=AssertionError('must not read')), contextlib.redirect_stdout(output):
            self.assertEqual(main(['does-not-exist', '--list-rules', '-f', 'json']), 0)
        rules = json.loads(output.getvalue())
        self.assertEqual([r['code'] for r in rules], sorted(RULE_CODES))
        self.assertTrue(all(r['severity'] in ('error', 'warning') and r['description'] for r in rules))
