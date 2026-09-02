"""
Nova Engine v127
Engineering Achievement Engine Tests

Verifies that EngineeringAchievementEngine:
- requests milestone progress,
- identifies completed milestones,
- ignores incomplete milestones,
- ignores zero-total milestones,
- creates achievements with completion dates,
- avoids duplicate achievements,
- persists new achievements,
- returns stored achievements,
- formats empty and populated achievement reports.
"""

from __future__ import annotations

import unittest
from datetime import datetime

from modules.engineering_achievements import EngineeringAchievementEngine


class MockHistory:

    def __init__(self):
        self.calls = []


class MockMilestoneEngine:

    def __init__(self, progress=None):
        self.progress = progress or []
        self.calls = []

    def milestone_progress(self):
        self.calls.append(("milestone_progress",))
        return self.progress


class MockMemory:

    def __init__(self, achievements=None):
        self._achievements = list(achievements or [])
        self.has_calls = []
        self.add_calls = []
        self.achievements_calls = 0

    def has_achievement(self, name):
        self.has_calls.append(name)

        return any(
            achievement["name"] == name
            for achievement in self._achievements
        )

    def add_achievement(self, achievement):
        self.add_calls.append(achievement)
        self._achievements.append(achievement)

    def achievements(self):
        self.achievements_calls += 1
        return list(self._achievements)


