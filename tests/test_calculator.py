import os
import sys
import unittest

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import calculator


class TestCalculatorModule(unittest.TestCase):

    def test_basic_arithmetic(self):
        self.assertEqual(calculator.calculate("2 + 2"), 4)
        self.assertEqual(calculator.calculate("10 - 4"), 6)
        self.assertEqual(calculator.calculate("3 * 5"), 15)
        self.assertEqual(calculator.calculate("20 / 4"), 5.0)

    def test_complex_expressions(self):
        self.assertEqual(calculator.calculate("(2 + 3) * 4"), 20)
        self.assertEqual(calculator.calculate("2 ** 3"), 8)

    def test_division_by_zero(self):
        self.assertEqual(calculator.calculate("1 / 0"), "Invalid expression")

    def test_invalid_syntax(self):
        self.assertEqual(calculator.calculate("2 + "), "Invalid expression")
        self.assertEqual(calculator.calculate("abc + 1"), "Invalid expression")


if __name__ == "__main__":
    unittest.main()