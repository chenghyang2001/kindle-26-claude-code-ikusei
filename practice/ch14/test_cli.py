"""calc.py 命令列介面測試"""
import os
import subprocess
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "calc.py", *args],
        capture_output=True, text=True, encoding="utf-8", cwd=BASE_DIR,
    )


class TestCli(unittest.TestCase):
    def test_avg(self):
        result = run_cli("avg", "1", "2", "3")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "2.0")

    def test_last(self):
        result = run_cli("last", "2", "1", "2", "3", "4", "5")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "[4.0, 5.0]")

    def test_non_numeric(self):
        result = run_cli("avg", "a", "b")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
