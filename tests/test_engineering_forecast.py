"""
Nova Engine v118
Engineering Forecast Tests

Verifies that engineering forecasts use the authoritative
EngineeringHealth baseline and EngineeringSimulator predictions.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from modules.engineering_forecast import EngineeringForecastEngine
from modules.engineering_graph import EngineeringGraph


@dataclass
class MockRoadmapItem:
    module: str
    priority: str = "HIGH"


class MockPlanner:

    def __init__(self, modules):
        self.modules = modules

    def generate(self):
        return [
            MockRoadmapItem(module)
            for module in self.modules
        ]


@dataclass
class MockHealthReport:
    engineering_health: float


class MockHealthEngine:

    def __init__(self, health):
        self.health = health
        self.calls = 0

    def analyze(self):
        self.calls += 1
        return MockHealthReport(
            engineering_health=self.health
        )


@dataclass
class MockSimulation:
    predicted_health: float


class MockSimulator:

    def __init__(self, graph, predictions):
        self.graph = graph
        self.predictions = predictions
        self.calls = []

    def simulate(self, module):
        self.calls.append(module)

        return MockSimulation(
            predicted_health=self.predictions[module]
        )


class TestEngineeringForecast(unittest.TestCase):

    def setUp(self) -> None:
        graph = EngineeringGraph()

        graph.add_module(
            module="modules.first",
            dependencies=["json"],
        )

        graph.add_module(
            module="modules.second",
            dependencies=["json", "os"],
        )

        graph.add_module(
            module="modules.third",
            dependencies=["json", "os", "typing"],
        )

        self.graph = graph

        self.planner = MockPlanner(
            [
                "modules.first",
                "modules.second",
                "modules.third",
            ]
        )

        self.health = MockHealthEngine(
            health=80.0
        )

        self.simulator = MockSimulator(
            graph,
            predictions={
                "modules.first": 83.5,
                "modules.second": 86.0,
                "modules.third": 88.5,
            },
        )

        self.forecast = EngineeringForecastEngine(
            self.planner,
            self.health,
            self.simulator,
        )

    def test_forecast_uses_authoritative_health_baseline(self) -> None:
        results = self.forecast.generate()

        self.assertEqual(
            len(results),
            3,
        )

        for result in results:
            self.assertEqual(
                result.current_health,
                80.0,
            )

        self.assertEqual(
            self.health.calls,
            1,
        )

    def test_forecast_delegates_prediction_to_simulator(self) -> None:
        self.forecast.generate()

        self.assertEqual(
            self.simulator.calls,
            [
                "modules.first",
                "modules.second",
                "modules.third",
            ],
        )

    def test_forecast_uses_simulated_predicted_health(self) -> None:
        results = self.forecast.generate()

        self.assertEqual(
            results[0].predicted_health,
            83.5,
        )

        self.assertEqual(
            results[1].predicted_health,
            86.0,
        )

        self.assertEqual(
            results[2].predicted_health,
            88.5,
        )

    def test_improvement_is_predicted_health_minus_current_health(
        self,
    ) -> None:
        results = self.forecast.generate()

        self.assertEqual(
            results[0].improvement,
            3.5,
        )

        self.assertEqual(
            results[1].improvement,
            6.0,
        )

        self.assertEqual(
            results[2].improvement,
            8.5,
        )

    def test_limit_restricts_number_of_forecasts(self) -> None:
        results = self.forecast.generate(
            limit=2
        )

        self.assertEqual(
            len(results),
            2,
        )

        self.assertEqual(
            self.simulator.calls,
            [
                "modules.first",
                "modules.second",
            ],
        )

    def test_forecast_does_not_mutate_health_baseline(self) -> None:
        results = self.forecast.generate()

        self.assertTrue(
            all(
                result.current_health == 80.0
                for result in results
            )
        )


if __name__ == "__main__":
    unittest.main()