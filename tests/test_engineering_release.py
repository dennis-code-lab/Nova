"""
Nova Engine v129
Engineering Release Manager Tests

Verifies that EngineeringReleaseManager:
- gathers release metrics from its dependencies
- sorts completed modules
- retrieves milestones and achievements
- resolves engineering health correctly
- returns the expected release metadata
- formats the release summary correctly
"""

import unittest

from modules.engineering_release import EngineeringReleaseManager


class MockHistory:
    def __init__(self, completed=None):
        self.completed = list(completed or [])
        self.calls = []

    def completed_modules(self):
        self.calls.append(("completed_modules",))
        return list(self.completed)


class MockMilestoneEngine:
    def __init__(self, milestones=None):
        self.milestones = list(milestones or [])
        self.calls = []

    def completed(self):
        self.calls.append(("completed",))
        return list(self.milestones)


class MockAchievementEngine:
    def __init__(self, achievements=None):
        self._achievements = list(achievements or [])
        self.calls = []

    def achievements(self):
        self.calls.append(("achievements",))
        return list(self._achievements)


class ScoreHealthEngine:
    def __init__(self, score=87.5):
        self._score = score
        self.calls = []

    def score(self):
        self.calls.append(("score",))
        return self._score


class HealthOnlyEngine:
    def __init__(self, health=76.25):
        self._health = health
        self.calls = []

    def health(self):
        self.calls.append(("health",))
        return self._health


class EmptyHealthEngine:
    pass


