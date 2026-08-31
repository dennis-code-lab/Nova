"""
Nova Engine v119
Engineering Decision Engine Tests

Verifies that engineering decisions:
- select the highest-priority remaining roadmap item,
- ignore completed modules,
- delegate recommendations to EngineeringAdvisor,
- delegate projections and confidence to EngineeringSimulator,
- fail clearly when no roadmap items remain.
"""

from __future__ import annotations

import unittest

from modules.engineering_decision_engine import EngineeringDecisionEngine
from modules.engineering_planner_v2 import RoadmapItem


class MockPlanner:
    def __init__(self, roadmap):
        self.roadmap = roadmap
        self.calls = 0

    def generate(self):
        self.calls += 1
        return list(self.roadmap)


class MockAdvice:
    def __init__(
        self,
        priority,
        estimated_effort,
        recommendation,
    ):
        self.priority = priority
        self.estimated_effort = estimated_effort
        self.recommendation = recommendation


class MockAdvisor:
    def __init__(self, advice):
        self.advice = advice
        self.calls = []

    def advise(self, module):
        self.calls.append(module)
        return self.advice


class MockSimulation:
    def __init__(
        self,
        predicted_health,
        confidence,
    ):
        self.predicted_health = predicted_health
        self.confidence = confidence


class MockSimulator:
    def __init__(self, simulation):
        self.simulation = simulation
        self.calls = []

    def simulate(self, module):
        self.calls.append(module)
        return self.simulation


class MockHistory:
    def __init__(self, completed=None):
        self.completed = set(completed or [])

    def is_completed(self, module):
        return module in self.completed


class TestEngineeringDecision(unittest.TestCase):

    def setUp(self):
        self.roadmap = [
            RoadmapItem(
                module="modules.first",
                priority="HIGH",
                engineering_score=2.5,
                estimated_effort="2-3 engineering hours",
                recommendation="Fix first module.",
            ),
            RoadmapItem(
                module="modules.second",
                priority="HIGH",
                engineering_score=4.0,
                estimated_effort="2-3 engineering hours",
                recommendation="Fix second module.",
            ),
            RoadmapItem(
                module="modules.third",
                priority="MEDIUM",
                engineering_score=6.0,
                estimated_effort="1-2 engineering hours",
                recommendation="Review third module.",
            ),
        ]

        self.planner = MockPlanner(self.roadmap)

        self.advice = MockAdvice(
            priority="HIGH",
            estimated_effort="2-3 engineering hours",
            recommendation="Split this module into smaller feature-specific modules.",
        )

        self.advisor = MockAdvisor(self.advice)

        self.simulation = MockSimulation(
            predicted_health=84.5,
            confidence=91,
        )

        self.simulator = MockSimulator(
            self.simulation
        )

        self.history = MockHistory()

        self.engine = EngineeringDecisionEngine(
            self.planner,
            self.advisor,
            self.simulator,
            self.history,
        )

    def test_decision_selects_first_remaining_roadmap_item(self):
        result = self.engine.decide()

        self.assertEqual(
            result.module,
            "modules.first",
        )

    def test_decision_uses_advisor_priority(self):
        result = self.engine.decide()

        self.assertEqual(
            result.priority,
            "HIGH",
        )

    def test_decision_uses_advisor_effort(self):
        result = self.engine.decide()

        self.assertEqual(
            result.effort,
            "2-3 engineering hours",
        )

    def test_decision_uses_advisor_recommendation(self):
        result = self.engine.decide()

        self.assertEqual(
            result.recommendation,
            "Split this module into smaller feature-specific modules.",
        )

    def test_decision_uses_simulated_predicted_health(self):
        result = self.engine.decide()

        self.assertEqual(
            result.projected_health,
            84.5,
        )

    def test_decision_uses_simulated_confidence(self):
        result = self.engine.decide()

        self.assertEqual(
            result.confidence,
            91,
        )

    def test_advisor_is_called_for_selected_module(self):
        self.engine.decide()

        self.assertEqual(
            self.advisor.calls,
            ["modules.first"],
        )

    def test_simulator_is_called_for_selected_module(self):
        self.engine.decide()

        self.assertEqual(
            self.simulator.calls,
            ["modules.first"],
        )

    def test_completed_high_priority_item_is_skipped(self):
        self.history.completed.add(
            "modules.first"
        )

        result = self.engine.decide()

        self.assertEqual(
            result.module,
            "modules.second",
        )

        self.assertEqual(
            self.advisor.calls,
            ["modules.second"],
        )

        self.assertEqual(
            self.simulator.calls,
            ["modules.second"],
        )

    def test_multiple_completed_items_are_skipped(self):
        self.history.completed.update(
            {
                "modules.first",
                "modules.second",
            }
        )

        result = self.engine.decide()

        self.assertEqual(
            result.module,
            "modules.third",
        )

    def test_all_completed_items_raise_runtime_error(self):
        self.history.completed.update(
            {
                "modules.first",
                "modules.second",
                "modules.third",
            }
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "All roadmap items have been completed.",
        ):
            self.engine.decide()

    def test_empty_roadmap_raises_runtime_error(self):
        self.planner.roadmap = []

        with self.assertRaisesRegex(
            RuntimeError,
            "All roadmap items have been completed.",
        ):
            self.engine.decide()

    def test_planner_is_called_once(self):
        self.engine.decide()

        self.assertEqual(
            self.planner.calls,
            1,
        )


if __name__ == "__main__":
    unittest.main()