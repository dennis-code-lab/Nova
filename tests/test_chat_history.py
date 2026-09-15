import os
import sys
import unittest
from unittest.mock import mock_open, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import chat_history


class TestChatHistoryModule(unittest.TestCase):

    @patch("chat_history.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_chat_creates_dir_and_appends_message(
        self, mock_file, mock_makedirs
    ):
        chat_history.save_chat("User: Hello Nova")

        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_file.assert_called_once_with(
            "data/chat_history.txt", "a", encoding="utf-8"
        )
        mock_file().write.assert_called_once_with("User: Hello Nova\n")

    @patch("chat_history.os.path.exists", return_value=False)
    def test_load_chat_file_not_found(self, mock_exists):
        result = chat_history.load_chat()

        self.assertEqual(result, "")
        mock_exists.assert_called_once_with("data/chat_history.txt")

    @patch("chat_history.os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="User: Hi\nNova: Hello!\n",
    )
    def test_load_chat_file_success(self, mock_file, mock_exists):
        result = chat_history.load_chat()

        self.assertEqual(result, "User: Hi\nNova: Hello!\n")
        mock_file.assert_called_once_with(
            "data/chat_history.txt", "r", encoding="utf-8"
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_clear_chat_file_truncates_file(self, mock_file):
        chat_history.clear_chat_file()

        mock_file.assert_called_once_with(
            "data/chat_history.txt", "w", encoding="utf-8"
        )
        mock_file().write.assert_called_once_with("")


if __name__ == "__main__":
    unittest.main()