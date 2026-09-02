"""
Nova Engine v125
Engineering Analytics Engine Tests

Verifies that EngineeringAnalytics:
- calculates total modules from milestone progress,
- counts completed modules through history,
- calculates remaining modules,
- calculates completion percentage,
- handles zero total modules,
- reports engineering velocity,
- formats the analytics report correctly.
"""

from __future__ import annotations

import unittest

from modules.engineering_analytics import EngineeringAnalytics


class MockHistory:

    def __init__(self, completed: int = 0):
        self.completed = completed
        self.calls = []

    def completed_count(self) -> int:
        self.calls.append(("completed_count",))
        return self.completed


class MockMilestoneEngine:

    def __init__(self, progress=None):
        self.progress = progress or []
        self.calls = []

    def milestone_progress(self):
        self.calls.append(("milestone_progress",))
        return self.progress


class TestEngineeringAnalytics(unittest.TestCase):

    def setUp(self):
        self.history = MockHistory(completed=3)

        self.milestone_engine = MockMilestoneEngine(
            progress=[
                {"name": "Foundation", "completed": 2, "total": 3},
                {
                    "name": "Engineering Intelligence",
                    "completed": 4,
                    "total": 5,
                },
                {"name": "Automation", "completed": 1, "total": 4},
            ]
        )

        self.engine = EngineeringAnalytics(
            self.history,
            self.milestone_engine,
        )

    # ------------------------------------------------------
    # Analytics calculation
    # ------------------------------------------------------

    def test_analytics_requests_milestone_progress(self):
        self.engine.analytics()

        self.assertEqual(
            self.milestone_engine.calls,
            [("milestone_progress",)],
        )

    def test_analytics_requests_completed_count(self):
        self.engine.analytics()

        self.assertEqual(
            self.history.calls,
            [("completed_count",)],
        )

    def test_analytics_calculates_total_modules(self):
        report = self.engine.analytics()

        self.assertEqual(
            report["total"],
            12,
        )

    def test_analytics_preserves_completed_count(self):
        report = self.engine.analytics()

        self.assertEqual(
            report["completed"],
            3,
        )

    def test_analytics_calculates_remaining_modules(self):
        report = self.engine.analytics()

        self.assertEqual(
            report["remaining"],
            9,
        )

    def test_analytics_calculates_completion_percentage(self):
        report = self.engine.analytics()

        self.assertAlmostEqual(
            report["completion"],
            25.0,
        )

    def test_analytics_velocity_matches_completed_modules(self):
        report = self.engine.analytics()

        self.assertEqual(
            report["velocity"],
            3,
        )

    # ------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------

    def test_zero_total_modules_produces_zero_completion(self):
        history = MockHistory(completed=0)

        milestone_engine = MockMilestoneEngine(
            progress=[]
        )

        engine = EngineeringAnalytics(
            history,
            milestone_engine,
        )

        report = engine.analytics()

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["completed"], 0)
        self.assertEqual(report["remaining"], 0)
        self.assertEqual(report["completion"], 0.0)
        self.assertEqual(report["velocity"], 0)

    def test_analytics_allows_fully_completed_project(self):
        history = MockHistory(completed=12)

        milestone_engine = MockMilestoneEngine(
            progress=[
                {"name": "Foundation", "total": 3},
                {"name": "Engineering Intelligence", "total": 5},
                {"name": "Automation", "total": 4},
            ]
        )

        engine = EngineeringAnalytics(
            history,
            milestone_engine,
        )

        report = engine.analytics()

        self.assertEqual(report["total"], 12)
        self.assertEqual(report["completed"], 12)
        self.assertEqual(report["remaining"], 0)
        self.assertEqual(report["completion"], 100.0)
        self.assertEqual(report["velocity"], 12)

    # ------------------------------------------------------
    # Formatting
    # ------------------------------------------------------

    def test_format_report_contains_title(self):
        report = self.engine.format_report()

        self.assertIn(
            "ENGINEERING ANALYTICS",
            report,
        )

    def test_format_report_contains_completed_modules(self):
        report = self.engine.format_report()

        self.assertIn(
            "Completed Modules",
            report,
        )
        self.assertIn(
            "\n3\n",
            report,
        )

    def test_format_report_contains_remaining_modules(self):
        report = self.engine.format_report()

        self.assertIn(
            "Remaining Modules",
            report,
        )
        self.assertIn(
            "\n9\n",
            report,
        )

    def test_format_report_contains_total_modules(self):
        report = self.engine.format_report()

        self.assertIn(
            "Total Modules",
            report,
        )
        self.assertIn(
            "\n12\n",
            report,
        )

    def test_format_report_formats_completion_to_one_decimal_place(self):
        report = self.engine.format_report()

        self.assertIn(
            "25.0%",
            report,
        )

    def test_format_report_contains_velocity(self):
        report = self.engine.format_report()

        self.assertIn(
            "Engineering Velocity",
            report,
        )
        self.assertIn(
            "3 module(s) completed",
            report,
        )

    def test_format_report_contains_all_metric_sections(self):
        report = self.engine.format_report()

        expected_sections = [
            "Completed Modules",
            "Remaining Modules",
            "Total Modules",
            "Completion",
            "Engineering Velocity",
        ]

        for section in expected_sections:
            with self.subTest(section=section):
                self.assertIn(section, report)


if __name__ == "__main__":
    unittest.main()