class TestEngineeringAchievementEngine(unittest.TestCase):

    def setUp(self):
        self.history = MockHistory()

        self.milestone_engine = MockMilestoneEngine(
            progress=[
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
                    "completed": 4,
                    "total": 4,
                },
            ]
        )

        self.memory = MockMemory()

        self.engine = EngineeringAchievementEngine(
            self.history,
            self.milestone_engine,
            self.memory,
        )

    # ------------------------------------------------------
    # Dependency calls
    # ------------------------------------------------------

    def test_achievements_requests_milestone_progress(self):
        self.engine.achievements()

        self.assertEqual(
            self.milestone_engine.calls,
            [("milestone_progress",)],
        )

    def test_achievements_returns_memory_achievements(self):
        expected = [
            {
                "name": "Existing",
                "completed_on": "2026-01-01",
            }
        ]

        self.milestone_engine.progress = []

        self.memory = MockMemory(expected)

        engine = EngineeringAchievementEngine(
            self.history,
            self.milestone_engine,
            self.memory,
        )

        result = engine.achievements()

        self.assertEqual(
            result,
            expected,
        )

    def test_achievements_requests_stored_achievements(self):
        self.engine.achievements()

        self.assertEqual(
            self.memory.achievements_calls,
            1,
        )

    # ------------------------------------------------------
    # Completed milestone detection
    # ------------------------------------------------------

    def test_completed_milestone_creates_achievement(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        result = self.engine.achievements()

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            result[0]["name"],
            "Foundation",
        )

    def test_incomplete_milestone_does_not_create_achievement(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 2,
                "total": 3,
            }
        ]

        result = self.engine.achievements()

        self.assertEqual(
            result,
            [],
        )
        self.assertEqual(
            self.memory.add_calls,
            [],
        )

    def test_zero_total_milestone_does_not_create_achievement(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 0,
                "total": 0,
            }
        ]

        result = self.engine.achievements()

        self.assertEqual(
            result,
            [],
        )
        self.assertEqual(
            self.memory.add_calls,
            [],
        )

    def test_partially_completed_milestone_does_not_create_achievement(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 1,
                "total": 2,
            }
        ]

        self.engine.achievements()

        self.assertEqual(
            self.memory.add_calls,
            [],
        )

    # ------------------------------------------------------
    # Achievement creation
    # ------------------------------------------------------

    def test_created_achievement_contains_milestone_name(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        self.engine.achievements()

        self.assertEqual(
            self.memory.add_calls[0]["name"],
            "Foundation",
        )

    def test_created_achievement_contains_completion_date(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        self.engine.achievements()

        achievement = self.memory.add_calls[0]

        self.assertEqual(
            achievement["completed_on"],
            datetime.now().strftime("%Y-%m-%d"),
        )

    def test_completion_date_uses_expected_format(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        self.engine.achievements()

        completed_on = self.memory.add_calls[0]["completed_on"]

        datetime.strptime(
            completed_on,
            "%Y-%m-%d",
        )

    def test_completed_milestone_is_persisted_through_memory(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        self.engine.achievements()

        self.assertEqual(
            len(self.memory.add_calls),
            1,
        )

    # ------------------------------------------------------
    # Duplicate prevention
    # ------------------------------------------------------

    def test_existing_achievement_is_not_added_again(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        self.memory = MockMemory(
            achievements=[
                {
                    "name": "Foundation",
                    "completed_on": "2026-01-01",
                }
            ]
        )

        engine = EngineeringAchievementEngine(
            self.history,
            self.milestone_engine,
            self.memory,
        )

        result = engine.achievements()

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            self.memory.add_calls,
            [],
        )

    def test_existing_achievement_is_checked_by_name(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        self.engine.achievements()

        self.assertEqual(
            self.memory.has_calls,
            ["Foundation"],
        )

    # ------------------------------------------------------
    # Multiple milestones
    # ------------------------------------------------------

    def test_multiple_completed_milestones_create_multiple_achievements(self):
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

        result = self.engine.achievements()

        self.assertEqual(
            len(result),
            3,
        )

        self.assertEqual(
            [achievement["name"] for achievement in result],
            [
                "Foundation",
                "Engineering Intelligence",
                "Automation",
            ],
        )

    def test_mixed_milestones_only_completed_positive_totals_are_added(self):
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
                "completed": 0,
                "total": 0,
            },
        ]

        result = self.engine.achievements()

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            result[0]["name"],
            "Foundation",
        )

    def test_empty_milestone_progress_returns_existing_achievements(self):
        existing = [
            {
                "name": "Foundation",
                "completed_on": "2026-01-01",
            }
        ]

        self.milestone_engine.progress = []
        self.memory = MockMemory(existing)

        engine = EngineeringAchievementEngine(
            self.history,
            self.milestone_engine,
            self.memory,
        )

        result = engine.achievements()

        self.assertEqual(
            result,
            existing,
        )

    # ------------------------------------------------------
    # Formatting
    # ------------------------------------------------------

    def test_format_report_contains_title(self):
        report = self.engine.format_report()

        self.assertIn(
            "ENGINEERING ACHIEVEMENTS",
            report,
        )

    def test_format_report_empty_state(self):
        self.milestone_engine.progress = []

        report = self.engine.format_report()

        self.assertIn(
            "No milestones completed yet.",
            report,
        )

    def test_format_report_contains_achievement_name(self):
        self.milestone_engine.progress = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
            }
        ]

        report = self.engine.format_report()

        self.assertIn(
            "Foundation",
            report,
        )

    def test_format_report_contains_completed_date(self):
        existing = [
            {
                "name": "Foundation",
                "completed_on": "2026-01-15",
            }
        ]

        self.milestone_engine.progress = []
        self.memory = MockMemory(existing)

        engine = EngineeringAchievementEngine(
            self.history,
            self.milestone_engine,
            self.memory,
        )

        report = engine.format_report()

        self.assertIn(
            "Completed: 2026-01-15",
            report,
        )

    def test_format_report_contains_trophy_marker(self):
        existing = [
            {
                "name": "Foundation",
                "completed_on": "2026-01-15",
            }
        ]

        self.milestone_engine.progress = []
        self.memory = MockMemory(existing)

        engine = EngineeringAchievementEngine(
            self.history,
            self.milestone_engine,
            self.memory,
        )

        report = engine.format_report()

        self.assertIn(
            "🏆 Foundation",
            report,
        )

    def test_format_report_contains_multiple_achievements(self):
        existing = [
            {
                "name": "Foundation",
                "completed_on": "2026-01-15",
            },
            {
                "name": "Automation",
                "completed_on": "2026-02-15",
            },
        ]

        self.milestone_engine.progress = []
        self.memory = MockMemory(existing)

        engine = EngineeringAchievementEngine(
            self.history,
            self.milestone_engine,
            self.memory,
        )

        report = engine.format_report()

        self.assertIn(
            "Foundation",
            report,
        )
        self.assertIn(
            "Automation",
            report,
        )


if __name__ == "__main__":
    unittest.main()