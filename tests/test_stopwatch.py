import os
import sys
import unittest
from unittest.mock import patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import stopwatch


class TestStopwatchModule(unittest.TestCase):

    def setUp(self):
        # Reset global start_time state before each test run
        stopwatch.start_time = None

    def test_stopwatch_time_not_running(self):
        self.assertEqual(
            stopwatch.stopwatch_time(), "Stopwatch is not running."
        )

    def test_stop_stopwatch_not_running(self):
        self.assertEqual(stopwatch.stop_stopwatch(), "Stopwatch is not running.")

    @patch("time.time")
    def test_stopwatch_lifecycle(self, mock_time):
        # Simulate initial start at t=100.0
        mock_time.return_value = 100.0
        start_msg = stopwatch.start_stopwatch()
        self.assertEqual(start_msg, "Stopwatch started.")

        # Simulate check elapsed at t=105.5 (5 seconds elapsed)
        mock_time.return_value = 105.5
        time_msg = stopwatch.stopwatch_time()
        self.assertEqual(time_msg, "Elapsed time: 5 seconds.")

        # Simulate stopping at t=112.9 (12 seconds elapsed)
        mock_time.return_value = 112.9
        stop_msg = stopwatch.stop_stopwatch()
        self.assertEqual(stop_msg, "Stopwatch stopped at 12 seconds.")

        # Verify state reset after stopping
        self.assertIsNone(stopwatch.start_time)
        self.assertEqual(
            stopwatch.stopwatch_time(), "Stopwatch is not running."
        )


if __name__ == "__main__":
    unittest.main()