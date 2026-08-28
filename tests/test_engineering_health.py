"""
Nova Engine v114
Engineering Health Tests

Verifies that project-wide engineering health is calculated
from the authoritative EngineeringScoreEngine.
"""

from __future__ import annotations

import unittest

from modules.engineering_graph import EngineeringGraph
from modules.engineering_health import EngineeringHealth
from modules.engineering_score import EngineeringScoreEngine
from modules.risk_engine import RiskEngine


class TestEngineeringHealth(unittest.TestCase):

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

        risk_engine = RiskEngine(graph)

        score_engine = EngineeringScoreEngine(
            graph,
            risk_engine,
        )

        self.health = EngineeringHealth(
            graph,
            score_engine,
        )

    def test_health_uses_authoritative_scores(self) -> None:
        report = self.health.analyze()

        self.assertEqual(
            report.total_modules,
            2,
        )

        # simple = 9.7
        # moderate = 6.5
        # average = 8.1
        # health = 81.0%
        self.assertEqual(
            report.engineering_health,
            81.0,
        )

    def test_risk_counts_match_score_assessments(self) -> None:
        report = self.health.analyze()

        self.assertEqual(report.low_risk, 1)
        self.assertEqual(report.medium_risk, 1)
        self.assertEqual(report.high_risk, 0)

    def test_empty_graph_has_full_health(self) -> None:
        graph = EngineeringGraph()
        risk_engine = RiskEngine(graph)
        score_engine = EngineeringScoreEngine(
            graph,
            risk_engine,
        )

        health = EngineeringHealth(
            graph,
            score_engine,
        )

        report = health.analyze()

        self.assertEqual(report.total_modules, 0)
        self.assertEqual(report.engineering_health, 100.0)


if __name__ == "__main__":
    unittest.main()