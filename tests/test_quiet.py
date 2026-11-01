import unittest
import contextlib
import io
from unittest import mock
from dotenv_lint.cli import main


class RegressionTest(unittest.TestCase):
    def test_quiet_preserves_failure_status(self):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("A=1\nA=2\n")), contextlib.redirect_stdout(out):
            self.assertEqual(main(["-", "--quiet"]), 1)
        self.assertEqual(out.getvalue(), "")

    def test_quiet_rejects_json(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(["--quiet", "--format", "json"])