class TestEngineeringReleaseManager(unittest.TestCase):

    def setUp(self):
        self.history = MockHistory()
        self.milestone_engine = MockMilestoneEngine()
        self.achievement_engine = MockAchievementEngine()
        self.health_engine = ScoreHealthEngine()

        self.engine = EngineeringReleaseManager(
            self.history,
            self.milestone_engine,
            self.achievement_engine,
            self.health_engine,
        )

    # ---------------------------------------------------------
    # Dependency tests
    # ---------------------------------------------------------

    def test_release_requests_completed_modules(self):
        self.engine.release()

        self.assertIn(
            ("completed_modules",),
            self.history.calls,
        )

    def test_release_requests_completed_milestones(self):
        self.engine.release()

        self.assertIn(
            ("completed",),
            self.milestone_engine.calls,
        )

    def test_release_requests_achievements(self):
        self.engine.release()

        self.assertIn(
            ("achievements",),
            self.achievement_engine.calls,
        )

    def test_release_requests_health_score_when_available(self):
        self.engine.release()

        self.assertIn(
            ("score",),
            self.health_engine.calls,
        )

    # ---------------------------------------------------------
    # Completed module tests
    # ---------------------------------------------------------

    def test_release_returns_completed_modules(self):
        self.history.completed = [
            "modules.beta",
            "modules.alpha",
        ]

        report = self.engine.release()

        self.assertEqual(
            report["completed"],
            [
                "modules.alpha",
                "modules.beta",
            ],
        )

    def test_release_sorts_completed_modules(self):
        self.history.completed = [
            "zeta",
            "alpha",
            "gamma",
            "beta",
        ]

        report = self.engine.release()

        self.assertEqual(
            report["completed"],
            [
                "alpha",
                "beta",
                "gamma",
                "zeta",
            ],
        )

    def test_release_returns_empty_completed_modules(self):
        report = self.engine.release()

        self.assertEqual(report["completed"], [])

    # ---------------------------------------------------------
    # Milestone tests
    # ---------------------------------------------------------

    def test_release_returns_completed_milestones(self):
        milestones = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
                "percent": 100.0,
            }
        ]
        self.milestone_engine.milestones = milestones

        report = self.engine.release()

        self.assertEqual(
            report["milestones"],
            milestones,
        )

    def test_release_returns_multiple_milestones(self):
        milestones = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
                "percent": 100.0,
            },
            {
                "name": "Engineering Intelligence",
                "completed": 5,
                "total": 5,
                "percent": 100.0,
            },
        ]
        self.milestone_engine.milestones = milestones

        report = self.engine.release()

        self.assertEqual(
            report["milestones"],
            milestones,
        )

    def test_release_returns_empty_milestones(self):
        report = self.engine.release()

        self.assertEqual(report["milestones"], [])

    # ---------------------------------------------------------
    # Achievement tests
    # ---------------------------------------------------------

    def test_release_returns_achievements(self):
        achievements = [
            {
                "name": "Foundation",
                "completed_on": "2026-08-01",
            }
        ]
        self.achievement_engine._achievements = achievements

        report = self.engine.release()

        self.assertEqual(
            report["achievements"],
            achievements,
        )

    def test_release_returns_multiple_achievements(self):
        achievements = [
            {
                "name": "Foundation",
                "completed_on": "2026-08-01",
            },
            {
                "name": "Engineering Intelligence",
                "completed_on": "2026-08-02",
            },
        ]
        self.achievement_engine._achievements = achievements

        report = self.engine.release()

        self.assertEqual(
            report["achievements"],
            achievements,
        )

    def test_release_returns_empty_achievements(self):
        report = self.engine.release()

        self.assertEqual(report["achievements"], [])

    # ---------------------------------------------------------
    # Health tests
    # ---------------------------------------------------------

    def test_release_uses_score_when_available(self):
        self.health_engine = ScoreHealthEngine(91.75)

        engine = EngineeringReleaseManager(
            self.history,
            self.milestone_engine,
            self.achievement_engine,
            self.health_engine,
        )

        report = engine.release()

        self.assertEqual(report["health"], 91.75)

    def test_release_converts_score_to_float(self):
        self.health_engine = ScoreHealthEngine(88)

        engine = EngineeringReleaseManager(
            self.history,
            self.milestone_engine,
            self.achievement_engine,
            self.health_engine,
        )

        report = engine.release()

        self.assertEqual(report["health"], 88.0)
        self.assertIsInstance(report["health"], float)

    def test_release_falls_back_to_health_method(self):
        health_engine = HealthOnlyEngine(76.25)

        engine = EngineeringReleaseManager(
            self.history,
            self.milestone_engine,
            self.achievement_engine,
            health_engine,
        )

        report = engine.release()

        self.assertEqual(report["health"], 76.25)
        self.assertIn(("health",), health_engine.calls)

    def test_release_falls_back_to_default_health(self):
        health_engine = EmptyHealthEngine()

        engine = EngineeringReleaseManager(
            self.history,
            self.milestone_engine,
            self.achievement_engine,
            health_engine,
        )

        report = engine.release()

        self.assertEqual(report["health"], 100.0)

    # ---------------------------------------------------------
    # Release metadata tests
    # ---------------------------------------------------------

    def test_release_version_is_v98(self):
        report = self.engine.release()

        self.assertEqual(report["version"], "v98")

    def test_release_status_is_ready(self):
        report = self.engine.release()

        self.assertEqual(report["status"], "READY")

    def test_release_contains_expected_fields(self):
        report = self.engine.release()

        expected_fields = {
            "version",
            "completed",
            "milestones",
            "achievements",
            "health",
            "status",
        }

        self.assertEqual(
            set(report.keys()),
            expected_fields,
        )

    def test_release_empty_state_is_valid(self):
        report = self.engine.release()

        self.assertEqual(report["completed"], [])
        self.assertEqual(report["milestones"], [])
        self.assertEqual(report["achievements"], [])
        self.assertEqual(report["health"], 87.5)
        self.assertEqual(report["status"], "READY")

    # ---------------------------------------------------------
    # format_release tests
    # ---------------------------------------------------------

    def test_format_release_contains_release_title(self):
        report = self.engine.format_release()

        self.assertIn("RELEASE v98", report)

    def test_format_release_contains_completed_modules_heading(self):
        report = self.engine.format_release()

        self.assertIn("Completed Modules", report)

    def test_format_release_contains_milestones_heading(self):
        report = self.engine.format_release()

        self.assertIn("Milestones", report)

    def test_format_release_contains_achievements_heading(self):
        report = self.engine.format_release()

        self.assertIn("Achievements", report)

    def test_format_release_contains_engineering_health_heading(self):
        report = self.engine.format_release()

        self.assertIn("Engineering Health", report)

    def test_format_release_contains_release_status_heading(self):
        report = self.engine.format_release()

        self.assertIn("Release Status", report)

    def test_format_release_contains_completed_module(self):
        self.history.completed = [
            "modules.engineering_runtime",
        ]

        report = self.engine.format_release()

        self.assertIn(
            "modules.engineering_runtime",
            report,
        )

    def test_format_release_contains_multiple_completed_modules(self):
        self.history.completed = [
            "modules.engineering_runtime",
            "modules.engineering_memory",
        ]

        report = self.engine.format_release()

        self.assertIn(
            "modules.engineering_runtime",
            report,
        )
        self.assertIn(
            "modules.engineering_memory",
            report,
        )

    def test_format_release_contains_milestone_name(self):
        self.milestone_engine.milestones = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
                "percent": 100.0,
            }
        ]

        report = self.engine.format_release()

        self.assertIn("Foundation", report)

    def test_format_release_contains_multiple_milestones(self):
        self.milestone_engine.milestones = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
                "percent": 100.0,
            },
            {
                "name": "Automation",
                "completed": 4,
                "total": 4,
                "percent": 100.0,
            },
        ]

        report = self.engine.format_release()

        self.assertIn("Foundation", report)
        self.assertIn("Automation", report)

    def test_format_release_contains_achievement_name(self):
        self.achievement_engine._achievements = [
            {
                "name": "Foundation",
                "completed_on": "2026-08-01",
            }
        ]

        report = self.engine.format_release()

        self.assertIn("Foundation", report)

    def test_format_release_contains_multiple_achievement_names(self):
        self.achievement_engine._achievements = [
            {
                "name": "Foundation",
                "completed_on": "2026-08-01",
            },
            {
                "name": "Automation",
                "completed_on": "2026-08-02",
            },
        ]

        report = self.engine.format_release()

        self.assertIn("Foundation", report)
        self.assertIn("Automation", report)

    def test_format_release_formats_health_to_one_decimal_place(self):
        self.health_engine = ScoreHealthEngine(87.56)

        engine = EngineeringReleaseManager(
            self.history,
            self.milestone_engine,
            self.achievement_engine,
            self.health_engine,
        )

        report = engine.format_release()

        self.assertIn("87.6%", report)

    def test_format_release_contains_ready_status(self):
        report = self.engine.format_release()

        self.assertIn("READY", report)

    def test_format_release_uses_none_for_empty_completed_modules(self):
        report = self.engine.format_release()

        self.assertIn("Completed Modules", report)
        self.assertIn("None", report)

    def test_format_release_uses_none_for_empty_milestones(self):
        report = self.engine.format_release()

        self.assertIn("Milestones", report)
        self.assertIn("None", report)

    def test_format_release_uses_none_for_empty_achievements(self):
        report = self.engine.format_release()

        self.assertIn("Achievements", report)
        self.assertIn("None", report)

    def test_format_release_contains_multiple_sections(self):
        self.history.completed = [
            "modules.engineering_runtime",
        ]
        self.milestone_engine.milestones = [
            {
                "name": "Foundation",
                "completed": 3,
                "total": 3,
                "percent": 100.0,
            }
        ]
        self.achievement_engine._achievements = [
            {
                "name": "Foundation",
                "completed_on": "2026-08-01",
            }
        ]

        report = self.engine.format_release()

        self.assertIn("Completed Modules", report)
        self.assertIn("Milestones", report)
        self.assertIn("Achievements", report)
        self.assertIn("Engineering Health", report)
        self.assertIn("Release Status", report)

    def test_format_release_reflects_release_health(self):
        self.health_engine = ScoreHealthEngine(63.42)

        engine = EngineeringReleaseManager(
            self.history,
            self.milestone_engine,
            self.achievement_engine,
            self.health_engine,
        )

        report = engine.format_release()

        self.assertIn("63.4%", report)


if __name__ == "__main__":
    unittest.main()