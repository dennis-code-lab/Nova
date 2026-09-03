"""
Nova Engine v128
Engineering Sprint Manager Tests

Verifies that EngineeringSprintManager:
- identifies the active sprint correctly
- skips completed sprints
- handles all sprints being complete
- calculates sprint progress correctly
- separates completed and remaining modules
- formats the sprint report correctly
"""

import unittest

from modules.engineering_sprints import EngineeringSprintManager


class MockHistory:
    def __init__(self, completed=None):
        self.completed = set(completed or [])
        self.calls = []

    def is_completed(self, module):
        self.calls.append(module)
        return module in self.completed


class TestEngineeringSprintManager(unittest.TestCase):

    def setUp(self):
        self.history = MockHistory()
        self.engine = EngineeringSprintManager(self.history)

    # ---------------------------------------------------------
    # Dependency tests
    # ---------------------------------------------------------

    def test_active_sprint_requests_completion_status(self):
        self.engine.active_sprint()

        self.assertGreater(len(self.history.calls), 0)

    def test_progress_requests_completion_status(self):
        self.engine.progress()

        self.assertGreater(len(self.history.calls), 0)

    # ---------------------------------------------------------
    # Sprint configuration tests
    # ---------------------------------------------------------

    def test_first_sprint_is_active_when_no_modules_are_complete(self):
        sprint = self.engine.active_sprint()

        self.assertIsNotNone(sprint)
        self.assertEqual(sprint["name"], "Sprint 1")
        self.assertEqual(sprint["goal"], "Foundation")

    def test_sprint_configuration_contains_expected_sprints(self):
        names = [sprint["name"] for sprint in self.engine.sprints]

        self.assertEqual(
            names,
            ["Sprint 1", "Sprint 2", "Sprint 3"],
        )

    def test_each_sprint_contains_name_goal_and_modules(self):
        for sprint in self.engine.sprints:
            self.assertIn("name", sprint)
            self.assertIn("goal", sprint)
            self.assertIn("modules", sprint)

    def test_each_sprint_has_at_least_one_module(self):
        for sprint in self.engine.sprints:
            self.assertGreater(len(sprint["modules"]), 0)

    # ---------------------------------------------------------
    # active_sprint tests
    # ---------------------------------------------------------

    def test_active_sprint_returns_first_incomplete_sprint(self):
        first_sprint = self.engine.sprints[0]

        self.history.completed = {
            module
            for module in first_sprint["modules"][:-1]
        }

        sprint = self.engine.active_sprint()

        self.assertEqual(sprint["name"], "Sprint 1")

    def test_active_sprint_skips_completed_first_sprint(self):
        self.history.completed.update(
            self.engine.sprints[0]["modules"]
        )

        sprint = self.engine.active_sprint()

        self.assertEqual(sprint["name"], "Sprint 2")

    def test_active_sprint_skips_multiple_completed_sprints(self):
        self.history.completed.update(
            self.engine.sprints[0]["modules"]
        )
        self.history.completed.update(
            self.engine.sprints[1]["modules"]
        )

        sprint = self.engine.active_sprint()

        self.assertEqual(sprint["name"], "Sprint 3")

    def test_active_sprint_returns_none_when_all_sprints_complete(self):
        for sprint in self.engine.sprints:
            self.history.completed.update(sprint["modules"])

        result = self.engine.active_sprint()

        self.assertIsNone(result)

    def test_active_sprint_returns_actual_sprint_dictionary(self):
        sprint = self.engine.active_sprint()

        self.assertIs(sprint, self.engine.sprints[0])

    # ---------------------------------------------------------
    # progress tests
    # ---------------------------------------------------------

    def test_progress_returns_active_sprint_information(self):
        result = self.engine.progress()

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Sprint 1")
        self.assertEqual(result["goal"], "Foundation")

    def test_progress_returns_none_when_all_sprints_complete(self):
        for sprint in self.engine.sprints:
            self.history.completed.update(sprint["modules"])

        result = self.engine.progress()

        self.assertIsNone(result)

    def test_progress_counts_completed_modules(self):
        modules = self.engine.sprints[0]["modules"]
        self.history.completed.add(modules[0])

        result = self.engine.progress()

        self.assertEqual(result["completed"], 1)

    def test_progress_counts_remaining_modules(self):
        modules = self.engine.sprints[0]["modules"]
        self.history.completed.add(modules[0])

        result = self.engine.progress()

        self.assertEqual(
            result["remaining"],
            len(modules) - 1,
        )

    def test_progress_reports_total_modules(self):
        result = self.engine.progress()

        self.assertEqual(
            result["total"],
            len(self.engine.sprints[0]["modules"]),
        )

    def test_progress_calculates_zero_percent_for_new_sprint(self):
        result = self.engine.progress()

        self.assertEqual(result["completed"], 0)
        self.assertEqual(result["percent"], 0)

    def test_progress_calculates_partial_percentage(self):
        modules = self.engine.sprints[0]["modules"]

        self.history.completed.update(modules[:1])

        result = self.engine.progress()

        expected = round((1 / len(modules)) * 100)

        self.assertEqual(result["percent"], expected)

    def test_progress_lists_completed_modules(self):
        modules = self.engine.sprints[0]["modules"]
        self.history.completed.add(modules[0])

        result = self.engine.progress()

        self.assertEqual(
            result["completed_modules"],
            [modules[0]],
        )

    def test_progress_lists_remaining_modules(self):
        modules = self.engine.sprints[0]["modules"]
        self.history.completed.add(modules[0])

        result = self.engine.progress()

        self.assertEqual(
            result["remaining_modules"],
            modules[1:],
        )

    def test_progress_preserves_module_order(self):
        modules = self.engine.sprints[0]["modules"]

        self.history.completed.update(
            [modules[0], modules[2]]
        )

        result = self.engine.progress()

        self.assertEqual(
            result["completed_modules"],
            [modules[0], modules[2]],
        )
        self.assertEqual(
            result["remaining_modules"],
            [modules[1]],
        )

    def test_progress_completed_plus_remaining_equals_total(self):
        result = self.engine.progress()

        self.assertEqual(
            result["completed"] + result["remaining"],
            result["total"],
        )

    def test_progress_completed_modules_match_completed_count(self):
        modules = self.engine.sprints[0]["modules"]

        self.history.completed.update(modules[:2])

        result = self.engine.progress()

        self.assertEqual(
            len(result["completed_modules"]),
            result["completed"],
        )

    def test_progress_remaining_modules_match_remaining_count(self):
        modules = self.engine.sprints[0]["modules"]

        self.history.completed.add(modules[0])

        result = self.engine.progress()

        self.assertEqual(
            len(result["remaining_modules"]),
            result["remaining"],
        )

    def test_progress_contains_expected_fields(self):
        result = self.engine.progress()

        expected_fields = {
            "name",
            "goal",
            "completed",
            "remaining",
            "total",
            "percent",
            "completed_modules",
            "remaining_modules",
        }

        self.assertEqual(set(result.keys()), expected_fields)

    # ---------------------------------------------------------
    # format_report tests
    # ---------------------------------------------------------

    def test_format_report_contains_sprint_name(self):
        report = self.engine.format_report()

        self.assertIn("Sprint 1", report)

    def test_format_report_contains_goal(self):
        report = self.engine.format_report()

        self.assertIn("Foundation", report)

    def test_format_report_contains_progress(self):
        report = self.engine.format_report()

        self.assertIn("Progress", report)
        self.assertIn("0%", report)

    def test_format_report_contains_remaining_modules(self):
        report = self.engine.format_report()

        self.assertIn("Remaining", report)

        for module in self.engine.sprints[0]["modules"]:
            self.assertIn(module, report)

    def test_format_report_contains_completed_module(self):
        module = self.engine.sprints[0]["modules"][0]
        self.history.completed.add(module)

        report = self.engine.format_report()

        self.assertIn(module, report)
        self.assertIn("Completed", report)

    def test_format_report_contains_estimated_completion(self):
        report = self.engine.format_report()

        self.assertIn("Estimated Completion", report)
        self.assertIn(
            f"{len(self.engine.sprints[0]['modules'])} engineering session(s)",
            report,
        )

    def test_format_report_uses_none_when_no_completed_modules(self):
        report = self.engine.format_report()

        self.assertIn("Completed", report)
        self.assertIn("None", report)

    def test_format_report_uses_none_when_no_remaining_modules(self):
        modules = self.engine.sprints[0]["modules"]

        self.history.completed.update(modules)

        # Sprint 1 is complete, so Sprint 2 becomes active.
        report = self.engine.format_report()

        self.assertIn("Sprint 2", report)
        self.assertIn("Remaining", report)

    def test_format_report_all_sprints_complete(self):
        for sprint in self.engine.sprints:
            self.history.completed.update(sprint["modules"])

        report = self.engine.format_report()

        self.assertIn("ALL SPRINTS COMPLETE", report)

    def test_format_report_contains_all_sprint_complete_header(self):
        for sprint in self.engine.sprints:
            self.history.completed.update(sprint["modules"])

        report = self.engine.format_report()

        self.assertIn("=" * 60, report)
        self.assertIn("ALL SPRINTS COMPLETE", report)

    # ---------------------------------------------------------
    # Sprint transition tests
    # ---------------------------------------------------------

    def test_progress_moves_to_next_sprint_when_current_is_complete(self):
        self.history.completed.update(
            self.engine.sprints[0]["modules"]
        )

        result = self.engine.progress()

        self.assertEqual(result["name"], "Sprint 2")
        self.assertEqual(
            result["goal"],
            "Engineering Intelligence",
        )

    def test_progress_only_reports_modules_from_active_sprint(self):
        self.history.completed.update(
            self.engine.sprints[0]["modules"]
        )

        result = self.engine.progress()

        self.assertEqual(
            result["total"],
            len(self.engine.sprints[1]["modules"]),
        )

        self.assertEqual(
            result["remaining_modules"],
            self.engine.sprints[1]["modules"],
        )


if __name__ == "__main__":
    unittest.main()