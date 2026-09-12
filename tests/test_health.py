import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import health


class TestHealthModule(unittest.TestCase):

    @patch("health.log_error")
    @patch("health.log_info")
    @patch("health.os.path.exists", return_value=True)
    def test_audit_file_integrity_all_present(
        self, mock_exists, mock_log_info, mock_log_error
    ):
        status, issues, restored = health.audit_file_integrity()

        self.assertTrue(status)
        self.assertEqual(issues, [])
        self.assertEqual(restored, [])
        mock_log_error.assert_not_called()
        mock_log_info.assert_not_called()

    @patch("modules.memory.save_memory")
    @patch("health.settings.initialize_settings")
    @patch("health.log_error")
    @patch("health.log_info")
    @patch("health.os.path.exists")
    def test_audit_file_integrity_missing_files_restored(
        self,
        mock_exists,
        mock_log_info,
        mock_log_error,
        mock_init_settings,
        mock_save_memory,
    ):
        # Simulate missing memory.json and plugin_config.json, but help_system.py present
        def exists_side_effect(filepath):
            return filepath == "modules/help_system.py"

        mock_exists.side_effect = exists_side_effect

        status, issues, restored = health.audit_file_integrity()

        self.assertFalse(status)
        self.assertEqual(
            issues,
            ["Missing: data/memory.json", "Missing: data/plugin_config.json"],
        )
        self.assertEqual(
            restored,
            ["data/memory.json", "data/plugin_config.json"],
        )
        mock_save_memory.assert_called_once_with({})
        mock_init_settings.assert_called_once()
        mock_log_error.assert_called_once()
        mock_log_info.assert_called_once()

    @patch("health.audit_file_integrity", return_value=(True, [], []))
    def test_run_system_diagnostic_healthy(self, mock_audit):
        report = health.run_system_diagnostic()

        self.assertIn("NOVA CORE DIAGNOSTIC LOG MATRIX", report)
        self.assertIn("[ HEALTHY ]", report)
        self.assertIn("INTEGRAL", report)

    @patch(
        "health.audit_file_integrity",
        return_value=(
            False,
            ["Missing: data/memory.json"],
            ["data/memory.json"],
        ),
    )
    def test_run_system_diagnostic_degraded(self, mock_audit):
        report = health.run_system_diagnostic()

        self.assertIn("[ DEGRADED ]", report)
        self.assertIn("RECOVERED", report)
        self.assertIn("1 detected", report)
        self.assertIn("Re-seeded default structure for data/memory.json", report)

    def test_safe_execute_tool_success(self):
        mock_tool = MagicMock(return_value="Success Output")
        result = health.safe_execute_tool(mock_tool, "arg1", key="value")

        self.assertEqual(result, "Success Output")
        mock_tool.assert_called_once_with("arg1", key="value")

    @patch("health.log_error")
    def test_safe_execute_tool_intercept_exception(self, mock_log_error):
        def faulty_tool():
            raise ValueError("Simulated fault inside tool")

        result = health.safe_execute_tool(faulty_tool)

        self.assertIsNone(result)
        mock_log_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()