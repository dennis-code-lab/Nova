import json
import os
import sys
import unittest
from unittest.mock import mock_open, patch

# Append project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Explicitly import from modules package to avoid stdlib profile collision
from modules import profile


class TestProfileModule(unittest.TestCase):

    @patch("modules.profile.os.path.exists", return_value=False)
    def test_load_profile_file_not_found(self, mock_exists):
        result = profile.load_profile()

        self.assertEqual(result, {})
        mock_exists.assert_called_once_with("data/profile.json")

    @patch("modules.profile.os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"name": "Dennis", "role": "Developer"}',
    )
    def test_load_profile_success(self, mock_file, mock_exists):
        result = profile.load_profile()

        self.assertEqual(result, {"name": "Dennis", "role": "Developer"})

    @patch("modules.profile.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_profile(self, mock_file, mock_makedirs):
        data = {"theme": "dark"}
        profile.save_profile(data)

        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_file.assert_called_once_with(
            "data/profile.json", "w", encoding="utf-8"
        )

    @patch("modules.profile.save_profile")
    @patch("modules.profile.load_profile", return_value={"theme": "dark"})
    def test_remember_fact(self, mock_load, mock_save):
        result = profile.remember_fact("editor", "VS Code")

        self.assertEqual(result, "I'll remember that.")
        mock_save.assert_called_once_with(
            {"theme": "dark", "editor": "VS Code"}
        )

    @patch("modules.profile.load_profile", return_value={"name": "Dennis"})
    def test_get_fact_and_list_facts(self, mock_load):
        self.assertEqual(profile.get_fact("name"), "Dennis")
        self.assertIsNone(profile.get_fact("unknown_key"))
        self.assertEqual(profile.list_facts(), {"name": "Dennis"})

    @patch("modules.profile.load_profile", return_value={})
    def test_profile_to_text_empty(self, mock_load):
        result = profile.profile_to_text()

        self.assertEqual(result, "No known user facts.")

    @patch(
        "modules.profile.load_profile",
        return_value={"name": "Dennis", "city": "Nairobi"},
    )
    def test_profile_to_text_formatted(self, mock_load):
        result = profile.profile_to_text()

        self.assertEqual(result, "name: Dennis\ncity: Nairobi\n")


if __name__ == "__main__":
    unittest.main()