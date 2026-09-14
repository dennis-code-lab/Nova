import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import task_queue
from task_queue import AutonomousTask, TaskPriority, TaskQueueEngine


class TestTaskQueueModule(unittest.TestCase):

    @patch("task_queue.log_info")
    def test_autonomous_task_execution_success(self, mock_log_info):
        mock_action = MagicMock(return_value="success_result")
        task = AutonomousTask(
            "TestTask", mock_action, TaskPriority.HIGH, "arg1", kwarg1="val1"
        )

        self.assertEqual(task.status, "PENDING")
        result = task.execute()

        self.assertEqual(result, "success_result")
        self.assertEqual(task.status, "COMPLETED")
        self.assertIsNotNone(task.started_at)
        self.assertIsNotNone(task.completed_at)
        mock_action.assert_called_once_with("arg1", kwarg1="val1")

    @patch("task_queue.log_error")
    def test_autonomous_task_execution_failure(self, mock_log_error):
        mock_action = MagicMock(side_effect=RuntimeError("Action Error"))
        task = AutonomousTask("FailingTask", mock_action)

        result = task.execute()

        self.assertIsNone(result)
        self.assertEqual(task.status, "FAILED")
        self.assertEqual(task.error_message, "Action Error")

    @patch("task_queue.log_info")
    def test_task_queue_engine_add_and_status_report(self, mock_log_info):
        engine = TaskQueueEngine()
        mock_action = MagicMock()

        task_id = engine.add_task(
            "Sample Task", mock_action, TaskPriority.HIGH
        )

        self.assertIn(task_id, engine.task_registry)
        report = engine.get_status_report()

        self.assertEqual(report["PENDING"], 1)
        self.assertEqual(report["COMPLETED"], 0)
        self.assertEqual(len(report["tasks"]), 1)
        self.assertEqual(report["tasks"][0]["priority"], "HIGH")

    @patch("task_queue.log_info")
    def test_task_queue_engine_worker_execution(self, mock_log_info):
        engine = TaskQueueEngine()
        mock_action = MagicMock(return_value="done")

        engine.start()
        # Call start() again to test double-start guard
        engine.start()

        task_id = engine.add_task(
            "Async Task", mock_action, TaskPriority.HIGH
        )

        # Allow worker thread time to pull and execute task from queue
        time.sleep(0.1)

        engine._running = False  # Graceful worker loop shutdown

        task = engine.task_registry[task_id]
        self.assertEqual(task.status, "COMPLETED")
        mock_action.assert_called_once()


if __name__ == "__main__":
    unittest.main()