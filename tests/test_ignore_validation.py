import unittest
import contextlib
import io
from dotenv_lint.cli import main


class RegressionTest(unittest.TestCase):
    def test_unknown_ignore_code_fails_before_reading_files(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as raised:
            main(["missing.env", "--ignore", "W999"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("unknown rule codes: W999", err.getvalue())
