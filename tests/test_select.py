import contextlib
import io
import unittest
from unittest.mock import patch
from dotenv_lint.cli import main

class SelectTests(unittest.TestCase):
    def run_cli(self, *options):
        output = io.StringIO()
        with patch('sys.stdin', io.StringIO('A=\nA=2\n')), contextlib.redirect_stdout(output):
            code = main(['-', *options])
        return code, output.getvalue()

    def test_select_limits_diagnostics_and_failure_status(self):
        code, output = self.run_cli('--select', ' w001 ')
        self.assertEqual(code, 0)
        self.assertIn('W001', output)
        self.assertNotIn('E003', output)
        self.assertEqual(self.run_cli('--select', 'W001', '--strict')[0], 1)

    def test_ignore_takes_precedence(self):
        self.assertEqual(self.run_cli('--select', 'W001', '--ignore', 'W001'), (0, ''))

    def test_invalid_or_empty_selection_is_an_argument_error(self):
        for value in ('', ' , ', 'E999'):
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main(['--select', value])
            self.assertEqual(error.exception.code, 2)
