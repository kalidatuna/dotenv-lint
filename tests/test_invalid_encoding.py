import unittest
import contextlib
import io
import tempfile
from pathlib import Path
from dotenv_lint.cli import main


class RegressionTest(unittest.TestCase):
    def test_invalid_utf8_exits_two_without_traceback(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.env"
            path.write_bytes(b"KEY=\xff")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(main([str(path)]), 2)
            self.assertIn("UTF-8", err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())
