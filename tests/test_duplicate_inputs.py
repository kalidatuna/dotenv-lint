import unittest
import contextlib
import io
import json
from unittest import mock
from dotenv_lint.cli import main


class RegressionTest(unittest.TestCase):
    def test_repeated_input_is_reported_once(self):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("A=\n")), contextlib.redirect_stdout(out):
            self.assertEqual(main(["-", "-", "--format", "json"]), 0)
        self.assertEqual(len(json.loads(out.getvalue())), 1)
