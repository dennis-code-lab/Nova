"""
Nova Engine
Engineering Score Tests

Baseline tests for EngineeringScoreEngine.
"""

from __future__ import annotations

import unittest

from modules.engineering_graph import EngineeringGraph
from modules.engineering_score import EngineeringScoreEngine
from modules.risk_engine import RiskEngine


class TestEngineeringScore(unittest.TestCase):

    def setUp(self) -> None:
        graph = EngineeringGraph()

        graph.add_module(
            module="modules.simple",
            dependencies=["json"],
        )

        graph.add_module(
            module="modules.moderate",
            dependencies=[
                "json",
                "os",
                "typing",
                "pathlib",
                "dataclasses",
            ],
        )

        graph.add_module(
            module="modules.complex",
            dependencies=[
                "json",
                "os",
                "typing",
                "pathlib",
                "dataclasses",
                "requests",
                "math",
                "re",
                "sys",
                "logging",
            ],
        )

        risk_engine = RiskEngine(graph)

        self.engine = EngineeringScoreEngine(
            graph,
            risk_engine,
        )

    def test_simple_module(self) -> None:
        result = self.engine.calculate("modules.simple")

        self.assertEqual(result.module, "modules.simple")
        self.assertEqual(result.dependency_count, 1)
        self.assertEqual(result.score, 9.7)
        self.assertEqual(result.risk, "LOW")

    def test_moderate_module(self) -> None:
        result = self.engine.calculate("modules.moderate")

        self.assertEqual(result.module, "modules.moderate")
        self.assertEqual(result.dependency_count, 5)
        self.assertEqual(result.score, 6.5)
        self.assertEqual(result.risk, "MEDIUM")

    def test_complex_module(self) -> None:
        result = self.engine.calculate("modules.complex")

        self.assertEqual(result.module, "modules.complex")
        self.assertEqual(result.dependency_count, 10)
        self.assertEqual(result.score, 3.0)
        self.assertEqual(result.risk, "HIGH")

    def test_score_is_authoritative_health_score(self) -> None:
        result = self.engine.calculate("modules.simple")

        self.assertEqual(result.score, 9.7)
        self.assertGreaterEqual(result.score, 0.0)
        self.assertLessEqual(result.score, 10.0)

    def test_unknown_module(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.calculate("modules.fake")


if __name__ == "__main__":
    unittest.main()