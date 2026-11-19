import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dotenv_lint.cli import main
from dotenv_lint.github import annotation
from dotenv_lint.rules import Issue


class GitHubOutputTests(unittest.TestCase):
    def run_cli(self, text, *options):
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(text)), contextlib.redirect_stdout(output):
            code = main(["-", "--stdin-filename", "project/.env", "-f", "github", *options])
        return code, output.getvalue()

    def test_warnings_and_errors_have_locations_and_rule_titles(self):
        code, output = self.run_cli("A=\nA=2\n")
        self.assertEqual(code, 1)
        self.assertEqual(output.splitlines(), [
            "::warning file=project/.env,line=1,title=W001::A has an empty value",
            "::error file=project/.env,line=2,title=E003::duplicate key 'A' (first defined on line 1)",
        ])

    def test_clean_input_emits_no_annotations(self):
        self.assertEqual(self.run_cli("A=1\n"), (0, ""))

    def test_strict_changes_exit_code_without_changing_warning_severity(self):
        normal_code, normal_output = self.run_cli("A=\n")
        strict_code, strict_output = self.run_cli("A=\n", "--strict")
        self.assertEqual((normal_code, strict_code), (0, 1))
        self.assertEqual(strict_output, normal_output)
        self.assertTrue(strict_output.startswith("::warning "))

    def test_rule_filters_apply_before_annotations_and_status(self):
        self.assertEqual(self.run_cli("A=\nA=2\n", "--select", "E003", "--ignore", "E003"), (0, ""))

    def test_missing_example_key_omits_invalid_zero_line(self):
        with tempfile.TemporaryDirectory() as folder:
            example = Path(folder) / "example.env"
            example.write_text("A=\nB=\n", encoding="utf-8")
            code, output = self.run_cli("A=1\n", "--example", str(example))
        self.assertEqual(code, 1)
        self.assertEqual(output, "::error file=project/.env,title=E004::B is defined in the example but missing\n")

    def test_filenames_and_messages_are_escaped_as_single_commands(self):
        result = annotation("dir/a,b:c%\r\n.env", Issue("E001", "error", 1, "bad%\r\n::warning::literal"))
        self.assertEqual(result, "::error file=dir/a%2Cb%3Ac%25%0D%0A.env,line=1,title=E001::bad%25%0D%0A::warning::literal")
        self.assertNotIn("\n", result)
        self.assertNotIn("\r", result)

    def test_incompatible_options_fail_before_reading_input(self):
        for option in ("--quiet", "--list-rules"):
            with self.subTest(option=option), patch("dotenv_lint.cli._read") as read:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    main(["-f", "github", option])
                self.assertEqual(error.exception.code, 2)
                read.assert_not_called()

    def test_executable_module_emits_annotations(self):
        result = subprocess.run([sys.executable, "-m", "dotenv_lint", "-", "-f", "github",
                                 "--stdin-filename", ".env.example"],
                                input=b"A=1\nA=2\n", capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, b"")
        self.assertTrue(result.stdout.startswith(b"::error file=.env.example,line=2,title=E003::"))
