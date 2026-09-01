"""
Nova Engine v124
Engineering Milestone Engine Tests

Verifies that EngineeringMilestoneEngine:
- defines the expected milestone groups,
- calculates milestone completion correctly,
- calculates milestone percentages correctly,
- identifies fully completed milestones,
- excludes incomplete milestones from completed(),
- formats milestone progress correctly,
- queries history for milestone completion state.
"""

from __future__ import annotations

import unittest

from modules.engineering_milestones import EngineeringMilestoneEngine


class MockHistory:

    def __init__(self, completed=None):
        self.completed = set(completed or [])
        self.calls = []

    def is_completed(self, module):
        self.calls.append(module)
        return module in self.completed


class TestEngineeringMilestoneEngine(unittest.TestCase):

    def setUp(self):
        self.history = MockHistory()

        self.engine = EngineeringMilestoneEngine(
            self.history
        )

    # ------------------------------------------------------
    # Milestone definitions
    # ------------------------------------------------------

    def test_expected_milestones_exist(self):
        self.assertEqual(
            list(self.engine.milestones.keys()),
            [
                "Foundation",
                "Engineering Intelligence",
                "Automation",
            ],
        )

    def test_foundation_contains_expected_modules(self):
        self.assertEqual(
            self.engine.milestones["Foundation"],
            [
                "modules.engineering_runtime",
                "modules.engineering_memory",
                "modules.engineering_history",
            ],
        )

    def test_engineering_intelligence_contains_expected_modules(self):
        self.assertEqual(
            self.engine.milestones["Engineering Intelligence"],
            [
                "modules.engineering_graph",
                "modules.engineering_score",
                "modules.risk_engine",
                "modules.change_predictor",
                "modules.engineering_decision_engine",
            ],
        )

    def test_automation_contains_expected_modules(self):
        self.assertEqual(
            self.engine.milestones["Automation"],
            [
                "modules.engineering_controller",
                "modules.engineering_progress",
                "modules.engineering_forecast",
                "modules.engineering_dashboard",
            ],
        )

    # ------------------------------------------------------
    # Progress calculations
    # ------------------------------------------------------

    def test_no_completed_modules_produces_zero_progress(self):
        result = self.engine.milestone_progress()

        for milestone in result:
            with self.subTest(
                milestone=milestone["name"]
            ):
                self.assertEqual(
                    milestone["completed"],
                    0,
                )
                self.assertGreater(
                    milestone["total"],
                    0,
                )
                self.assertEqual(
                    milestone["percent"],
                    0.0,
                )

    def test_foundation_progress_is_calculated(self):
        self.history.completed.update(
            {
                "modules.engineering_runtime",
            }
        )

        result = self.engine.milestone_progress()

        foundation = result[0]

        self.assertEqual(
            foundation["name"],
            "Foundation",
        )
        self.assertEqual(
            foundation["completed"],
            1,
        )
        self.assertEqual(
            foundation["total"],
            3,
        )
        self.assertAlmostEqual(
            foundation["percent"],
            33.3333333333,
        )

    def test_engineering_intelligence_progress_is_calculated(self):
        self.history.completed.update(
            {
                "modules.engineering_graph",
                "modules.engineering_score",
                "modules.risk_engine",
            }
        )

        result = self.engine.milestone_progress()

        intelligence = result[1]

        self.assertEqual(
            intelligence["name"],
            "Engineering Intelligence",
        )
        self.assertEqual(
            intelligence["completed"],
            3,
        )
        self.assertEqual(
            intelligence["total"],
            5,
        )
        self.assertEqual(
            intelligence["percent"],
            60.0,
        )

    def test_automation_progress_is_calculated(self):
        self.history.completed.update(
            {
                "modules.engineering_controller",
                "modules.engineering_progress",
            }
        )

        result = self.engine.milestone_progress()

        automation = result[2]

        self.assertEqual(
            automation["name"],
            "Automation",
        )
        self.assertEqual(
            automation["completed"],
            2,
        )
        self.assertEqual(
            automation["total"],
            4,
        )
        self.assertEqual(
            automation["percent"],
            50.0,
        )

    def test_fully_completed_milestone_reaches_100_percent(self):
        self.history.completed.update(
            self.engine.milestones["Foundation"]
        )

        result = self.engine.milestone_progress()

        foundation = result[0]

        self.assertEqual(
            foundation["completed"],
            foundation["total"],
        )
        self.assertEqual(
            foundation["percent"],
            100.0,
        )

    # ------------------------------------------------------
    # Completed milestones
    # ------------------------------------------------------

    def test_completed_returns_fully_completed_milestone(self):
        self.history.completed.update(
            self.engine.milestones["Foundation"]
        )

        result = self.engine.completed()

        self.assertEqual(
            len(result),
            1,
        )

        self.assertEqual(
            result[0]["name"],
            "Foundation",
        )

    def test_completed_excludes_partially_completed_milestone(self):
        self.history.completed.add(
            "modules.engineering_runtime"
        )

        result = self.engine.completed()

        self.assertEqual(
            result,
            [],
        )

    def test_completed_excludes_uncompleted_milestones(self):
        result = self.engine.completed()

        self.assertEqual(
            result,
            [],
        )

    def test_multiple_completed_milestones_are_returned(self):
        self.history.completed.update(
            self.engine.milestones["Foundation"]
        )

        self.history.completed.update(
            self.engine.milestones["Automation"]
        )

        result = self.engine.completed()

        self.assertEqual(
            [item["name"] for item in result],
            [
                "Foundation",
                "Automation",
            ],
        )

    def test_completed_preserves_milestone_order(self):
        self.history.completed.update(
            self.engine.milestones["Automation"]
        )

        self.history.completed.update(
            self.engine.milestones["Foundation"]
        )

        result = self.engine.completed()

        self.assertEqual(
            [item["name"] for item in result],
            [
                "Foundation",
                "Automation",
            ],
        )

    # ------------------------------------------------------
    # History delegation
    # ------------------------------------------------------

    def test_milestone_progress_checks_every_module(self):
        self.engine.milestone_progress()

        expected_calls = sum(
            len(modules)
            for modules in self.engine.milestones.values()
        )

        self.assertEqual(
            len(self.history.calls),
            expected_calls,
        )

    def test_milestone_progress_checks_each_module_by_name(self):
        self.engine.milestone_progress()

        expected_modules = [
            module
            for modules in self.engine.milestones.values()
            for module in modules
        ]

        self.assertEqual(
            self.history.calls,
            expected_modules,
        )

    # ------------------------------------------------------
    # Formatting
    # ------------------------------------------------------

    def test_format_report_contains_title(self):
        result = self.engine.format_report()

        self.assertIn(
            "ENGINEERING MILESTONES",
            result,
        )

    def test_format_report_contains_all_milestones(self):
        result = self.engine.format_report()

        self.assertIn(
            "Foundation",
            result,
        )

        self.assertIn(
            "Engineering Intelligence",
            result,
        )

        self.assertIn(
            "Automation",
            result,
        )

    def test_format_report_contains_zero_progress(self):
        result = self.engine.format_report()

        self.assertIn(
            "0%",
            result,
        )

    def test_format_report_contains_completion_counts(self):
        self.history.completed.update(
            {
                "modules.engineering_runtime",
                "modules.engineering_graph",
            }
        )

        result = self.engine.format_report()

        self.assertIn(
            "Completed: 1/3",
            result,
        )

        self.assertIn(
            "Completed: 1/5",
            result,
        )

    def test_format_report_contains_full_completion(self):
        self.history.completed.update(
            self.engine.milestones["Foundation"]
        )

        result = self.engine.format_report()

        self.assertIn(
            "Completed: 3/3",
            result,
        )

        self.assertIn(
            "100%",
            result,
        )

    def test_format_report_uses_progress_bar(self):
        self.history.completed.update(
            {
                "modules.engineering_runtime",
            }
        )

        result = self.engine.format_report()

        self.assertIn(
            "33%",
            result,
        )

    def test_format_report_preserves_milestone_order(self):
        result = self.engine.format_report()

        foundation_position = result.index(
            "Foundation"
        )

        intelligence_position = result.index(
            "Engineering Intelligence"
        )

        automation_position = result.index(
            "Automation"
        )

        self.assertLess(
            foundation_position,
            intelligence_position,
        )

        self.assertLess(
            intelligence_position,
            automation_position,
        )


if __name__ == "__main__":
    unittest.main()