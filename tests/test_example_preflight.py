import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dotenv_lint.cli import main


class ExamplePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.example = Path(self.tmp.name) / "example.env"

    def test_invalid_example_does_not_consume_stdin(self):
        for text in ("BROKEN", "A=1\nA=2", "1INVALID=value"):
            with self.subTest(text=text):
                self.example.write_text(text, encoding="utf-8")
                stream = io.StringIO("TOKEN=do-not-consume\n")
                error = io.StringIO()
                with patch("sys.stdin", stream), contextlib.redirect_stderr(error):
                    code = main(["-", "--example", str(self.example)])
                self.assertEqual(code, 2)
                self.assertEqual(stream.tell(), 0)
                self.assertIn(str(self.example), error.getvalue())

    def test_invalid_example_is_reported_before_opening_inputs(self):
        self.example.write_text("BROKEN", encoding="utf-8")
        missing = Path(self.tmp.name) / "missing.env"
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            code = main([str(missing), "--example", str(self.example)])
        self.assertEqual(code, 2)
        self.assertIn("E001", error.getvalue())
        self.assertNotIn(str(missing), error.getvalue())

    def test_valid_example_still_reads_and_compares_stdin(self):
        self.example.write_text("A=\nB=\n", encoding="utf-8")
        stream = io.StringIO("A=1\n")
        output = io.StringIO()
        with patch("sys.stdin", stream), contextlib.redirect_stdout(output):
            code = main(["-", "--example", str(self.example)])
        self.assertEqual(code, 1)
        self.assertEqual(stream.tell(), len("A=1\n"))
        self.assertIn("E004", output.getvalue())
