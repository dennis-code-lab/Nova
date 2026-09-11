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

import memory


class TestMemoryModule(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"user": "dev", "session": 1}')
    def test_load_memory_success(self, mock_file):
        result = memory.load_memory()
        self.assertEqual(result, {"user": "dev", "session": 1})
        mock_file.assert_called_once_with(memory.MEMORY_FILE, "r")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_memory_file_not_found(self, mock_file):
        result = memory.load_memory()
        self.assertEqual(result, {})

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json content {{{")
    def test_load_memory_corrupted_json(self, mock_file):
        result = memory.load_memory()
        self.assertEqual(result, {})

    @patch("builtins.open", side_effect=PermissionError)
    def test_load_memory_generic_exception(self, mock_file):
        result = memory.load_memory()
        self.assertEqual(result, {})

    @patch("builtins.open", new_callable=mock_open)
    def test_save_memory_success(self, mock_file):
        sample_data = {"key": "value", "count": 42}
        memory.save_memory(sample_data)

        mock_file.assert_called_once_with(memory.MEMORY_FILE, "w")
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(json.loads(written_data), sample_data)


if __name__ == "__main__":
    unittest.main()