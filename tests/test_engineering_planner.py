"""
Nova Engine v134
Engineering Planner Tests

Verifies EngineeringPlanner roadmap loading, saving, task estimation,
priority analysis, roadmap formatting, dashboard generation, task
selection, and task creation behavior.
"""

import json
import tempfile
import unittest
from pathlib import Path

from modules.engineering_planner import EngineeringPlanner


class TestEngineeringPlanner(unittest.TestCase):

    # =====================================================
    # Helpers
    # =====================================================

    def make_planner(self, roadmap_data=None):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        roadmap_path = Path(temp_dir.name) / "roadmap.json"

        if roadmap_data is not None:
            roadmap_path.write_text(
                json.dumps(roadmap_data),
                encoding="utf-8",
            )

        return EngineeringPlanner(str(roadmap_path)), roadmap_path

    # =====================================================
    # Initialization
    # =====================================================

    def test_init_default_path(self):
        planner = EngineeringPlanner()

        self.assertEqual(
            planner.roadmap_path,
            "data/roadmap.json",
        )

    def test_init_custom_path(self):
        planner = EngineeringPlanner("custom/roadmap.json")

        self.assertEqual(
            planner.roadmap_path,
            "custom/roadmap.json",
        )

    # =====================================================
    # Roadmap Loading
    # =====================================================

    def test_load_roadmap_returns_default_when_file_missing(self):
        planner, _ = self.make_planner()

        result = planner.load_roadmap()

        self.assertEqual(
            result,
            {
                "milestone": "v83-beta",
                "sprints": {},
                "tasks": [],
            },
        )

    def test_load_roadmap_reads_existing_json(self):
        roadmap = {
            "milestone": "v134",
            "sprints": {
                "Sprint 1": "Testing",
            },
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Planner tests",
                    "status": "DONE",
                }
            ],
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.load_roadmap()

        self.assertEqual(result, roadmap)

    def test_load_roadmap_returns_dictionary(self):
        planner, _ = self.make_planner(
            {
                "milestone": "v134",
                "tasks": [],
            }
        )

        result = planner.load_roadmap()

        self.assertIsInstance(result, dict)

    # =====================================================
    # Roadmap Saving
    # =====================================================

    def test_save_roadmap_creates_json_file(self):
        planner, roadmap_path = self.make_planner()

        data = {
            "milestone": "v134",
            "tasks": [],
        }

        planner.save_roadmap(data)

        self.assertTrue(roadmap_path.exists())

    def test_save_roadmap_writes_valid_json(self):
        planner, roadmap_path = self.make_planner()

        data = {
            "milestone": "v134",
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Test",
                }
            ],
        }

        planner.save_roadmap(data)

        saved = json.loads(
            roadmap_path.read_text(encoding="utf-8")
        )

        self.assertEqual(saved, data)

    def test_save_roadmap_round_trip(self):
        planner, _ = self.make_planner()

        data = {
            "milestone": "v134",
            "sprints": {
                "Sprint 1": "Testing",
            },
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Planner tests",
                    "status": "DONE",
                }
            ],
        }

        planner.save_roadmap(data)

        self.assertEqual(
            planner.load_roadmap(),
            data,
        )

    # =====================================================
    # Task Estimation
    # =====================================================

    def test_estimate_task_is_case_insensitive(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Build planner tests",
                    "effort": "Low",
                    "risk": "Low",
                    "dependencies": ["TASK-100"],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("task-101")

        self.assertIn("Task TASK-101", result)

    def test_estimate_task_low_effort(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Low effort task",
                    "effort": "Low",
                    "risk": "Low",
                    "dependencies": ["None"],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("TASK-101")

        self.assertIn("Effort:       Low", result)
        self.assertIn("Est. Time:    1-2 hours", result)
        self.assertIn("Risk:         Low", result)

    def test_estimate_task_medium_effort(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Medium effort task",
                    "effort": "Medium",
                    "risk": "Medium",
                    "dependencies": ["TASK-100"],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("TASK-101")

        self.assertIn("Effort:       Medium", result)
        self.assertIn("Est. Time:    4-6 hours", result)
        self.assertIn("Risk:         Moderate - Needs review", result)

    def test_estimate_task_high_effort(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "High effort task",
                    "effort": "High",
                    "risk": "High",
                    "dependencies": ["TASK-100"],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("TASK-101")

        self.assertIn("Effort:       High", result)
        self.assertIn("Est. Time:    8-12 hours", result)
        self.assertIn("Risk:         Critical", result)

    def test_estimate_task_unknown_effort_uses_default_time(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Unknown effort",
                    "effort": "Extreme",
                    "risk": "Low",
                    "dependencies": [],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("TASK-101")

        self.assertIn("Effort:       Extreme", result)
        self.assertIn("Est. Time:    4-6 hours", result)

    def test_estimate_task_unknown_risk_uses_low(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Unknown risk",
                    "effort": "Medium",
                    "risk": "Extreme",
                    "dependencies": [],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("TASK-101")

        self.assertIn("Risk:         Low", result)

    def test_estimate_task_includes_dependencies(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Dependency task",
                    "effort": "Medium",
                    "risk": "Low",
                    "dependencies": ["TASK-100", "TASK-099"],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("TASK-101")

        self.assertIn(
            "Dependencies: TASK-100, TASK-099",
            result,
        )

    def test_estimate_task_defaults_dependencies_to_none(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "No dependencies",
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.estimate_task("TASK-101")

        self.assertIn(
            "Dependencies: None",
            result,
        )

    def test_estimate_task_missing_task(self):
        planner, _ = self.make_planner({"tasks": []})

        result = planner.estimate_task("TASK-999")

        self.assertEqual(
            result,
            "Task TASK-999 not found.",
        )

    # =====================================================
    # Intelligent Priority
    # =====================================================

    def test_get_intelligent_priority_is_case_insensitive(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "priority": "P2",
                    "priority_reasons": ["Important task"],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.get_intelligent_priority("task-101")

        self.assertIn("TASK-101", result)
        self.assertIn("Priority: P2", result)

    def test_get_intelligent_priority_uses_custom_reasons(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "priority": "P1",
                    "priority_reasons": [
                        "Reason one",
                        "Reason two",
                    ],
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.get_intelligent_priority("TASK-101")

        self.assertIn("Reason one", result)
        self.assertIn("Reason two", result)

    def test_get_intelligent_priority_uses_default_reasons(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.get_intelligent_priority("TASK-101")

        self.assertIn(
            "Core dependency for downstream modules",
            result,
        )
        self.assertIn(
            "Maintains operational stability",
            result,
        )
        self.assertIn(
            "Reduces system technical debt",
            result,
        )

    def test_get_intelligent_priority_defaults_to_p1(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                }
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.get_intelligent_priority("TASK-101")

        self.assertIn(
            "Priority: P1",
            result,
        )

    def test_get_intelligent_priority_missing_task(self):
        planner, _ = self.make_planner({"tasks": []})

        result = planner.get_intelligent_priority("TASK-999")

        self.assertEqual(
            result,
            "Task TASK-999 not found.",
        )

    # =====================================================
    # Sprint Roadmap Formatting
    # =====================================================

    def test_format_sprint_roadmap_uses_default_sprints(self):
        planner, _ = self.make_planner(
            {
                "milestone": "v134",
                "tasks": [],
            }
        )

        result = planner.format_sprint_roadmap()

        self.assertIn("ENGINEERING ROADMAP", result)
        self.assertIn("Sprint 1", result)
        self.assertIn("Sprint 2", result)
        self.assertIn("Sprint 3", result)
        self.assertIn("Sprint 4", result)

    def test_format_sprint_roadmap_uses_custom_sprints(self):
        roadmap = {
            "sprints": {
                "Sprint A": "Custom work",
                "Sprint B": "More work",
            }
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.format_sprint_roadmap()

        self.assertIn("Sprint A", result)
        self.assertIn("Custom work", result)
        self.assertIn("Sprint B", result)
        self.assertIn("More work", result)

    def test_format_sprint_roadmap_preserves_sprint_order(self):
        roadmap = {
            "sprints": {
                "Sprint A": "First",
                "Sprint B": "Second",
                "Sprint C": "Third",
            }
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.format_sprint_roadmap()

        self.assertLess(
            result.index("Sprint A"),
            result.index("Sprint B"),
        )
        self.assertLess(
            result.index("Sprint B"),
            result.index("Sprint C"),
        )

    def test_format_sprint_roadmap_includes_borders(self):
        planner, _ = self.make_planner(
            {
                "sprints": {},
            }
        )

        result = planner.format_sprint_roadmap()

        self.assertIn("=" * 50, result)

    # =====================================================
    # Plan Dashboard
    # =====================================================

    def test_format_plan_dashboard_empty_tasks(self):
        roadmap = {
            "milestone": "v134",
            "tasks": [],
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.format_plan_dashboard()

        self.assertIn(
            "NOVA ENGINE ROADMAP [v134]",
            result,
        )
        self.assertIn(
            "Progress: [¦¦¦¦¦¦¦¦¦¦] 0% (0/0 Tasks Completed)",
            result,
        )

    def test_format_plan_dashboard_all_tasks_done(self):
        roadmap = {
            "milestone": "v134",
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "First task",
                    "status": "DONE",
                },
                {
                    "id": "TASK-102",
                    "title": "Second task",
                    "status": "DONE",
                },
            ],
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.format_plan_dashboard()

        self.assertIn(
            "100% (2/2 Tasks Completed)",
            result,
        )

    def test_format_plan_dashboard_partial_progress(self):
        roadmap = {
            "milestone": "v134",
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Done task",
                    "status": "DONE",
                },
                {
                    "id": "TASK-102",
                    "title": "Backlog task",
                    "status": "BACKLOG",
                },
            ],
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.format_plan_dashboard()

        self.assertIn(
            "50% (1/2 Tasks Completed)",
            result,
        )

    def test_format_plan_dashboard_lists_tasks(self):
        roadmap = {
            "milestone": "v134",
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "First task",
                    "status": "DONE",
                },
                {
                    "id": "TASK-102",
                    "title": "Second task",
                    "status": "BACKLOG",
                },
            ],
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.format_plan_dashboard()

        self.assertIn(
            "[TASK-101] First task (DONE)",
            result,
        )
        self.assertIn(
            "[TASK-102] Second task (BACKLOG)",
            result,
        )

    def test_format_plan_dashboard_uses_default_milestone(self):
        planner, _ = self.make_planner(
            {
                "tasks": [],
            }
        )

        result = planner.format_plan_dashboard()

        self.assertIn(
            "NOVA ENGINE ROADMAP [v83]",
            result,
        )

    # =====================================================
    # Next Task
    # =====================================================

    def test_get_next_task_returns_first_incomplete_task(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "Completed",
                    "status": "DONE",
                },
                {
                    "id": "TASK-102",
                    "title": "Next task",
                    "status": "BACKLOG",
                },
                {
                    "id": "TASK-103",
                    "title": "Later task",
                    "status": "BACKLOG",
                },
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.get_next_task()

        self.assertEqual(
            result,
            roadmap["tasks"][1],
        )

    def test_get_next_task_returns_first_task_when_not_done(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "title": "First task",
                    "status": "BACKLOG",
                },
                {
                    "id": "TASK-102",
                    "title": "Second task",
                    "status": "BACKLOG",
                },
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.get_next_task()

        self.assertEqual(
            result,
            roadmap["tasks"][0],
        )

    def test_get_next_task_returns_none_when_all_done(self):
        roadmap = {
            "tasks": [
                {
                    "id": "TASK-101",
                    "status": "DONE",
                },
                {
                    "id": "TASK-102",
                    "status": "DONE",
                },
            ]
        }

        planner, _ = self.make_planner(roadmap)

        self.assertIsNone(
            planner.get_next_task()
        )

    def test_get_next_task_returns_none_for_empty_tasks(self):
        planner, _ = self.make_planner(
            {
                "tasks": [],
            }
        )

        self.assertIsNone(
            planner.get_next_task()
        )

    # =====================================================
    # Add Task
    # =====================================================

    def test_add_task_creates_task(self):
        planner, _ = self.make_planner(
            {
                "tasks": [],
            }
        )

        result = planner.add_task("Build planner tests")

        self.assertEqual(
            result["title"],
            "Build planner tests",
        )

    def test_add_task_generates_first_task_id(self):
        planner, _ = self.make_planner(
            {
                "tasks": [],
            }
        )

        result = planner.add_task("First task")

        self.assertEqual(
            result["id"],
            "TASK-101",
        )

    def test_add_task_generates_next_id_from_task_count(self):
        roadmap = {
            "tasks": [
                {"id": "TASK-101"},
                {"id": "TASK-102"},
                {"id": "TASK-103"},
            ]
        }

        planner, _ = self.make_planner(roadmap)

        result = planner.add_task("Fourth task")

        self.assertEqual(
            result["id"],
            "TASK-104",
        )

    def test_add_task_default_fields(self):
        planner, _ = self.make_planner(
            {
                "tasks": [],
            }
        )

        result = planner.add_task("Default fields")

        self.assertEqual(result["status"], "BACKLOG")
        self.assertEqual(result["priority"], "P1")
        self.assertEqual(result["effort"], "Medium")
        self.assertEqual(result["risk"], "Low")
        self.assertEqual(
            result["dependencies"],
            ["TASK-103"],
        )

    def test_add_task_persists_to_roadmap(self):
        planner, _ = self.make_planner(
            {
                "milestone": "v134",
                "tasks": [],
            }
        )

        result = planner.add_task("Persistent task")

        roadmap = planner.load_roadmap()

        self.assertEqual(
            roadmap["tasks"],
            [result],
        )

    def test_add_task_preserves_existing_tasks(self):
        existing_task = {
            "id": "TASK-101",
            "title": "Existing task",
            "status": "BACKLOG",
        }

        planner, _ = self.make_planner(
            {
                "tasks": [existing_task],
            }
        )

        result = planner.add_task("New task")

        roadmap = planner.load_roadmap()

        self.assertEqual(
            roadmap["tasks"][0],
            existing_task,
        )
        self.assertEqual(
            roadmap["tasks"][1],
            result,
        )

    # =====================================================
    # Test Runner
    # =====================================================


if __name__ == "__main__":
    unittest.main()