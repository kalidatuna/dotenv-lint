import os
import subprocess
import sys
import unittest

class StdinEncodingTests(unittest.TestCase):
    def run_cli(self, data):
        env = dict(os.environ, PYTHONIOENCODING='ascii:surrogateescape')
        return subprocess.run([sys.executable, '-m', 'dotenv_lint', '-', '-f', 'json'],
                              input=data, capture_output=True, env=env)

    def test_stdin_uses_utf8_even_when_python_stream_uses_ascii(self):
        result = self.run_cli('NAME="Café"\n'.encode('utf-8'))
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b'[]\n', b''))

    def test_invalid_stdin_encoding_is_an_input_error(self):
        result = self.run_cli(b'TOKEN=\xff\n')
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'UTF-8', result.stderr)
        self.assertNotIn(b'Traceback', result.stderr)

    def test_stdin_accepts_utf8_bom(self):
        result = self.run_cli(b'\xef\xbb\xbfA=1\r\n')
        self.assertEqual(result.returncode, 0)
