import contextlib
import io
import json
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

    def test_strict_fails_on_warnings(self):
        path = self.write(".env", "A=\n")
        self.assertEqual(self.run_cli(path, "--strict")[0], 1)

    def test_ignore_skips_codes(self):
        path = self.write(".env", "A=\nA=1\n")
        code, out, _ = self.run_cli(path, "--ignore", "w001, e003")
        self.assertEqual((code, out), (0, ""))

    def test_json_output(self):
        path = self.write(".env", "A=1\nA=2\n")
        code, out, _ = self.run_cli(path, "--format", "json")
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data[0]["code"], "E003")
        self.assertEqual(data[0]["file"], path)
        self.assertEqual(data[0]["key"], "A")

    def test_json_output_empty_list_when_clean(self):
        _, out, _ = self.run_cli(self.write(".env", "A=1\n"), "-f", "json")
        self.assertEqual(json.loads(out), [])

    def test_utf8_bom_and_crlf_are_accepted(self):
        path = os.path.join(self.tmp.name, ".env")
        with open(path, "wb") as f:
            f.write(b"\xef\xbb\xbfA=1\r\nB=2\r\n")
        self.assertEqual(self.run_cli(path)[:2], (0, ""))

    def test_invalid_utf8_returns_read_error(self):
        path = os.path.join(self.tmp.name, "invalid.env")
        with open(path, "wb") as handle:
            handle.write(b"A=\xff")
        code, out, err = self.run_cli(path)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("UTF-8", err)

    def test_malformed_example_reports_its_own_path(self):
        env = self.write(".env", "A=1\n")
        example = self.write(".env.example", 'A="unterminated\n')
        code, out, _ = self.run_cli(env, "-e", example, "-f", "json")
        self.assertEqual(code, 1)
        self.assertTrue(any(i["file"] == example and i["code"] == "E001" for i in json.loads(out)))
        example = self.write(".env.example", "A=\n")
        self.assertEqual(self.run_cli(env, "-e", example, "--strict")[0], 0)

    def test_unknown_ignore_code_is_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as raised:
                main(["--ignore", "W999"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("W999", err.getvalue())


if __name__ == "__main__":
    unittest.main()
