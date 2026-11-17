import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dotenv_lint.cli import main


class StdinFilenameTests(unittest.TestCase):
    def run_cli(self, content, *options):
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(content)), contextlib.redirect_stdout(output):
            code = main(list(options))
        return code, output.getvalue()

    def test_json_and_jsonl_use_virtual_path_without_accessing_it(self):
        with tempfile.TemporaryDirectory() as folder:
            virtual = Path(folder) / "unsaved config.env"
            for format_name in ("json", "jsonl"):
                with self.subTest(format_name=format_name):
                    code, output = self.run_cli("A=1\nA=2\n", "-", "--stdin-filename",
                                                str(virtual), "-f", format_name)
                    self.assertEqual(code, 1)
                    records = json.loads(output) if format_name == "json" else [json.loads(output)]
                    self.assertEqual([(r["file"], r["code"], r["line"]) for r in records],
                                     [(str(virtual), "E003", 2)])
                    self.assertFalse(virtual.exists())

    def test_text_diagnostics_and_quiet_status(self):
        options = ("-", "--stdin-filename", "project/.env")
        code, output = self.run_cli("A=\n", *options, "--strict")
        self.assertEqual(code, 1)
        self.assertIn("project/.env:1: W001 warning", output)
        self.assertEqual(self.run_cli("A=\n", *options, "--strict", "--quiet"), (1, ""))

    def test_mixed_inputs_keep_physical_file_names(self):
        with tempfile.TemporaryDirectory() as folder:
            physical = Path(folder) / "physical.env"
            physical.write_text("A=\n", encoding="utf-8")
            code, output = self.run_cli("B=\n", str(physical), "-", "--stdin-filename",
                                       "virtual.env", "-f", "json")
        self.assertEqual(code, 0)
        self.assertEqual([r["file"] for r in json.loads(output)], [str(physical), "virtual.env"])

    def test_invalid_usage_fails_before_reading_any_input(self):
        cases = [["--stdin-filename", "virtual.env"],
                 ["input.env", "--example", "-", "--stdin-filename", "virtual.env"],
                 ["-", "--stdin-filename", ""], ["-", "--stdin-filename", "   "]]
        for options in cases:
            with self.subTest(options=options), patch("dotenv_lint.cli._read") as read:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    main(options)
                self.assertEqual(error.exception.code, 2)
                read.assert_not_called()

    def test_module_accepts_utf8_stdin_with_a_diagnostic_name(self):
        result = subprocess.run([sys.executable, "-m", "dotenv_lint", "-", "--stdin-filename",
                                 "unsaved.env", "-f", "json"],
                                input=b"A=1\nA=2\n", capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(json.loads(result.stdout)[0]["file"], "unsaved.env")
