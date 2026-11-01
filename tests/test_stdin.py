import unittest
import contextlib
import io
import json
from unittest import mock
from dotenv_lint.cli import main


class RegressionTest(unittest.TestCase):
    def test_stdin_linting(self):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("A=1\nA=2\n")), contextlib.redirect_stdout(out):
            self.assertEqual(main(["-", "-f", "json"]), 1)
        self.assertEqual(json.loads(out.getvalue())[0]["file"], "-")

    def test_stdin_cannot_supply_both_inputs(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            main(["-", "--example", "-"])
        self.assertEqual(raised.exception.code, 2)
