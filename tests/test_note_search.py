import os
import sys
import unittest
from unittest.mock import mock_open, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import note_search


class TestNoteSearchModule(unittest.TestCase):

    @patch("note_search.os.path.exists", return_value=False)
    def test_search_notes_folder_not_found(self, mock_exists):
        result = note_search.search_notes("project")

        self.assertEqual(result, "No notes folder found.")
        mock_exists.assert_called_once_with("notes")

    @patch("note_search.os.path.exists", return_value=True)
    @patch("note_search.os.listdir", return_value=[])
    def test_search_notes_empty_folder(self, mock_listdir, mock_exists):
        result = note_search.search_notes("project")

        self.assertEqual(result, "No matching notes found.")

    @patch("note_search.os.path.exists", return_value=True)
    @patch("note_search.os.listdir", return_value=["meeting.txt", "shopping.txt", "archived_project.txt"])
    def test_search_notes_filename_and_content_matching(self, mock_listdir, mock_exists):
        def custom_open(path, mode="r", encoding="utf-8"):
            filename = os.path.basename(path)
            if filename == "meeting.txt":
                content = "Discuss nova engine updates"
            elif filename == "shopping.txt":
                content = "Buy groceries and milk"
            else:
                content = "Old project ideas"
            return mock_open(read_data=content)()

        with patch("builtins.open", side_effect=custom_open):
            # Keyword matching content in meeting.txt
            result_content = note_search.search_notes("engine")
            self.assertEqual(result_content, "Matching notes:\nmeeting.txt")

            # Keyword matching filename in archived_project.txt
            result_filename = note_search.search_notes("project")
            self.assertEqual(
                result_filename,
                "Matching notes:\narchived_project.txt",
            )

    @patch("note_search.os.path.exists", return_value=True)
    @patch("note_search.os.listdir", return_value=["corrupted.txt", "valid.txt"])
    def test_search_notes_handles_read_exceptions(self, mock_listdir, mock_exists):
        def custom_open(path, mode="r", encoding="utf-8"):
            filename = os.path.basename(path)
            if filename == "corrupted.txt":
                raise PermissionError("Access Denied")
            return mock_open(read_data="This is valid data")()

        with patch("builtins.open", side_effect=custom_open):
            result = note_search.search_notes("valid")
            self.assertEqual(result, "Matching notes:\nvalid.txt")


if __name__ == "__main__":
    unittest.main()