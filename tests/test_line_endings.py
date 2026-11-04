import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dotenv_lint.parser import parse


class LineEndingTests(unittest.TestCase):
    def test_physical_line_endings_preserve_entries_and_error_locations(self):
        for ending in ("\n", "\r\n", "\r"):
            with self.subTest(ending=repr(ending)):
                result = parse(ending.join(["# comment", "A=1", "INVALID", "B=2", ""]))
                self.assertEqual([(e.key, e.value, e.line) for e in result.entries],
                                 [("A", "1", 2), ("B", "2", 4)])
                self.assertEqual([e.line for e in result.errors], [3])

    def test_cr_piped_input_matches_the_same_file(self):
        data = b"FIRST=1\rSECOND=2\rFIRST=3\r"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.env"
            path.write_bytes(data)
            command = [sys.executable, "-m", "dotenv_lint", "-f", "json"]
            file_result = subprocess.run(command + [str(path)], capture_output=True)
            stdin_result = subprocess.run(command + ["-"], input=data, capture_output=True)
        self.assertEqual((file_result.returncode, stdin_result.returncode), (1, 1))
        self.assertEqual((file_result.stderr, stdin_result.stderr), (b"", b""))
        file_issues = json.loads(file_result.stdout)
        stdin_issues = json.loads(stdin_result.stdout)
        for issue in file_issues + stdin_issues:
            issue.pop("file")
        self.assertEqual(stdin_issues, file_issues)
        self.assertEqual([(i["code"], i["line"]) for i in stdin_issues], [("E003", 3)])

    def test_mixed_line_endings_and_escaped_carriage_return(self):
        result = parse('A=1\rB=2\r\nC="left\\rright"\nD=4')
        self.assertEqual(result.errors, [])
        self.assertEqual([(e.key, e.line) for e in result.entries],
                         [("A", 1), ("B", 2), ("C", 3), ("D", 4)])
        self.assertEqual(result.entries[2].value, "left\rright")
