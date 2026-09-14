import json
import os
import sys
import unittest
from unittest.mock import mock_open, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import tasks


class TestTasksModule(unittest.TestCase):

    @patch("tasks.os.path.exists", return_value=False)
    @patch("tasks._save_tasks_raw")
    @patch("tasks.os.makedirs")
    def test_load_tasks_raw_seeds_initial_when_file_missing(
        self, mock_makedirs, mock_save, mock_exists
    ):
        result = tasks._load_tasks_raw()
        self.assertEqual(result, ["Study Python", "Finish Nova GUI", "Study Python"])
        mock_save.assert_called_once_with(
            ["Study Python", "Finish Nova GUI", "Study Python"]
        )

    @patch("tasks.os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data='["Task 1", "Task 2"]')
    @patch("tasks.os.makedirs")
    def test_load_tasks_raw_success(self, mock_makedirs, mock_file, mock_exists):
        result = tasks._load_tasks_raw()
        self.assertEqual(result, ["Task 1", "Task 2"])

    @patch("tasks.os.path.exists", return_value=True)
    @patch("builtins.open", side_effect=IOError)
    @patch("tasks.os.makedirs")
    def test_load_tasks_raw_handles_io_error(
        self, mock_makedirs, mock_file, mock_exists
    ):
        result = tasks._load_tasks_raw()
        self.assertEqual(result, [])

    def test_add_task_empty_validation(self):
        result = tasks.add_task("   ")
        self.assertEqual(result, "Task content cannot be empty.")

    @patch("tasks._save_tasks_raw")
    @patch("tasks._load_tasks_raw", return_value=["Task 1"])
    def test_add_task_success(self, mock_load, mock_save):
        result = tasks.add_task("  Task 2  ")
        self.assertEqual(result, "Task added:   Task 2  ")
        mock_save.assert_called_once_with(["Task 1", "Task 2"])

    @patch("tasks._load_tasks_raw", return_value=[])
    def test_show_tasks_empty(self, mock_load):
        result = tasks.show_tasks()
        self.assertEqual(
            result, "You have no pending tasks on your list! All done. 🎉"
        )

    @patch("tasks._load_tasks_raw", return_value=["Task A", "Task B"])
    def test_show_tasks_formatted(self, mock_load):
        result = tasks.show_tasks()
        self.assertEqual(result, "1. Task A\n2. Task B")

    @patch("tasks._load_tasks_raw", return_value=[])
    def test_complete_task_empty_list(self, mock_load):
        result = tasks.complete_task(1)
        self.assertEqual(
            result, "Your task list is already completely empty!"
        )

    @patch("tasks._save_tasks_raw")
    @patch("tasks._load_tasks_raw", return_value=["Task A", "Task B"])
    def test_complete_task_by_index_valid(self, mock_load, mock_save):
        result = tasks.complete_task("2")
        self.assertEqual(result, "Task completed: Task B")
        mock_save.assert_called_once_with(["Task A"])

    @patch("tasks._load_tasks_raw", return_value=["Task A"])
    def test_complete_task_by_index_invalid(self, mock_load):
        result = tasks.complete_task("5")
        self.assertEqual(
            result, "Invalid task number. You have 1 tasks remaining."
        )

    @patch("tasks._save_tasks_raw")
    @patch("tasks._load_tasks_raw", return_value=["Write Docs", "Run Tests"])
    def test_complete_task_by_name_matching(self, mock_load, mock_save):
        result = tasks.complete_task("tests")
        self.assertEqual(result, "Task completed: Run Tests")
        mock_save.assert_called_once_with(["Write Docs"])

    @patch("tasks._load_tasks_raw", return_value=["Write Docs"])
    def test_complete_task_by_name_not_found(self, mock_load):
        result = tasks.complete_task("nonexistent")
        self.assertEqual(
            result, "Could not find any pending task matching: 'nonexistent'"
        )


if __name__ == "__main__":
    unittest.main()