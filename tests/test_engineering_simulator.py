"""
Nova Engine v115
Engineering Simulator Tests

Verifies that simulation predictions remain internally
consistent with the authoritative engineering score model.
"""

from __future__ import annotations

import unittest

from modules.engineering_graph import EngineeringGraph
from modules.engineering_simulator import EngineeringSimulator


class MockScore:

    def __init__(
        self,
        module,
        score,
        dependency_count,
    ):
        self.module = module
        self.score = score
        self.dependency_count = dependency_count


class MockRisk:

    def __init__(self, risk):
        self.risk = risk


class MockScoreEngine:

    def __init__(self, graph):
        self.graph = graph

    def calculate(self, module):
        node = self.graph.get_node(module)

        if node is None:
            raise ValueError(
                f"Unknown module: {module}"
            )

        dependencies = len(node.dependencies)

        scores = {
            "modules.target": 4.5,
            "modules.other": 8.0,
            "modules.third": 9.0,
        }

        return MockScore(
            module,
            scores[module],
            dependencies,
        )


class MockRiskEngine:

    def analyze(self, module):
        return MockRisk("HIGH")


class TestEngineeringSimulator(unittest.TestCase):

    def setUp(self):
        self.graph = EngineeringGraph()

        self.graph.add_module(
            module="modules.target",
            dependencies=[
                "json",
                "os",
                "typing",
                "pathlib",
                "dataclasses",
            ],
        )

        self.graph.add_module(
            module="modules.other",
            dependencies=[
                "json",
            ],
        )

        self.graph.add_module(
            module="modules.third",
            dependencies=[
                "json",
            ],
        )

        self.score_engine = MockScoreEngine(
            self.graph
        )

        self.simulator = EngineeringSimulator(
            self.graph,
            self.score_engine,
            MockRiskEngine(),
        )

    def test_simulation_returns_current_score(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        self.assertEqual(
            result.current_score,
            4.5,
        )

    def test_simulation_returns_current_risk(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        self.assertEqual(
            result.current_risk,
            "HIGH",
        )

    def test_predicted_score_is_higher_than_current(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        self.assertGreater(
            result.predicted_score,
            result.current_score,
        )

    def test_predicted_score_does_not_exceed_ten(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        self.assertLessEqual(
            result.predicted_score,
            10.0,
        )

    def test_prediction_is_not_hard_coded_plus_three(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        self.assertNotEqual(
            result.predicted_score,
            result.current_score + 3.0,
        )

    def test_confidence_is_not_hard_coded_85(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        self.assertNotEqual(
            result.confidence,
            85,
        )

    def test_confidence_is_valid_percentage(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        self.assertGreaterEqual(
            result.confidence,
            0,
        )

        self.assertLessEqual(
            result.confidence,
            100,
        )

    def test_predicted_health_matches_simulated_score(self):
        result = self.simulator.simulate(
            "modules.target"
        )

        current_total = (
            4.5 +
            8.0 +
            9.0
        )

        predicted_total = (
            current_total
            - 4.5
            + result.predicted_score
        )

        expected_health = round(
            predicted_total / 3 * 10,
            1,
        )

        self.assertEqual(
            result.predicted_health,
            expected_health,
        )


if __name__ == "__main__":
    unittest.main()
