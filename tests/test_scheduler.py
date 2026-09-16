import sys
import os
import unittest
import time
from unittest.mock import MagicMock, patch

# Append project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules import scheduler


class TestSchedulerModule(unittest.TestCase):

    def setUp(self):
        # Reset internal module state before each test
        scheduler._jobs.clear()
        scheduler._running = False
        scheduler._scheduler_thread = None

    def tearDown(self):
        scheduler._running = False
        scheduler._jobs.clear()

    @patch("modules.scheduler.log_info")
    def test_add_job(self, mock_log_info):
        callback_mock = MagicMock()
        scheduler.add_job("test_job", callback_mock, 5)

        self.assertIn("test_job", scheduler._jobs)
        self.assertEqual(scheduler._jobs["test_job"]["interval"], 5)
        self.assertEqual(scheduler._jobs["test_job"]["callback"], callback_mock)
        self.assertEqual(scheduler._jobs["test_job"]["last_run"], 0)
        mock_log_info.assert_called_once()

    @patch("modules.scheduler.threading.Thread")
    @patch("modules.scheduler.log_info")
    def test_start_scheduler_when_not_running(self, mock_log_info, mock_thread):
        mock_thread_inst = MagicMock()
        mock_thread.return_value = mock_thread_inst

        scheduler.start_scheduler()

        self.assertTrue(scheduler._running)
        mock_thread.assert_called_once_with(
            target=scheduler._scheduler_loop, daemon=True
        )
        mock_thread_inst.start.assert_called_once()
        mock_log_info.assert_called_once_with(
            "Scheduler", "Dynamic Background Job Scheduler Engine activated."
        )

    @patch("modules.scheduler.threading.Thread")
    def test_start_scheduler_already_running(self, mock_thread):
        scheduler._running = True
        scheduler.start_scheduler()

        # Thread instantiation should be skipped if already running
        mock_thread.assert_not_called()

    @patch("modules.scheduler.log_info")
    def test_stop_scheduler(self, mock_log_info):
        scheduler._running = True
        scheduler.stop_scheduler()

        self.assertFalse(scheduler._running)
        mock_log_info.assert_called_once_with(
            "Scheduler", "Dynamic Background Job Scheduler Engine deactivated."
        )

    @patch("modules.scheduler.time.sleep", side_effect=InterruptedError("Stop loop"))
    @patch("modules.scheduler.threading.Thread")
    @patch("modules.scheduler.log_info")
    def test_scheduler_loop_dispatches_due_job(
        self, mock_log_info, mock_thread, mock_sleep
    ):
        mock_callback = MagicMock()
        scheduler.add_job("due_job", mock_callback, 10)

        # Force state: running = True
        scheduler._running = True

        # Run loop (mock_sleep side_effect breaks the loop)
        with self.assertRaises(InterruptedError):
            scheduler._scheduler_loop()

        # Assert worker thread was spawned for callback
        mock_thread.assert_called_once_with(
            target=mock_callback, daemon=True
        )

    @patch("modules.scheduler.time.sleep", side_effect=InterruptedError("Stop loop"))
    @patch("modules.scheduler.threading.Thread")
    def test_scheduler_loop_skips_not_due_job(self, mock_thread, mock_sleep):
        mock_callback = MagicMock()
        scheduler.add_job("recent_job", mock_callback, 100)
        scheduler._jobs["recent_job"]["last_run"] = time.time()

        scheduler._running = True

        with self.assertRaises(InterruptedError):
            scheduler._scheduler_loop()

        mock_thread.assert_not_called()

    @patch("modules.scheduler.time.sleep", side_effect=InterruptedError("Stop loop"))
    @patch("modules.scheduler.threading.Thread", side_effect=Exception("Thread spawn error"))
    @patch("modules.scheduler.log_error")
    def test_scheduler_loop_handles_exception(
        self, mock_log_error, mock_thread, mock_sleep
    ):
        mock_callback = MagicMock()
        scheduler.add_job("failing_dispatch_job", mock_callback, 5)
        scheduler._running = True

        with self.assertRaises(InterruptedError):
            scheduler._scheduler_loop()

        mock_log_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()