"""
Nova Engine v126
Engineering Insights Engine Tests

Verifies that EngineeringInsights:
- requests analytics, milestone progress and roadmap data,
- determines the correct engineering phase,
- identifies the next roadmap module,
- identifies the current milestone,
- handles a fully completed roadmap,
- generates state-aware recommendations,
- preserves analytics metrics,
- formats the insights report correctly.
"""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from modules.engineering_insights import EngineeringInsights


class MockAnalyticsEngine:

    def __init__(
        self,
        completion: float = 20.0,
        velocity: int = 3,
        remaining: int = 9,
    ):
        self.completion = completion
        self.velocity = velocity
        self.remaining = remaining
        self.calls = []

    def analytics(self):
        self.calls.append(("analytics",))
        return {
            "completion": self.completion,
            "velocity": self.velocity,
            "remaining": self.remaining,
        }


class MockMilestoneEngine:

    def __init__(self, progress=None):
        self.progress = progress or []
        self.calls = []

    def milestone_progress(self):
        self.calls.append(("milestone_progress",))
        return self.progress


class MockPlanner:

    def __init__(self, roadmap=None):
        self.roadmap = roadmap or []
        self.calls = []

    def generate(self):
        self.calls.append(("generate",))
        return self.roadmap


class TestEngineeringInsights(unittest.TestCase):

    def setUp(self):
        self.analytics_engine = MockAnalyticsEngine(
            completion=20.0,
            velocity=3,
            remaining=9,
        )

        self.milestone_engine = MockMilestoneEngine(
            progress=[
                {
                    "name": "Foundation",
                    "completed": 2,
                    "total": 3,
                },
                {
                    "name": "Engineering Intelligence",
                    "completed": 4,
                    "total": 5,
                },
                {
                    "name": "Automation",
                    "completed": 1,
                    "total": 4,
                },
            ]
        )

        self.planner = MockPlanner(
            roadmap=[
                SimpleNamespace(
                    module="modules.first_module"
                ),
                SimpleNamespace(
                    module="modules.second_module"
                ),
            ]
        )

        self.engine = EngineeringInsights(
            self.analytics_engine,
            self.milestone_engine,
            self.planner,
        )

    # ------------------------------------------------------
    # Dependency calls
    # ------------------------------------------------------

    def test_generate_requests_analytics(self):
        self.engine.generate()

        self.assertEqual(
            self.analytics_engine.calls,
            [("analytics",)],
        )

    def test_generate_requests_milestone_progress(self):
        self.engine.generate()

        self.assertEqual(
            self.milestone_engine.calls,
            [("milestone_progress",)],
        )

    def test_generate_requests_roadmap(self):
        self.engine.generate()

        self.assertEqual(
            self.planner.calls,
            [("generate",)],
        )

    # ------------------------------------------------------
    # Phase selection
    # ------------------------------------------------------

    def test_completion_below_25_enters_foundation_phase(self):
        self.analytics_engine.completion = 24.9

        report = self.engine.generate()

        self.assertEqual(
            report["phase"],
            "Foundation Phase",
        )

    def test_completion_at_25_enters_engineering_phase(self):
        self.analytics_engine.completion = 25.0

        report = self.engine.generate()

        self.assertEqual(
            report["phase"],
            "Engineering Phase",
        )

    def test_completion_below_60_enters_engineering_phase(self):
        self.analytics_engine.completion = 59.9

        report = self.engine.generate()

        self.assertEqual(
            report["phase"],
            "Engineering Phase",
        )

    def test_completion_at_60_enters_optimization_phase(self):
        self.analytics_engine.completion = 60.0

        report = self.engine.generate()

        self.assertEqual(
            report["phase"],
            "Optimization Phase",
        )

    # ------------------------------------------------------
    # Next module
    # ------------------------------------------------------

    def test_generate_selects_first_roadmap_module(self):
        report = self.engine.generate()

        self.assertEqual(
            report["next_module"],
            "modules.first_module",
        )

    def test_generate_ignores_later_roadmap_modules(self):
        report = self.engine.generate()

        self.assertNotEqual(
            report["next_module"],
            "modules.second_module",
        )

    def test_empty_roadmap_returns_none_as_next_module(self):
        self.planner.roadmap = []

        report = self.engine.generate()

        self.assertEqual(
            report["next_module"],
            "None",
        )

    # ------------------------------------------------------
    # Current milestone
    # ------------------------------------------------------

    def test_generate_selects_first_incomplete_milestone(self):
        report = self.engine.generate()

        self.assertEqual(
            report["current_milestone"],
            "Foundation",
        )

    def test_generate_skips_completed_milestones(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            },
            {
                "name": "Engineering Intelligence",
                "completed": 4,
                "total": 5,
            },
            {
                "name": "Automation",
                "completed": 1,
                "total": 4,
            },
        ]

        report = self.engine.generate()

        self.assertEqual(
            report["current_milestone"],
            "Engineering Intelligence",
        )

    def test_all_completed_milestones_return_complete(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            },
            {
                "name": "Engineering Intelligence",
                "completed": 5,
                "total": 5,
            },
            {
                "name": "Automation",
                "completed": 4,
                "total": 4,
            },
        ]

        report = self.engine.generate()

        self.assertEqual(
            report["current_milestone"],
            "Complete",
        )

    # ------------------------------------------------------
    # Recommendation branches
    # ------------------------------------------------------

    def test_empty_roadmap_generates_completed_project_recommendation(self):
        self.planner.roadmap = []

        report = self.engine.generate()

        self.assertIn(
            "All roadmap modules are complete.",
            report["recommendation"],
        )

    def test_foundation_phase_generates_foundation_recommendation(self):
        self.analytics_engine.completion = 20.0

        report = self.engine.generate()

        self.assertIn(
            "Focus on the Foundation milestone",
            report["recommendation"],
        )
        self.assertIn(
            "modules.first_module",
            report["recommendation"],
        )

    def test_engineering_phase_generates_engineering_recommendation(self):
        self.analytics_engine.completion = 40.0

        report = self.engine.generate()

        self.assertIn(
            "Continue Engineering Intelligence work",
            report["recommendation"],
        )
        self.assertIn(
            "modules.first_module",
            report["recommendation"],
        )

    def test_optimization_phase_generates_optimization_recommendation(self):
        self.analytics_engine.completion = 70.0

        report = self.engine.generate()

        self.assertIn(
            "Prioritize optimization and automation",
            report["recommendation"],
        )
        self.assertIn(
            "modules.first_module",
            report["recommendation"],
        )

    # ------------------------------------------------------
    # Returned metrics
    # ------------------------------------------------------

    def test_generate_preserves_completion(self):
        self.analytics_engine.completion = 37.5

        report = self.engine.generate()

        self.assertEqual(
            report["completion"],
            37.5,
        )

    def test_generate_preserves_velocity(self):
        self.analytics_engine.velocity = 7

        report = self.engine.generate()

        self.assertEqual(
            report["velocity"],
            7,
        )

    def test_generate_preserves_remaining_modules(self):
        self.analytics_engine.remaining = 14

        report = self.engine.generate()

        self.assertEqual(
            report["remaining"],
            14,
        )

    def test_sessions_matches_remaining_modules(self):
        self.analytics_engine.remaining = 11

        report = self.engine.generate()

        self.assertEqual(
            report["sessions"],
            11,
        )

    def test_generate_returns_all_expected_fields(self):
        report = self.engine.generate()

        expected_fields = {
            "phase",
            "current_milestone",
            "completion",
            "velocity",
            "remaining",
            "next_module",
            "sessions",
            "recommendation",
        }

        self.assertEqual(
            set(report.keys()),
            expected_fields,
        )

    # ------------------------------------------------------
    # Formatting
    # ------------------------------------------------------

    def test_format_report_contains_title(self):
        report = self.engine.format_report()

        self.assertIn(
            "ENGINEERING INSIGHTS",
            report,
        )

    def test_format_report_contains_current_phase(self):
        report = self.engine.format_report()

        self.assertIn(
            "Current Phase",
            report,
        )
        self.assertIn(
            "Foundation Phase",
            report,
        )

    def test_format_report_contains_current_milestone(self):
        report = self.engine.format_report()

        self.assertIn(
            "Current Milestone",
            report,
        )
        self.assertIn(
            "Foundation",
            report,
        )

    def test_format_report_formats_completion_to_one_decimal_place(self):
        self.analytics_engine.completion = 37.567

        report = self.engine.format_report()

        self.assertIn(
            "37.6%",
            report,
        )

    def test_format_report_contains_velocity(self):
        report = self.engine.format_report()

        self.assertIn(
            "Engineering Velocity",
            report,
        )
        self.assertIn(
            "3 module(s)",
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

    def test_format_report_contains_next_module(self):
        report = self.engine.format_report()

        self.assertIn(
            "Recommended Next Module",
            report,
        )
        self.assertIn(
            "modules.first_module",
            report,
        )

    def test_format_report_contains_sessions(self):
        report = self.engine.format_report()

        self.assertIn(
            "Estimated Sessions Remaining",
            report,
        )
        self.assertIn(
            "\n9\n",
            report,
        )

    def test_format_report_contains_recommendation(self):
        report = self.engine.format_report()

        self.assertIn(
            "Recommendation",
            report,
        )
        self.assertIn(
            "Focus on the Foundation milestone",
            report,
        )


if __name__ == "__main__":
    unittest.main()