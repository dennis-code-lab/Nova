"""
Nova Engine v84
Unit Tests - Risk Engine

Verifies risk assessment calculation across different dependency surfaces
and engineering impact scores.
"""

from __future__ import annotations

import unittest

from modules.engineering_graph import EngineeringGraph
from modules.risk_engine import RiskEngine


class TestRiskEngine(unittest.TestCase):

    def setUp(self) -> None:
        graph = EngineeringGraph()

        graph.add_module(
            module="modules.ai",
            dependencies=[
                "json",
                "os",
                "requests",
                "typing",
                "re",
                "math",
            ],
            impact_score=4.5,
            risk="LOW",
        )

        graph.add_module(
            module="modules.logger",
            dependencies=["datetime"],
            impact_score=9.0,
            risk="LOW",
        )

        self.engine = RiskEngine(graph)

    def test_medium_risk(self) -> None:
        result = self.engine.analyze("modules.ai")

        self.assertEqual(result.module, "modules.ai")
        self.assertEqual(result.risk, "MEDIUM")
        self.assertEqual(result.dependency_count, 6)

    def test_low_risk(self) -> None:
        result = self.engine.analyze("modules.logger")

        self.assertEqual(result.risk, "LOW")

    def test_unknown_module(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.analyze("modules.fake")


if __name__ == "__main__":
    unittest.main()