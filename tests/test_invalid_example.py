import unittest
import contextlib
import io
import tempfile
from pathlib import Path
from dotenv_lint.cli import main


class RegressionTest(unittest.TestCase):
    def test_malformed_example_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as folder:
            env, example = Path(folder) / "input.env", Path(folder) / "example.env"
            env.write_text("A=1\n")
            for text in ("BROKEN", "A=1\nA=2", "1BAD=value"):
                example.write_text(text)
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main([str(env), "-e", str(example)]), 2)

    def test_example_placeholders_are_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            env, example = Path(folder) / "input.env", Path(folder) / "example.env"
            env.write_text("A=1\n")
            example.write_text("A=\n")
            self.assertEqual(main([str(env), "-e", str(example)]), 0)
