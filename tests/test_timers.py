import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import timers


class TestTimersModule(unittest.TestCase):

    @patch("timers.threading.Thread")
    def test_start_timer_returns_message_and_spawns_thread(self, mock_thread_cls):
        mock_thread_instance = MagicMock()
        mock_thread_cls.return_value = mock_thread_instance

        result = timers.start_timer(5)

        self.assertEqual(result, "Timer started for 5 seconds.")
        mock_thread_cls.assert_called_once()
        self.assertTrue(mock_thread_cls.call_args[1].get("daemon"))
        mock_thread_instance.start.assert_called_once()

    @patch("timers.notification")
    @patch("timers.speak")
    @patch("timers.time.sleep")
    def test_timer_thread_execution_with_notification(
        self, mock_sleep, mock_speak, mock_notification
    ):
        # Intercept thread target and execute synchronously
        with patch("timers.threading.Thread") as mock_thread_cls:
            timers.start_timer(3)
            timer_target = mock_thread_cls.call_args[1]["target"]
            timer_target()

        mock_sleep.assert_called_once_with(3)
        mock_speak.assert_called_once_with("Timer finished (3 seconds)")
        mock_notification.notify.assert_called_once_with(
            title="Nova Timer", message="Timer finished (3 seconds)", timeout=10
        )

    @patch("timers.speak")
    @patch("timers.time.sleep")
    def test_timer_thread_execution_without_notification(
        self, mock_sleep, mock_speak
    ):
        with patch("timers.notification", None):
            with patch("timers.threading.Thread") as mock_thread_cls:
                timers.start_timer(10)
                timer_target = mock_thread_cls.call_args[1]["target"]
                timer_target()

        mock_sleep.assert_called_once_with(10)
        mock_speak.assert_called_once_with("Timer finished (10 seconds)")


if __name__ == "__main__":
    unittest.main()