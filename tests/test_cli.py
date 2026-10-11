import contextlib
import io
import os
import tempfile
import unittest

from dotenv_lint.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, text):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_clean_file_exits_zero(self):
        code, out, _ = self.run_cli(self.write(".env", "A=1\n"))
        self.assertEqual((code, out), (0, ""))

    def test_errors_exit_one(self):
        path = self.write(".env", "A=1\nA=2\n")
        code, out, _ = self.run_cli(path)
        self.assertEqual(code, 1)
        self.assertIn(f"{path}:2: E003 error", out)

    def test_warnings_only_exit_zero(self):
        code, out, _ = self.run_cli(self.write(".env", "A=\n"))
        self.assertEqual(code, 0)
        self.assertIn("W001", out)

    def test_missing_file_exits_two(self):
        code, _, err = self.run_cli(os.path.join(self.tmp.name, "nope.env"))
        self.assertEqual(code, 2)
        self.assertIn("No such file", err)

    def test_example_comparison(self):
        env = self.write(".env", "A=1\n")
        example = self.write(".env.example", "A=\nB=\n")
        code, out, _ = self.run_cli(env, "--example", example)
        self.assertEqual(code, 1)
        self.assertIn("E004", out)


if __name__ == "__main__":
    unittest.main()
