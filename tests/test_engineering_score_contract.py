"""
Nova Engine v104
Engineering Score Contract Tests

Verifies that the authoritative engineering score is exposed
through EngineeringScoreEngine.
"""

from __future__ import annotations

import unittest

from modules.engineering_graph import EngineeringGraph
from modules.engineering_score import EngineeringScoreEngine
from modules.risk_engine import RiskEngine


class TestEngineeringScoreContract(unittest.TestCase):

    def setUp(self) -> None:
        graph = EngineeringGraph()

        graph.add_module(
            module="modules.target",
            dependencies=[
                "json",
                "os",
            ],
        )

        self.graph = graph
        self.risk_engine = RiskEngine(graph)
        self.score_engine = EngineeringScoreEngine(
            graph,
            self.risk_engine,
        )

    def test_authoritative_score_exists(self) -> None:
        result = self.score_engine.calculate("modules.target")

        self.assertIsInstance(result.score, float)
        self.assertGreaterEqual(result.score, 0.0)
        self.assertLessEqual(result.score, 10.0)

    def test_score_contains_module_identity(self) -> None:
        result = self.score_engine.calculate("modules.target")

        self.assertEqual(
            result.module,
            "modules.target",
        )

    def test_score_contains_dependency_count(self) -> None:
        result = self.score_engine.calculate("modules.target")

        self.assertEqual(
            result.dependency_count,
            2,
        )

    def test_risk_assessment_does_not_own_engineering_score(self) -> None:
        assessment = self.risk_engine.analyze("modules.target")

        self.assertFalse(
            hasattr(assessment, "engineering_score")
        )


if __name__ == "__main__":
    unittest.main()