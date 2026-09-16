import json
import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Append project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules import projects


class TestProjectsModule(unittest.TestCase):

    @patch("modules.projects.os.path.exists", return_value=False)
    def test_load_projects_ledger_file_not_found(self, mock_exists):
        result = projects._load_projects_ledger()
        self.assertEqual(result, {})

    @patch("modules.projects.os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data='{"nova": {}}')
    def test_load_projects_ledger_success(self, mock_file, mock_exists):
        result = projects._load_projects_ledger()
        self.assertEqual(result, {"nova": {}})

    @patch("modules.projects.log_error")
    @patch("modules.projects.os.path.exists", return_value=True)
    @patch("builtins.open", side_effect=Exception("Disk read error"))
    def test_load_projects_ledger_exception(
        self, mock_file, mock_exists, mock_log_error
    ):
        result = projects._load_projects_ledger()
        self.assertEqual(result, {})
        mock_log_error.assert_called_once()

    @patch("modules.projects.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_projects_ledger_success(self, mock_file, mock_makedirs):
        data = {"nova": {"completion_percentage": 0.0}}
        projects._save_projects_ledger(data)
        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_file.assert_called_once_with(
            projects.PROJECTS_FILE, "w", encoding="utf-8"
        )

    @patch("modules.projects.log_error")
    @patch("modules.projects.os.makedirs", side_effect=Exception("Disk full"))
    def test_save_projects_ledger_exception(
        self, mock_makedirs, mock_log_error
    ):
        projects._save_projects_ledger({"test": "data"})
        mock_log_error.assert_called_once()

    @patch("modules.projects._save_projects_ledger")
    @patch("modules.projects._load_projects_ledger", return_value={})
    @patch("modules.projects.log_info")
    def test_initialize_project(self, mock_log_info, mock_load, mock_save):
        res = projects.initialize_project(
            "Nova Assistant", "Build AI assistant", ["Phase 1", "Phase 2"]
        )
        self.assertIn("successfully initialized", res)
        mock_save.assert_called_once()
        saved_ledger = mock_save.call_args[0][0]
        self.assertIn("nova_assistant", saved_ledger)
        self.assertEqual(
            saved_ledger["nova_assistant"]["project_name"], "Nova Assistant"
        )
        self.assertEqual(
            len(saved_ledger["nova_assistant"]["milestones"]), 2
        )

    @patch(
        "modules.projects._load_projects_ledger",
        return_value={
            "nova": {
                "milestones": [
                    {"id": 1, "status": "Completed"},
                    {"id": 2, "status": "Pending", "title": "Next Step"},
                ]
            }
        },
    )
    def test_get_next_active_milestone(self, mock_load):
        milestone = projects.get_next_active_milestone("Nova")
        self.assertIsNotNone(milestone)
        self.assertEqual(milestone["id"], 2)
        self.assertEqual(milestone["title"], "Next Step")

    @patch("modules.projects._load_projects_ledger", return_value={})
    def test_get_next_active_milestone_not_found(self, mock_load):
        self.assertIsNone(projects.get_next_active_milestone("NonExistent"))

    @patch(
        "modules.projects._load_projects_ledger",
        return_value={
            "nova": {
                "milestones": [{"id": 1, "status": "Completed"}]
            }
        },
    )
    def test_get_next_active_milestone_all_completed(self, mock_load):
        self.assertIsNone(projects.get_next_active_milestone("Nova"))

    @patch("modules.projects._load_projects_ledger", return_value={})
    def test_mark_milestone_complete_not_found(self, mock_load):
        res = projects.mark_milestone_complete("Unknown", 1)
        self.assertEqual(res, "Project not found.")

    @patch("modules.projects._save_projects_ledger")
    @patch(
        "modules.projects._load_projects_ledger",
        return_value={
            "nova": {
                "completion_percentage": 0.0,
                "milestones": [
                    {
                        "id": 1,
                        "status": "Pending",
                        "completed_at": None,
                        "execution_traces": [],
                    },
                    {
                        "id": 2,
                        "status": "Pending",
                        "completed_at": None,
                        "execution_traces": [],
                    },
                ],
            }
        },
    )
    @patch("modules.projects.log_info")
    def test_mark_milestone_complete_success(
        self, mock_log_info, mock_load, mock_save
    ):
        res = projects.mark_milestone_complete(
            "Nova", 1, traces=["trace log"]
        )
        self.assertIn("Milestone #1 closed out", res)
        self.assertIn("50.0%", res)
        mock_save.assert_called_once()
        saved_ledger = mock_save.call_args[0][0]
        self.assertEqual(
            saved_ledger["nova"]["milestones"][0]["status"], "Completed"
        )
        self.assertEqual(
            saved_ledger["nova"]["milestones"][0]["execution_traces"],
            ["trace log"],
        )

    @patch("modules.projects._load_projects_ledger", return_value={})
    def test_render_project_boards_empty(self, mock_load):
        res = projects.render_project_boards()
        self.assertEqual(
            res,
            "No long-term project lifecycles are currently tracked in active"
            " storage.",
        )

    @patch(
        "modules.projects._load_projects_ledger",
        return_value={
            "nova": {
                "project_name": "Nova Assistant",
                "goal": "Build AI",
                "completion_percentage": 50.0,
                "created_at": "2026-09-01 10:00:00",
                "milestones": [
                    {
                        "id": 1,
                        "title": "Phase 1",
                        "status": "Completed",
                        "completed_at": "2026-09-02 12:00:00",
                    },
                    {
                        "id": 2,
                        "title": "Phase 2",
                        "status": "Pending",
                        "completed_at": None,
                    },
                ],
            }
        },
    )
    def test_render_project_boards_populated(self, mock_load):
        res = projects.render_project_boards()
        self.assertIn("NOVA ACTIVE LONG-TERM ROADMAP DASHBOARD", res)
        self.assertIn("PROJECT: NOVA ASSISTANT", res)
        self.assertIn("[✓] Phase 1: Phase 1 (Done: 2026-09-02 12:00:00)", res)
        self.assertIn("[ ] Phase 2: Phase 2", res)


if __name__ == "__main__":
    unittest.main()