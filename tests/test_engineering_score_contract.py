"""
Nova Engine v104
Engineering Score Contract Tests

Verifies that the authoritative engineering score is exposed
through EngineeringScoreEngine and remains independent from
the legacy ImpactEngine score.
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
            impact_score=8.0,
            risk="LOW",
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

    def test_legacy_impact_score_remains_separate(self) -> None:
        node = self.graph.get_node("modules.target")

        self.assertIsNotNone(node)
        self.assertEqual(node.impact_score, 8.0)

        score = self.score_engine.calculate("modules.target")

        self.assertNotEqual(
            score.score,
            node.impact_score,
        )

    def test_authoritative_score_is_independent_of_legacy_impact_score(
        self,
    ) -> None:
        node = self.graph.get_node("modules.target")

        self.assertIsNotNone(node)

        first = self.score_engine.calculate("modules.target")

        node.impact_score = 2.0

        second = self.score_engine.calculate("modules.target")

        self.assertEqual(
            first.score,
            second.score,
        )

    def test_risk_is_independent_of_legacy_impact_score(
        self,
    ) -> None:
        node = self.graph.get_node("modules.target")

        self.assertIsNotNone(node)

        first = self.risk_engine.analyze("modules.target")

        node.impact_score = 1.0

        second = self.risk_engine.analyze("modules.target")

        self.assertEqual(
            first.risk,
            second.risk,
        )


if __name__ == "__main__":
    unittest.main()