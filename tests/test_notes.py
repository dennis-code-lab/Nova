import os
import sys
import unittest
from unittest.mock import mock_open, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import notes


class TestNotesModule(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    def test_save_note_success(self, mock_file):
        result = notes.save_note("meeting", "Discuss roadmap")

        self.assertEqual(result, "Note saved.")
        mock_file.assert_called_once_with(
            "notes/meeting.txt", "w", encoding="utf-8"
        )
        mock_file().write.assert_called_once_with("Discuss roadmap")

    @patch("builtins.open", new_callable=mock_open, read_data="Project ideas")
    def test_read_note_success(self, mock_file):
        result = notes.read_note("ideas")

        self.assertEqual(result, "Project ideas")
        mock_file.assert_called_once_with(
            "notes/ideas.txt", "r", encoding="utf-8"
        )

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_read_note_not_found(self, mock_file):
        result = notes.read_note("nonexistent")

        self.assertEqual(result, "Note not found.")

    @patch("notes.os.listdir", return_value=["ideas.txt", "todo.txt", "archive.pdf"])
    def test_list_notes_with_files(self, mock_listdir):
        result = notes.list_notes()

        self.assertEqual(result, "ideas, todo")
        mock_listdir.assert_called_once_with("notes")

    @patch("notes.os.listdir", return_value=["archive.pdf", "readme.md"])
    def test_list_notes_no_matching_txt(self, mock_listdir):
        result = notes.list_notes()

        self.assertEqual(result, "No notes found.")

    @patch("notes.os.listdir", return_value=[])
    def test_list_notes_empty_directory(self, mock_listdir):
        result = notes.list_notes()

        self.assertEqual(result, "No notes found.")


if __name__ == "__main__":
    unittest.main()