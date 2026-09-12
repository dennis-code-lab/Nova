import json
import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import reminders


class TestRemindersModule(unittest.TestCase):

    @patch("reminders.os.path.exists", return_value=False)
    def test_load_reminders_file_not_found(self, mock_exists):
        result = reminders.load_reminders()
        self.assertEqual(result, [])

    @patch("reminders.os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"task": "Buy milk", "time": "14:00"}]',
    )
    def test_load_reminders_success(self, mock_file, mock_exists):
        result = reminders.load_reminders()
        self.assertEqual(
            result, [{"task": "Buy milk", "time": "14:00"}]
        )

    @patch("reminders.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_reminders_success(self, mock_file, mock_makedirs):
        sample = [{"task": "Write unit tests", "time": "10:00"}]
        reminders.save_reminders(sample)

        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_file.assert_called_once_with(
            reminders.REMINDER_FILE, "w", encoding="utf-8"
        )
        handle = mock_file()
        written_data = "".join(
            call.args[0] for call in handle.write.call_args_list
        )
        self.assertEqual(json.loads(written_data), sample)

    @patch("reminders.load_reminders", return_value=[])
    @patch("reminders.save_reminders")
    def test_add_reminder(self, mock_save, mock_load):
        result = reminders.add_reminder("Submit report", "16:30")
        self.assertEqual(result, "Reminder saved.")
        mock_save.assert_called_once_with(
            [{"task": "Submit report", "time": "16:30"}]
        )

    @patch("reminders.load_reminders", return_value=[])
    def test_list_reminders_empty(self, mock_load):
        result = reminders.list_reminders()
        self.assertEqual(result, "No reminders.")

    @patch(
        "reminders.load_reminders",
        return_value=[
            {"task": "Call client", "time": "11:00"},
            {"task": "Review PR", "time": None},
        ],
    )
    def test_list_reminders_populated(self, mock_load):
        result = reminders.list_reminders()
        expected = "1. Call client (at 11:00)\n2. Review PR\n"
        self.assertEqual(result, expected)

    @patch("reminders.notification.notify")
    @patch("reminders.datetime")
    @patch(
        "reminders.load_reminders",
        return_value=[{"task": "Standup meeting", "time": "09:00"}],
    )
    def test_check_reminders_triggered(
        self, mock_load, mock_datetime, mock_notify
    ):
        mock_now = MagicMock()
        mock_now.strftime.return_value = "09:00"
        mock_datetime.now.return_value = mock_now

        result = reminders.check_reminders()

        self.assertEqual(result, "Reminder: Standup meeting")
        mock_notify.assert_called_once_with(
            title="Nova Reminder",
            message="Standup meeting",
            timeout=10,
        )

    @patch("reminders.datetime")
    @patch(
        "reminders.load_reminders",
        return_value=[{"task": "Evening walk", "time": "18:00"}],
    )
    def test_check_reminders_no_match(self, mock_load, mock_datetime):
        mock_now = MagicMock()
        mock_now.strftime.return_value = "10:15"
        mock_datetime.now.return_value = mock_now

        result = reminders.check_reminders()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()