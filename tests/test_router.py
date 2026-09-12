import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import router


class TestRouterModule(unittest.TestCase):

    def setUp(self):
        # Reset TOOL_REGISTRY before each test to maintain isolation
        router.TOOL_REGISTRY.clear()

    @patch("router.log_info")
    def test_register_tool(self, mock_log):
        mock_cb = MagicMock()
        router.register_tool("weather", ["weather", "forecast"], "weather <city>", mock_cb)

        self.assertIn("weather", router.TOOL_REGISTRY)
        self.assertEqual(router.TOOL_REGISTRY["weather"]["keywords"], ["weather", "forecast"])
        self.assertEqual(router.TOOL_REGISTRY["weather"]["usage"], "weather <city>")
        self.assertEqual(router.TOOL_REGISTRY["weather"]["callback"], mock_cb)
        mock_log.assert_called_once()

    def test_match_and_execute_empty_input(self):
        self.assertFalse(router.match_and_execute(""))
        self.assertFalse(router.match_and_execute("   "))

    def test_match_and_execute_no_match(self):
        mock_cb = MagicMock()
        router.register_tool("weather", ["weather"], "usage", mock_cb)

        # "hello" has no match score
        self.assertFalse(router.match_and_execute("hello world"))

    @patch("router.safe_execute_tool")
    @patch("router.log_info")
    def test_match_and_execute_successful_match(self, mock_log, mock_safe_exec):
        mock_cb = MagicMock()
        router.register_tool("weather", ["check weather", "forecast"], "usage", mock_cb)

        handled = router.match_and_execute("Please check weather in Nairobi")

        self.assertTrue(handled)
        mock_safe_exec.assert_called_once_with(mock_cb, "Please check weather in Nairobi")

    @patch("router.safe_execute_tool")
    def test_match_and_execute_highest_score_selection(self, mock_safe_exec):
        cb_single = MagicMock()
        cb_multi = MagicMock()

        router.register_tool("simple_weather", ["weather"], "usage", cb_single)
        router.register_tool("detailed_weather", ["get weather forecast"], "usage", cb_multi)

        # "get weather forecast" matches multi-word keyword with higher weight score
        handled = router.match_and_execute("get weather forecast for today")

        self.assertTrue(handled)
        mock_safe_exec.assert_called_once_with(cb_multi, "get weather forecast for today")

    def test_get_tool_directory(self):
        router.register_tool("alarm", ["set alarm"], "alarm <time>", MagicMock())

        directory_output = router.get_tool_directory()

        self.assertIn("INTELLIGENT TOOL DIRECTORY", directory_output)
        self.assertIn("[ALARM]", directory_output)
        self.assertIn("Usage: alarm <time>", directory_output)
        self.assertIn("Triggers: set alarm", directory_output)


if __name__ == "__main__":
    unittest.main()