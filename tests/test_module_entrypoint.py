import unittest
import json
import subprocess
import sys


class RegressionTest(unittest.TestCase):
    def test_module_entrypoint_accepts_stdin_json(self):
        result = subprocess.run([sys.executable, "-m", "dotenv_lint", "-", "-f", "json"],
                                input="A=1\nA=2\n", text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)[0]["code"], "E003")

    def test_module_version(self):
        result = subprocess.run([sys.executable, "-m", "dotenv_lint", "--version"],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("dotenv-lint", result.stdout)
