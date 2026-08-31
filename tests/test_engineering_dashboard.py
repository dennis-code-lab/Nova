"""
Nova Engine v120
Engineering Dashboard Tests

Verifies that the engineering dashboard:
- uses the authoritative health engine,
- uses the engineering decision engine,
- reports completion state,
- renders projected health and confidence,
- clamps its health progress bar correctly.
"""

from __future__ import annotations

import unittest

from modules.engineering_dashboard import EngineeringDashboard


class MockHealthReport:
    def __init__(
        self,
        engineering_health,
        total_modules,
    ):
        self.engineering_health = engineering_health
        self.total_modules = total_modules


class MockHealth:
    def __init__(self, report):
        self.report = report
        self.calls = 0

    def analyze(self):
        self.calls += 1
        return self.report


class MockForecast:
    pass


class MockDecision:
    def __init__(
        self,
        module,
        priority,
        projected_health,
        confidence,
    ):
        self.module = module
        self.priority = priority
        self.projected_health = projected_health
        self.confidence = confidence


class MockDecisionEngine:
    def __init__(self, decision):
        self.decision = decision
        self.calls = 0

    def decide(self):
        self.calls += 1
        return self.decision


class MockHistory:
    def __init__(self, completed_count):
        self.count = completed_count
        self.calls = 0

    def completed_count(self):
        self.calls += 1
        return self.count


class TestEngineeringDashboard(unittest.TestCase):

    def setUp(self):
        self.report = MockHealthReport(
            engineering_health=81.0,
            total_modules=10,
        )

        self.health = MockHealth(
            self.report
        )

        self.decision = MockDecision(
            module="modules.target",
            priority="HIGH",
            projected_health=88.5,
            confidence=92,
        )

        self.decision_engine = MockDecisionEngine(
            self.decision
        )

        self.history = MockHistory(
            completed_count=3
        )

        self.dashboard = EngineeringDashboard(
            self.health,
            MockForecast(),
            self.decision_engine,
            self.history,
        )

    def test_dashboard_uses_health_engine(self):
        self.dashboard.generate()

        self.assertEqual(
            self.health.calls,
            1,
        )

    def test_dashboard_uses_decision_engine(self):
        self.dashboard.generate()

        self.assertEqual(
            self.decision_engine.calls,
            1,
        )

    def test_dashboard_uses_history(self):
        self.dashboard.generate()

        self.assertEqual(
            self.history.calls,
            1,
        )

    def test_dashboard_displays_engineering_health(self):
        output = self.dashboard.generate()

        self.assertIn(
            "Engineering Health : 81.0%",
            output,
        )

    def test_dashboard_displays_completed_improvements(self):
        output = self.dashboard.generate()

        self.assertIn(
            "Completed Improvements : 3",
            output,
        )

    def test_dashboard_calculates_remaining_improvements(self):
        output = self.dashboard.generate()

        self.assertIn(
            "Remaining Improvements : 7",
            output,
        )

    def test_dashboard_displays_highest_priority_module(self):
        output = self.dashboard.generate()

        self.assertIn(
            "Highest Priority : modules.target",
            output,
        )

    def test_dashboard_displays_priority(self):
        output = self.dashboard.generate()

        self.assertIn(
            "Priority         : HIGH",
            output,
        )

    def test_dashboard_displays_projected_health(self):
        output = self.dashboard.generate()

        self.assertIn(
            "Projected Health : 88.5%",
            output,
        )

    def test_dashboard_displays_confidence(self):
        output = self.dashboard.generate()

        self.assertIn(
            "Confidence       : 92%",
            output,
        )

    def test_dashboard_contains_title(self):
        output = self.dashboard.generate()

        self.assertIn(
            "NOVA ENGINEERING DASHBOARD",
            output,
        )

    def test_dashboard_bar_represents_health(self):
        bar = self.dashboard._bar(81.0)

        self.assertEqual(
            len(bar),
            10,
        )

        self.assertEqual(
            bar.count("█"),
            8,
        )

        self.assertEqual(
            bar.count("░"),
            2,
        )

    def test_dashboard_bar_clamps_above_100(self):
        bar = self.dashboard._bar(150.0)

        self.assertEqual(
            len(bar),
            10,
        )

        self.assertEqual(
            bar.count("█"),
            10,
        )

        self.assertEqual(
            bar.count("░"),
            0,
        )

    def test_dashboard_bar_clamps_below_zero(self):
        bar = self.dashboard._bar(-20.0)

        self.assertEqual(
            len(bar),
            10,
        )

        self.assertEqual(
            bar.count("█"),
            0,
        )

        self.assertEqual(
            bar.count("░"),
            10,
        )


if __name__ == "__main__":
    unittest.main()