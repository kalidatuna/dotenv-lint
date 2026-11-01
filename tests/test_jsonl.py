import contextlib
import io
import json
import unittest
from unittest.mock import patch
from dotenv_lint.cli import main

class JsonLinesTests(unittest.TestCase):
    def run_cli(self, text, *options):
        output = io.StringIO()
        with patch('sys.stdin', io.StringIO(text)), contextlib.redirect_stdout(output):
            code = main(['-', '-f', 'jsonl', *options])
        return code, output.getvalue()

    def test_each_diagnostic_is_one_json_record(self):
        code, output = self.run_cli('A=\nA=2\n')
        self.assertEqual(code, 1)
        records = [json.loads(line) for line in output.splitlines()]
        self.assertEqual([r['code'] for r in records], ['W001', 'E003'])
        self.assertTrue(all(r['file'] == '-' and 'value' not in r for r in records))

    def test_clean_input_emits_no_records(self):
        self.assertEqual(self.run_cli('A=1'), (0, ''))

    def test_filters_apply_before_serialization(self):
        code, output = self.run_cli('A=\nA=2', '--select', 'W001')
        self.assertEqual(code, 0)
        self.assertEqual(len(output.splitlines()), 1)
        self.assertEqual(json.loads(output)['code'], 'W001')

    def test_rule_inventory_supports_json_lines(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(['--list-rules', '-f', 'jsonl']), 0)
        self.assertEqual(len([json.loads(line) for line in output.getvalue().splitlines()]), 7)

    def test_quiet_rejects_json_lines(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(['--quiet', '-f', 'jsonl'])
        self.assertEqual(error.exception.code, 2)
