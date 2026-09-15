import os
import sys
import unittest

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import context


class TestContextModule(unittest.TestCase):

    def setUp(self):
        # Reset context_data before each test run
        context.clear_context()

    def test_get_context_nonexistent_key(self):
        self.assertIsNone(context.get_context("unknown_key"))

    def test_set_and_get_context(self):
        context.set_context("user_role", "admin")
        context.set_context("active_session", 101)

        self.assertEqual(context.get_context("user_role"), "admin")
        self.assertEqual(context.get_context("active_session"), 101)

    def test_clear_context(self):
        context.set_context("temp_key", "temp_val")
        self.assertEqual(context.get_context("temp_key"), "temp_val")

        context.clear_context()
        self.assertIsNone(context.get_context("temp_key"))
        self.assertEqual(context.context_data, {})


if __name__ == "__main__":
    unittest.main()