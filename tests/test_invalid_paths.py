import contextlib
import io
import unittest
from dotenv_lint.cli import main

class InvalidPathTests(unittest.TestCase):
    def test_embedded_nul_path_returns_input_error(self):
        for args in (['bad\0path'], ['--example', 'bad\0example']):
            with self.subTest(args=args):
                error = io.StringIO()
                with contextlib.redirect_stderr(error):
                    self.assertEqual(main(args), 2)
                self.assertIn('invalid input path', error.getvalue())
                self.assertNotIn('Traceback', error.getvalue())
